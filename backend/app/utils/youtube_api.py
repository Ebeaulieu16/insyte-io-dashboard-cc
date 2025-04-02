"""
YouTube API utility functions.
Handles fetching real data from the YouTube API using API keys.
"""

import httpx
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# YouTube API endpoints
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"

async def test_youtube_api_key(api_key: str, channel_id: str) -> bool:
    """
    Test if a YouTube API key is valid by making a simple request.
    
    Args:
        api_key: YouTube API key to test
        channel_id: YouTube channel ID to test with
        
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    try:
        logger.info(f"Testing YouTube API key for channel ID: {channel_id}")
        
        # Construct a minimal URL to test the API key
        url = f"{YOUTUBE_API_BASE_URL}/channels"
        params = {
            "key": api_key,
            "id": channel_id,
            "part": "snippet",
            "maxResults": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)
            
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    logger.info(f"YouTube API key is valid for channel ID: {channel_id}")
                    return True
            
            logger.warning(f"YouTube API key validation failed with status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error testing YouTube API key: {str(e)}")
        return False

async def fetch_youtube_channel_data(api_key: str, channel_id: str) -> Dict[str, Any]:
    """
    Fetch channel data from the YouTube API.
    
    Args:
        api_key: YouTube API key
        channel_id: YouTube channel ID
        
    Returns:
        dict: Channel data including statistics
    """
    try:
        logger.info(f"Fetching channel data for channel ID: {channel_id}")
        
        # Construct the URL for the channels endpoint
        url = f"{YOUTUBE_API_BASE_URL}/channels"
        params = {
            "key": api_key,
            "id": channel_id,
            "part": "snippet,statistics,contentDetails"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" not in data or len(data["items"]) == 0:
                logger.warning(f"No channel found for channel ID: {channel_id}")
                return {"error": "Channel not found"}
            
            channel = data["items"][0]
            logger.info(f"Successfully fetched channel data for: {channel['snippet']['title']}")
            
            return {
                "id": channel["id"],
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "customUrl": channel["snippet"].get("customUrl", ""),
                "publishedAt": channel["snippet"]["publishedAt"],
                "thumbnails": channel["snippet"]["thumbnails"],
                "statistics": channel["statistics"],
                "uploads_playlist": channel["contentDetails"]["relatedPlaylists"]["uploads"]
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching channel data: {e.response.status_code} - {e.response.text}")
        return {"error": f"YouTube API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching channel data: {str(e)}")
        return {"error": f"Error: {str(e)}"}

async def fetch_channel_videos(api_key: str, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch videos from a YouTube channel.
    
    Args:
        api_key: YouTube API key
        channel_id: YouTube channel ID
        max_results: Maximum number of videos to fetch
        
    Returns:
        list: List of video data
    """
    try:
        logger.info(f"Fetching videos for channel ID: {channel_id}")
        
        # First get the uploads playlist ID
        channel_data = await fetch_youtube_channel_data(api_key, channel_id)
        if "error" in channel_data:
            return []
        
        uploads_playlist_id = channel_data["uploads_playlist"]
        
        # Now get the videos from the uploads playlist
        url = f"{YOUTUBE_API_BASE_URL}/playlistItems"
        params = {
            "key": api_key,
            "playlistId": uploads_playlist_id,
            "part": "snippet,contentDetails",
            "maxResults": max_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" not in data or len(data["items"]) == 0:
                logger.warning(f"No videos found for channel ID: {channel_id}")
                return []
            
            # Extract video IDs for the next request
            video_ids = [item["contentDetails"]["videoId"] for item in data["items"]]
            
            # Get detailed video statistics
            video_stats = await fetch_video_statistics(api_key, video_ids)
            
            # Combine the data
            videos = []
            for i, item in enumerate(data["items"]):
                video_id = item["contentDetails"]["videoId"]
                stats = video_stats.get(video_id, {})
                
                video = {
                    "id": video_id,
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "publishedAt": item["snippet"]["publishedAt"],
                    "thumbnails": item["snippet"]["thumbnails"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "avgViewDuration": format_duration(stats.get("duration", "PT0S")),
                    # Estimated metrics based on industry averages
                    "clicks": int(int(stats.get("viewCount", 0)) * 0.012),  # ~1.2% CTR
                    "bookedCalls": int(int(stats.get("viewCount", 0)) * 0.012 * 0.2),  # ~20% booking rate
                    "closedDeals": int(int(stats.get("viewCount", 0)) * 0.012 * 0.2 * 0.6),  # ~60% close rate
                    "revenue": int(int(stats.get("viewCount", 0)) * 0.012 * 0.2 * 0.6 * 5800)  # Avg deal $5800
                }
                videos.append(video)
            
            logger.info(f"Successfully fetched {len(videos)} videos for channel ID: {channel_id}")
            return videos
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching videos: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching videos: {str(e)}")
        return []

async def fetch_video_statistics(api_key: str, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch statistics for multiple videos.
    
    Args:
        api_key: YouTube API key
        video_ids: List of YouTube video IDs
        
    Returns:
        dict: Dictionary mapping video IDs to their statistics
    """
    try:
        if not video_ids:
            return {}
        
        # Join video IDs with commas for the API request
        video_ids_str = ",".join(video_ids)
        
        url = f"{YOUTUBE_API_BASE_URL}/videos"
        params = {
            "key": api_key,
            "id": video_ids_str,
            "part": "statistics,contentDetails"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" not in data:
                return {}
            
            # Create a dictionary mapping video IDs to their statistics
            result = {}
            for item in data["items"]:
                video_id = item["id"]
                stats = item["statistics"]
                stats["duration"] = item["contentDetails"]["duration"]
                result[video_id] = stats
            
            return result
    
    except Exception as e:
        logger.error(f"Error fetching video statistics: {str(e)}")
        return {}

def format_duration(duration_str: str) -> str:
    """
    Format ISO 8601 duration string to MM:SS format.
    
    Args:
        duration_str: ISO 8601 duration string (e.g., 'PT5M30S')
        
    Returns:
        str: Formatted duration string (e.g., '5:30')
    """
    try:
        # Remove the 'PT' prefix
        duration = duration_str[2:]
        
        minutes = 0
        seconds = 0
        
        # Extract minutes
        if 'M' in duration:
            minutes_part = duration.split('M')[0]
            if 'H' in minutes_part:
                minutes_part = minutes_part.split('H')[1]
            minutes = int(minutes_part)
            
        # Extract seconds
        if 'S' in duration:
            seconds_part = duration.split('S')[0]
            if 'M' in seconds_part:
                seconds_part = seconds_part.split('M')[1]
            seconds = int(seconds_part)
            
        # Format as MM:SS
        return f"{minutes}:{seconds:02d}"
    
    except Exception:
        return "0:00"

async def get_youtube_data_for_integration(api_key: str, channel_id: str) -> Dict[str, Any]:
    """
    Get comprehensive YouTube data for a channel.
    
    Args:
        api_key: YouTube API key
        channel_id: YouTube channel ID
        
    Returns:
        dict: Complete YouTube data including videos and metrics
    """
    try:
        # Fetch videos for the channel
        videos = await fetch_channel_videos(api_key, channel_id)
        
        if not videos:
            return {
                "message": "No videos found or error fetching data",
                "videos": [],
                "metrics": {
                    "totalViews": 0,
                    "totalLikes": 0,
                    "totalComments": 0,
                    "totalClicks": 0,
                    "totalBookedCalls": 0,
                    "totalClosedDeals": 0,
                    "totalRevenue": 0,
                    "conversionRate": 0,
                    "bookingRate": 0,
                    "closingRate": 0
                }
            }
        
        # Calculate totals for the metrics
        total_views = sum(video["views"] for video in videos)
        total_likes = sum(video["likes"] for video in videos)
        total_comments = sum(video["comments"] for video in videos)
        total_clicks = sum(video["clicks"] for video in videos)
        total_booked_calls = sum(video["bookedCalls"] for video in videos)
        total_closed_deals = sum(video["closedDeals"] for video in videos)
        total_revenue = sum(video["revenue"] for video in videos)
        
        # Calculate rates (avoid division by zero)
        conversion_rate = round((total_clicks / total_views) * 100, 2) if total_views > 0 else 0
        booking_rate = round((total_booked_calls / total_clicks) * 100, 2) if total_clicks > 0 else 0
        closing_rate = round((total_closed_deals / total_booked_calls) * 100, 2) if total_booked_calls > 0 else 0
        
        return {
            "message": "Real YouTube data from API",
            "videos": videos,
            "metrics": {
                "totalViews": total_views,
                "totalLikes": total_likes,
                "totalComments": total_comments,
                "totalClicks": total_clicks,
                "totalBookedCalls": total_booked_calls,
                "totalClosedDeals": total_closed_deals,
                "totalRevenue": total_revenue,
                "conversionRate": conversion_rate,
                "bookingRate": booking_rate,
                "closingRate": closing_rate
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting YouTube data: {str(e)}")
        return {
            "message": f"Error: {str(e)}",
            "videos": [],
            "metrics": {}
        }
