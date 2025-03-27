"""
Manual test script for the redirect flow.
This script tests the redirect functionality without running the FastAPI server.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from dotenv import load_dotenv

# Import models
from app.models.video_link import VideoLink
from app.models.click import Click

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://emilebeaulieu@localhost:5432/insyte_dashboard")

# Use the psycopg driver with SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def create_test_link():
    """Create a test video link if it doesn't exist."""
    existing_link = db.query(VideoLink).filter(VideoLink.slug == "test-video").first()
    if existing_link:
        print(f"Using existing link: {existing_link.slug} -> {existing_link.destination_url}")
        return existing_link
    
    new_link = VideoLink(
        slug="test-video",
        title="Test Video",
        destination_url="https://example.com/landing-page"
    )
    
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    
    print(f"Created test link: {new_link.slug} -> {new_link.destination_url}")
    return new_link

def simulate_redirect(slug, ip_address="127.0.0.1", referrer=None):
    """Simulate the redirect process."""
    print(f"\nSimulating redirect for slug: {slug}")
    
    # Find the video link
    link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
    if not link:
        print(f"ERROR: Link with slug '{slug}' not found")
        return None
    
    # Log the click
    click = Click(
        slug=slug,
        ip_address=ip_address,
        referrer=referrer
    )
    
    db.add(click)
    db.commit()
    
    print(f"✓ Logged click from IP: {ip_address}")
    
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
    
    print(f"✓ Would redirect to: {new_url}")
    return new_url

def check_recent_clicks(slug="test-video", limit=5):
    """Check recent clicks for the given slug."""
    clicks = db.query(Click).filter(Click.slug == slug).order_by(Click.timestamp.desc()).limit(limit).all()
    
    print(f"\nRecent clicks for slug '{slug}':")
    print("-" * 60)
    
    if not clicks:
        print("No clicks found.")
        return
    
    for i, click in enumerate(clicks, 1):
        print(f"Click #{i}")
        print(f"  Timestamp: {click.timestamp}")
        print(f"  IP: {click.ip_address}")
        print(f"  Referrer: {click.referrer or 'None'}")
        print("-" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("UTM REDIRECT FLOW TEST")
    print("=" * 60)
    
    # Create or get test link
    link = create_test_link()
    
    # Simulate a redirect
    simulate_redirect(link.slug, ip_address="192.168.1.1", referrer="https://youtube.com/watch?v=test123")
    
    # Check recent clicks
    check_recent_clicks(link.slug)
    
    print("\nTest completed successfully!")
    print(f"In the real app, users would be redirected when visiting: /go/{link.slug}") 