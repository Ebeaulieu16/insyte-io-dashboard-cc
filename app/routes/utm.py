"""
UTM routes module.
Contains endpoints for UTM link generation and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, validator, Field
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import datetime

from app.database import get_db
from app.models.video_link import VideoLink
from app.models.click import Click

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
            destination_url=str(link_data.destination_url)
        )
        
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        # Construct the full URL for the link
        base_url = "https://yourdomain.com"  # This should come from config in production
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
    
    # Add UTM parameters
    query_params["utm_source"] = ["youtube"]
    query_params["utm_medium"] = ["video"]
    query_params["utm_content"] = [slug]
    
    # Rebuild the URL with new query parameters
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, 
         parsed_url.params, new_query, parsed_url.fragment)
    )
    
    # Return redirect response
    return RedirectResponse(url=new_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
