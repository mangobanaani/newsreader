"""Scraper and OCR destination models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class SourceType(str, Enum):
    """Type of scraping source."""

    RSS = "rss"  # Standard RSS feed
    WEB_PAGE = "web_page"  # Scrape HTML from web page
    IMAGE_URL = "image_url"  # OCR from image URL
    PDF_URL = "pdf_url"  # Extract text from PDF
    SCREENSHOT = "screenshot"  # Take screenshot and OCR
    API = "api"  # Fetch from API endpoint


class ScraperDestination(Base):
    """Scraping destination configuration."""

    __tablename__ = "scraper_destinations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    source_type = Column(String, nullable=False)  # SourceType enum
    source_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Scraping configuration
    scrape_interval_minutes = Column(Integer, default=60)  # How often to scrape
    last_scraped_at = Column(DateTime, nullable=True)

    # OCR settings
    ocr_enabled = Column(Boolean, default=False)
    ocr_languages = Column(JSON, default=["eng"])  # Tesseract language codes
    ocr_preprocessing = Column(JSON, default=dict)  # Image preprocessing options

    # Extraction rules
    css_selectors = Column(JSON, default=dict)  # {"title": "h1", "content": ".article"}
    xpath_rules = Column(JSON, default=dict)  # Alternative to CSS selectors

    # Content transformation
    clean_html = Column(Boolean, default=True)
    extract_images = Column(Boolean, default=False)
    extract_links = Column(Boolean, default=False)

    # Authentication (if needed)
    auth_type = Column(String, nullable=True)  # "basic", "bearer", "api_key"
    auth_credentials = Column(JSON, default=dict)  # Encrypted credentials

    # Additional headers
    custom_headers = Column(JSON, default=dict)

    # Processing options
    run_nlp = Column(Boolean, default=True)
    apply_rules = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", backref="scraper_destinations")


class ScrapedContent(Base):
    """Scraped content from destinations."""

    __tablename__ = "scraped_content"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("scraper_destinations.id"), nullable=False)

    # Content
    title = Column(String, nullable=True)
    content_text = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    extracted_images = Column(JSON, default=list)  # URLs of extracted images
    extracted_links = Column(JSON, default=list)

    # OCR results
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Integer, nullable=True)  # 0-100
    ocr_metadata = Column(JSON, default=dict)

    # Metadata
    source_url = Column(String, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String, nullable=True)  # For deduplication

    # Processing status
    processing_status = Column(String, default="pending")
    processing_errors = Column(JSON, default=list)

    destination = relationship("ScraperDestination", backref="scraped_contents")
