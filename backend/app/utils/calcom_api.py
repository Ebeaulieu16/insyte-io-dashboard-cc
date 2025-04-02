"""
Cal.com API utility functions.
Handles fetching real data from the Cal.com API using API keys.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# Cal.com API base URL
CALCOM_API_BASE_URL = "https://api.cal.com/v1"

async def fetch_calcom_user_data(api_key: str) -> Dict[str, Any]:
    """
    Fetch user data from the Cal.com API.
    
    Args:
        api_key: Cal.com API key
        
    Returns:
        dict: User data
    """
    try:
        logger.info("Fetching Cal.com user data")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CALCOM_API_BASE_URL}/me", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Successfully fetched Cal.com user data for: {data.get('email', 'Unknown')}")
            
            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "email": data.get("email"),
                "username": data.get("username"),
                "timeZone": data.get("timeZone"),
                "avatar": data.get("avatar"),
                "bio": data.get("bio"),
                "weekStart": data.get("weekStart")
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Cal.com user data: {e.response.status_code} - {e.response.text}")
        return {"error": f"Cal.com API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching Cal.com user data: {str(e)}")
        return {"error": f"Error: {str(e)}"}

async def fetch_calcom_bookings(api_key: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch bookings from Cal.com.
    
    Args:
        api_key: Cal.com API key
        days: Number of days to look back
        
    Returns:
        list: List of booking data
    """
    try:
        logger.info(f"Fetching Cal.com bookings for the past {days} days")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CALCOM_API_BASE_URL}/bookings", headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                logger.warning("No bookings found in Cal.com account")
                return []
            
            bookings = []
            for item in data:
                booking = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "startTime": item.get("startTime"),
                    "endTime": item.get("endTime"),
                    "attendees": item.get("attendees", []),
                    "status": item.get("status"),
                    "eventTypeId": item.get("eventTypeId"),
                    "location": item.get("location"),
                    "createdAt": item.get("createdAt")
                }
                bookings.append(booking)
            
            logger.info(f"Successfully fetched {len(bookings)} bookings from Cal.com")
            return bookings
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Cal.com bookings: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching Cal.com bookings: {str(e)}")
        return []

async def fetch_calcom_event_types(api_key: str) -> List[Dict[str, Any]]:
    """
    Fetch event types from Cal.com.
    
    Args:
        api_key: Cal.com API key
        
    Returns:
        list: List of event type data
    """
    try:
        logger.info("Fetching Cal.com event types")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CALCOM_API_BASE_URL}/event-types", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                logger.warning("No event types found in Cal.com account")
                return []
            
            event_types = []
            for item in data:
                event_type = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "length": item.get("length"),
                    "slug": item.get("slug"),
                    "hidden": item.get("hidden", False),
                    "position": item.get("position"),
                    "price": item.get("price"),
                    "currency": item.get("currency")
                }
                event_types.append(event_type)
            
            logger.info(f"Successfully fetched {len(event_types)} event types from Cal.com")
            return event_types
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Cal.com event types: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching Cal.com event types: {str(e)}")
        return []

async def get_calcom_data_for_integration(api_key: str) -> Dict[str, Any]:
    """
    Get comprehensive Cal.com data.
    
    Args:
        api_key: Cal.com API key
        
    Returns:
        dict: Complete Cal.com data including user info, bookings, and event types
    """
    try:
        # Fetch user data
        user_data = await fetch_calcom_user_data(api_key)
        if "error" in user_data:
            return {
                "message": user_data["error"],
                "bookings": [],
                "eventTypes": [],
                "user": {},
                "metrics": {}
            }
        
        # Fetch bookings
        bookings = await fetch_calcom_bookings(api_key)
        
        # Fetch event types
        event_types = await fetch_calcom_event_types(api_key)
        
        # Calculate metrics
        total_bookings = len(bookings)
        
        # Group bookings by day
        bookings_by_day = {}
        for booking in bookings:
            if "startTime" in booking:
                day = booking["startTime"].split("T")[0]
                if day not in bookings_by_day:
                    bookings_by_day[day] = 0
                bookings_by_day[day] += 1
        
        # Convert to list for charting
        daily_data = [{"date": day, "count": count} for day, count in bookings_by_day.items()]
        daily_data.sort(key=lambda x: x["date"])
        
        # Group bookings by event type
        bookings_by_type = {}
        for booking in bookings:
            event_type_id = booking.get("eventTypeId", "Unknown")
            if event_type_id not in bookings_by_type:
                bookings_by_type[event_type_id] = 0
            bookings_by_type[event_type_id] += 1
        
        # Map event type IDs to names
        event_type_map = {str(et.get("id")): et.get("title", "Unknown") for et in event_types}
        
        # Convert to list for charting with proper names
        type_data = [
            {"type": event_type_map.get(str(type_id), f"Type {type_id}"), "count": count} 
            for type_id, count in bookings_by_type.items()
        ]
        
        return {
            "message": "Real Cal.com data from API",
            "bookings": bookings,
            "eventTypes": event_types,
            "user": user_data,
            "metrics": {
                "totalBookings": total_bookings,
                "dailyData": daily_data,
                "bookingsByType": type_data,
                "averageBookingsPerDay": total_bookings / 30 if total_bookings > 0 else 0
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting Cal.com data: {str(e)}")
        return {
            "message": f"Error: {str(e)}",
            "bookings": [],
            "eventTypes": [],
            "user": {},
            "metrics": {}
        }
