"""
UTM routes module.
Contains endpoints for UTM link generation and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct, case, and_, extract
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, validator, Field
import re
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
# import datetime
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models.video_link import VideoLink
from app.models.click import Click
from app.models.call import Call, CallStatus
from app.models.payment import Payment
from app.models.video_analytics import VideoAnalytics

router = APIRouter(
    tags=["utm"],
    responses={404: {"description": "Not found"}},
)

# Pydantic model for link creation request
class LinkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the link")
    slug: str = Field(..., min_length=3, max_length=100, description="Unique slug for the link")
    destination_url: HttpUrl = Field(..., description="Destination URL for redirection")
    
    @validator('slug')
    def validate_slug_format(cls, v):
        """Validate slug format: lowercase, alphanumeric with dashes."""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase, alphanumeric with dashes only')
        return v

# Pydantic model for link response
class LinkResponse(BaseModel):
    slug: str
    link: str

# Pydantic model for link statistics
class LinkStats(BaseModel):
    id: int
    slug: str
    title: str
    destination_url: str
    clicks: int
    booked_calls: int
    deals_closed: int
    revenue: float
    created_at: datetime

@router.post("/api/links/create", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    link_data: LinkCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tracked UTM link.
    
    Args:
        link_data: Link creation data with title, slug and destination URL
        
    Returns:
        dict: Created link information.
    
    Raises:
        HTTPException: 400 Bad Request if slug format is invalid
        HTTPException: 409 Conflict if slug already exists
        HTTPException: 500 Internal Server Error for database issues
    """
    try:
        # Check if slug already exists
        existing_link = db.query(VideoLink).filter(VideoLink.slug == link_data.slug).first()
        if existing_link:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slug '{link_data.slug}' already exists"
            )
        
        # Create new video link
        new_link = VideoLink(
            slug=link_data.slug,
            title=link_data.title,
            destination_url=str(link_data.destination_url),
            utm_source=link_data.utm_source,
            utm_medium=link_data.utm_medium,
            utm_campaign=link_data.utm_campaign
        )
        
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        # Construct the full URL for the link
        base_url = os.getenv("BASE_URL", "https://insyte-io-dashboard-cc.onrender.com")
        link_url = f"{base_url}/go/{new_link.slug}"
        
        return {
            "slug": new_link.slug,
            "link": link_url
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create link: {str(e)}"
        )

