"""
Authentication routes module.
Contains endpoints for OAuth and platform integrations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import secrets
import json
import httpx
import os
from urllib.parse import urlencode
import jwt
import logging

from app.database import get_db
from app.models.integration import Integration, IntegrationType, IntegrationStatus, IntegrationAuthType
from app.schemas.integration import IntegrationStatusList, IntegrationUpdate, IntegrationCreate
from app.utils.security import get_optional_current_user
from app.models.user import User

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

# Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-do-not-use-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 30  # days

# OAuth configuration
OAUTH_CONFIG = {
    "youtube": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        "scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
        "redirect_uri": f"{APP_URL}/auth/youtube/callback",
    },
    "stripe": {
        "auth_url": "https://connect.stripe.com/oauth/authorize",
        "token_url": "https://connect.stripe.com/oauth/token",
        "client_id": os.getenv("STRIPE_CLIENT_ID", ""),
        "client_secret": os.getenv("STRIPE_SECRET_KEY", ""),
        "scopes": ["read_write"],
        "redirect_uri": f"{APP_URL}/auth/stripe/callback",
    },
    "calendly": {
        "auth_url": "https://auth.calendly.com/oauth/authorize",
        "token_url": "https://auth.calendly.com/oauth/token",
        "client_id": os.getenv("CALENDLY_CLIENT_ID", ""),
        "client_secret": os.getenv("CALENDLY_CLIENT_SECRET", ""),
        "scopes": ["default"],
        "redirect_uri": f"{APP_URL}/auth/calendly/callback",
    },
    "calcom": {
        "auth_url": "https://app.cal.com/auth/oauth",
        "token_url": "https://app.cal.com/api/auth/oauth/token",
        "client_id": os.getenv("CALCOM_CLIENT_ID", ""),
        "client_secret": os.getenv("CALCOM_CLIENT_SECRET", ""),
        "scopes": ["read_bookings", "read_profile"],
        "redirect_uri": f"{APP_URL}/auth/calcom/callback",
    }
}

# Helper functions
def get_oauth_config(platform: str):
    """Get OAuth configuration for a platform."""
    if platform not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(OAUTH_CONFIG.keys())}"
        )
    return OAUTH_CONFIG[platform]

# Get user ID from request (session or JWT)
def get_user_id(request: Request) -> int:
    """Extract user ID from session or JWT token."""
    # In a real app, you would use proper session management or JWT tokens
    # This is a simplified version that assumes a user ID in the session or query param
    
    # Try to get from session first
    user_id = request.session.get("user_id") if hasattr(request, "session") else None
    
    # Then try query param (for testing)
    if not user_id:
        user_id = request.query_params.get("user_id", "1")
    
    # Ensure it's an integer
    try:
        return int(user_id)
    except (TypeError, ValueError):
        return 1  # Default user ID for testing

# API routes
@router.get("/auth/{platform}")
async def initiate_auth(
    platform: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Initiate OAuth flow for a platform.
    
    Args:
        platform: The platform to authenticate with (youtube, stripe, calendly, calcom)
        
    Returns:
        RedirectResponse: Redirects to the platform's OAuth consent screen.
    """
    # Validate platform
    config = get_oauth_config(platform)
    
    # Get user ID from session or request
    user_id = get_user_id(request)
    
    # Generate state token to prevent CSRF
    state = f"{user_id}:{secrets.token_urlsafe(32)}"
    
    # Extra logging for Calendly to debug client_id issue
    if platform == "calendly":
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        logger.info(f"Calendly client_id: '{client_id}', length: {len(client_id)}")
        logger.info(f"CALENDLY_CLIENT_ID from env: '{os.getenv('CALENDLY_CLIENT_ID', 'not set')}'")
        logger.info(f"Calendly client_secret length: {len(client_secret) if client_secret else 0}")
        logger.info(f"Calendly auth URL: {config['auth_url']}")
        if not client_id:
            logger.error("Calendly client_id is empty - please check CALENDLY_CLIENT_ID environment variable")
        # Print all environment variables for debugging (without exposing secrets)
        env_vars = {k: (v[:5] + '...' + v[-5:] if len(v) > 10 else v) 
                    for k, v in os.environ.items() if k.startswith('CALENDLY')}
        logger.info(f"All Calendly environment variables: {env_vars}")
    
    # Extra logging for Cal.com to debug API issues
    if platform == "calcom":
        client_id = config["client_id"]
        logger.info(f"Cal.com client_id: '{client_id}', length: {len(client_id)}")
        logger.info(f"CALCOM_CLIENT_ID from env: '{os.getenv('CALCOM_CLIENT_ID', 'not set')}'")
        logger.info(f"Cal.com auth URL: {config['auth_url']}")
        if not client_id:
            logger.error("Cal.com client_id is empty - please check CALCOM_CLIENT_ID environment variable")
    
    # Build authorization URL
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": " ".join(config["scopes"]),
        "state": state,
        "access_type": "offline",  # For refresh tokens (Google-specific)
        "prompt": "consent",       # Force consent screen to get refresh token
    }
    
    # For Stripe, add additional params for Connect
    if platform == "stripe":
        params.update({
            "stripe_user[email]": request.query_params.get("email", ""),
            "stripe_user[url]": request.query_params.get("website", ""),
            "stripe_user[country]": request.query_params.get("country", "US"),
        })
    
    # For Cal.com, modify parameters according to their OAuth requirements
    if platform == "calcom":
        # Cal.com may use different parameter names
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "state": state,
        }
    
    # Log OAuth information for debugging
    logger.info(f"Initiating OAuth flow for platform: {platform}")
    logger.info(f"Using client_id: {params['client_id'][:5]}...{params['client_id'][-5:] if len(params['client_id']) > 10 else ''}")
    logger.info(f"Using redirect_uri: {params['redirect_uri']}")
    logger.info(f"Using scopes: {params['scope']}")
    
    # Log the complete auth URL for debugging
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    logger.info(f"Complete auth URL: {auth_url}")
    
    # Redirect to authorization URL
    return RedirectResponse(url=auth_url)

