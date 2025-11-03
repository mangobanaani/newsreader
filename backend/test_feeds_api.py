#!/usr/bin/env python3
"""Test feeds API and generate fresh token."""

import sys
import requests
from datetime import datetime, timedelta

sys.path.insert(0, '/Users/pekka/Documents/newsreader/backend')

from jose import jwt
from app.core.config import settings

def generate_token(user_id: int) -> str:
    """Generate a JWT token for testing."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def test_feeds_api():
    """Test the feeds API endpoint."""
    # Generate a fresh token
    token = generate_token(user_id=1)
    print(f"Generated fresh token for user 1")
    print(f"Token (use this in frontend localStorage as 'access_token'):")
    print(f"{token}\n")

    # Test feeds endpoint
    base_url = "http://localhost:8000/api/v1"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{base_url}/feeds/", headers=headers)
        print(f"GET /feeds/ - Status: {response.status_code}")

        if response.status_code == 200:
            feeds = response.json()
            print(f"✓ Found {len(feeds)} feeds:")
            for feed in feeds:
                print(f"  - {feed['title']} ({feed['url']})")
        else:
            print(f"✗ Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend at http://localhost:8000")
        print("  Make sure the backend is running (cd backend && make run-backend)")

if __name__ == "__main__":
    test_feeds_api()
