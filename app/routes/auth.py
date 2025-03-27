"""
Authentication routes module.
Contains endpoints for OAuth and platform integrations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{platform}")
async def initiate_auth(
    platform: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate OAuth flow for a platform.
    
    Args:
        platform: The platform to authenticate with (youtube, stripe, calendly, calcom)
        
    Returns:
        dict: Redirect URL or authentication information.
    """
    # Placeholder for platform authentication logic (to be implemented)
    valid_platforms = ["youtube", "stripe", "calendly", "calcom"]
    
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )
    
    return {
        "message": f"Initiating {platform} authentication",
        "auth_url": f"https://example.com/oauth/{platform}"
    }

@router.get("/{platform}/callback")
async def auth_callback(
    platform: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth callback from platform.
    
    Args:
        platform: The platform authentication is for
        code: Authorization code from OAuth provider
        state: State parameter for security verification
        error: Error message if authorization failed
        
    Returns:
        dict: Authentication result information.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code"
        )
    
    # Placeholder for callback handling logic (to be implemented)
    return {
        "message": f"{platform} authentication successful",
        "platform": platform,
        "status": "connected"
    }

@router.get("/api/integrations")
async def get_integration_status(db: AsyncSession = Depends(get_db)):
    """
    Get the status of all platform integrations.
    
    Returns:
        dict: Status of each integration platform.
    """
    # Placeholder for integration status logic (to be implemented)
    return {
        "integrations": [
            {"platform": "youtube", "status": "disconnected"},
            {"platform": "stripe", "status": "disconnected"},
            {"platform": "calendly", "status": "disconnected"},
            {"platform": "calcom", "status": "disconnected"}
        ]
    }
