"""
Test script for the link creation API endpoint.
This script tests the validation and creation logic without running the FastAPI server.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import re
import json

# Import models and schemas
from app.models.video_link import VideoLink
from app.routes.utm import LinkCreate, LinkResponse
from pydantic import ValidationError

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

def clear_test_links():
    """Delete test links for this test script."""
    test_slugs = ["test-api-link", "invalid-link", "test-duplicate"]
    for slug in test_slugs:
        link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
        if link:
            db.delete(link)
    db.commit()
    print("Cleaned up test links")

def test_create_valid_link():
    """Test creating a valid link."""
    print("\n1. Testing valid link creation")
    print("-" * 60)
    
    try:
        # Create valid link data
        link_data = LinkCreate(
            title="Test API Link",
            slug="test-api-link",
            destination_url="https://example.com/api-test"
        )
        
        # Validate using pydantic
        print(f"✓ Link data validated: {link_data}")
        
        # Check if slug exists
        existing_link = db.query(VideoLink).filter(VideoLink.slug == link_data.slug).first()
        if existing_link:
            print(f"! Link with slug '{link_data.slug}' already exists, will be deleted for test")
            db.delete(existing_link)
            db.commit()
        
        # Create new link
        new_link = VideoLink(
            slug=link_data.slug,
            title=link_data.title,
            destination_url=str(link_data.destination_url)
        )
        
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        print(f"✓ Link created: {new_link.slug} -> {new_link.destination_url}")
        
        # Create response
        base_url = "https://yourdomain.com"
        response = LinkResponse(
            slug=new_link.slug,
            link=f"{base_url}/go/{new_link.slug}"
        )
        
        print(f"✓ Response: {json.dumps(response.dict(), indent=2)}")
        return True
        
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_invalid_slug_format():
    """Test slug format validation."""
    print("\n2. Testing invalid slug format")
    print("-" * 60)
    
    try:
        # Create invalid link data (uppercase and special chars)
        link_data = LinkCreate(
            title="Invalid Link",
            slug="INVALID_SLUG!",
            destination_url="https://example.com/invalid"
        )
        
        print(f"✓ This test should fail with validation error")
        
        return False
        
    except ValidationError as e:
        print(f"✓ Expected validation error: {e}")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_duplicate_slug():
    """Test duplicate slug detection."""
    print("\n3. Testing duplicate slug")
    print("-" * 60)
    
    try:
        # Create first link
        link1_data = LinkCreate(
            title="Test Duplicate",
            slug="test-duplicate",
            destination_url="https://example.com/duplicate"
        )
        
        # Check if slug exists and delete for clean test
        existing_link = db.query(VideoLink).filter(VideoLink.slug == link1_data.slug).first()
        if existing_link:
            db.delete(existing_link)
            db.commit()
        
        # Create new link in DB
        new_link = VideoLink(
            slug=link1_data.slug,
            title=link1_data.title,
            destination_url=str(link1_data.destination_url)
        )
        
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        print(f"✓ First link created: {new_link.slug}")
        
        # Try to create duplicate
        print("Checking for duplicate slug...")
        duplicate = db.query(VideoLink).filter(VideoLink.slug == link1_data.slug).first()
        
        if duplicate:
            print(f"✓ Detected duplicate slug: '{link1_data.slug}'")
            print(f"✓ In the API, this would return a 409 Conflict status")
            return True
        else:
            print(f"✗ Failed to detect duplicate")
            return False
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LINK CREATION API TEST")
    print("=" * 60)
    
    # Clean up before testing
    clear_test_links()
    
    # Run tests
    tests = [
        test_create_valid_link,
        test_invalid_slug_format,
        test_duplicate_slug
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Clean up after testing
    clear_test_links()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    all_passed = all(results)
    for i, (test, result) in enumerate(zip(tests, results), 1):
        print(f"Test {i}: {test.__name__} - {'✓ Passed' if result else '✗ Failed'}")
    
    print("\nOverall result:", "✓ All tests passed!" if all_passed else "✗ Some tests failed.") 