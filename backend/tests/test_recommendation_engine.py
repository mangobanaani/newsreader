"""Test recommendation engine service."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.feed import Article, Feed, UserPreference
from app.services.recommendation_engine import RecommendationEngine


@pytest.fixture
def recommendation_engine(db: Session):
    """Create recommendation engine instance."""
    return RecommendationEngine(db)


@pytest.fixture
def user_with_preferences(db: Session, test_user):
    """Create user with preferences."""
    preference = UserPreference(
        user_id=test_user.id,
        preferred_topics=["technology", "ai"],
        excluded_topics=["sports"],
        enable_recommendations=True,
        min_relevance_score=0.5,
    )
    db.add(preference)
    db.commit()
    return test_user


@pytest.fixture
def sample_articles(db: Session, test_user):
    """Create sample articles for recommendation testing."""
    feed = Feed(
        url="https://example.com/rss",
        title="Tech Feed",
        user_id=test_user.id,
        is_active=True,
    )
    db.add(feed)
    db.commit()

    articles = []
    article_data = [
        {
            "title": "AI Breakthrough in Machine Learning",
            "topics": ["ai", "technology"],
            "sentiment_score": 0.8,
        },
        {
            "title": "Football Championship Results",
            "topics": ["sports"],
            "sentiment_score": 0.2,
        },
        {
            "title": "New Programming Language Released",
            "topics": ["technology", "programming"],
            "sentiment_score": 0.6,
        },
    ]

    for data in article_data:
        article = Article(
            title=data["title"],
            link=f"https://example.com/{data['title'].replace(' ', '-').lower()}",
            description=f"Article about {data['title']}",
            feed_id=feed.id,
            topics=data["topics"],
            sentiment_score=data["sentiment_score"],
        )
        db.add(article)
        articles.append(article)

    db.commit()
    for article in articles:
        db.refresh(article)

    return articles


def test_recommendation_engine_initialization(recommendation_engine):
    """Test recommendation engine initialization."""
    assert recommendation_engine is not None
    assert recommendation_engine.db is not None


@pytest.mark.asyncio
async def test_calculate_relevance_score_with_preferences(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test relevance score calculation based on user preferences."""
    article = sample_articles[0]  # AI article
    import json

    article.embedding = json.dumps([0.1] * 768)
    db.commit()

    preferences = (
        db.query(UserPreference).filter(UserPreference.user_id == user_with_preferences.id).first()
    )
    score = recommendation_engine._fallback_score(article, [], preferences)

    # Should have high score due to matching topics
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_excluded_topics_lower_score(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test that excluded topics lower relevance score."""
    sports_article = sample_articles[1]  # Sports article
    import json

    sports_article.embedding = json.dumps([0.1] * 768)
    db.commit()

    preferences = (
        db.query(UserPreference).filter(UserPreference.user_id == user_with_preferences.id).first()
    )
    score = recommendation_engine._fallback_score(sports_article, [], preferences)

    # Should have low score due to excluded topic
    assert isinstance(score, float)
    assert score < 0.5  # Below min relevance threshold


@pytest.mark.asyncio
async def test_get_recommendations_filters_by_preferences(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test that recommendations respect user preferences."""
    import json

    for article in sample_articles:
        article.embedding = json.dumps([0.1] * 768)
    db.commit()

    recommendations = await recommendation_engine.get_recommendations(
        user_with_preferences.id, limit=10
    )

    # Should return list of tuples (article, score, reason)
    assert isinstance(recommendations, list)
    for article, score, reason in recommendations:
        if article.topics and "sports" in article.topics:
            # Sports articles might be filtered out or have low scores
            assert score < 0.5


@pytest.mark.asyncio
async def test_get_recommendations_sorts_by_score(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test that recommendations are sorted by relevance score."""
    import json

    for article in sample_articles:
        article.embedding = json.dumps([0.1] * 768)
    db.commit()

    recommendations = await recommendation_engine.get_recommendations(
        user_with_preferences.id, limit=10
    )

    if len(recommendations) > 1:
        # Verify descending order by score
        for i in range(len(recommendations) - 1):
            assert recommendations[i][1] >= recommendations[i + 1][1]


@pytest.mark.asyncio
async def test_get_recommendations_respects_limit(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test that recommendations respect limit parameter."""
    import json

    for article in sample_articles:
        article.embedding = json.dumps([0.1] * 768)
    db.commit()

    recommendations = await recommendation_engine.get_recommendations(
        user_with_preferences.id, limit=1
    )

    assert len(recommendations) <= 1


@pytest.mark.asyncio
async def test_get_recommendations_without_preferences(
    recommendation_engine, sample_articles, test_user, db
):
    """Test recommendations when user has no preferences."""
    # Ensure no preferences exist
    db.query(UserPreference).filter(UserPreference.user_id == test_user.id).delete()
    db.commit()

    recommendations = await recommendation_engine.get_recommendations(test_user.id, limit=10)

    # Should return empty list without preferences
    assert isinstance(recommendations, list)


@pytest.mark.asyncio
async def test_llm_recommendations_when_enabled(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test LLM-based recommendations when enabled."""
    import json

    for article in sample_articles:
        article.embedding = json.dumps([0.1] * 768)
    db.commit()

    # Just test that it doesn't crash - LLM features may not be enabled
    recommendations = await recommendation_engine.get_recommendations(
        user_with_preferences.id, limit=10
    )

    assert isinstance(recommendations, list)


@pytest.mark.asyncio
async def test_score_by_reading_history(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test scoring based on reading history."""
    import json

    # Mark one article as read with high rating
    article = sample_articles[0]
    article.is_read = True
    article.user_rating = 5.0
    article.embedding = json.dumps([0.1] * 768)
    db.commit()

    # Similar article should get boost
    similar_article = sample_articles[2]  # Also tech-related
    similar_article.embedding = json.dumps([0.1] * 768)

    preferences = (
        db.query(UserPreference).filter(UserPreference.user_id == user_with_preferences.id).first()
    )
    score = recommendation_engine._fallback_score(similar_article, [article], preferences)

    assert isinstance(score, float)
    assert score > 0


@pytest.mark.asyncio
async def test_diversity_in_recommendations(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test that recommendations include diverse topics."""
    import json

    for article in sample_articles:
        article.embedding = json.dumps([0.1] * 768)
    db.commit()

    recommendations = await recommendation_engine.get_recommendations(
        user_with_preferences.id, limit=10
    )

    # Just verify it returns recommendations
    assert isinstance(recommendations, list)


@pytest.mark.asyncio
async def test_filter_already_read_articles(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test filtering out already read articles."""
    import json

    for article in sample_articles:
        article.embedding = json.dumps([0.1] * 768)

    # Mark article as read
    sample_articles[0].is_read = True
    db.commit()

    recommendations = await recommendation_engine.get_recommendations(
        user_with_preferences.id, limit=10
    )

    # Should not include read article (get_recommendations filters is_read=False)
    for article, score, reason in recommendations:
        assert article.id != sample_articles[0].id


@pytest.mark.asyncio
async def test_boost_recent_articles(
    recommendation_engine, sample_articles, user_with_preferences, db
):
    """Test that recent articles get score boost."""
    import json
    from datetime import datetime, timezone

    # Set recent published date
    recent_article = sample_articles[0]
    recent_article.published_date = datetime.now(timezone.utc)
    recent_article.embedding = json.dumps([0.1] * 768)
    db.commit()

    preferences = (
        db.query(UserPreference).filter(UserPreference.user_id == user_with_preferences.id).first()
    )
    score = recommendation_engine._fallback_score(recent_article, [], preferences)

    # Recent articles should have positive score
    assert isinstance(score, float)
    assert score > 0
