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
import enum

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
    # Require authentication for disconnecting integrations
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to disconnect integrations"
        )
    
    user_id = current_user.id
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
        # If no authenticated user, return empty integrations list
        if not current_user:
            return {
                "integrations": [],
                "message": "Please log in to view your integrations"
            }
        
        user_id = current_user.id
        logger.info(f"Getting integration status for user {user_id}")
        
        # Get all platforms from config
        platforms = list(OAUTH_CONFIG.keys())
        
        # Initialize integrations list
        db_integrations = []
        
        # Create a new session for database operations
        from app.database import SessionLocal
        from sqlalchemy.sql import text
        
        with SessionLocal() as session:
            try:
                # First, check if the integrations table exists and what columns it has
                # This handles both schema migration scenarios and different database states
                table_info = {
                    'has_user_id': False,
                    'has_status': False,
                    'has_is_connected': False,
                    'has_account_name': False,
                    'has_last_sync': False
                }
                
                try:
                    # Check what columns exist in the integrations table
                    columns_query = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'integrations' 
                    AND table_schema = 'public'
                    """
                    result = session.execute(text(columns_query))
                    columns = [row[0] for row in result]
                    
                    if 'user_id' in columns:
                        table_info['has_user_id'] = True
                    if 'status' in columns:
                        table_info['has_status'] = True
                    if 'is_connected' in columns:
                        table_info['has_is_connected'] = True
                    if 'account_name' in columns:
                        table_info['has_account_name'] = True
                    if 'last_sync' in columns:
                        table_info['has_last_sync'] = True
                    
                    logger.info(f"Integration table columns: {table_info}")
                except Exception as e:
                    logger.error(f"Error checking integrations table schema: {str(e)}")
                
                try:
                    # Build a query based on the columns that exist
                    select_columns = ["id", "platform"]
                    if table_info.get('has_status', False):
                        select_columns.append("status")
                    if table_info.get('has_account_name', False):
                        select_columns.append("account_name")
                    if table_info.get('has_last_sync', False):
                        select_columns.append("last_sync")
                    if table_info.get('has_is_connected', False):
                        select_columns.append("is_connected")
                    
                    # Construct the query
                    query = f"SELECT {', '.join(select_columns)} FROM integrations"
                    
                    # Add WHERE clause if user_id exists and we have a user_id
                    if table_info.get('has_user_id', False):
                        query += " WHERE user_id = :user_id"
                        logger.info(f"Querying integrations with user_id filter for user {user_id}. Full query: {query}")
                        result = session.execute(text(query), {"user_id": user_id})
                        logger.info(f"Executed query with user_id={user_id}")
                    else:
                        # If user_id column doesn't exist, return empty list since we can't determine ownership
                        logger.warning("Integration table exists but lacks user_id column - returning empty list")
                        return {
                            "integrations": [],
                            "message": "Integration table schema is outdated. Please contact support."
                        }
                    
                    # Process results
                    rows = result.fetchall()
                    logger.info(f"Found {len(rows)} integrations for user_id={user_id}")
                    for row in rows:
                        # Create dictionary from row - but only with fields we know exist
                        integration_data = {}
                        for i, col in enumerate(select_columns):
                            integration_data[col] = row[i]
                        
                        # Always include a clear is_connected flag in the response
                        # This ensures the frontend has consistent data regardless of DB schema
                        if not 'is_connected' in integration_data:
                            # If we have status and it's 'connected', set is_connected to True
                            if 'status' in integration_data and integration_data['status'] == 'connected':
                                integration_data['is_connected'] = True
                            else:
                                integration_data['is_connected'] = False
                                
                        db_integrations.append(integration_data)
                    
                    logger.info(f"Retrieved {len(db_integrations)} integrations")
                except Exception as e:
                    logger.error(f"Error querying integrations: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Error in get_integration_status: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get integration status: {str(e)}"
                )
        
        # Return available platforms with their connection status
        platforms_with_status = []
        
        # For each platform, find its status in db_integrations or set as disconnected
        for platform in platforms:
            platform_status = next(
                (
                    integration for integration in db_integrations 
                    if integration.get("platform") == platform
                ), 
                None
            )
            
            # Default integration data
            integration_data = {
                "platform": platform,
                "status": "disconnected",
                "is_connected": False,
                "account_name": None,
                "last_sync": None
            }
            
            # Update with data from database if we found the integration
            if platform_status:
                # Ensure consistent status and is_connected fields
                if 'status' in platform_status:
                    integration_data['status'] = platform_status['status']
                    # Make sure is_connected is in sync with status
                    integration_data['is_connected'] = (
                        platform_status['status'] == 'connected' or 
                        platform_status.get('is_connected', False)
                    )
                elif 'is_connected' in platform_status and platform_status['is_connected']:
                    integration_data['status'] = 'connected'
                    integration_data['is_connected'] = True
                
                # Copy other fields if they exist
                if 'account_name' in platform_status:
                    integration_data['account_name'] = platform_status['account_name']
                if 'last_sync' in platform_status:
                    integration_data['last_sync'] = platform_status['last_sync']
            
            platforms_with_status.append(integration_data)
        
        # Check if any integrations are connected but we're still using demo data
        any_connected = any(integration['status'] == 'connected' for integration in platforms_with_status)
        using_demo_data = False
        
        # Check if we have any connected integrations but are still using demo data
        # This could happen if the API keys are invalid or there's an API error
        if any_connected:
            try:
                # Check all connected integrations
                for platform in ['youtube', 'stripe', 'calendly', 'calcom']:
                    platform_integration = next((i for i in platforms_with_status if i['platform'] == platform and i['status'] == 'connected'), None)
                    if platform_integration:
                        # Get the integration from the database to check if it has valid API keys
                        db_integration = db.query(Integration).filter(
                            Integration.platform == platform,
                            Integration.user_id == user_id
                        ).first()
                        
                        if db_integration and db_integration.extra_data:
                            # Check if API keys are working based on platform
                            if platform == 'youtube':
                                from app.utils.youtube_api import test_youtube_api_key
                                api_key = db_integration.extra_data.get('api_key')
                                channel_id = db_integration.extra_data.get('channel_id')
                                
                                if api_key and channel_id:
                                    is_valid = await test_youtube_api_key(api_key, channel_id)
                                    if not is_valid:
                                        using_demo_data = True
                                        logger.warning(f"YouTube API key for user {user_id} is not working properly")
                                        break
                            
                            elif platform == 'stripe':
                                from app.utils.stripe_api import test_stripe_api_key
                                api_key = db_integration.extra_data.get('api_key')
                                
                                if api_key:
                                    is_valid = await test_stripe_api_key(api_key)
                                    if not is_valid:
                                        using_demo_data = True
                                        logger.warning(f"Stripe API key for user {user_id} is not working properly")
                                        break
                            
                            elif platform == 'calendly':
                                from app.utils.calendly_api import test_calendly_api_key
                                api_key = db_integration.extra_data.get('api_key')
                                
                                if api_key:
                                    is_valid = await test_calendly_api_key(api_key)
                                    if not is_valid:
                                        using_demo_data = True
                                        logger.warning(f"Calendly API key for user {user_id} is not working properly")
                                        break
                            
                            elif platform == 'calcom':
                                from app.utils.calcom_api import test_calcom_api_key
                                api_key = db_integration.extra_data.get('api_key')
                                
                                if api_key:
                                    is_valid = await test_calcom_api_key(api_key)
                                    if not is_valid:
                                        using_demo_data = True
                                        logger.warning(f"Cal.com API key for user {user_id} is not working properly")
                                        break
            except Exception as e:
                logger.error(f"Error checking real data status: {str(e)}")
                using_demo_data = True
        
        return {
            "integrations": platforms_with_status,
            "using_demo_data": using_demo_data,
            "backend_available": True
        }
    
    except Exception as e:
        logger.error(f"Error in get_integration_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration status: {str(e)}"
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
    # Require authentication for creating integrations
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to connect integrations"
        )
    
    user_id = current_user.id
    
    logger.info(f"Connecting Stripe via API key for user {user_id}")
    
    if "api_key" not in api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is required"
        )
    
    stripe_api_key = api_key["api_key"].strip()
    logger.info(f"Received API key: {stripe_api_key[:4]}...{stripe_api_key[-4:] if len(stripe_api_key) > 8 else ''}")

    # Validate API key format and prepare for storage
    if stripe_api_key.startswith("sk_"):
        logger.info(f"Processing Stripe connection with valid API key format")
        
        # Store API key in extra_data JSON field
        extra_data = {"api_key": stripe_api_key}
        
        account_name = "Your Stripe Account"
        account_id = "acct_" + stripe_api_key[-8:]  # Use part of API key to make unique
        
        # Create a new session for database operations
        from app.database import SessionLocal
        from sqlalchemy.sql import text
        
        with SessionLocal() as session:
            try:
                # First, check what columns actually exist in the integrations table
                table_info = {}
                try:
                    # Get column information
                    columns_result = session.execute(text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'integrations'"
                    ))
                    existing_columns = [row[0] for row in columns_result]
                    logger.info(f"Existing columns in integrations table: {existing_columns}")
                    
                    # Store which columns exist
                    table_info = {
                        'has_status': 'status' in existing_columns,
                        'has_is_connected': 'is_connected' in existing_columns,
                        'has_extra_data': 'extra_data' in existing_columns,
                        'has_api_key': 'api_key' in existing_columns
                    }
                    
                    logger.info(f"Table info: {table_info}")
                    
                    # If extra_data column doesn't exist, try to add it
                    if not table_info['has_extra_data']:
                        logger.warning("extra_data column missing - attempting to add it now")
                        try:
                            # Try multiple approaches to add the column
                            try:
                                # First attempt - standard ALTER TABLE
                                session.execute(text("ALTER TABLE integrations ADD COLUMN extra_data JSONB NULL"))
                                logger.info("Successfully added extra_data column using ALTER TABLE")
                            except Exception as e1:
                                logger.warning(f"First attempt to add column failed: {str(e1)}")
                                # Second attempt - with IF NOT EXISTS
                                session.execute(text("ALTER TABLE integrations ADD COLUMN IF NOT EXISTS extra_data JSONB NULL"))
                                logger.info("Successfully added extra_data column using IF NOT EXISTS")
                            
                            session.commit()
                            # Update our table info after adding the column
                            table_info['has_extra_data'] = True
                            logger.info("Successfully added extra_data column to integrations table")
                        except Exception as col_error:
                            session.rollback()
                            logger.error(f"Failed to add extra_data column: {str(col_error)}")
                            # Continue without the column - we'll store the API key elsewhere
                except Exception as e:
                    logger.warning(f"Could not get table schema: {str(e)}")
                    session.rollback()
                    # Assume columns for maximum compatibility
                    table_info = {
                        'has_status': False,
                        'has_is_connected': True,
                        'has_extra_data': False,
                        'has_api_key': True  # Most installations should have this
                    }
                
                # Simplified approach - check if integration exists for this platform AND user
                result = session.execute(
                    text("SELECT id FROM integrations WHERE platform = :platform AND user_id = :user_id"),
                    {"platform": "stripe", "user_id": user_id}
                )
                existing_row = result.fetchone()
                
                if existing_row:
                    # Update existing integration with only columns that exist
                    update_sql = """
                        UPDATE integrations 
                        SET account_name = :account_name, 
                            account_id = :account_id"""
                            
                    # Only include extra_data if the column exists
                    update_params = {
                        "id": existing_row[0],
                        "account_name": account_name,
                        "account_id": account_id
                    }
                    
                    if table_info.get('has_extra_data', False):
                        update_sql += ", extra_data = :extra_data"
                        update_params["extra_data"] = json.dumps(extra_data)
                    elif table_info.get('has_api_key', False):
                        # Fallback to store in api_key column if it exists
                        update_sql += ", api_key = :api_key"
                        update_params["api_key"] = stripe_api_key
                        logger.info("Using api_key column as fallback for storage")
                    
                    if table_info['has_is_connected']:
                        update_sql += ", is_connected = TRUE"
                        
                    if table_info['has_status']:
                        update_sql += ", status = 'connected'"
                        
                    update_sql += " WHERE id = :id"
                    
                    session.execute(text(update_sql), update_params)
                    logger.info(f"Updated existing Stripe integration (ID: {existing_row[0]})")
                else:
                    # Insert new integration with only columns that exist
                    insert_columns = ["platform", "account_name", "account_id", "user_id"]
                    insert_values = [":platform", ":account_name", ":account_id", ":user_id"]
                    insert_params = {
                        "platform": "stripe",
                        "account_name": account_name,
                        "account_id": account_id,
                        "user_id": user_id
                    }
                    
                    # Only include extra_data if the column exists
                    if table_info.get('has_extra_data', False):
                        insert_columns.append("extra_data")
                        insert_values.append(":extra_data")
                        insert_params["extra_data"] = json.dumps(extra_data)
                    elif table_info.get('has_api_key', False):
                        # Fallback to store in api_key column if it exists
                        insert_columns.append("api_key")
                        insert_values.append(":api_key")
                        insert_params["api_key"] = stripe_api_key
                        logger.info("Using api_key column as fallback for storage")
                    
                    # Add optional columns if they exist
                    if table_info['has_is_connected']:
                        insert_columns.append("is_connected")
                        insert_values.append("TRUE")
                        
                    if table_info['has_status']:
                        insert_columns.append("status")
                        insert_values.append("'connected'")
                        
                    # Build the SQL statement
                    insert_sql = f"""
                        INSERT INTO integrations 
                        ({', '.join(insert_columns)})
                        VALUES 
                        ({', '.join(insert_values)})
                    """
                    
                    # Log the final SQL and parameters for debugging
                    logger.info(f"SQL to execute: {insert_sql}")
                    logger.info(f"Parameters: {insert_params}")
                    
                    try:
                        session.execute(text(insert_sql), insert_params)
                        logger.info("Created new Stripe integration")
                    except Exception as insert_error:
                        # If this fails, we'll try a simplified version without the extra_data column
                        logger.error(f"Error inserting integration: {str(insert_error)}")
                        session.rollback()
                        
                        # Simplified approach - just the essential columns
                        simple_sql = """
                            INSERT INTO integrations (platform, account_name, account_id, user_id)
                            VALUES (:platform, :account_name, :account_id, :user_id)
                        """
                        session.execute(text(simple_sql), {
                            "platform": "stripe",
                            "account_name": account_name,
                            "account_id": account_id,
                            "user_id": user_id
                        })
                        logger.info("Created new Stripe integration with simplified approach")
                
                # Commit the transaction
                session.commit()
                logger.info("Successfully saved Stripe integration to database")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error: {str(e)}")
                # Try one last approach with minimal columns
                try:
                    # Direct SQL approach without checking schema
                    session.execute(text("""
                        INSERT INTO integrations (platform, account_name, account_id, user_id)
                        VALUES (:platform, :account_name, :account_id, :user_id)
                    """), {
                        "platform": "stripe",
                        "account_name": account_name,
                        "account_id": account_id,
                        "user_id": user_id
                    })
                    session.commit()
                    logger.info("Created integration with emergency fallback method")
                except Exception as final_error:
                    session.rollback()
                    logger.error(f"All attempts failed. Last error: {str(final_error)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database error: {str(e)}"
                    )
        
        return {
            "status": "success", 
            "account_name": account_name, 
            "is_connected": True,
            "display_name": "Your Stripe Account"  # Added display_name for frontend
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe API key format. Key should start with 'sk_'."
        )

@router.post("/api/integrations/youtube/api-key")
async def connect_youtube_api_key(
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
    # Require authentication for creating integrations
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to connect integrations"
        )
    
    user_id = current_user.id
    
    logger.info(f"Connecting YouTube via API key for user {user_id}")
    
    if "api_key" not in api_data or "channel_id" not in api_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key and channel ID are required"
        )
    
    youtube_api_key = api_data["api_key"].strip()
    channel_id = api_data["channel_id"].strip()
    logger.info(f"Received API key: {youtube_api_key[:4]}...{youtube_api_key[-4:] if len(youtube_api_key) > 8 else ''}")
    logger.info(f"Received channel ID: {channel_id[:4]}...{channel_id[-4:] if len(channel_id) > 8 else ''}")

    # Validate API key format and prepare for storage
    if youtube_api_key and channel_id:
        logger.info(f"Processing YouTube connection with valid API key and channel ID")
        
        # Store API key and channel ID in extra_data JSON field
        extra_data = {
            "api_key": youtube_api_key,
            "channel_id": channel_id
        }
        
        account_name = "Your YouTube Channel"
        account_id = channel_id
        
        # Create a new session for database operations
        from app.database import SessionLocal
        from sqlalchemy.sql import text
        
        with SessionLocal() as session:
            try:
                # First, check what columns actually exist in the integrations table
                table_info = {}
                try:
                    # Get column information
                    columns_result = session.execute(text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'integrations'"
                    ))
                    existing_columns = [row[0] for row in columns_result]
                    logger.info(f"Existing columns in integrations table: {existing_columns}")
                    
                    # Store which columns exist
                    table_info = {
                        'has_status': 'status' in existing_columns,
                        'has_is_connected': 'is_connected' in existing_columns
                    }
                    
                    logger.info(f"Table info: {table_info}")
                except Exception as e:
                    logger.warning(f"Could not get table schema: {str(e)}")
                    session.rollback()
                    # Assume columns for maximum compatibility
                    table_info = {
                        'has_status': False,
                        'has_is_connected': True
                    }
                
                # Simplified approach - check if integration exists for this platform AND user
                result = session.execute(
                    text("SELECT id FROM integrations WHERE platform = :platform AND user_id = :user_id"),
                    {"platform": "youtube", "user_id": user_id}
                )
                existing_row = result.fetchone()
                
                if existing_row:
                    # Update existing integration with only columns that exist
                    update_sql = """
                        UPDATE integrations 
                        SET account_name = :account_name, 
                            account_id = :account_id,
                            extra_data = :extra_data"""
                    
                    if table_info['has_is_connected']:
                        update_sql += ", is_connected = TRUE"
                        
                    if table_info['has_status']:
                        update_sql += ", status = 'connected'"
                        
                    update_sql += " WHERE id = :id"
                    
                    session.execute(
                        text(update_sql),
                        {
                            "id": existing_row[0],
                            "account_name": account_name,
                            "account_id": account_id,
                            "extra_data": json.dumps(extra_data)
                        }
                    )
                    logger.info(f"Updated existing YouTube integration (ID: {existing_row[0]})")
                else:
                    # Insert new integration with only columns that exist
                    insert_columns = ["platform", "account_name", "account_id", "user_id", "extra_data"]
                    insert_values = [":platform", ":account_name", ":account_id", ":user_id", ":extra_data"]
                    insert_params = {
                        "platform": "youtube",
                        "account_name": account_name,
                        "account_id": account_id,
                        "user_id": user_id,
                        "extra_data": json.dumps(extra_data)
                    }
                    
                    # Add optional columns if they exist
                    if table_info['has_is_connected']:
                        insert_columns.append("is_connected")
                        insert_values.append("TRUE")
                        
                    if table_info['has_status']:
                        insert_columns.append("status")
                        insert_values.append("'connected'")
                        
                    # Build the SQL statement
                    insert_sql = f"""
                        INSERT INTO integrations 
                        ({', '.join(insert_columns)})
                        VALUES 
                        ({', '.join(insert_values)})
                    """
                    
                    session.execute(text(insert_sql), insert_params)
                    logger.info("Created new YouTube integration")
                
                # Commit the transaction
                session.commit()
                logger.info("Successfully saved YouTube integration to database")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error: {str(e)}"
                )
        
        return {
            "status": "success", 
            "account_name": account_name, 
            "is_connected": True,
            "display_name": "Your YouTube Channel"  # Added display_name for frontend
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube API key or channel ID format"
        )

@router.post("/api/integrations/calendly/api-key")
async def connect_calendly_api_key(
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
    # Require authentication for creating integrations
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to connect integrations"
        )
    
    user_id = current_user.id
    
    logger.info(f"Connecting Calendly via API key for user {user_id}")
    
    if "api_key" not in api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is required"
        )
    
    calendly_api_key = api_key["api_key"].strip()
    logger.info(f"Received API key: {calendly_api_key[:4]}...{calendly_api_key[-4:] if len(calendly_api_key) > 8 else ''}")

    # Validate API key format and prepare for storage
    if calendly_api_key:
        logger.info(f"Processing Calendly connection with valid API key format")
        
        # Store API key in extra_data JSON field
        extra_data = {"api_key": calendly_api_key}
        
        account_name = "Your Calendly Account"
        account_id = "cal_" + calendly_api_key[-8:]  # Use part of API key to make unique
        
        # Create a new session for database operations
        from app.database import SessionLocal
        from sqlalchemy.sql import text
        
        with SessionLocal() as session:
            try:
                # First, check what columns actually exist in the integrations table
                table_info = {}
                try:
                    # Get column information
                    columns_result = session.execute(text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'integrations'"
                    ))
                    existing_columns = [row[0] for row in columns_result]
                    logger.info(f"Existing columns in integrations table: {existing_columns}")
                    
                    # Store which columns exist
                    table_info = {
                        'has_status': 'status' in existing_columns,
                        'has_is_connected': 'is_connected' in existing_columns
                    }
                    
                    logger.info(f"Table info: {table_info}")
                except Exception as e:
                    logger.warning(f"Could not get table schema: {str(e)}")
                    session.rollback()
                    # Assume columns for maximum compatibility
                    table_info = {
                        'has_status': False,
                        'has_is_connected': True
                    }
                
                # Simplified approach - check if integration exists for this platform AND user
                result = session.execute(
                    text("SELECT id FROM integrations WHERE platform = :platform AND user_id = :user_id"),
                    {"platform": "calendly", "user_id": user_id}
                )
                existing_row = result.fetchone()
                
                if existing_row:
                    # Update existing integration with only columns that exist
                    update_sql = """
                        UPDATE integrations 
                        SET account_name = :account_name, 
                            account_id = :account_id,
                            extra_data = :extra_data"""
                    
                    if table_info['has_is_connected']:
                        update_sql += ", is_connected = TRUE"
                        
                    if table_info['has_status']:
                        update_sql += ", status = 'connected'"
                        
                    update_sql += " WHERE id = :id"
                    
                    session.execute(
                        text(update_sql),
                        {
                            "id": existing_row[0],
                            "account_name": account_name,
                            "account_id": account_id,
                            "extra_data": json.dumps(extra_data)
                        }
                    )
                    logger.info(f"Updated existing Calendly integration (ID: {existing_row[0]})")
                else:
                    # Insert new integration with only columns that exist
                    insert_columns = ["platform", "account_name", "account_id", "user_id", "extra_data"]
                    insert_values = [":platform", ":account_name", ":account_id", ":user_id", ":extra_data"]
                    insert_params = {
                        "platform": "calendly",
                        "account_name": account_name,
                        "account_id": account_id,
                        "user_id": user_id,
                        "extra_data": json.dumps(extra_data)
                    }
                    
                    # Add optional columns if they exist
                    if table_info['has_is_connected']:
                        insert_columns.append("is_connected")
                        insert_values.append("TRUE")
                        
                    if table_info['has_status']:
                        insert_columns.append("status")
                        insert_values.append("'connected'")
                        
                    # Build the SQL statement
                    insert_sql = f"""
                        INSERT INTO integrations 
                        ({', '.join(insert_columns)})
                        VALUES 
                        ({', '.join(insert_values)})
                    """
                    
                    session.execute(text(insert_sql), insert_params)
                    logger.info("Created new Calendly integration")
                
                # Commit the transaction
                session.commit()
                logger.info("Successfully saved Calendly integration to database")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error: {str(e)}"
                )
        
        return {
            "status": "success", 
            "account_name": account_name, 
            "is_connected": True,
            "display_name": "Your Calendly Account"  # Added display_name for frontend
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Calendly API key format"
        )

@router.post("/api/integrations/calcom/api-key")
async def connect_calcom_api_key(
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
    # Require authentication for creating integrations
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to connect integrations"
        )
    
    user_id = current_user.id
    
    logger.info(f"Connecting Cal.com via API key for user {user_id}")
    
    if "api_key" not in api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is required"
        )
    
    calcom_api_key = api_key["api_key"].strip()
    logger.info(f"Received API key: {calcom_api_key[:4]}...{calcom_api_key[-4:] if len(calcom_api_key) > 8 else ''}")

    # Validate API key format and prepare for storage
    if calcom_api_key:
        logger.info(f"Processing Cal.com connection with valid API key format")
        
        # Store API key in extra_data JSON field
        extra_data = {"api_key": calcom_api_key}
        
        account_name = "Your Cal.com Account"
        account_id = "cal_" + calcom_api_key[-8:]  # Use part of API key to make unique
        
        # Create a new session for database operations
        from app.database import SessionLocal
        from sqlalchemy.sql import text
        
        with SessionLocal() as session:
            try:
                # First, check what columns actually exist in the integrations table
                table_info = {}
                try:
                    # Get column information
                    columns_result = session.execute(text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = 'integrations'"
                    ))
                    existing_columns = [row[0] for row in columns_result]
                    logger.info(f"Existing columns in integrations table: {existing_columns}")
                    
                    # Store which columns exist
                    table_info = {
                        'has_status': 'status' in existing_columns,
                        'has_is_connected': 'is_connected' in existing_columns,
                        'has_extra_data': 'extra_data' in existing_columns,
                        'has_api_key': 'api_key' in existing_columns
                    }
                    
                    logger.info(f"Table info: {table_info}")
                    
                    # If extra_data column doesn't exist, try to add it
                    if not table_info['has_extra_data']:
                        logger.warning("extra_data column missing - attempting to add it now")
                        try:
                            # Try multiple approaches to add the column
                            try:
                                # First attempt - standard ALTER TABLE
                                session.execute(text("ALTER TABLE integrations ADD COLUMN extra_data JSONB NULL"))
                                logger.info("Successfully added extra_data column using ALTER TABLE")
                            except Exception as e1:
                                logger.warning(f"First attempt to add column failed: {str(e1)}")
                                # Second attempt - with IF NOT EXISTS
                                session.execute(text("ALTER TABLE integrations ADD COLUMN IF NOT EXISTS extra_data JSONB NULL"))
                                logger.info("Successfully added extra_data column using IF NOT EXISTS")
                            
                            session.commit()
                            # Update our table info after adding the column
                            table_info['has_extra_data'] = True
                            logger.info("Successfully added extra_data column to integrations table")
                        except Exception as col_error:
                            session.rollback()
                            logger.error(f"Failed to add extra_data column: {str(col_error)}")
                            # Continue without the column - we'll store the API key elsewhere
                except Exception as e:
                    logger.warning(f"Could not get table schema: {str(e)}")
                    session.rollback()
                    # Assume columns for maximum compatibility
                    table_info = {
                        'has_status': False,
                        'has_is_connected': True,
                        'has_extra_data': False,
                        'has_api_key': True  # Most installations should have this
                    }
                
                # Simplified approach - check if integration exists for this platform AND user
                result = session.execute(
                    text("SELECT id FROM integrations WHERE platform = :platform AND user_id = :user_id"),
                    {"platform": "calcom", "user_id": user_id}
                )
                existing_row = result.fetchone()
                
                if existing_row:
                    # Update existing integration with only columns that exist
                    update_sql = """
                        UPDATE integrations 
                        SET account_name = :account_name, 
                            account_id = :account_id"""
                            
                    # Only include extra_data if the column exists
                    update_params = {
                        "id": existing_row[0],
                        "account_name": account_name,
                        "account_id": account_id
                    }
                    
                    if table_info.get('has_extra_data', False):
                        update_sql += ", extra_data = :extra_data"
                        update_params["extra_data"] = json.dumps(extra_data)
                    elif table_info.get('has_api_key', False):
                        # Fallback to store in api_key column if it exists
                        update_sql += ", api_key = :api_key"
                        update_params["api_key"] = calcom_api_key
                        logger.info("Using api_key column as fallback for storage")
                    
                    if table_info['has_is_connected']:
                        update_sql += ", is_connected = TRUE"
                        
                    if table_info['has_status']:
                        update_sql += ", status = 'connected'"
                        
                    update_sql += " WHERE id = :id"
                    
                    session.execute(text(update_sql), update_params)
                    logger.info(f"Updated existing Cal.com integration (ID: {existing_row[0]})")
                else:
                    # Insert new integration with only columns that exist
                    insert_columns = ["platform", "account_name", "account_id", "user_id"]
                    insert_values = [":platform", ":account_name", ":account_id", ":user_id"]
                    insert_params = {
                        "platform": "calcom",
                        "account_name": account_name,
                        "account_id": account_id,
                        "user_id": user_id
                    }
                    
                    # Only include extra_data if the column exists
                    if table_info.get('has_extra_data', False):
                        insert_columns.append("extra_data")
                        insert_values.append(":extra_data")
                        insert_params["extra_data"] = json.dumps(extra_data)
                    elif table_info.get('has_api_key', False):
                        # Fallback to store in api_key column if it exists
                        insert_columns.append("api_key")
                        insert_values.append(":api_key")
                        insert_params["api_key"] = calcom_api_key
                        logger.info("Using api_key column as fallback for storage")
                    
                    # Add optional columns if they exist
                    if table_info['has_is_connected']:
                        insert_columns.append("is_connected")
                        insert_values.append("TRUE")
                        
                    if table_info['has_status']:
                        insert_columns.append("status")
                        insert_values.append("'connected'")
                        
                    # Build the SQL statement
                    insert_sql = f"""
                        INSERT INTO integrations 
                        ({', '.join(insert_columns)})
                        VALUES 
                        ({', '.join(insert_values)})
                    """
                    
                    # Log the final SQL and parameters for debugging
                    logger.info(f"SQL to execute: {insert_sql}")
                    logger.info(f"Parameters: {insert_params}")
                    
                    try:
                        session.execute(text(insert_sql), insert_params)
                        logger.info("Created new Cal.com integration")
                    except Exception as insert_error:
                        # If this fails, we'll try a simplified version without the extra_data column
                        logger.error(f"Error inserting integration: {str(insert_error)}")
                        session.rollback()
                        
                        # Simplified approach - just the essential columns that should exist in all installations
                        simple_sql = """
                            INSERT INTO integrations (platform, account_name, account_id, user_id)
                            VALUES (:platform, :account_name, :account_id, :user_id)
                        """
                        session.execute(text(simple_sql), {
                            "platform": "calcom",
                            "account_name": account_name,
                            "account_id": account_id,
                            "user_id": user_id
                        })
                        logger.info("Created new Cal.com integration with simplified approach")
                
                # Commit the transaction
                session.commit()
                logger.info("Successfully saved Cal.com integration to database")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Database error: {str(e)}")
                # Try one last approach - use raw SQL that should work regardless of schema
                try:
                    # Direct SQL approach without checking schema
                    session.execute(text("""
                        INSERT INTO integrations (platform, account_name, account_id, user_id)
                        VALUES (:platform, :account_name, :account_id, :user_id)
                    """), {
                        "platform": "calcom",
                        "account_name": account_name,
                        "account_id": account_id,
                        "user_id": user_id
                    })
                    session.commit()
                    logger.info("Created integration with emergency fallback method")
                except Exception as final_error:
                    session.rollback()
                    logger.error(f"All attempts failed. Last error: {str(final_error)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database error: {str(e)}"
                    )
        
        return {
            "status": "success", 
            "account_name": account_name, 
            "is_connected": True,
            "display_name": "Your Cal.com Account"  # Added display_name for frontend
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Cal.com API key format"
        )
