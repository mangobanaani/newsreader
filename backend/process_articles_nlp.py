#!/usr/bin/env python3
"""Process articles with NLP - manual script."""

import os
import sys
import json

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./dev.db'
os.environ['SECRET_KEY'] = 'test-key'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from collections import Counter

# Create database session
DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Initialize sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

def extract_topics(text):
    """Extract topics from text."""
    stop_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
        'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
        'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
        'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
        'were', 'said', 'did', 'having', 'may', 'such', 'being', 'here', 'should'
    }

    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()

    # Filter words
    filtered_words = [
        word for word in words
        if word not in stop_words
        and len(word) > 4
        and not word.isdigit()
    ]

    # Get most common words
    word_counts = Counter(filtered_words)
    topics = [word for word, _ in word_counts.most_common(10)]

    # Add categories
    categories = []
    category_keywords = {
        'technology': ['tech', 'software', 'hardware', 'computer', 'digital', 'internet'],
        'ai': ['artificial', 'intelligence', 'machine', 'learning', 'neural', 'openai', 'anthropic', 'claude', 'chatgpt'],
        'business': ['business', 'company', 'market', 'stock', 'investment', 'finance'],
        'politics': ['politics', 'government', 'election', 'president'],
        'security': ['security', 'cybersecurity', 'breach', 'hack', 'vulnerability'],
        'sports': ['sports', 'game', 'player', 'team', 'football', 'basketball'],
    }

    text_lower = text.lower()
    for category, keywords in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            categories.append(category)

    return list(set(topics + categories))[:15]

def calculate_sentiment(text):
    """Calculate sentiment using VADER."""
    scores = sentiment_analyzer.polarity_scores(text)
    return scores['compound']

# Get all articles for user 1
result = db.execute(
    text("""
        SELECT a.id, a.title, a.description
        FROM articles a
        JOIN feeds f ON a.feed_id = f.id
        WHERE f.user_id = 1
    """)
)

articles = result.fetchall()
print(f"Processing {len(articles)} articles...")

for article in articles:
    article_id, title, description = article
    text_content = f"{title}. {description or ''}"

    # Calculate sentiment
    sentiment = calculate_sentiment(text_content)

    # Extract topics
    topics = extract_topics(text_content)
    topics_json = json.dumps(topics)

    # Update database
    db.execute(
        text("""
            UPDATE articles
            SET sentiment_score = :sentiment,
                topics = :topics
            WHERE id = :id
        """),
        {"sentiment": sentiment, "topics": topics_json, "id": article_id}
    )

    print(f"Article {article_id}: {title[:50]}...")
    print(f"  Sentiment: {sentiment:.3f}")
    print(f"  Topics: {', '.join(topics[:5])}")
    print()

db.commit()
print(f"✓ Successfully processed {len(articles)} articles!")
db.close()
