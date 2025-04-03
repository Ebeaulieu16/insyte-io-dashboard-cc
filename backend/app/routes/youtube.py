"""
YouTube routes module.
Contains endpoints for YouTube metrics and video analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
import random
import logging
import json

from app.database import get_db
from app.utils.youtube_api import get_youtube_data_for_integration
from app.routes.auth import get_optional_current_user
from app.models.user import User
from app.models.integration import Integration
from sqlalchemy import select

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/youtube",
    tags=["youtube"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_youtube_metrics(
    slug: Optional[str] = Query(None, description="Filter by video slug"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get YouTube metrics, optionally filtered by video slug.
    
    Args:
        slug: Optional slug to filter by specific video
        
    Returns:
        dict: A dictionary containing YouTube metrics.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Get user's YouTube integration
    integration_query = select(Integration).where(
        Integration.platform == "youtube",
        Integration.user_id == current_user.id
    )
    
    integration = await db.execute(integration_query)
    integration = integration.scalars().first()
    
    if not integration or not integration.extra_data:
        return {
            "message": "Demo Mode - No YouTube integration found",
            "metrics": get_demo_youtube_metrics()
        }
        
    # If we have an integration with valid extra_data, get real metrics
    try:
        api_key = integration.extra_data.get("api_key")
        channel_id = integration.extra_data.get("channel_id")
        
        if not api_key or not channel_id:
            return {
                "message": "YouTube integration missing API key or channel ID",
                "metrics": get_demo_youtube_metrics()
            }
            
        # Get real YouTube metrics using the API key and channel ID
        metrics = await get_youtube_data_for_integration(api_key, channel_id)
        return {
            "message": "Success",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error getting YouTube metrics: {str(e)}")
        return {
            "message": f"Error getting YouTube metrics: {str(e)}",
            "metrics": get_demo_youtube_metrics()
        }

@router.get("/data")
async def get_youtube_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """
    Get YouTube video and performance data.
    
    This endpoint checks if a YouTube integration is connected for the current user
    and returns real data if available. Otherwise, it returns demo data.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: A dictionary containing YouTube metrics and video data
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_id = current_user.id
    logger.info(f"Getting YouTube data for user_id: {user_id}")
    
    try:
        # Check if user has a YouTube integration connected
        has_youtube_integration = False
        youtube_integration = None
        
        # First, get the user's YouTube integration
        try:
            integration_query = """
                SELECT id, platform, user_id, extra_data 
                FROM integrations 
                WHERE platform = 'youtube' AND user_id = :user_id
                AND (status = 'connected' OR is_connected = TRUE)
            """
            result = await db.execute(text(integration_query), {"user_id": user_id})
            youtube_integration = result.fetchone()
            
            has_youtube_integration = youtube_integration is not None
            logger.info(f"YouTube integration found: {has_youtube_integration}")
            
        except Exception as e:
            logger.error(f"Error checking YouTube integration: {str(e)}")
        
        # If user has a YouTube integration with valid credentials
        if has_youtube_integration and youtube_integration and youtube_integration.extra_data:
            try:
                # Extract API key and channel ID
                extra_data = youtube_integration.extra_data
                if isinstance(extra_data, str):
                    import json
                    extra_data = json.loads(extra_data)
                
                api_key = extra_data.get('api_key')
                channel_id = extra_data.get('channel_id')
                
                if api_key and channel_id:
                    logger.info(f"Found valid YouTube credentials for user {user_id}")
                    
                    # Try to get real video data from the database
                    videos_query = """
                        SELECT * FROM video_analytics
                        WHERE user_id = :user_id AND is_demo = FALSE
                        ORDER BY created_at DESC
                        LIMIT 10
                    """
                    videos_result = await db.execute(text(videos_query), {"user_id": user_id})
                    real_videos = videos_result.fetchall()
                    
                    if real_videos and len(real_videos) > 0:
                        logger.info(f"Found {len(real_videos)} real videos for user {user_id}")
                        
                        # Convert real videos to response format
                        videos = []
                        for video in real_videos:
                            videos.append({
                                "id": video.id,
                                "title": video.title,
                                "views": video.views or 0,
                                "likes": video.likes or 0,
                                "comments": video.comments or 0,
                                "avgViewDuration": video.avg_view_duration or "0:00",
                                "clicks": video.clicks or 0,
                                "bookedCalls": video.booked_calls or 0,
                                "closedDeals": video.closed_deals or 0,
                                "revenue": video.revenue or 0,
                            })
                        
                        return {
                            "videos": videos,
                            "is_demo": False,
                            "message": "Real video data retrieved successfully"
                        }
                    else:
                        logger.info(f"No real videos found for user {user_id}, syncing from YouTube API")
                        # TODO: Implement API sync here
                        # For now, return demo data with a note
                        demo_videos = get_demo_youtube_videos()
                        return {
                            "videos": demo_videos,
                            "is_demo": True,
                            "message": "No real videos found yet. Please sync your YouTube channel or add videos."
                        }
                        
                else:
                    logger.warning(f"YouTube integration missing API key or channel ID for user {user_id}")
            except Exception as e:
                logger.error(f"Error processing YouTube integration: {str(e)}")
        
        # Return demo data if no integration or error occurred
        logger.info(f"Using demo data for user {user_id}")
        demo_videos = get_demo_youtube_videos()
        return {
            "videos": demo_videos,
            "is_demo": True,
            "message": "Demo data - Connect your YouTube channel to see real data"
        }
        
    except Exception as e:
        logger.error(f"Error in get_youtube_data: {str(e)}")
        # Return demo data as fallback
        return {
            "videos": get_demo_youtube_videos(),
            "is_demo": True,
            "message": f"Error retrieving data: {str(e)}"
        }

# Define helper function for demo YouTube videos
def get_demo_youtube_videos() -> List[Dict[str, Any]]:
    """Return demo YouTube video data for users without real data."""
    return [
            {
                "id": 1,
                "title": "Scale Your Agency with Systems & Automations",
                "views": 32450,
                "likes": 1850,
                "comments": 324,
                "avgViewDuration": "8:45",
                "clicks": 423,
                "bookedCalls": 86,
                "closedDeals": 52,
                "revenue": 302600,
            },
            {
                "id": 2,
                "title": "Content Marketing Secrets for 2023",
                "views": 28750,
                "likes": 1620,
                "comments": 287,
                "avgViewDuration": "7:32",
                "clicks": 378,
                "bookedCalls": 75,
                "closedDeals": 43,
                "revenue": 250600,
            },
            {
                "id": 3,
                "title": "LinkedIn Lead Gen Strategy Masterclass",
                "views": 24320,
                "likes": 1320,
                "comments": 245,
                "avgViewDuration": "9:15",
                "clicks": 312,
                "bookedCalls": 68,
                "closedDeals": 38,
                "revenue": 221400,
            },
            {
                "id": 4,
                "title": "SEO Tips for Digital Agencies",
                "views": 21580,
                "likes": 1150,
                "comments": 198,
                "avgViewDuration": "6:48",
                "clicks": 287,
                "bookedCalls": 55,
                "closedDeals": 32,
                "revenue": 186400,
            },
            {
                "id": 5,
                "title": "Email Marketing for Client Attraction",
                "views": 18970,
                "likes": 980,
                "comments": 164,
                "avgViewDuration": "8:12",
                "clicks": 235,
                "bookedCalls": 48,
                "closedDeals": 28,
                "revenue": 163100,
            },
        ]
