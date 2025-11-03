"""API schemas."""

from app.schemas.feed import (
    Article,
    ArticleWithRecommendation,
    Feed,
    FeedCreate,
    FeedUpdate,
    UserPreference,
    UserPreferenceCreate,
    UserPreferenceUpdate,
)
from app.schemas.user import Token, User, UserCreate, UserUpdate

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "Token",
    "Feed",
    "FeedCreate",
    "FeedUpdate",
    "Article",
    "ArticleWithRecommendation",
    "UserPreference",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
]
