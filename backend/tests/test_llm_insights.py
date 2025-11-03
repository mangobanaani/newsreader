"""Test LLM insights service."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.feed import Article, Feed
from app.services.llm_insights import (
    LLMContentError,
    LLMFeatureDisabledError,
    LLMInsightService,
)


@pytest.fixture
def test_article(db: Session, test_user):
    """Create test article."""
    feed = Feed(
        url="https://example.com/rss",
        title="Test Feed",
        user_id=test_user.id,
        is_active=True,
    )
    db.add(feed)
    db.commit()

    article = Article(
        title="Breaking: Major AI Breakthrough Announced",
        link="https://example.com/article",
        description="Researchers have announced a significant breakthrough in artificial intelligence.",
        content="Scientists at a leading research institution have developed a new AI model that shows remarkable capabilities in natural language understanding and generation.",
        author="John Doe",
        feed_id=feed.id,
        sentiment_score=0.1,
        readability_label="Standard",
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def test_llm_service_disabled():
    """Test LLM service when features are disabled."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = False
        mock_settings.OPENAI_API_KEY = None

        service = LLMInsightService()
        assert service.enabled is False


def test_llm_service_enabled():
    """Test LLM service when features are enabled."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = True
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.LLM_MODEL_OPENAI = "gpt-4-turbo-preview"

        with patch("app.services.llm_insights.OpenAI"):
            service = LLMInsightService()
            assert service.enabled is True


def test_generate_insights_disabled(test_article):
    """Test generating insights when service is disabled."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = False
        mock_settings.OPENAI_API_KEY = None

        service = LLMInsightService()
        with pytest.raises(LLMFeatureDisabledError):
            service.generate_insights(test_article)


def test_generate_insights_success(test_article):
    """Test successful insights generation."""
    mock_response = {
        "summary": "A major breakthrough in AI has been announced by researchers.",
        "key_points": [
            "New AI model developed",
            "Significant improvement in NLU",
            "Developed by leading research institution",
        ],
        "reliability_score": 0.85,
        "reliability_label": "Highly Reliable",
        "reliability_reason": "Published by reputable source with clear authorship",
        "tone": "Neutral/Informational",
        "suggested_actions": ["Read the full paper", "Compare with other sources"],
    }

    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = True
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.LLM_MODEL_OPENAI = "gpt-4-turbo-preview"

        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = str(mock_response).replace("'", '"')

        with patch("app.services.llm_insights.OpenAI") as MockOpenAI:
            MockOpenAI.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_completion

            service = LLMInsightService()
            insights = service.generate_insights(test_article)

            assert "summary" in insights
            assert "key_points" in insights
            assert "reliability_score" in insights
            assert isinstance(insights["key_points"], list)


def test_generate_insights_fallback(test_article):
    """Test fallback insights when LLM fails."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = True
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.LLM_MODEL_OPENAI = "gpt-4-turbo-preview"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch("app.services.llm_insights.OpenAI") as MockOpenAI:
            MockOpenAI.return_value = mock_client

            service = LLMInsightService()
            insights = service.generate_insights(test_article)

            # Should return fallback insights
            assert "summary" in insights
            assert "key_points" in insights
            assert insights["summary"] != ""
            assert isinstance(insights["key_points"], list)


def test_build_summary(test_article):
    """Test summary building from article."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = False
        mock_settings.OPENAI_API_KEY = None

        service = LLMInsightService()
        summary = service._build_summary(test_article)

        assert summary != ""
        assert len(summary) > 0


def test_estimate_reliability(test_article):
    """Test reliability estimation."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = False
        mock_settings.OPENAI_API_KEY = None

        service = LLMInsightService()
        score = service._estimate_reliability(test_article)

        assert 0.0 <= score <= 1.0


def test_reliability_labels():
    """Test reliability label mapping."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = False
        mock_settings.OPENAI_API_KEY = None

        service = LLMInsightService()

        assert service._reliability_label(0.9) == "Highly Reliable"
        assert service._reliability_label(0.75) == "Reliable"
        assert service._reliability_label(0.6) == "Mixed Signals"
        assert service._reliability_label(0.4) == "Unverified"
        assert service._reliability_label(0.2) == "Questionable"


def test_estimate_tone(test_article):
    """Test tone estimation."""
    with patch("app.services.llm_insights.settings") as mock_settings:
        mock_settings.ENABLE_LLM_FEATURES = False
        mock_settings.OPENAI_API_KEY = None

        service = LLMInsightService()

        # Test neutral tone
        test_article.sentiment_score = 0.1
        tone = service._estimate_tone(test_article)
        assert "neutral" in tone.lower()

        # Test positive tone
        test_article.sentiment_score = 0.5
        tone = service._estimate_tone(test_article)
        assert "positive" in tone.lower() or "upbeat" in tone.lower()

        # Test negative tone
        test_article.sentiment_score = -0.5
        tone = service._estimate_tone(test_article)
        assert "critical" in tone.lower() or "concerned" in tone.lower()
