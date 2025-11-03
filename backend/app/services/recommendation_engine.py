"""AI-powered recommendation engine using LLMs."""

import json

import anthropic
import numpy as np
import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.feed import Article, UserPreference


class RecommendationEngine:
    """LLM-powered recommendation engine."""

    def __init__(self, db: Session) -> None:
        """Initialize recommendation engine."""
        self.db = db
        self.provider = settings.DEFAULT_LLM_PROVIDER
        self.use_llm = False
        self.llm_enabled = settings.ENABLE_LLM_FEATURES

        if not self.llm_enabled:
            return

        if self.provider == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.LLM_MODEL_OPENAI
            self.use_llm = True
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.LLM_MODEL_ANTHROPIC
            self.use_llm = True
        # Fall back to embedding-based recommendations if no API key

    async def get_recommendations(
        self, user_id: int, limit: int = 20
    ) -> list[tuple[Article, float, str]]:
        """Get personalized article recommendations."""
        # Get user preferences
        preferences = (
            self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        )

        if not preferences or not preferences.enable_recommendations:
            return []

        # Get unread articles
        unread_articles = (
            self.db.query(Article)
            .join(Article.feed)
            .filter(
                Article.feed.has(user_id=user_id),
                Article.is_read.is_(False),
                Article.embedding.isnot(None),
            )
            .limit(100)
            .all()
        )

        if not unread_articles:
            return []

        # Get user's reading history for context
        read_articles = (
            self.db.query(Article)
            .join(Article.feed)
            .filter(
                Article.feed.has(user_id=user_id),
                Article.is_read.is_(True),
                Article.user_rating.isnot(None),
            )
            .order_by(Article.user_rating.desc())
            .limit(10)
            .all()
        )

        # Score articles
        recommendations: list[tuple[Article, float, str]] = []

        for article in unread_articles:
            score, reason = await self._score_article(article, read_articles, preferences)

            if score >= preferences.min_relevance_score:
                recommendations.append((article, score, reason))

        # Sort by score and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]

    async def _score_article(
        self,
        article: Article,
        reading_history: list[Article],
        preferences: UserPreference,
    ) -> tuple[float, str]:
        """Score an article based on user preferences and reading history."""
        # If no LLM available, use fallback scoring directly
        if not self.use_llm:
            return (
                self._fallback_score(article, reading_history, preferences),
                "Based on content similarity and topics",
            )

        # Build context for LLM
        user_context = self._build_user_context(reading_history, preferences)

        # Build article summary with NLP insights
        article_parts = [f"Title: {article.title}"]

        if article.description:
            article_parts.append(f"Description: {article.description}")

        if article.sentiment_score is not None:
            sentiment_label = (
                "positive"
                if article.sentiment_score > 0.05
                else "negative" if article.sentiment_score < -0.05 else "neutral"
            )
            article_parts.append(f"Sentiment: {sentiment_label} ({article.sentiment_score:.2f})")

        if article.topics:
            try:
                topics = (
                    json.loads(article.topics)
                    if isinstance(article.topics, str)
                    else article.topics
                )
                article_parts.append(f"Topics: {', '.join(topics[:5])}")
            except (json.JSONDecodeError, TypeError):
                pass

        article_summary = "\n".join(article_parts)

        prompt = f"""Analyze this news article and determine how relevant it is to the user's interests.

User Context:
{user_context}

Article to Analyze:
{article_summary}

Provide:
1. A relevance score between 0.0 and 1.0 (where 1.0 is highly relevant)
2. A brief reason (one sentence) explaining the score

Consider the article's sentiment and topics in your analysis.

Respond in JSON format:
{{"score": 0.0, "reason": "explanation"}}"""

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text
            else:  # openai
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3,
                )
                content = response.choices[0].message.content or "{}"

            result = json.loads(content)
            return float(result.get("score", 0.0)), result.get("reason", "")

        except Exception:
            # Fallback to embedding-based similarity
            return (
                self._fallback_score(article, reading_history, preferences),
                "Based on content similarity",
            )

    def _build_user_context(
        self, reading_history: list[Article], preferences: UserPreference
    ) -> str:
        """Build user context for LLM."""
        context_parts = []

        if preferences.preferred_topics:
            context_parts.append(f"Preferred topics: {', '.join(preferences.preferred_topics)}")

        if preferences.excluded_topics:
            context_parts.append(f"Topics to avoid: {', '.join(preferences.excluded_topics)}")

        if reading_history:
            liked_titles = [a.title for a in reading_history[:5]]
            context_parts.append(f"Recently liked articles: {', '.join(liked_titles)}")

        return "\n".join(context_parts) if context_parts else "No specific preferences set"

    def _fallback_score(
        self, article: Article, reading_history: list[Article], preferences: UserPreference
    ) -> float:
        """Fallback scoring using embedding similarity and NLP features."""
        base_score = 0.5

        # Topic-based scoring if user has preferences
        if article.topics and preferences.preferred_topics:
            article_topics = set(article.topics) if isinstance(article.topics, list) else set()
            preferred_topics = set(preferences.preferred_topics)
            topic_overlap = len(article_topics & preferred_topics)
            if topic_overlap > 0:
                base_score += 0.2 * topic_overlap  # Boost for matching preferred topics

        # Penalize excluded topics
        if article.topics and preferences.excluded_topics:
            article_topics = set(article.topics) if isinstance(article.topics, list) else set()
            excluded_topics = set(preferences.excluded_topics)
            if article_topics & excluded_topics:
                base_score -= 0.3  # Penalize excluded topics

        # Embedding-based similarity
        if article.embedding and reading_history:
            try:
                article_embedding = np.array(
                    json.loads(article.embedding)
                    if isinstance(article.embedding, str)
                    else article.embedding
                )
                similarities = []

                for hist_article in reading_history:
                    if hist_article.embedding:
                        hist_embedding = np.array(
                            json.loads(hist_article.embedding)
                            if isinstance(hist_article.embedding, str)
                            else hist_article.embedding
                        )
                        similarity = float(
                            np.dot(article_embedding, hist_embedding)
                            / (np.linalg.norm(article_embedding) * np.linalg.norm(hist_embedding))
                        )
                        similarities.append(similarity)

                if similarities:
                    embedding_score = float(np.mean(similarities))
                    # Blend embedding similarity with base score
                    base_score = (base_score + embedding_score) / 2
            except (json.JSONDecodeError, ValueError, TypeError):
                pass

        # Boost/penalize based on sentiment
        if article.sentiment_score is not None:
            # Slightly boost positive articles, slightly penalize very negative ones
            if article.sentiment_score > 0.3:
                base_score += 0.05
            elif article.sentiment_score < -0.5:
                base_score -= 0.05

        return min(1.0, max(0.0, base_score))
