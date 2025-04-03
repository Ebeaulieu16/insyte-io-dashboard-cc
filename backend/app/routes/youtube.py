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
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    """
    Get YouTube video and performance data.
    
    This endpoint checks if any integration is connected and returns real-looking data
    if there's at least one active integration. Otherwise, it returns demo data.
    
    Args:
        db: Database session
        
    Returns:
        dict: A dictionary containing YouTube metrics and video data
    """
    try:
        # Check if any integration is connected
        is_any_integration_connected = False
        
        # Query the integrations table to check if any platform is connected
        try:
            # First check if the table exists and has is_connected column
            table_info = {}
            try:
                # Check if integrations table has is_connected column
                table_check_query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'integrations' 
                AND table_schema = 'public'
                """
                result = await db.execute(text(table_check_query))
                columns = result.fetchall()
                
                # Create a dictionary of column existence
                table_info = {
                    "has_is_connected": any(col[0] == 'is_connected' for col in columns),
                    "has_status": any(col[0] == 'status' for col in columns),
                }
                
                logger.debug(f"Integration table columns: {table_info}")
            except Exception as e:
                logger.error(f"Error checking table schema: {e}")
                table_info = {"has_is_connected": False, "has_status": False}
            
            # Build the query based on available columns to check for any connected integration
            if table_info.get("has_is_connected", False):
                query = """
                SELECT COUNT(*) FROM integrations 
                WHERE is_connected = true
                """
            elif table_info.get("has_status", False):
                query = """
                SELECT COUNT(*) FROM integrations 
                WHERE status = 'connected'
                """
            else:
                query = """
                SELECT COUNT(*) FROM integrations
                """
            
            # Log the detailed query we're about to execute
            logger.info(f"Executing query for YouTube connection check: {query}")
            
            result = await db.execute(text(query))
            count = result.scalar()
            
            # Log the count result
            logger.info(f"Found {count} connected integrations for YouTube data")
            
            is_any_integration_connected = count > 0
            logger.info(f"Integration connection status: {'Connected' if is_any_integration_connected else 'Not connected'}")
            
            # Also try checking specific platforms as a backup
            if not is_any_integration_connected:
                # Try to check if any YouTube integration exists specifically
                backup_query = """
                SELECT platform FROM integrations 
                WHERE platform = 'youtube'
                """
                backup_result = await db.execute(text(backup_query))
                backup_rows = backup_result.fetchall()
                
                if len(backup_rows) > 0:
                    logger.info(f"Found YouTube platform via backup query: {backup_rows}")
                    is_any_integration_connected = True
            
        except Exception as e:
            logger.error(f"Error checking integration connections: {e}")
            is_any_integration_connected = False
        
        # Check if we actually have connected integrations
        logger.info(f"Integration connection status: {'Connected' if is_any_integration_connected else 'Not connected'}")
        
        # Demo data for YouTube videos
        demo_videos = [
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
        
        if not is_any_integration_connected:
            logger.info("No integrations found, returning demo data")
            # Return static demo data
            return {
                "message": "Demo data - No integrations connected",
                "videos": demo_videos
            }
        
        # At least one integration is connected, fetch real data from YouTube API
        logger.info("Fetching real data from YouTube API")
        
        try:
            # Get YouTube API key and channel ID from the integration
            integration_query = """
            SELECT account_id, extra_data 
            FROM integrations 
            WHERE platform = 'youtube' AND 
            (status = 'connected' OR is_connected = true)
            LIMIT 1
            """
            
            result = await db.execute(text(integration_query))
            integration = result.fetchone()
            
            if not integration:
                logger.warning("No YouTube integration found in database despite connection check")
                # Fall back to demo data
                return {
                    "message": "Demo data - No YouTube integration found",
                    "videos": demo_videos
                }
            
            channel_id = integration[0]  # account_id contains the channel ID
            extra_data = integration[1]
            
            # Parse extra_data to get the API key
            api_key = None
            if extra_data:
                try:
                    if isinstance(extra_data, str):
                        data = json.loads(extra_data)
                    else:
                        data = extra_data
                    
                    api_key = data.get("api_key")
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.error(f"Error parsing extra_data: {e}")
            
            # If we couldn't get the API key from extra_data, try environment variables
            if not api_key:
                import os
                api_key = os.getenv("YOUTUBE_API_KEY")
                logger.info("Using YouTube API key from environment variables")
            
            if not api_key:
                logger.error("No YouTube API key found")
                # Fall back to demo data
                return {
                    "message": "Demo data - No YouTube API key found",
                    "videos": demo_videos
                }
            
            # Fetch real data from YouTube API
            youtube_data = await get_youtube_data_for_integration(api_key, channel_id)
            
            if not youtube_data.get("videos"):
                logger.warning("No videos found from YouTube API")
                # Fall back to demo data
                return {
                    "message": "Demo data - No videos found from YouTube API",
                    "videos": demo_videos
                }
            
            logger.info(f"Successfully fetched {len(youtube_data['videos'])} videos from YouTube API")
            return youtube_data
            
        except Exception as e:
            logger.error(f"Error fetching real YouTube data: {e}")
            # Fall back to demo data on error
            return {
                "message": f"Demo data - Error fetching real data: {str(e)}",
                "videos": demo_videos
            }
        
    except Exception as e:
        logger.error(f"Error fetching YouTube data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch YouTube data: {str(e)}"
        )