@router.get("/auth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    OAuth callback endpoint.
    Handles the redirect from the OAuth provider and exchanges the code for tokens.
    
    Args:
        platform: The platform (youtube, stripe, etc.)
        code: The authorization code from the OAuth provider
        state: State parameter for CSRF protection
        error: Error message if authorization failed
        
    Returns:
        RedirectResponse: Redirects back to the frontend
    """
    # Enhanced logging for debugging
    logger.info(f"OAuth callback received for platform: {platform}")
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Full request URL: {request.url}")
    logger.info(f"Code present: {bool(code)}")
    logger.info(f"State present: {bool(state)}")
    logger.info(f"Error present: {bool(error)}")
    
    # Log callback parameters
    if error:
        logger.error(f"OAuth error from provider: {error}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error={error}&platform={platform}"
        )
    
    if not code:
        logger.error(f"No authorization code provided in callback for {platform}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error=no_code&platform={platform}"
        )
    
    # Extract user ID from state
    user_id = 1
    if state and ":" in state:
        try:
            user_id, _ = state.split(":", 1)
            user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = 1
    
    try:
        # Get configuration
        config = get_oauth_config(platform)
        logger.info(f"Using redirect_uri for token exchange: {config['redirect_uri']}")
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": config["redirect_uri"]
            }
            
            # Handle Cal.com specifically for token exchange
            headers = {"Accept": "application/json"}
            if platform == "calcom":
                # Cal.com might require additional headers or different format
                headers["Content-Type"] = "application/json"
                logger.info("Using JSON format for Cal.com token exchange")
                response = await client.post(
                    config["token_url"],
                    json=token_data,
                    headers=headers
                )
            else:
                # Make token request for other platforms
                logger.info(f"Making token request to: {config['token_url']}")
                response = await client.post(
                    config["token_url"],
                    data=token_data,
                    headers=headers
                )
            
            # Check response
            if response.status_code != 200:
                logger.error(f"Token exchange failed with status {response.status_code}: {response.text}")
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/integrations?error=token_error&platform={platform}"
                )
            
            # Parse token response
            token_info = response.json()
            logger.info(f"Token exchange successful for {platform}")
            
            # Get access token
            access_token = token_info.get("access_token")
            if not access_token:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/integrations?error=no_token&platform={platform}"
                )
            
            # Get refresh token (if available)
            refresh_token = token_info.get("refresh_token")
            
            # Get token expiration (if available)
            expires_in = token_info.get("expires_in")
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=int(expires_in))
            
            # Get account info
            account_name, account_id = await get_account_info(platform, access_token)
            
            # Check if integration already exists for this user and platform
            existing_integration = db.query(Integration).filter(
                Integration.user_id == user_id,
                Integration.platform == platform
            ).first()
            
            if existing_integration:
                # Update existing integration
                existing_integration.access_token = access_token
                if refresh_token:
                    existing_integration.refresh_token = refresh_token
                existing_integration.status = IntegrationStatus.CONNECTED
                existing_integration.account_name = account_name
                existing_integration.account_id = account_id
                existing_integration.expires_at = expires_at
                existing_integration.last_sync = datetime.now()
                
                # For Stripe, store additional extra data
                if platform == "stripe" and not existing_integration.extra_data:
                    existing_integration.extra_data = {}
                
                if platform == "stripe":
                    # Store stripe-specific data
                    stripe_user_id = token_info.get("stripe_user_id")
                    if stripe_user_id and stripe_user_id != existing_integration.account_id:
                        existing_integration.account_id = stripe_user_id
                    
                    existing_integration.extra_data.update({
                        "stripe_publishable_key": token_info.get("stripe_publishable_key"),
                        "scope": token_info.get("scope"),
                        "livemode": token_info.get("livemode", False)
                    })
                
                db.commit()
            else:
                # Create new integration
                integration = Integration(
                    user_id=user_id,
                    platform=platform,
                    status=IntegrationStatus.CONNECTED,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    account_name=account_name,
                    account_id=account_id,
                    expires_at=expires_at,
                    last_sync=datetime.now()
                )
                
                # For Stripe, store additional extra data
                if platform == "stripe":
                    stripe_user_id = token_info.get("stripe_user_id")
                    if stripe_user_id and stripe_user_id != integration.account_id:
                        integration.account_id = stripe_user_id
                    
                    integration.extra_data = {
                        "stripe_publishable_key": token_info.get("stripe_publishable_key"),
                        "scope": token_info.get("scope"),
                        "livemode": token_info.get("livemode", False)
                    }
                
                db.add(integration)
                db.commit()
            
            # Redirect to the frontend with success message
            return RedirectResponse(
                url=f"{FRONTEND_URL}/integrations?success=true&platform={platform}&account={account_name}"
            )
            
    except Exception as e:
        # Log the error in production
        print(f"OAuth error: {str(e)}")
        
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error=server_error&platform={platform}"
        )

@router.delete("/api/integrations/{platform}", status_code=status.HTTP_200_OK)
async def disconnect_integration(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Disconnect an integration for the current user.
    
    Args:
        platform: The platform to disconnect
        db: Database session
        current_user: Current authenticated user (optional)
        
    Returns:
        dict: Disconnection result.
    """
    # Use the authenticated user's ID if available, otherwise default to 1 for demo
    user_id = current_user.id if current_user else 1
    logger.info(f"Disconnecting {platform} for user {user_id}")
    
    # Validate platform
    if platform not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(OAUTH_CONFIG.keys())}"
        )
    
    # Find integration in database for the current user
    integration = db.query(Integration).filter(
        Integration.platform == platform,
        Integration.user_id == user_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration for {platform} not found for this user"
        )
    
    # Update integration status
    integration.status = IntegrationStatus.DISCONNECTED
    db.commit()
    
    return {
        "message": f"{platform} disconnected successfully",
        "platform": platform,
        "status": "disconnected"
    }

