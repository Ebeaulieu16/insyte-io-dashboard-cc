"""
Standalone test script for the link creation API endpoint.
This script tests the link creation logic without depending on FastAPI or Pydantic.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import re
import json
from dotenv import load_dotenv
from datetime import datetime

# Import models
from app.models.video_link import VideoLink

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

def validate_slug(slug):
    """Validate slug format: lowercase, alphanumeric with dashes."""
    if not slug or not isinstance(slug, str):
        return False, "Slug must be a non-empty string"
    
    if len(slug) < 3 or len(slug) > 100:
        return False, f"Slug must be between 3 and 100 characters (got {len(slug)})"
    
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False, "Slug must be lowercase, alphanumeric with dashes only"
    
    return True, "Slug is valid"

def clean_test_links():
    """Delete test links for this test script."""
    test_slugs = ["test-api-link", "invalid-link", "test-duplicate"]
    for slug in test_slugs:
        link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
        if link:
            db.delete(link)
    db.commit()
    print("Cleaned up test links")

def create_link(title, slug, destination_url):
    """Create a new link with validation."""
    print(f"\nAttempting to create link: '{slug}'")
    
    # Validate inputs
    if not title or not isinstance(title, str):
        return False, "Title must be a non-empty string"
    
    valid_slug, slug_message = validate_slug(slug)
    if not valid_slug:
        return False, slug_message
    
    if not destination_url or not isinstance(destination_url, str):
        return False, "Destination URL must be a non-empty string"
    
    # Check if URL looks valid
    if not (destination_url.startswith("http://") or destination_url.startswith("https://")):
        return False, "Destination URL must start with http:// or https://"
    
    # Check if slug already exists
    existing_link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
    if existing_link:
        return False, f"Slug '{slug}' already exists"
    
    # Create new link
    try:
        new_link = VideoLink(
            slug=slug,
            title=title,
            destination_url=destination_url
        )
        
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        # Construct response
        base_url = "https://yourdomain.com"
        response = {
            "slug": new_link.slug,
            "link": f"{base_url}/go/{new_link.slug}"
        }
        
        return True, response
    except Exception as e:
        db.rollback()
        return False, f"Error creating link: {str(e)}"

def test_successful_creation():
    """Test creating a valid link."""
    print("\n1. Testing successful link creation")
    print("-" * 60)
    
    success, result = create_link(
        title="Test API Link",
        slug="test-api-link",
        destination_url="https://example.com/api-test"
    )
    
    if success:
        print(f"✓ Link created successfully")
        print(f"✓ Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"✗ Failed: {result}")
        return False

def test_invalid_slug():
    """Test invalid slug format."""
    print("\n2. Testing invalid slug format")
    print("-" * 60)
    
    success, result = create_link(
        title="Invalid Link",
        slug="INVALID_SLUG!",
        destination_url="https://example.com/invalid"
    )
    
    if not success and "lowercase" in result:
        print(f"✓ Validation caught invalid slug as expected: {result}")
        return True
    else:
        print(f"✗ Unexpected result: {result}")
        return False

def test_duplicate_slug():
    """Test duplicate slug detection."""
    print("\n3. Testing duplicate slug")
    print("-" * 60)
    
    # First, create a link
    success, result = create_link(
        title="Test Duplicate",
        slug="test-duplicate",
        destination_url="https://example.com/duplicate"
    )
    
    if not success:
        print(f"✗ Failed to create first link: {result}")
        return False
    
    print(f"✓ First link created successfully")
    
    # Now try to create another with the same slug
    success, result = create_link(
        title="Test Duplicate 2",
        slug="test-duplicate",
        destination_url="https://example.com/duplicate2"
    )
    
    if not success and "already exists" in result:
        print(f"✓ Duplicate slug detected as expected: {result}")
        return True
    else:
        print(f"✗ Unexpected result: {result}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LINK CREATION API TEST (Standalone)")
    print("=" * 60)
    
    # Clean up before testing
    clean_test_links()
    
    # Run tests
    tests = [
        test_successful_creation,
        test_invalid_slug,
        test_duplicate_slug
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Clean up after testing
    clean_test_links()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    all_passed = all(results)
    for i, (test, result) in enumerate(zip(tests, results), 1):
        print(f"Test {i}: {test.__name__} - {'✓ Passed' if result else '✗ Failed'}")
    
    print("\nOverall result:", "✓ All tests passed!" if all_passed else "✗ Some tests failed.") 