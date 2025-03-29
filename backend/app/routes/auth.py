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

from app.database import get_db
from app.models.integration import Integration, IntegrationType, IntegrationStatus
from app.schemas.integration import IntegrationStatusList, IntegrationUpdate, IntegrationCreate

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
        "scopes": ["read_only"],
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
        "auth_url": "https://api.cal.com/oauth/authorize",
        "token_url": "https://api.cal.com/oauth/token",
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
    
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    
    # Redirect to authorization URL
    return RedirectResponse(url=auth_url)

@router.get("/auth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str,
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
    # Check for error
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error={error}&platform={platform}"
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
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": config["redirect_uri"]
            }
            
            # Make token request
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"}
            )
            
            # Check response
            if response.status_code != 200:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/integrations?error=token_error&platform={platform}"
                )
            
            # Parse token response
            token_info = response.json()
            
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
                
                # For Stripe, store additional metadata
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
                
                # For Stripe, store additional metadata
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
    db: Session = Depends(get_db)
):
    """
    Disconnect an integration.
    
    Args:
        platform: The platform to disconnect
        
    Returns:
        dict: Disconnection result.
    """
    # Validate platform
    if platform not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(OAUTH_CONFIG.keys())}"
        )
    
    # Find integration in database
    integration = db.query(Integration).filter(Integration.platform == platform).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration for {platform} not found"
        )
    
    # Update integration status
    integration.status = IntegrationStatus.DISCONNECTED
    db.commit()
    
    return {
        "message": f"{platform} disconnected successfully",
        "platform": platform,
        "status": "disconnected"
    }

@router.get("/api/integrations/status", response_model=IntegrationStatusList)
async def get_integration_status(db: Session = Depends(get_db)):
    """
    Get the status of all platform integrations.
    
    Returns:
        IntegrationStatusList: Status of each integration platform.
    """
    # Get all platforms from config
    platforms = list(OAUTH_CONFIG.keys())
    
    # Get integrations from database
    integrations = db.query(Integration).all()
    
    # Create status dict with default values
    status_dict = {platform: {"platform": platform, "status": "disconnected"} for platform in platforms}
    
    # Update with actual values from DB
    for integration in integrations:
        status = integration.status if isinstance(integration.status, str) else str(integration.status)
        status_dict[integration.platform] = {
            "platform": integration.platform,
            "status": status,
            "account_name": integration.account_name,
            "last_sync": integration.last_sync
        }
    
    # Convert to list and return
    status_list = list(status_dict.values())
    
    return {"integrations": status_list}

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

async def sync_platform_data(platform: str, db: Session):
    """
    Sync data from the integrated platform.
    This function would be implemented to pull data from the platform APIs.
    
    Args:
        platform: The platform to sync data from
        db: Database session
    """
    # This is a placeholder - in a real implementation, this would:
    # 1. Get the integration record from the database
    # 2. Use the access token to fetch data from the platform API
    # 3. Process and store the data in the appropriate tables
    # 4. Update the last_sync timestamp on the integration record
    
    try:
        # Get integration record
        integration = db.query(Integration).filter(Integration.platform == platform).first()
        
        if not integration or not integration.is_connected:
            return
        
        # For demonstration purposes, just update the last_sync timestamp
        integration.last_sync = datetime.utcnow()
        db.commit()
        
        print(f"Data sync for {platform} completed successfully!")
    
    except Exception as e:
        print(f"Error syncing data for {platform}: {str(e)}")
