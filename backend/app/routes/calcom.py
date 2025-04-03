"""
Cal.com API routes module.
Contains endpoints for interacting with Cal.com API using API key.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import httpx
import logging
import os
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models.integration import Integration, IntegrationType, IntegrationStatus, IntegrationAuthType
from app.models.call import CallStatus
from app.utils.calcom_api import get_calcom_data_for_integration
from app.routes.auth import get_optional_current_user

router = APIRouter(
    prefix="/api/calcom",
    tags=["calcom"],
    responses={404: {"description": "Not found"}}
)

# Get logger
logger = logging.getLogger(__name__)

# Constants
CALCOM_API_BASE = "https://api.cal.com/v2"

# Helper functions
def get_calcom_integration(db: Session, user_id: int):
    """Get Cal.com integration for the user."""
    integration = db.query(Integration).filter(
        Integration.user_id == user_id,
        Integration.platform == "calcom",
        Integration.status == IntegrationStatus.CONNECTED
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cal.com integration not found or not connected"
        )
    
    if integration.auth_type != IntegrationAuthType.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cal.com integration is not configured with API key"
        )
    
    # Get API key from integration
    api_key = None
    if integration.extra_data:
        if isinstance(integration.extra_data, str):
            data = json.loads(integration.extra_data)
        else:
            data = integration.extra_data
        api_key = data.get("api_key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cal.com API key not found in integration"
        )
    
    return integration, api_key

def map_calcom_status_to_internal(calcom_status: str) -> str:
    """
    Map Cal.com booking status to internal CallStatus.
    
    Args:
        calcom_status: Status from Cal.com API
        
    Returns:
        str: Corresponding internal CallStatus value
    """
    status_mapping = {
        "ACCEPTED": CallStatus.CONFIRMED,
        "PENDING": CallStatus.PENDING,
        "CANCELLED": CallStatus.CANCELLED,
        "REJECTED": CallStatus.CANCELLED,
        # Default to BOOKED if status is unknown
        "UNKNOWN": CallStatus.BOOKED
    }
    
    return status_mapping.get(calcom_status, CallStatus.BOOKED)

# API endpoints
@router.get("/")
async def get_calcom_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    """
    Get Cal.com user profile.
    
    Args:
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Cal.com user profile data
    """
    try:
        # Get Cal.com integration and API key
        integration, api_key = get_calcom_integration(db, current_user.id)
        
        # Make request to Cal.com API
        with httpx.Client() as client:
            response = client.get(
                f"{CALCOM_API_BASE}/me",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Cal.com API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cal.com API error: {response.text}"
                )
            
            # Update last sync timestamp
            integration.last_sync = datetime.utcnow()
            db.commit()
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Cal.com user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Cal.com user profile: {str(e)}"
        )

@router.get("/bookings")
async def get_calcom_bookings(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    """
    Get Cal.com bookings.
    
    Args:
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Cal.com bookings data
    """
    try:
        # Get Cal.com integration and API key
        integration, api_key = get_calcom_integration(db, current_user.id)
        
        # Build query parameters
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        # Make request to Cal.com API
        with httpx.Client() as client:
            response = await client.get(
                f"{CALCOM_API_BASE}/api/bookings",
                headers={"Authorization": f"Bearer {api_key}"},
                params=params
            )
            response.raise_for_status()
            return response.json()
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting Cal.com bookings: {str(e)}")
        return {
            "message": f"Error getting Cal.com bookings: {str(e)}",
            "bookings": []
        }

@router.get("/event-types")
async def get_calcom_event_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    """
    Get Cal.com event types.
    
    Args:
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Cal.com event types data
    """
    try:
        # Get Cal.com integration and API key
        integration, api_key = get_calcom_integration(db, current_user.id)
        
        # Make request to Cal.com API
        with httpx.Client() as client:
            response = client.get(
                f"{CALCOM_API_BASE}/event-types",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Cal.com API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cal.com API error: {response.text}"
                )
            
            # Update last sync timestamp
            integration.last_sync = datetime.utcnow()
            db.commit()
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Cal.com event types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Cal.com event types: {str(e)}"
        )

@router.get("/stats")
async def get_calcom_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    """
    Get Cal.com booking statistics.
    
    Args:
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Cal.com booking statistics
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Get bookings
        bookings_data = await get_calcom_bookings(start_date, end_date, db, current_user)
        bookings = bookings_data.get("bookings", [])
        
        # Calculate statistics using our internal status values
        total_bookings = len(bookings)
        
        # Count by status using our internal status names
        status_counts = {status.value: 0 for status in CallStatus}
        
        for booking in bookings:
            calcom_status = booking.get("status", "UNKNOWN")
            internal_status = map_calcom_status_to_internal(calcom_status)
            status_counts[internal_status] += 1
        
        # Get event types to map IDs to names
        event_types_data = await get_calcom_event_types(db, current_user)
        event_types = {str(et.get("id")): et.get("title") for et in event_types_data.get("event_types", [])}
        
        # Calculate bookings by event type
        bookings_by_event_type = {}
        for booking in bookings:
            event_type_id = str(booking.get("eventTypeId", ""))
            event_type_name = event_types.get(event_type_id, f"Event Type {event_type_id}")
            
            if event_type_name not in bookings_by_event_type:
                bookings_by_event_type[event_type_name] = 0
            
            bookings_by_event_type[event_type_name] += 1
        
        # Return statistics with our internal status counts
        return {
            "total_bookings": total_bookings,
            "status_counts": status_counts,
            "confirmed_bookings": status_counts[CallStatus.CONFIRMED],
            "pending_bookings": status_counts[CallStatus.PENDING],
            "cancelled_bookings": status_counts[CallStatus.CANCELLED],
            "completed_bookings": status_counts[CallStatus.COMPLETED],
            "no_show_bookings": status_counts[CallStatus.NO_SHOW],
            "bookings_by_event_type": bookings_by_event_type,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Cal.com statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Cal.com statistics: {str(e)}"
        )

