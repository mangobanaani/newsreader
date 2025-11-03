"""Feed and Article schemas."""

import json
from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator


class FeedBase(BaseModel):
    """Base feed schema."""

    url: HttpUrl
    title: str | None = None
    description: str | None = None
    country_code: str | None = None
    category: str | None = None
    is_library: bool = False


class FeedCreate(FeedBase):
    """Feed creation schema."""

    pass


class FeedUpdate(BaseModel):
    """Feed update schema."""

    title: str | None = None
    description: str | None = None
    country_code: str | None = None
    category: str | None = None
    is_active: bool | None = None


class FeedInDB(FeedBase):
    """Feed schema from database."""

    id: int
    last_fetched: datetime | None
    is_active: bool
    user_id: int

    model_config = {"from_attributes": True}


class Feed(FeedInDB):
    """Public feed schema."""

    pass


class ArticleBase(BaseModel):
    """Base article schema."""

    title: str
    link: HttpUrl
    description: str | None = None
    content: str | None = None
    author: str | None = None
    published_date: datetime | None = None


class ArticleInDB(ArticleBase):
    """Article schema from database."""

    id: int
    feed_id: int
    created_at: datetime
    cluster_id: int | None = None
    sentiment_score: float | None = None
    topics: list[str] | None = None
    readability_score: float | None = None
    readability_label: str | None = None
    writing_style: str | None = None
    is_read: bool
    is_bookmarked: bool
    user_rating: float | None = None

    model_config = {"from_attributes": True}


class Article(ArticleInDB):
    """Public article schema."""

    pass  # JSONEncodedList in model handles conversion automatically


class ArticleWithRecommendation(Article):
    """Article with recommendation score."""

    recommendation_score: float
    recommendation_reason: str | None = None


class ArticleLLMInsights(BaseModel):
    """AI-generated insights for an article."""

    summary: str
    key_points: list[str]
    reliability_score: float | None = None
    reliability_label: str | None = None
    reliability_reason: str | None = None
    tone: str | None = None
    suggested_actions: list[str] = []


class UserPreferenceBase(BaseModel):
    """Base user preference schema."""

    preferred_topics: list[str] = []
    excluded_topics: list[str] = []
    preferred_sources: list[str] = []
    excluded_sources: list[str] = []
    excluded_words: list[str] = []
    enable_recommendations: bool = True
    min_relevance_score: float = 0.5


class UserPreferenceCreate(UserPreferenceBase):
    """User preference creation schema."""

    pass


class UserPreferenceUpdate(BaseModel):
    """User preference update schema."""

    preferred_topics: list[str] | None = None
    excluded_topics: list[str] | None = None
    preferred_sources: list[str] | None = None
    excluded_sources: list[str] | None = None
    excluded_words: list[str] | None = None
    enable_recommendations: bool | None = None
    min_relevance_score: float | None = None


class UserPreference(UserPreferenceBase):
    """Public user preference schema."""

    id: int
    user_id: int

    model_config = {"from_attributes": True}


class ArticleLLMInsights(BaseModel):
    """LLM-generated insights for an article."""

    summary: str
    key_points: list[str]
    reliability_score: float | None = None
    reliability_label: str | None = None
    reliability_reason: str | None = None
    tone: str | None = None
    suggested_actions: list[str] = []
