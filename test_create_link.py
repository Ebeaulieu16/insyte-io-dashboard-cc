"""
Test script to create a sample video link in the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import models
from app.models.video_link import VideoLink
from app.database import Base

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
    """Create a test video link."""
    # Check if test link already exists
    existing_link = db.query(VideoLink).filter(VideoLink.slug == "test-video").first()
    if existing_link:
        print(f"Test link already exists: {existing_link.destination_url}")
        return existing_link
    
    # Create new test link
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

if __name__ == "__main__":
    link = create_test_link()
    print(f"To test redirect, go to: http://localhost:8000/go/{link.slug}") 