@router.get("/comprehensive-data")
async def get_calcom_comprehensive_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    """
    Get comprehensive Cal.com data using the new API utility.
    Fetches user profile, bookings, event types, and calculates metrics.
    
    Args:
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Comprehensive Cal.com data
    """
    try:
        # Get Cal.com integration and API key
        try:
            integration, api_key = get_calcom_integration(db, current_user.id)
            logger.info(f"Found Cal.com integration for user {current_user.id}")
        except HTTPException as e:
            # If integration not found, return demo data
            logger.warning(f"Cal.com integration not found: {e.detail}")
            return {
                "message": "Demo Cal.com data (no integration connected)",
                "data": get_demo_calcom_data()
            }
        
        # Fetch real data using the API utility
        logger.info("Fetching real Cal.com data from API")
        calcom_data = await get_calcom_data_for_integration(api_key)
        
        return {
            "message": "Real Cal.com data from API",
            "data": calcom_data
        }
    
    except Exception as e:
        logger.error(f"Error in get_calcom_comprehensive_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Cal.com data: {str(e)}"
        )

def get_demo_calcom_data() -> Dict[str, Any]:
    """
    Get demo Cal.com data for testing.
    
    Returns:
        dict: Demo Cal.com data
    """
    # Generate some demo bookings
    now = datetime.now()
    bookings = []
    
    for i in range(10):
        booking_date = now - timedelta(days=i*2)
        bookings.append({
            "id": f"booking_{i}",
            "title": f"Demo Booking {i+1}",
            "description": f"This is a demo booking {i+1}",
            "startTime": (booking_date + timedelta(hours=9)).isoformat(),
            "endTime": (booking_date + timedelta(hours=10)).isoformat(),
            "attendees": [
                {"email": f"attendee{i}@example.com", "name": f"Attendee {i}"}
            ],
            "status": "ACCEPTED" if i % 4 != 0 else "CANCELLED",
            "eventTypeId": i % 3 + 1,
            "location": "Zoom",
            "createdAt": (booking_date - timedelta(days=3)).isoformat()
        })
    
    # Create event types
    event_types = [
        {
            "id": 1,
            "title": "15 Minute Meeting",
            "description": "Quick 15 minute meeting",
            "length": 15,
            "slug": "15min",
            "hidden": False,
            "position": 1,
            "price": 0,
            "currency": "USD"
        },
        {
            "id": 2,
            "title": "30 Minute Meeting",
            "description": "Standard 30 minute meeting",
            "length": 30,
            "slug": "30min",
            "hidden": False,
            "position": 2,
            "price": 0,
            "currency": "USD"
        },
        {
            "id": 3,
            "title": "60 Minute Meeting",
            "description": "Extended 60 minute meeting",
            "length": 60,
            "slug": "60min",
            "hidden": False,
            "position": 3,
            "price": 0,
            "currency": "USD"
        }
    ]
    
    # Create daily data for chart
    daily_data = []
    for i in range(30):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        count = i % 3  # 0, 1, or 2 bookings per day
        if count > 0:
            daily_data.append({"date": day, "count": count})
    
    # Sort by date
    daily_data.sort(key=lambda x: x["date"])
    
    return {
        "message": "Demo Cal.com data",
        "bookings": bookings,
        "eventTypes": event_types,
        "user": {
            "id": "user_demo",
            "name": "Demo User",
            "email": "demo@example.com",
            "username": "demo_user",
            "timeZone": "America/New_York",
            "avatar": "https://ui-avatars.com/api/?name=Demo+User",
            "bio": "This is a demo user for Cal.com integration",
            "weekStart": "Sunday"
        },
        "metrics": {
            "totalBookings": len(bookings),
            "dailyData": daily_data,
            "bookingsByType": [
                {"type": "15 Minute Meeting", "count": 3},
                {"type": "30 Minute Meeting", "count": 4},
                {"type": "60 Minute Meeting", "count": 3}
            ],
            "averageBookingsPerDay": 1.0
        }
    }