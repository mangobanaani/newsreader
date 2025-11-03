#!/usr/bin/env python3
"""Clean HTML and JavaScript from existing articles."""

import os
import sys
import re

os.environ['DATABASE_URL'] = 'sqlite:///./dev.db'
os.environ['SECRET_KEY'] = 'test-key'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

# Create database session
DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def clean_html(text):
    """Remove HTML tags and JavaScript from text."""
    if not text:
        return ""

    # Remove script and style tags with their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Use BeautifulSoup to clean remaining HTML
    soup = BeautifulSoup(text, 'html.parser')

    # Remove any remaining script/style tags
    for script in soup(['script', 'style', 'noscript']):
        script.decompose()

    # Get text and clean up whitespace
    cleaned = soup.get_text(separator=' ', strip=True)

    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove any remaining HTML entities
    cleaned = re.sub(r'&[a-zA-Z]+;', ' ', cleaned)

    return cleaned.strip()

# Get all articles
result = db.execute(
    text("SELECT id, description, content FROM articles")
)

articles = result.fetchall()
print(f"Cleaning HTML from {len(articles)} articles...")

processed = 0
for article in articles:
    article_id, description, content = article

    # Clean description and content
    cleaned_description = clean_html(description) if description else None
    cleaned_content = clean_html(content) if content else None

    # Update database
    db.execute(
        text("""
            UPDATE articles
            SET description = :description,
                content = :content
            WHERE id = :id
        """),
        {
            "description": cleaned_description,
            "content": cleaned_content,
            "id": article_id
        }
    )

    processed += 1
    if processed % 50 == 0:
        db.commit()
        print(f"  Cleaned {processed}/{len(articles)} articles...")

# Final commit
db.commit()
print(f"\n✓ Successfully cleaned {len(articles)} articles!")
db.close()
