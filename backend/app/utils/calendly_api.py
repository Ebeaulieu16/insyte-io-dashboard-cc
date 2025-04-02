"""
Calendly API utility functions.
Handles fetching real data from the Calendly API using API keys.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# Calendly API base URL
CALENDLY_API_BASE_URL = "https://api.calendly.com"

async def fetch_calendly_user_data(api_key: str) -> Dict[str, Any]:
    """
    Fetch user data from the Calendly API.
    
    Args:
        api_key: Calendly API key
        
    Returns:
        dict: User data
    """
    try:
        logger.info("Fetching Calendly user data")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CALENDLY_API_BASE_URL}/users/me", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            resource = data.get("resource", {})
            
            logger.info(f"Successfully fetched Calendly user data for: {resource.get('email', 'Unknown')}")
            
            return {
                "uri": resource.get("uri"),
                "name": resource.get("name"),
                "email": resource.get("email"),
                "scheduling_url": resource.get("scheduling_url"),
                "timezone": resource.get("timezone"),
                "created_at": resource.get("created_at"),
                "updated_at": resource.get("updated_at")
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Calendly user data: {e.response.status_code} - {e.response.text}")
        return {"error": f"Calendly API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching Calendly user data: {str(e)}")
        return {"error": f"Error: {str(e)}"}

async def fetch_calendly_events(api_key: str, user_uri: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch scheduled events from Calendly.
    
    Args:
        api_key: Calendly API key
        user_uri: Calendly user URI
        days: Number of days to look back
        
    Returns:
        list: List of event data
    """
    try:
        logger.info(f"Fetching Calendly events for the past {days} days")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Calculate date range
        min_start_time = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
        max_start_time = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        
        params = {
            "user": user_uri,
            "min_start_time": min_start_time,
            "max_start_time": max_start_time,
            "status": "active"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CALENDLY_API_BASE_URL}/scheduled_events", headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "collection" not in data or len(data["collection"]) == 0:
                logger.warning("No events found in Calendly account")
                return []
            
            events = []
            for item in data["collection"]:
                event = {
                    "uri": item.get("uri"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "start_time": item.get("start_time"),
                    "end_time": item.get("end_time"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "event_type": item.get("event_type"),
                    "location": item.get("location", {}).get("type", "Unknown")
                }
                events.append(event)
            
            logger.info(f"Successfully fetched {len(events)} events from Calendly")
            return events
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Calendly events: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching Calendly events: {str(e)}")
        return []

async def get_calendly_data_for_integration(api_key: str) -> Dict[str, Any]:
    """
    Get comprehensive Calendly data.
    
    Args:
        api_key: Calendly API key
        
    Returns:
        dict: Complete Calendly data including user info and events
    """
    try:
        # Fetch user data
        user_data = await fetch_calendly_user_data(api_key)
        if "error" in user_data:
            return {
                "message": user_data["error"],
                "events": [],
                "user": {},
                "metrics": {}
            }
        
        # Fetch events using the user URI
        user_uri = user_data.get("uri")
        if not user_uri:
            return {
                "message": "Could not determine Calendly user URI",
                "events": [],
                "user": user_data,
                "metrics": {}
            }
        
        # Fetch past events (30 days)
        past_events = await fetch_calendly_events(api_key, user_uri, 30)
        
        # Calculate metrics
        total_events = len(past_events)
        
        # Group events by day
        events_by_day = {}
        for event in past_events:
            if "start_time" in event:
                day = event["start_time"].split("T")[0]
                if day not in events_by_day:
                    events_by_day[day] = 0
                events_by_day[day] += 1
        
        # Convert to list for charting
        daily_data = [{"date": day, "count": count} for day, count in events_by_day.items()]
        daily_data.sort(key=lambda x: x["date"])
        
        # Group events by type
        events_by_type = {}
        for event in past_events:
            event_type = event.get("event_type", "Unknown")
            if event_type not in events_by_type:
                events_by_type[event_type] = 0
            events_by_type[event_type] += 1
        
        # Convert to list for charting
        type_data = [{"type": type_name, "count": count} for type_name, count in events_by_type.items()]
        
        return {
            "message": "Real Calendly data from API",
            "events": past_events,
            "user": user_data,
            "metrics": {
                "totalEvents": total_events,
                "dailyData": daily_data,
                "eventsByType": type_data,
                "averageEventsPerDay": total_events / 30 if total_events > 0 else 0
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting Calendly data: {str(e)}")
        return {
            "message": f"Error: {str(e)}",
            "events": [],
            "user": {},
            "metrics": {}
        }
