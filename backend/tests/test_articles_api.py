"""Additional comprehensive tests for articles API endpoints."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.feed import Article, Feed


@pytest.fixture
def test_feed_with_articles(db: Session, test_user):
    """Create test feed with articles."""
    feed = Feed(
        url="https://example.com/rss",
        title="Test Feed",
        user_id=test_user.id,
        is_active=True,
    )
    db.add(feed)
    db.commit()

    articles = []
    for i in range(10):
        article = Article(
            title=f"Article {i}",
            link=f"https://example.com/article{i}",
            description=f"Description {i}",
            feed_id=feed.id,
            sentiment_score=0.5 if i % 2 == 0 else -0.3,
            topics=["tech", "ai"] if i % 2 == 0 else ["politics"],
            published_date=datetime.now(timezone.utc),
        )
        db.add(article)
        articles.append(article)
    db.commit()
    for article in articles:
        db.refresh(article)
    return feed, articles


def test_mark_article_as_read(client: TestClient, auth_headers, test_feed_with_articles, db):
    """Test marking article as read."""
    feed, articles = test_feed_with_articles
    article_id = articles[0].id

    # Mark as read
    response = client.post(f"/api/v1/articles/{article_id}/read", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True

    # Verify in database
    article = db.query(Article).filter(Article.id == article_id).first()
    assert article.is_read is True


def test_toggle_bookmark(client: TestClient, auth_headers, test_feed_with_articles, db):
    """Test toggling bookmark status."""
    feed, articles = test_feed_with_articles
    article_id = articles[0].id

    # Toggle bookmark on
    response = client.post(f"/api/v1/articles/{article_id}/bookmark", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_bookmarked"] is True

    # Toggle bookmark off
    response = client.post(f"/api/v1/articles/{article_id}/bookmark", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_bookmarked"] is False


def test_rate_article(client: TestClient, auth_headers, test_feed_with_articles, db):
    """Test rating an article."""
    feed, articles = test_feed_with_articles
    article_id = articles[0].id

    # Rate article
    response = client.post(f"/api/v1/articles/{article_id}/rate?rating=4.5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_rating"] == 4.5


def test_rate_article_invalid_rating(client: TestClient, auth_headers, test_feed_with_articles):
    """Test rating article with invalid rating."""
    feed, articles = test_feed_with_articles
    article_id = articles[0].id

    # Try invalid rating
    response = client.post(f"/api/v1/articles/{article_id}/rate?rating=6.0", headers=auth_headers)
    assert response.status_code == 400


def test_filter_by_sentiment(client: TestClient, auth_headers, test_feed_with_articles):
    """Test filtering articles by sentiment."""
    # Get positive sentiment articles
    response = client.get("/api/v1/articles/?min_sentiment=0.3", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should only get articles with positive sentiment
    for article in data:
        if article["sentiment_score"] is not None:
            assert article["sentiment_score"] >= 0.3


def test_filter_by_topic(client: TestClient, auth_headers, test_feed_with_articles):
    """Test filtering articles by topic."""
    response = client.get("/api/v1/articles/?topic=tech", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should only get articles with tech topic
    for article in data:
        if article["topics"]:
            assert "tech" in article["topics"]


def test_get_topic_trends(client: TestClient, auth_headers, test_feed_with_articles):
    """Test getting topic trends."""
    response = client.get("/api/v1/articles/analytics/topics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "trending_topics" in data


def test_export_articles_csv(client: TestClient, auth_headers, test_feed_with_articles):
    """Test exporting articles as CSV."""
    response = client.get("/api/v1/articles/export/csv", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    # Check that CSV content exists
    assert len(response.content) > 0


def test_export_articles_json(client: TestClient, auth_headers, test_feed_with_articles):
    """Test exporting articles as JSON."""
    response = client.get("/api/v1/articles/export/json", headers=auth_headers)
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    data = response.json()
    assert "articles" in data
    assert "count" in data


def test_process_single_article(client: TestClient, auth_headers, test_feed_with_articles, db):
    """Test processing a single article with NLP."""
    feed, articles = test_feed_with_articles
    article_id = articles[0].id

    response = client.post(f"/api/v1/articles/{article_id}/process", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id


def test_process_all_articles(client: TestClient, auth_headers, test_feed_with_articles):
    """Test processing all articles with NLP."""
    response = client.post("/api/v1/articles/process-all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "processed" in data or "total" in data


def test_cluster_articles(client: TestClient, auth_headers, test_feed_with_articles):
    """Test clustering articles."""
    response = client.post("/api/v1/articles/cluster", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data


def test_get_cluster_analytics(client: TestClient, auth_headers, test_feed_with_articles):
    """Test getting cluster analytics."""
    response = client.get("/api/v1/articles/analytics/clusters", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data
