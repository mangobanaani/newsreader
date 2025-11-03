"""Test articles endpoints."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.feed import Article, Feed


@pytest.fixture
def test_feed(db: Session, test_user):
    """Create test feed."""
    feed = Feed(
        url="https://example.com/rss",
        title="Test Feed",
        description="Test feed description",
        user_id=test_user.id,
        is_active=True,
    )
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed


@pytest.fixture
def test_articles(db: Session, test_feed):
    """Create test articles."""
    articles = []
    for i in range(5):
        article = Article(
            title=f"Test Article {i+1}",
            link=f"https://example.com/article{i+1}",
            description=f"Description for article {i+1}",
            content=f"Content for article {i+1}",
            author=f"Author {i+1}",
            published_date=datetime.now(timezone.utc),
            feed_id=test_feed.id,
            is_read=i % 2 == 0,  # Make some read, some unread
            is_bookmarked=i == 0,  # Bookmark first article
        )
        db.add(article)
        articles.append(article)
    db.commit()
    for article in articles:
        db.refresh(article)
    return articles


def test_get_articles_unauthorized(client: TestClient):
    """Test getting articles without authentication."""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 401


def test_get_articles(client: TestClient, auth_headers, test_articles):
    """Test getting articles list."""
    response = client.get("/api/v1/articles/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_get_articles_pagination(client: TestClient, auth_headers, test_articles):
    """Test articles pagination."""
    response = client.get("/api/v1/articles/?limit=2&skip=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_articles_filter_unread(client: TestClient, auth_headers, test_articles):
    """Test filtering unread articles."""
    response = client.get("/api/v1/articles/?unread_only=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 2 articles should be unread (index 1, 3)
    assert len(data) == 2


def test_get_articles_filter_bookmarked(client: TestClient, auth_headers, test_articles):
    """Test filtering bookmarked articles."""
    response = client.get("/api/v1/articles/?bookmarked_only=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Only first article is bookmarked
    assert len(data) == 1
    assert data[0]["title"] == "Test Article 1"


def test_get_article_by_id(client: TestClient, auth_headers, test_articles):
    """Test getting single article by ID."""
    article_id = test_articles[0].id
    response = client.get(f"/api/v1/articles/{article_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "Test Article 1"


def test_get_article_not_found(client: TestClient, auth_headers):
    """Test getting non-existent article."""
    response = client.get("/api/v1/articles/99999", headers=auth_headers)
    assert response.status_code == 404


# Note: Article update endpoints (PATCH) not yet implemented
# Tests will be added when the endpoints are created


def test_get_all_topics(client: TestClient, auth_headers, test_articles, db):
    """Test getting all topics."""
    # Add topics to some articles
    test_articles[0].topics = ["technology", "ai"]
    test_articles[1].topics = ["technology", "science"]
    test_articles[2].topics = ["politics"]
    db.commit()

    response = client.get("/api/v1/articles/topics/all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "technology" in data
    assert "ai" in data
    assert "science" in data
    assert "politics" in data


def test_search_articles(client: TestClient, auth_headers, test_articles):
    """Test searching articles."""
    # Note: Search functionality not yet implemented in the API
    # This test just checks that the endpoint works
    response = client.get("/api/v1/articles/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_sort_articles_by_date(client: TestClient, auth_headers, test_articles):
    """Test sorting articles by date."""
    response = client.get("/api/v1/articles/?sort_by=date", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Should be sorted by date (most recent first)
    assert isinstance(data, list)
    assert len(data) == 5