@router.get("/api/integrations/status")
async def get_integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get the status of all platform integrations for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user (optional)
        
    Returns:
        IntegrationStatusList: Status of each integration platform.
    """
    try:
        # Use the authenticated user's ID if available, otherwise default to 1 for demo
        user_id = current_user.id if current_user else 1
        logger.info(f"Getting integration status for user {user_id}")
        
        # Get all platforms from config
        platforms = list(OAUTH_CONFIG.keys())
        
        # Initialize integrations list
        db_integrations = []
        
        # Get integrations from database for the current user
        # Create a new session for each attempt to avoid transaction issues
        try:
            # Try to query with user_id first
            try:
                # Create new session for this query
                from app.database import SessionLocal
                with SessionLocal() as new_db:
                    db_integrations = new_db.query(Integration).filter(Integration.user_id == user_id).all()
                    # Copy the results to detach them from the session
                    db_integrations = [integration for integration in db_integrations]
                logger.info(f"Retrieved {len(db_integrations)} integrations for user {user_id} using user_id column")
            except Exception as user_id_error:
                # If that fails (possibly because user_id column doesn't exist),
                # just get all integrations as a fallback
                logger.warning(f"Error querying by user_id, falling back to all integrations: {str(user_id_error)}")
                # Create new session for fallback query
                from app.database import SessionLocal
                with SessionLocal() as new_db:
                    db_integrations = new_db.query(Integration).all()
                    # Copy the results to detach them from the session
                    db_integrations = [integration for integration in db_integrations]
                logger.info(f"Retrieved {len(db_integrations)} integrations without user_id filter")
        except Exception as db_error:
            logger.error(f"Database error fetching integrations: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}"
            )
        
        # Create status dict with default values
        status_dict = {platform: {"platform": platform, "status": "disconnected"} for platform in platforms}
        
        # Update with actual values from DB
        for integration in db_integrations:
            try:
                status = integration.status if isinstance(integration.status, str) else str(integration.status)
                status_dict[integration.platform] = {
                    "platform": integration.platform,
                    "status": status,
                    "account_name": integration.account_name,
                    "last_sync": integration.last_sync
                }
            except Exception as integration_error:
                logger.error(f"Error processing integration {getattr(integration, 'id', 'unknown')}: {str(integration_error)}")
                # Continue processing other integrations
                continue
        
        # Convert to list and return
        integrations_list = list(status_dict.values())
        logger.info(f"Returning status for {len(integrations_list)} integrations")
        
        return {"integrations": integrations_list}
    except Exception as e:
        logger.error(f"Unexpected error in get_integration_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving integration status: {str(e)}"
        )

# Helper functions for integration-specific operations
async def get_account_info(platform: str, access_token: str) -> tuple:
    """
    Get account information for the integrated platform.
    
    Args:
        platform: The platform to get account info for
        access_token: The OAuth access token
        
    Returns:
        tuple: (account_name, account_id)
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            if platform == "youtube":
                # Get YouTube channel info
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                    headers=headers
                )
                data = response.json()
                if "items" in data and data["items"]:
                    return data["items"][0]["snippet"]["title"], data["items"][0]["id"]
                
            elif platform == "stripe":
                # Get Stripe account info
                response = await client.get(
                    "https://api.stripe.com/v1/account",
                    headers=headers
                )
                data = response.json()
                return data.get("business_profile", {}).get("name", "Stripe Account"), data.get("id", "")
                
            elif platform == "calendly":
                # Get Calendly user info
                response = await client.get(
                    "https://api.calendly.com/users/me",
                    headers=headers
                )
                data = response.json()
                return data.get("resource", {}).get("name", "Calendly User"), data.get("resource", {}).get("uri", "").split("/")[-1]
                
            elif platform == "calcom":
                # Get Cal.com user info
                response = await client.get(
                    "https://api.cal.com/v1/me",
                    headers=headers
                )
                data = response.json()
                return data.get("name", "Cal.com User"), str(data.get("id", ""))
    
    except Exception as e:
        # Log the error in production
        print(f"Error getting account info: {str(e)}")
    
    # Default values if we couldn't get account info
    return f"{platform.capitalize()} Account", ""

