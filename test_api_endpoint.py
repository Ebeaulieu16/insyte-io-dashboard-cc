"""
Test script to verify the FastAPI endpoint is working correctly.
This script directly tests the route handler without starting the FastAPI server.
"""

import pytest
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

# Import your FastAPI app and router
from app.main import app
from app.models.video_link import VideoLink
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

# Create a test client
client = TestClient(app)

def clean_test_links():
    """Delete test links for this test script."""
    test_slugs = ["test-api-endpoint", "test-invalid-api", "test-duplicate-api"]
    for slug in test_slugs:
        link = db.query(VideoLink).filter(VideoLink.slug == slug).first()
        if link:
            db.delete(link)
    db.commit()
    print("Cleaned up test links")

def test_create_link_endpoint():
    """Test the link creation endpoint directly."""
    print("\n1. Testing valid link creation via API")
    print("-" * 60)
    
    # Payload for link creation
    payload = {
        "title": "Test API Endpoint",
        "slug": "test-api-endpoint",
        "destination_url": "https://example.com/test-endpoint"
    }
    
    # Make the POST request
    response = client.post("/api/links/create", json=payload)
    
    # Check status code and response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    assert "slug" in response.json(), "Response should contain slug"
    assert "link" in response.json(), "Response should contain link"
    assert response.json()["slug"] == payload["slug"], "Slug in response should match request"
    
    return response.status_code == 201

def test_invalid_slug_endpoint():
    """Test the API with an invalid slug."""
    print("\n2. Testing invalid slug format via API")
    print("-" * 60)
    
    # Payload with invalid slug
    payload = {
        "title": "Invalid API Test",
        "slug": "INVALID_SLUG!",
        "destination_url": "https://example.com/invalid-test"
    }
    
    # Make the POST request
    response = client.post("/api/links/create", json=payload)
    
    # Check status code
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json() if response.status_code != 422 else 'Validation Error'}")
    
    # Should return 422 Unprocessable Entity for validation errors
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}"
    
    return response.status_code == 422

def test_duplicate_slug_endpoint():
    """Test the API with a duplicate slug."""
    print("\n3. Testing duplicate slug via API")
    print("-" * 60)
    
    # First create a link
    payload = {
        "title": "Test Duplicate API",
        "slug": "test-duplicate-api",
        "destination_url": "https://example.com/duplicate-api-test"
    }
    
    # Make the first POST request
    response1 = client.post("/api/links/create", json=payload)
    print(f"First request status code: {response1.status_code}")
    
    if response1.status_code != 201:
        print(f"First request failed: {response1.json()}")
        return False
    
    print(f"First link created successfully")
    
    # Now try to create another with the same slug
    response2 = client.post("/api/links/create", json=payload)
    print(f"Second request status code: {response2.status_code}")
    print(f"Second request response: {response2.json() if response2.status_code != 422 else 'Error'}")
    
    # Should return 409 Conflict for duplicate slug
    assert response2.status_code == 409, f"Expected status code 409, got {response2.status_code}"
    
    return response2.status_code == 409

if __name__ == "__main__":
    print("=" * 60)
    print("FASTAPI ENDPOINT TEST")
    print("=" * 60)
    
    # Clean up before testing
    clean_test_links()
    
    try:
        # Run tests
        tests = [
            test_create_link_endpoint,
            test_invalid_slug_endpoint,
            test_duplicate_slug_endpoint
        ]
        
        results = []
        for test in tests:
            try:
                results.append(test())
            except Exception as e:
                print(f"Test failed with error: {str(e)}")
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