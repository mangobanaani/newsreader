"""Feed and Article database models."""

import json as json_lib
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from app.db.base import Base


class JSONEncodedList(TypeDecorator):
    """Represents an immutable list of strings as JSON."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert Python list to JSON string."""
        if value is None:
            return None
        return json_lib.dumps(value)

    def process_result_value(self, value, dialect):
        """Convert JSON string to Python list."""
        if value is None:
            return None
        try:
            return json_lib.loads(value)
        except (json_lib.JSONDecodeError, TypeError):
            return None


class Feed(Base):
    """RSS Feed model."""

    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    country_code = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2 country code
    category = Column(String, nullable=True)  # Feed category (News, Tech, Sports, etc.)
    is_library = Column(Boolean, default=False)  # Whether this is a library feed
    last_fetched = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="feeds")
    articles = relationship("Article", back_populates="feed")


class Article(Base):
    """Article model."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable=False)
    title = Column(String, nullable=False)
    link = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    published_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # NLP fields
    embedding = Column(Text, nullable=True)  # Store as JSON string
    cluster_id = Column(Integer, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    topics = Column(JSONEncodedList, nullable=True)  # Auto-convert JSON to list
    readability_score = Column(Float, nullable=True)
    readability_label = Column(String, nullable=True)
    writing_style = Column(String, nullable=True)

    # User interaction
    is_read = Column(Boolean, default=False)
    is_bookmarked = Column(Boolean, default=False)
    user_rating = Column(Float, nullable=True)

    feed = relationship("Feed", back_populates="articles")


class UserPreference(Base):
    """User reading preferences."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    preferred_topics = Column(JSONEncodedList, default=list)
    excluded_topics = Column(JSONEncodedList, default=list)
    preferred_sources = Column(JSONEncodedList, default=list)
    excluded_sources = Column(JSONEncodedList, default=list)
    excluded_words = Column(
        JSONEncodedList, default=list
    )  # Filter out articles containing these words

    # AI recommendation settings
    enable_recommendations = Column(Boolean, default=True)
    min_relevance_score = Column(Float, default=0.5)

    user = relationship("User", back_populates="preferences")