async def sync_platform_data(platform: str, db: Session, user_id: int = 1):
    """
    Sync data from the integrated platform for a specific user.
    This function would be implemented to pull data from the platform APIs.
    
    Args:
        platform: The platform to sync data from
        db: Database session
        user_id: User ID to sync data for (defaults to 1 for testing/demo)
    """
    # This is a placeholder - in a real implementation, this would:
    # 1. Get the integration record from the database
    # 2. Use the access token to fetch data from the platform API
    # 3. Process and store the data in the appropriate tables
    # 4. Update the last_sync timestamp on the integration record
    
    try:
        # Get integration record for the user
        integration = db.query(Integration).filter(
            Integration.platform == platform,
            Integration.user_id == user_id
        ).first()
        
        if not integration or not integration.is_connected:
            return
        
        # For demonstration purposes, just update the last_sync timestamp
        integration.last_sync = datetime.utcnow()
        db.commit()
        
        logger.info(f"Data sync for {platform} (user {user_id}) completed successfully!")
    
    except Exception as e:
        logger.error(f"Error syncing data for {platform} (user {user_id}): {str(e)}")

@router.post("/api/integrations/calcom/api-key")
def connect_calcom_api_key(
    api_key: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Connect Cal.com using API key.
    
    Args:
        api_key: JSON object containing the API key
        db: Database session
        current_user: Current authenticated user (optional)
        
    Returns:
        JSON response with connection status
    """
    # Use a new database session to ensure clean transactions
    from app.database import SessionLocal
    
    try:
        # Use the authenticated user's ID if available, otherwise default to 1 for demo
        # IMPORTANT: Use INTEGER for user_id to match INTEGER type in database
        user_id = current_user.id if current_user else 1  # Changed back to integer 1 to match INTEGER in database
        
        logger.info(f"Connecting Cal.com via API key for user {user_id}")
        
        if "api_key" not in api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required"
            )
        
        calcom_api_key = api_key["api_key"].strip()
        logger.info(f"Received API key: {calcom_api_key[:4]}...{calcom_api_key[-4:] if len(calcom_api_key) > 8 else ''}")

        # TEMPORARY DEBUGGING SOLUTION - Skip validation if API key looks valid
        if calcom_api_key.startswith("cal_"):
            logger.warning("TEMPORARY: Skipping actual API validation and proceeding with mock data")
            account_name = "Cal.com Test User"
            account_id = "user_test123"
            
            # Create a new session for database operations
            with SessionLocal() as session:
                # Check if this integration already exists for the user
                # Try to query with user_id, but handle case where column may not exist yet
                existing_integration = None
                try:
                    # Try with user_id filter
                    existing_integration = session.query(Integration).filter(
                        Integration.user_id == user_id,
                        Integration.platform == "calcom"
                    ).first()
                    
                    logger.info(f"Queried integrations with user_id filter: {existing_integration}")
                except Exception as user_id_error:
                    # Fallback: if user_id column doesn't exist, just filter by platform
                    logger.warning(f"Error querying by user_id (may not exist yet): {str(user_id_error)}")
                    session.rollback()  # Important: roll back the transaction
                    
                    try:
                        existing_integration = session.query(Integration).filter(
                            Integration.platform == "calcom"
                        ).first()
                        
                        logger.info(f"Queried integrations with platform-only filter: {existing_integration}")
                    except Exception as platform_query_error:
                        logger.error(f"Error querying by platform: {str(platform_query_error)}")
                        session.rollback()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error: {str(platform_query_error)}"
                        )
                
                now = datetime.utcnow()
                
                try:
                    if existing_integration:
                        # Update existing integration
                        existing_integration.auth_type = IntegrationAuthType.API_KEY
                        existing_integration.access_token = None
                        existing_integration.account_name = account_name
                        existing_integration.account_id = account_id
                        existing_integration.extra_data = {
                            "api_key": calcom_api_key,
                            "user_data": {"name": account_name, "id": account_id}
                        }
                        
                        # Try to set user_id if the column exists
                        try:
                            existing_integration.user_id = user_id
                        except Exception as user_id_error:
                            logger.warning(f"Could not set user_id on integration - column may not exist yet: {str(user_id_error)}")
                            # Continue without setting user_id
                            
                        existing_integration.last_sync = now
                        existing_integration.status = IntegrationStatus.CONNECTED
                        logger.info(f"Updated existing Cal.com integration for user {user_id}")
                    else:
                        # Create new integration
                        try:
                            new_integration = Integration(
                                user_id=user_id,
                                platform="calcom",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=account_name,
                                account_id=account_id,
                                extra_data={
                                    "api_key": calcom_api_key,
                                    "user_data": {"name": account_name, "id": account_id}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        except Exception as create_error:
                            # If user_id column doesn't exist, try creating without it
                            logger.warning(f"Error creating integration with user_id: {str(create_error)}")
                            session.rollback()
                            
                            new_integration = Integration(
                                platform="calcom",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=account_name,
                                account_id=account_id,
                                extra_data={
                                    "api_key": calcom_api_key,
                                    "user_data": {"name": account_name, "id": account_id}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        
                        session.add(new_integration)
                        logger.info(f"Created new Cal.com integration for user {user_id}")
                    
                    # Commit the transaction
                    session.commit()
                    logger.info("Successfully saved Cal.com integration to database")
                except Exception as db_operation_error:
                    logger.error(f"Error during database operation: {str(db_operation_error)}")
                    session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error saving integration: {str(db_operation_error)}"
                    )
            
            return {"status": "success", "account_name": account_name}
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Cal.com API key format. Key should start with 'cal_'."
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in connect_calcom_api_key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.post("/api/integrations/youtube/api-key")
def connect_youtube_api_key(
    api_data: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Connect YouTube using API key and channel ID.
    
    Args:
        api_data: JSON object containing the API key and channel ID
        db: Database session
        current_user: Current authenticated user (optional)
        
    Returns:
        JSON response with connection status
    """
    # Use a new database session to ensure clean transactions
    from app.database import SessionLocal
    
    try:
        # Use the authenticated user's ID if available, otherwise default to 1 for demo
        # IMPORTANT: Use INTEGER for user_id to match INTEGER type in database
        user_id = current_user.id if current_user else 1  # Changed back to integer 1 to match INTEGER in database
        
        logger.info(f"Connecting YouTube via API key for user {user_id}")
        
        if "api_key" not in api_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required"
            )
        
        if "channel_id" not in api_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YouTube channel ID is required"
            )
        
        youtube_api_key = api_data["api_key"].strip()
        channel_id = api_data["channel_id"].strip()
        
        logger.info(f"Received API key: {youtube_api_key[:4]}...{youtube_api_key[-4:] if len(youtube_api_key) > 8 else ''}")
        logger.info(f"Received channel ID: {channel_id}")

        # TEMPORARY DEBUGGING SOLUTION - Skip validation if API key starts with appropriate prefix
        if youtube_api_key.startswith("AIza"):
            logger.warning("TEMPORARY: Skipping actual API validation and proceeding with mock data")
            channel_name = "YouTube Test Channel" 
            
            # Create a new session for database operations
            with SessionLocal() as session:
                # Check if this integration already exists for the user
                # Try to query with user_id, but handle case where column may not exist yet
                existing_integration = None
                try:
                    # Try with user_id filter
                    existing_integration = session.query(Integration).filter(
                        Integration.user_id == user_id,
                        Integration.platform == "youtube"
                    ).first()
                    
                    logger.info(f"Queried integrations with user_id filter: {existing_integration}")
                except Exception as user_id_error:
                    # Fallback: if user_id column doesn't exist, just filter by platform
                    logger.warning(f"Error querying by user_id (may not exist yet): {str(user_id_error)}")
                    session.rollback()  # Important: roll back the transaction
                    
                    try:
                        existing_integration = session.query(Integration).filter(
                            Integration.platform == "youtube"
                        ).first()
                        
                        logger.info(f"Queried integrations with platform-only filter: {existing_integration}")
                    except Exception as platform_query_error:
                        logger.error(f"Error querying by platform: {str(platform_query_error)}")
                        session.rollback()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error: {str(platform_query_error)}"
                        )
                
                now = datetime.utcnow()
                
                try:
                    if existing_integration:
                        # Update existing integration
                        existing_integration.auth_type = IntegrationAuthType.API_KEY
                        existing_integration.access_token = None
                        existing_integration.account_name = channel_name
                        existing_integration.account_id = channel_id
                        existing_integration.extra_data = {
                            "api_key": youtube_api_key,
                            "channel_id": channel_id,
                            "channel_info": {"title": channel_name}
                        }
                        
                        # Try to set user_id if the column exists
                        try:
                            existing_integration.user_id = user_id
                        except Exception as user_id_error:
                            logger.warning(f"Could not set user_id on integration - column may not exist yet: {str(user_id_error)}")
                            # Continue without setting user_id
                            
                        existing_integration.last_sync = now
                        existing_integration.status = IntegrationStatus.CONNECTED
                        logger.info(f"Updated existing YouTube integration for user {user_id}")
                    else:
                        # Create new integration
                        try:
                            new_integration = Integration(
                                user_id=user_id,
                                platform="youtube",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=channel_name,
                                account_id=channel_id,
                                extra_data={
                                    "api_key": youtube_api_key,
                                    "channel_id": channel_id,
                                    "channel_info": {"title": channel_name}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        except Exception as create_error:
                            # If user_id column doesn't exist, try creating without it
                            logger.warning(f"Error creating integration with user_id: {str(create_error)}")
                            session.rollback()
                            
                            new_integration = Integration(
                                platform="youtube",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=channel_name,
                                account_id=channel_id,
                                extra_data={
                                    "api_key": youtube_api_key,
                                    "channel_id": channel_id,
                                    "channel_info": {"title": channel_name}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        
                        session.add(new_integration)
                        logger.info(f"Created new YouTube integration for user {user_id}")
                    
                    # Commit the transaction
                    session.commit()
                    logger.info("Successfully saved YouTube integration to database")
                except Exception as db_operation_error:
                    logger.error(f"Error during database operation: {str(db_operation_error)}")
                    session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error saving integration: {str(db_operation_error)}"
                    )
            
            return {"status": "success", "account_name": channel_name}
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid YouTube API key format. Key should start with 'AIza'."
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in connect_youtube_api_key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.post("/api/integrations/stripe/api-key")
def connect_stripe_api_key(
    api_key: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Connect Stripe using API key.
    
    Args:
        api_key: JSON object containing the API key
        db: Database session
        current_user: Current authenticated user (optional)
        
    Returns:
        JSON response with connection status
    """
    # Use a new database session to ensure clean transactions
    from app.database import SessionLocal
    
    try:
        # Use the authenticated user's ID if available, otherwise default to 1 for demo
        # IMPORTANT: Use INTEGER for user_id to match INTEGER type in database
        user_id = current_user.id if current_user else 1  # Changed back to integer 1 to match INTEGER in database
        
        logger.info(f"Connecting Stripe via API key for user {user_id}")
        
        if "api_key" not in api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required"
            )
        
        stripe_api_key = api_key["api_key"].strip()
        logger.info(f"Received API key: {stripe_api_key[:4]}...{stripe_api_key[-4:] if len(stripe_api_key) > 8 else ''}")

        # TEMPORARY DEBUGGING SOLUTION - Skip validation if API key starts with sk_
        if stripe_api_key.startswith("sk_"):
            logger.warning("TEMPORARY: Skipping actual API validation and proceeding with mock data")
            account_name = "Stripe Test Account"
            account_id = "acct_test123"
            
            # Create a new session for database operations
            with SessionLocal() as session:
                # Check if this integration already exists for the user
                # Try to query with user_id, but handle case where column may not exist yet
                existing_integration = None
                try:
                    # Try with user_id filter
                    existing_integration = session.query(Integration).filter(
                        Integration.user_id == user_id,
                        Integration.platform == "stripe"
                    ).first()
                    
                    logger.info(f"Queried integrations with user_id filter: {existing_integration}")
                except Exception as user_id_error:
                    # Fallback: if user_id column doesn't exist, just filter by platform
                    logger.warning(f"Error querying by user_id (may not exist yet): {str(user_id_error)}")
                    session.rollback()  # Important: roll back the transaction
                    
                    try:
                        existing_integration = session.query(Integration).filter(
                            Integration.platform == "stripe"
                        ).first()
                        
                        logger.info(f"Queried integrations with platform-only filter: {existing_integration}")
                    except Exception as platform_query_error:
                        logger.error(f"Error querying by platform: {str(platform_query_error)}")
                        session.rollback()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error: {str(platform_query_error)}"
                        )
                
                now = datetime.utcnow()
                
                try:
                    if existing_integration:
                        # Update existing integration
                        existing_integration.auth_type = IntegrationAuthType.API_KEY
                        existing_integration.access_token = None
                        existing_integration.account_name = account_name
                        existing_integration.account_id = account_id
                        existing_integration.extra_data = {
                            "api_key": stripe_api_key,
                            "account_data": {"name": account_name, "id": account_id}
                        }
                        
                        # Try to set user_id if the column exists
                        try:
                            existing_integration.user_id = user_id
                        except Exception as user_id_error:
                            logger.warning(f"Could not set user_id on integration - column may not exist yet: {str(user_id_error)}")
                            # Continue without setting user_id
                            
                        existing_integration.last_sync = now
                        existing_integration.status = IntegrationStatus.CONNECTED
                        logger.info(f"Updated existing Stripe integration for user {user_id}")
                    else:
                        # Create new integration
                        try:
                            new_integration = Integration(
                                user_id=user_id,
                                platform="stripe",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=account_name,
                                account_id=account_id,
                                extra_data={
                                    "api_key": stripe_api_key,
                                    "account_data": {"name": account_name, "id": account_id}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        except Exception as create_error:
                            # If user_id column doesn't exist, try creating without it
                            logger.warning(f"Error creating integration with user_id: {str(create_error)}")
                            session.rollback()
                            
                            new_integration = Integration(
                                platform="stripe",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=account_name,
                                account_id=account_id,
                                extra_data={
                                    "api_key": stripe_api_key,
                                    "account_data": {"name": account_name, "id": account_id}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        
                        session.add(new_integration)
                        logger.info(f"Created new Stripe integration for user {user_id}")
                    
                    # Commit the transaction
                    session.commit()
                    logger.info("Successfully saved Stripe integration to database")
                except Exception as db_operation_error:
                    logger.error(f"Error during database operation: {str(db_operation_error)}")
                    session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error saving integration: {str(db_operation_error)}"
                    )
            
            return {"status": "success", "account_name": account_name}
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Stripe API key format. Key should start with 'sk_'."
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in connect_stripe_api_key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.post("/api/integrations/calendly/api-key")
def connect_calendly_api_key(
    api_key: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Connect Calendly using API key.
    
    Args:
        api_key: JSON object containing the API key
        db: Database session
        current_user: Current authenticated user (optional)
        
    Returns:
        JSON response with connection status
    """
    # Use a new database session to ensure clean transactions
    from app.database import SessionLocal
    
    try:
        # Use the authenticated user's ID if available, otherwise default to 1 for demo
        # IMPORTANT: Use INTEGER for user_id to match INTEGER type in database
        user_id = current_user.id if current_user else 1  # Changed back to integer 1 to match INTEGER in database
        
        logger.info(f"Connecting Calendly via API key for user {user_id}")
        
        if "api_key" not in api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is required"
            )
        
        calendly_api_key = api_key["api_key"].strip()
        logger.info(f"Received API key: {calendly_api_key[:4]}...{calendly_api_key[-4:] if len(calendly_api_key) > 8 else ''}")

        # TEMPORARY DEBUGGING SOLUTION - Skip validation if API key format looks valid
        if calendly_api_key:
            logger.warning("TEMPORARY: Skipping actual API validation and proceeding with mock data")
            account_name = "Calendly Test User"
            account_id = "user_test123"
            
            # Create a new session for database operations
            with SessionLocal() as session:
                # Check if this integration already exists for the user
                # Try to query with user_id, but handle case where column may not exist yet
                existing_integration = None
                try:
                    # Try with user_id filter
                    existing_integration = session.query(Integration).filter(
                        Integration.user_id == user_id,
                        Integration.platform == "calendly"
                    ).first()
                    
                    logger.info(f"Queried integrations with user_id filter: {existing_integration}")
                except Exception as user_id_error:
                    # Fallback: if user_id column doesn't exist, just filter by platform
                    logger.warning(f"Error querying by user_id (may not exist yet): {str(user_id_error)}")
                    session.rollback()  # Important: roll back the transaction
                    
                    try:
                        existing_integration = session.query(Integration).filter(
                            Integration.platform == "calendly"
                        ).first()
                        
                        logger.info(f"Queried integrations with platform-only filter: {existing_integration}")
                    except Exception as platform_query_error:
                        logger.error(f"Error querying by platform: {str(platform_query_error)}")
                        session.rollback()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error: {str(platform_query_error)}"
                        )
                
                now = datetime.utcnow()
                
                try:
                    if existing_integration:
                        # Update existing integration
                        existing_integration.auth_type = IntegrationAuthType.API_KEY
                        existing_integration.access_token = None
                        existing_integration.account_name = account_name
                        existing_integration.account_id = account_id
                        existing_integration.extra_data = {
                            "api_key": calendly_api_key,
                            "user_data": {"name": account_name, "id": account_id}
                        }
                        
                        # Try to set user_id if the column exists
                        try:
                            existing_integration.user_id = user_id
                        except Exception as user_id_error:
                            logger.warning(f"Could not set user_id on integration - column may not exist yet: {str(user_id_error)}")
                            # Continue without setting user_id
                            
                        existing_integration.last_sync = now
                        existing_integration.status = IntegrationStatus.CONNECTED
                        logger.info(f"Updated existing Calendly integration for user {user_id}")
                    else:
                        # Create new integration
                        try:
                            new_integration = Integration(
                                user_id=user_id,
                                platform="calendly",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=account_name,
                                account_id=account_id,
                                extra_data={
                                    "api_key": calendly_api_key,
                                    "user_data": {"name": account_name, "id": account_id}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        except Exception as create_error:
                            # If user_id column doesn't exist, try creating without it
                            logger.warning(f"Error creating integration with user_id: {str(create_error)}")
                            session.rollback()
                            
                            new_integration = Integration(
                                platform="calendly",
                                auth_type=IntegrationAuthType.API_KEY,
                                account_name=account_name,
                                account_id=account_id,
                                extra_data={
                                    "api_key": calendly_api_key,
                                    "user_data": {"name": account_name, "id": account_id}
                                },
                                last_sync=now,
                                status=IntegrationStatus.CONNECTED
                            )
                        
                        session.add(new_integration)
                        logger.info(f"Created new Calendly integration for user {user_id}")
                    
                    # Commit the transaction
                    session.commit()
                    logger.info("Successfully saved Calendly integration to database")
                except Exception as db_operation_error:
                    logger.error(f"Error during database operation: {str(db_operation_error)}")
                    session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error saving integration: {str(db_operation_error)}"
                    )
            
            return {"status": "success", "account_name": account_name}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in connect_calendly_api_key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
