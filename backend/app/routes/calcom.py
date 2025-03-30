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
def get_calcom_integration(db: Session, user_id: int = 1):
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
    user_id: int = 1
):
    """
    Get Cal.com user profile.
    
    Args:
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Cal.com user profile data
    """
    try:
        # Get Cal.com integration and API key
        integration, api_key = get_calcom_integration(db, user_id)
        
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
    user_id: int = 1
):
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
        integration, api_key = get_calcom_integration(db, user_id)
        
        # Build query parameters
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        # Make request to Cal.com API
        with httpx.Client() as client:
            response = client.get(
                f"{CALCOM_API_BASE}/bookings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                params=params
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
        logger.error(f"Error getting Cal.com bookings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Cal.com bookings: {str(e)}"
        )

@router.get("/event-types")
async def get_calcom_event_types(
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Get Cal.com event types.
    
    Args:
        user_id: User ID (defaults to 1 for testing/demo)
        
    Returns:
        dict: Cal.com event types data
    """
    try:
        # Get Cal.com integration and API key
        integration, api_key = get_calcom_integration(db, user_id)
        
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
    user_id: int = 1
):
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
        bookings_data = await get_calcom_bookings(start_date, end_date, db, user_id)
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
        event_types_data = await get_calcom_event_types(db, user_id)
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