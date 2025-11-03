"""Test feed endpoints."""

from fastapi.testclient import TestClient


def test_create_feed(client: TestClient, auth_headers):
    """Test creating a feed."""
    response = client.post(
        "/api/v1/feeds/",
        json={"url": "https://example.com/feed.xml", "title": "Test Feed"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://example.com/feed.xml"
    assert data["title"] == "Test Feed"


def test_list_feeds(client: TestClient, auth_headers):
    """Test listing feeds."""
    # Create a feed first
    client.post(
        "/api/v1/feeds/",
        json={"url": "https://example.com/feed.xml"},
        headers=auth_headers,
    )

    response = client.get("/api/v1/feeds/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_unauthorized_access(client: TestClient):
    """Test accessing feeds without authentication."""
    response = client.get("/api/v1/feeds/")
    assert response.status_code == 401
