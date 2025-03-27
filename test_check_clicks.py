"""
Test script to check if clicks are being logged properly.
"""

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import models
from app.models.click import Click
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

def check_clicks(slug="test-video"):
    """Check clicks for a specific slug."""
    # Get the most recent clicks for the slug
    clicks = db.query(Click).filter(
        Click.slug == slug
    ).order_by(desc(Click.timestamp)).limit(5).all()
    
    if not clicks:
        print(f"No clicks found for slug: {slug}")
        return
    
    print(f"Recent clicks for slug: {slug}")
    print("-" * 50)
    for i, click in enumerate(clicks, 1):
        print(f"Click {i}:")
        print(f"  Timestamp: {click.timestamp}")
        print(f"  IP Address: {click.ip_address}")
        print(f"  Referrer: {click.referrer or 'None'}")
        print("-" * 50)

if __name__ == "__main__":
    check_clicks()
    print("Note: Visit http://localhost:8000/go/test-video to generate clicks") 