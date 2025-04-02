"""
Calendly routes module.
Contains endpoints for Calendly data and metrics.
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from datetime import datetime, timedelta

from app.database import get_db
from app.models.integration import Integration
from app.utils.calendly_api import get_calendly_data_for_integration

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/api/calendly/data")
async def get_calendly_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Get Calendly data for the current user.
    
    Returns:
        dict: Calendly data including events and metrics
    """
    try:
        # For demo/testing, use user_id=1
        user_id = 1
        
        # Check if user has Calendly integration
        integration_query = select(Integration).where(
            Integration.platform == "calendly",
            Integration.user_id == user_id
        )
        
        integration = await db.execute(integration_query)
        integration = integration.scalars().first()
        
        is_integration_connected = False
        api_key = None
        
        if integration:
            # Check if integration is connected
            if hasattr(integration, 'status') and integration.status == 'connected':
                is_integration_connected = True
            elif hasattr(integration, 'is_connected') and integration.is_connected:
                is_integration_connected = True
                
            # Get API key from extra_data if available
            if hasattr(integration, 'extra_data') and integration.extra_data:
                try:
                    if isinstance(integration.extra_data, str):
                        extra_data = json.loads(integration.extra_data)
                    else:
                        extra_data = integration.extra_data
                        
                    api_key = extra_data.get('api_key')
                    if api_key:
                        logger.info(f"Found Calendly API key for user {user_id}")
                except Exception as e:
                    logger.error(f"Error parsing extra_data: {str(e)}")
        
        # If no API key in database, try environment variable
        if not api_key:
            api_key = os.environ.get("CALENDLY_API_KEY")
            if api_key:
                logger.info("Using Calendly API key from environment variables")
        
        # If integration is connected and we have an API key, fetch real data
        if is_integration_connected and api_key:
            logger.info("Fetching real Calendly data from API")
            
            # Fetch real data from Calendly API
            calendly_data = await get_calendly_data_for_integration(api_key)
            
            return {
                "message": "Real Calendly data from API",
                "data": calendly_data
            }
        else:
            # Return demo data
            logger.info("Returning demo Calendly data")
            return {
                "message": "Demo Calendly data (no integration connected)",
                "data": get_demo_calendly_data()
            }
    
    except Exception as e:
        logger.error(f"Error in get_calendly_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Calendly data: {str(e)}"
        )

def get_demo_calendly_data() -> Dict[str, Any]:
    """
    Get demo Calendly data for testing.
    
    Returns:
        dict: Demo Calendly data
    """
    # Generate some demo events
    now = datetime.now()
    events = []
    
    for i in range(10):
        event_date = now - timedelta(days=i*3)
        events.append({
            "uri": f"https://api.calendly.com/scheduled_events/event_{i}",
            "name": f"Demo Meeting {i+1}",
            "status": "active",
            "start_time": (event_date + timedelta(hours=10)).isoformat() + "Z",
            "end_time": (event_date + timedelta(hours=11)).isoformat() + "Z",
            "created_at": (event_date - timedelta(days=5)).isoformat() + "Z",
            "updated_at": (event_date - timedelta(days=5)).isoformat() + "Z",
            "event_type": "30min" if i % 2 == 0 else "60min",
            "location": "Zoom" if i % 3 == 0 else "Google Meet"
        })
    
    # Create daily data for chart
    daily_data = []
    for i in range(30):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        count = i % 3  # 0, 1, or 2 events per day
        if count > 0:
            daily_data.append({"date": day, "count": count})
    
    # Sort by date
    daily_data.sort(key=lambda x: x["date"])
    
    return {
        "message": "Demo Calendly data",
        "events": events,
        "user": {
            "uri": "https://api.calendly.com/users/demo-user",
            "name": "Demo User",
            "email": "demo@example.com",
            "scheduling_url": "https://calendly.com/demo-user",
            "timezone": "America/New_York",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        "metrics": {
            "totalEvents": len(events),
            "dailyData": daily_data,
            "eventsByType": [
                {"type": "30min", "count": 5},
                {"type": "60min", "count": 5}
            ],
            "averageEventsPerDay": 1.2
        }
    }