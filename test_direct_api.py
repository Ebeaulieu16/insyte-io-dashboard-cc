"""
Direct test for the link creation logic without FastAPI dependencies.
This script tests the same functions that would be called by the API endpoint.
"""

import os
import re
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

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

def validate_slug(slug):
    """Validate slug format: lowercase, alphanumeric with dashes."""
    if not slug or not isinstance(slug, str):
        return False, "Slug must be a non-empty string"
    
    if len(slug) < 3 or len(slug) > 100:
        return False, f"Slug must be between 3 and 100 characters (got {len(slug)})"
    
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False, "Slug must be lowercase, alphanumeric with dashes only"
    
    return True, "Slug is valid"

def validate_url(url):
    """Simple validation for URL format."""
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "URL must start with http:// or https://"
    
    return True, "URL is valid"

def clean_test_links():
    """Delete test links for this test script."""
    test_slugs = ["test-direct-api", "invalid-direct-api", "test-duplicate-direct"]
    
    # Create a new session for this function
    db = SessionLocal()
    try:
        for slug in test_slugs:
            link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
            if link:
                db.delete(link)
        db.commit()
        print("Cleaned up test links")
    except Exception as e:
        db.rollback()
        print(f"Error cleaning test links: {str(e)}")
    finally:
        db.close()

def create_link(title, slug, destination_url):
    """Create a new link with validation."""
    db = SessionLocal()
    try:
        # Validate title
        if not title or not isinstance(title, str) or len(title) == 0:
            return 400, {"detail": "Title must be a non-empty string"}
        
        # Validate slug
        valid_slug, slug_message = validate_slug(slug)
        if not valid_slug:
            return 400, {"detail": slug_message}
        
        # Validate URL
        valid_url, url_message = validate_url(destination_url)
        if not valid_url:
            return 400, {"detail": url_message}
        
        # Check if slug already exists
        existing_link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
        if existing_link:
            return 409, {"detail": f"Slug '{slug}' already exists"}
        
        # Create new link
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
        
        return 201, response
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        return 500, {"detail": f"Error creating link: {str(e)}"}
    finally:
        db.close()

def test_create_valid_link():
    """Test creating a valid link directly."""
    print("\n1. Testing valid link creation")
    print("-" * 60)
    
    status_code, response = create_link(
        title="Test Direct API",
        slug="test-direct-api",
        destination_url="https://example.com/direct-api-test"
    )
    
    print(f"Status code: {status_code}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    assert status_code == 201, f"Expected status code 201, got {status_code}"
    assert "slug" in response, "Response should contain slug"
    assert "link" in response, "Response should contain link"
    assert response["slug"] == "test-direct-api", "Slug in response should match request"
    
    return status_code == 201

def test_invalid_slug():
    """Test invalid slug format directly."""
    print("\n2. Testing invalid slug format")
    print("-" * 60)
    
    status_code, response = create_link(
        title="Invalid Direct API",
        slug="INVALID_SLUG!",
        destination_url="https://example.com/invalid-direct"
    )
    
    print(f"Status code: {status_code}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    assert status_code == 400, f"Expected status code 400, got {status_code}"
    assert "detail" in response, "Response should contain error detail"
    assert "lowercase" in response["detail"].lower(), "Error should mention lowercase requirement"
    
    return status_code == 400

def test_duplicate_slug():
    """Test duplicate slug detection directly."""
    print("\n3. Testing duplicate slug")
    print("-" * 60)
    
    # First create a link
    status_code1, response1 = create_link(
        title="Test Duplicate Direct",
        slug="test-duplicate-direct",
        destination_url="https://example.com/duplicate-direct"
    )
    
    print(f"First request status code: {status_code1}")
    print(f"First request response: {json.dumps(response1, indent=2)}")
    
    if status_code1 != 201:
        print(f"First request failed")
        return False
    
    print(f"First link created successfully")
    
    # Now try to create another with the same slug
    status_code2, response2 = create_link(
        title="Test Duplicate Direct 2",
        slug="test-duplicate-direct",
        destination_url="https://example.com/duplicate-direct-2"
    )
    
    print(f"Second request status code: {status_code2}")
    print(f"Second request response: {json.dumps(response2, indent=2)}")
    
    assert status_code2 == 409, f"Expected status code 409, got {status_code2}"
    assert "detail" in response2, "Response should contain error detail"
    assert "already exists" in response2["detail"], "Error should mention duplicate slug"
    
    return status_code2 == 409

if __name__ == "__main__":
    print("=" * 60)
    print("DIRECT API LOGIC TEST")
    print("=" * 60)
    
    # Clean up before testing
    clean_test_links()
    
    try:
        # Run tests
        tests = [
            test_create_valid_link,
            test_invalid_slug,
            test_duplicate_slug
        ]
        
        results = []
        for test in tests:
            try:
                results.append(test())
            except Exception as e:
                print(f"Test failed with error: {str(e)}")
                traceback.print_exc()
                results.append(False)
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        all_passed = all(results)
        for i, (test, result) in enumerate(zip(tests, results), 1):
            print(f"Test {i}: {test.__name__} - {'✓ Passed' if result else '✗ Failed'}")
        
        print("\nOverall result:", "✓ All tests passed!" if all_passed else "✗ Some tests failed.")
        
    finally:
        # Clean up after testing
        clean_test_links() 