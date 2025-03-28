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

from app.database import get_db
from app.models.integration import Integration, IntegrationType
from app.schemas.integration import IntegrationStatus, IntegrationStatusList, IntegrationUpdate, IntegrationCreate

router = APIRouter(
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

# Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

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
    
    # Generate state token to prevent CSRF
    state = secrets.token_urlsafe(32)
    
    # Store state in the session or database
    # For simplicity, we'll return it in the URL but should use session in production
    
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
    
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    
    # Redirect to authorization URL
    return RedirectResponse(url=auth_url)

@router.get("/auth/{platform}/callback")
async def auth_callback(
    platform: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from platform.
    
    Args:
        platform: The platform authentication is for
        code: Authorization code from OAuth provider
        state: State parameter for security verification
        error: Error message if authorization failed
        
    Returns:
        RedirectResponse: Redirects back to the frontend application.
    """
    # Check for errors
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error={error}&platform={platform}"
        )
    
    if not code:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error=missing_code&platform={platform}"
        )
    
    # Get platform configuration
    config = get_oauth_config(platform)
    
    try:
        # Exchange code for access token
        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(config["token_url"], data=token_data)
            
            if response.status_code != 200:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/integrations?error=token_exchange_failed&platform={platform}"
                )
            
            token_info = response.json()
            
            # Get account information (implementation differs by platform)
            account_name, account_id = await get_account_info(platform, token_info["access_token"])
            
            # Store token in database
            integration = db.query(Integration).filter(Integration.platform == platform).first()
            
            if not integration:
                # Create new integration record
                integration = Integration(
                    platform=platform,
                    is_connected=True,
                    access_token=token_info["access_token"],
                    refresh_token=token_info.get("refresh_token"),
                    token_expires_at=datetime.utcnow() + timedelta(seconds=token_info.get("expires_in", 3600)),
                    account_name=account_name,
                    account_id=account_id
                )
                db.add(integration)
            else:
                # Update existing integration
                integration.is_connected = True
                integration.access_token = token_info["access_token"]
                if "refresh_token" in token_info:
                    integration.refresh_token = token_info["refresh_token"]
                integration.token_expires_at = datetime.utcnow() + timedelta(seconds=token_info.get("expires_in", 3600))
                integration.account_name = account_name
                integration.account_id = account_id
            
            db.commit()
            
            # Schedule initial data sync in the background
            if background_tasks:
                background_tasks.add_task(sync_platform_data, platform, db)
            
            # Redirect back to frontend with success message
            return RedirectResponse(
                url=f"{FRONTEND_URL}/integrations?success=true&platform={platform}"
            )
    
    except Exception as e:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/integrations?error={str(e)}&platform={platform}"
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
    integration.is_connected = False
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
        status = "connected" if integration.is_connected else "disconnected"
        status_dict[integration.platform] = {
            "platform": integration.platform,
            "status": status,
            "account_name": integration.account_name,
            "last_sync": integration.last_sync
        }
    
    # Convert to list and return
    status_list = [IntegrationStatus(**data) for data in status_dict.values()]
    
    return IntegrationStatusList(integrations=status_list)

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
        print(f"Error getting account info for {platform}: {str(e)}")
    
    # Default fallback
    return f"{platform.title()} Account", ""

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
