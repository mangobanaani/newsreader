"""Rule engine models for feed filtering and processing."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class RuleType(str, Enum):
    """Type of rule."""

    FILTER = "filter"  # Filter articles in/out
    PRIORITY = "priority"  # Adjust article priority
    CATEGORY = "category"  # Assign categories
    EXTRACT = "extract"  # Extract information
    SUMMARIZE = "summarize"  # Generate summaries
    CUSTOM_PROMPT = "custom_prompt"  # Run custom LLM prompt


class ConditionOperator(str, Enum):
    """Condition operators."""

    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    MATCHES_REGEX = "matches_regex"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


class ActionType(str, Enum):
    """Action types."""

    HIDE = "hide"
    STAR = "star"
    SET_PRIORITY = "set_priority"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    MARK_READ = "mark_read"
    CATEGORIZE = "categorize"
    EXTRACT_ENTITIES = "extract_entities"
    SUMMARIZE = "summarize"
    RUN_PROMPT = "run_prompt"
    SKIP = "skip"


class Rule(Base):
    """Feed processing rule."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String, nullable=False)  # RuleType enum
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority runs first
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Conditions: JSON array of condition objects
    # Example: [{"field": "title", "operator": "contains", "value": "AI"}]
    conditions = Column(JSON, default=list)

    # Actions: JSON array of action objects
    # Example: [{"type": "add_tag", "value": "artificial-intelligence"}]
    actions = Column(JSON, default=list)

    # Settings: JSON object for additional configuration
    settings = Column(JSON, default=dict)

    owner = relationship("User", backref="rules")


class PromptTemplate(Base):
    """LLM prompt template for content analysis."""

    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # None = global template
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "summarization", "extraction", "analysis"
    prompt_text = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False)  # Public templates available to all users
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Variables that can be used in prompt: {title}, {content}, {author}, etc.
    variables = Column(JSON, default=list)

    # Expected output format: "text", "json", "markdown"
    output_format = Column(String, default="text")

    owner = relationship("User", backref="prompt_templates")


class FeedTemplate(Base):
    """Pre-configured feed template with rules."""

    __tablename__ = "feed_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "tech", "news", "research"
    icon = Column(String, nullable=True)

    # Pre-configured RSS feed URLs
    suggested_feeds = Column(JSON, default=list)

    # Pre-configured rules
    rules = Column(JSON, default=list)

    # Pre-configured preferences
    preferences = Column(JSON, default=dict)

    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ArticleMetadata(Base):
    """Extended metadata for articles (NLP results, custom fields)."""

    __tablename__ = "article_metadata"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), unique=True, nullable=False)

    # NLP Extracted Data
    entities = Column(JSON, default=dict)  # {"people": [], "organizations": [], "locations": []}
    keywords = Column(JSON, default=list)  # Extracted keywords
    summary = Column(Text, nullable=True)  # Auto-generated summary
    main_content = Column(Text, nullable=True)  # Cleaned main content

    # Custom fields from rules/prompts
    custom_fields = Column(JSON, default=dict)

    # Processing metadata
    processed_at = Column(DateTime, nullable=True)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_errors = Column(JSON, default=list)

    article = relationship("Article", backref="metadata")