@router.get("/go/{slug}")
async def redirect_link(
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Track click and redirect to destination with UTM parameters.
    
    Args:
        slug: The link slug to redirect
        
    Returns:
        RedirectResponse: Redirects to destination URL with UTM parameters.
    """
    # Find the video link by slug
    link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link with slug '{slug}' not found"
        )
    
    # Log the click
    click = Click(
        slug=slug,
        ip_address=request.client.host,
        referrer=request.headers.get("referer")  # Note: HTTP header is "referer", not "referrer"
    )
    
    db.add(click)
    db.commit()
    
    # Parse the destination URL to add UTM parameters
    parsed_url = urlparse(link.destination_url)
    query_params = parse_qs(parsed_url.query)
    
    # Get UTM parameters from the link record
    query_params["utm_source"] = [link.utm_source or "youtube"]
    query_params["utm_medium"] = [link.utm_medium or "video"]
    query_params["utm_content"] = [slug]
    
    # Add campaign if available
    if link.utm_campaign:
        query_params["utm_campaign"] = [link.utm_campaign]
    
    # Rebuild the URL with new query parameters
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, 
         parsed_url.params, new_query, parsed_url.fragment)
    )
    
    # Return redirect response
    return RedirectResponse(url=new_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/api/links", status_code=status.HTTP_200_OK)
async def get_all_links(
    start_date: Optional[date] = Query(None, description="Start date for filtering stats"),
    end_date: Optional[date] = Query(None, description="End date for filtering stats"),
    db: Session = Depends(get_db)
):
    """
    Get all UTM links with their performance statistics.
    
    Args:
        start_date: Optional start date for filtering stats
        end_date: Optional end date for filtering stats
        
    Returns:
        dict: List of UTM links with their performance statistics.
    """
    try:
        # Get all links
        links_query = db.query(VideoLink)
        
        # Order by most recently created
        links = links_query.order_by(desc(VideoLink.created_at)).all()
        
        result = []
        for link in links:
            # Build click stats query
            clicks_query = db.query(func.count(Click.id)).filter(Click.slug == link.slug)
            
            # Build calls query
            calls_query = db.query(func.count(Call.id)).filter(
                Call.slug == link.slug,
                Call.status == CallStatus.BOOKED
            )
            
            # Build deals query
            deals_query = db.query(func.count(Payment.id)).filter(
                Payment.slug == link.slug
            )
            
            # Build revenue query
            revenue_query = db.query(func.sum(Payment.amount)).filter(
                Payment.slug == link.slug
            )
            
            # Apply date filters if provided
            if start_date:
                clicks_query = clicks_query.filter(Click.timestamp >= start_date)
                calls_query = calls_query.filter(Call.timestamp >= start_date)
                deals_query = deals_query.filter(Payment.timestamp >= start_date)
                revenue_query = revenue_query.filter(Payment.timestamp >= start_date)
            
            if end_date:
                # Add one day to include the end date fully (up to midnight)
                end_date_inclusive = end_date + timedelta(days=1)
                clicks_query = clicks_query.filter(Click.timestamp < end_date_inclusive)
                calls_query = calls_query.filter(Call.timestamp < end_date_inclusive)
                deals_query = deals_query.filter(Payment.timestamp < end_date_inclusive)
                revenue_query = revenue_query.filter(Payment.timestamp < end_date_inclusive)
            
            # Execute queries
            clicks_count = clicks_query.scalar() or 0
            calls_count = calls_query.scalar() or 0
            deals_count = deals_query.scalar() or 0
            revenue_total = revenue_query.scalar() or 0.0
            
            # Create link stats object
            link_stats = {
                "id": link.id,
                "slug": link.slug,
                "title": link.title,
                "destination_url": link.destination_url,
                "clicks": clicks_count,
                "booked_calls": calls_count,
                "deals_closed": deals_count,
                "revenue": float(revenue_total),
                "created_at": link.created_at
            }
            
            result.append(link_stats)
        
        return {
            "links": result,
            "count": len(result),
            "date_range": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch links: {str(e)}"
        )

@router.get("/api/links/deep-view/{slug}", response_model=Dict[str, Any])
async def get_deep_view(
    slug: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific UTM link identified by its slug.
    
    Args:
        slug: The short URL slug.
        start_date: Optional start date for filtering data (format: YYYY-MM-DD).
        end_date: Optional end date for filtering data (format: YYYY-MM-DD).
        db: Database session.
        
    Returns:
        Detailed analytics for the UTM link including views, clicks, calls, deals, video data, etc.
    """
    # Default to last 30 days if no dates provided
    end_date_dt = datetime.now()
    if end_date:
        try:
            end_date_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)")
    
    start_date_dt = end_date_dt - timedelta(days=30)
    if start_date:
        try:
            start_date_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)")
    
    try:
        # Get the link
        link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Get clicks data
        clicks_query = db.query(Click).filter(
            Click.slug == slug,
            Click.timestamp >= start_date_dt,
            Click.timestamp <= end_date_dt
        )
        
        total_clicks = clicks_query.count()
        
        # Group clicks by day
        clicks_by_day = {}
        for click in clicks_query.all():
            day_str = click.timestamp.strftime("%Y-%m-%d")
            if day_str not in clicks_by_day:
                clicks_by_day[day_str] = 0
            clicks_by_day[day_str] += 1
        
        # Format for chart display
        clicks_data = [
            {"date": day, "count": count}
            for day, count in sorted(clicks_by_day.items())
        ]
        
        # Get calls data
        calls_query = db.query(Call).filter(
            Call.slug == slug,
            Call.timestamp >= start_date_dt,
            Call.timestamp <= end_date_dt
        )
        
        calls_list = []
        calls_booked = 0
        calls_confirmed = 0
        calls_completed = 0
        calls_cancelled = 0
        calls_no_show = 0
        calls_rescheduled = 0
        calls_pending = 0
        
        for call in calls_query.all():
            calls_list.append({
                "date": call.timestamp.isoformat(),
                "status": call.status,
                "email": call.email,
                "id": call.id
            })
            
            # Count calls by status (using the updated CallStatus)
            if call.status == CallStatus.BOOKED:
                calls_booked += 1
            elif call.status == CallStatus.CONFIRMED:
                calls_confirmed += 1
            elif call.status == CallStatus.COMPLETED:
                calls_completed += 1
            elif call.status == CallStatus.CANCELLED:
                calls_cancelled += 1
            elif call.status == CallStatus.NO_SHOW:
                calls_no_show += 1
            elif call.status == CallStatus.RESCHEDULED:
                calls_rescheduled += 1
            elif call.status == CallStatus.PENDING:
                calls_pending += 1
        
        # Get deals and revenue data
        deals_query = db.query(Payment).filter(
            Payment.slug == slug,
            Payment.timestamp >= start_date_dt,
            Payment.timestamp <= end_date_dt
        )
        
        total_revenue = 0
        closed_deals = 0
        
        for deal in deals_query.all():
            total_revenue += deal.amount
            closed_deals += 1
        
        # Check if there's video data and get view counts
        video_data = None
        total_views = 0
        
        video_analytics = db.query(VideoAnalytics).filter(
            VideoAnalytics.slug == slug,
            VideoAnalytics.last_updated >= start_date_dt,
            VideoAnalytics.last_updated < end_date_dt
        ).first()
        
        if video_analytics:
            # Get view count from video analytics
            total_views = video_analytics.views
            
            # Calculate leads from this video
            video_leads = db.query(func.count(Call.id)).filter(
                Call.slug == slug,
                Call.timestamp >= start_date_dt,
                Call.timestamp < end_date_dt
            ).scalar() or 0
            
            # Calculate revenue from this video
            video_revenue = db.query(func.sum(Payment.amount)).filter(
                Payment.slug == slug,
                Payment.timestamp >= start_date_dt,
                Payment.timestamp < end_date_dt
            ).scalar() or 0
            
            video_data = {
                "video_id": video_analytics.video_id,
                "title": f"YouTube Video: {video_analytics.video_id}",
                "description": "Learn the proven strategies to scale your agency to 7-figures and beyond. In this video, we cover client acquisition, team building, and systems that will help you grow.",
                "thumbnail_url": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg",
                "views": video_analytics.views,
                "watch_time_seconds": int(video_analytics.avg_view_duration * video_analytics.views),
                "likes": video_analytics.likes,
                "comments": video_analytics.comments,
                "duration_seconds": int(video_analytics.avg_view_duration),
                "published_at": video_analytics.last_updated.isoformat(),
                "engagement_rate": video_analytics.engagement_rate,
                "leads_generated": video_leads,
                "revenue": float(video_revenue)
            }
        
        # If there's no video data, default views to 2-3x clicks as an estimate
        if total_views == 0:
            total_views = total_clicks * 2  # Default assumption: about 50% of viewers click
        
        # Compile the response with updated structure for funnel
        return {
            "title": link.title,
            "slug": link.slug,
            "short_url": f"yourdomain.com/go/{link.slug}",
            "destination": link.destination_url,
            "created_at": link.created_at.isoformat(),
            "views": total_views,
            "clicks": total_clicks,
            "clicks_data": clicks_data,
            "calls": {
                "booked": calls_booked,
                "confirmed": calls_confirmed,
                "completed": calls_completed,
                "cancelled": calls_cancelled,
                "pending": calls_pending,
                "no_show": calls_no_show,
                "rescheduled": calls_rescheduled,
                "list": calls_list
            },
            "deals": {
                "closed": closed_deals,
                "revenue": float(total_revenue)
            },
            "video_data": video_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in get_deep_view: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
