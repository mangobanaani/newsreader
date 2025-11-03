"""Test user preferences endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.feed import UserPreference


@pytest.fixture
def test_preference(db: Session, test_user):
    """Create test user preference."""
    preference = UserPreference(
        user_id=test_user.id,
        preferred_topics=["technology", "ai"],
        excluded_topics=["sports"],
        preferred_sources=["example.com"],
        excluded_sources=["spam.com"],
        excluded_words=["clickbait"],
        enable_recommendations=True,
        min_relevance_score=0.5,
    )
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def test_get_preferences_unauthorized(client: TestClient):
    """Test getting preferences without authentication."""
    response = client.get("/api/v1/preferences/")
    assert response.status_code == 401


def test_get_preferences_creates_default(client: TestClient, auth_headers):
    """Test getting preferences when none exist - creates default."""
    response = client.get("/api/v1/preferences/", headers=auth_headers)
    # Should return 200 with default preferences
    assert response.status_code == 200
    data = response.json()
    assert "preferred_topics" in data
    assert "enable_recommendations" in data


def test_get_preferences(client: TestClient, auth_headers, test_preference):
    """Test getting user preferences."""
    response = client.get("/api/v1/preferences/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_topics"] == ["technology", "ai"]
    assert data["excluded_topics"] == ["sports"]
    assert data["enable_recommendations"] is True
    assert data["min_relevance_score"] == 0.5


def test_update_preferences(client: TestClient, auth_headers, test_preference):
    """Test updating user preferences."""
    update_data = {
        "preferred_topics": ["politics", "economics"],
        "min_relevance_score": 0.8,
    }
    response = client.put(
        "/api/v1/preferences/", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_topics"] == ["politics", "economics"]
    assert data["min_relevance_score"] == 0.8
    # Other fields should remain unchanged
    assert data["excluded_topics"] == ["sports"]


def test_update_preferences_partial(client: TestClient, auth_headers, test_preference):
    """Test partial update of preferences."""
    update_data = {"enable_recommendations": False}
    response = client.put(
        "/api/v1/preferences/", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enable_recommendations"] is False
    # Other fields should remain unchanged
    assert data["preferred_topics"] == ["technology", "ai"]


# Note: DELETE and POST endpoints not implemented for preferences
# Only GET and PUT exist
