#!/usr/bin/env python3
"""Fetch articles from all RSS feeds."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Use dev database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create articles table
with engine.begin() as conn:
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                link VARCHAR NOT NULL UNIQUE,
                description TEXT,
                content TEXT,
                author VARCHAR,
                published_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                is_bookmarked BOOLEAN DEFAULT 0,
                user_rating FLOAT,
                FOREIGN KEY (feed_id) REFERENCES feeds (id)
            )
        """))
        print("✅ Articles table created/verified")
    except Exception as e:
        print(f"Table creation note: {e}")

# Now fetch articles from feeds
import feedparser
from datetime import datetime
import time

db = SessionLocal()

try:
    # Get all active feeds
    result = db.execute(text("SELECT id, url, title FROM feeds WHERE is_active = 1"))
    feeds = result.fetchall()

    print(f"\n📡 Fetching articles from {len(feeds)} feeds...")

    total_added = 0
    total_skipped = 0

    for feed_id, feed_url, feed_title in feeds:
        print(f"\n  Fetching: {feed_title}")
        print(f"  URL: {feed_url}")

        try:
            # Parse the feed
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"  ⚠️  Warning: Feed may have issues")

            added = 0
            skipped = 0

            # Add articles
            for entry in feed.entries[:10]:  # Limit to 10 most recent
                title = entry.get('title', 'No title')
                link = entry.get('link', '')

                if not link:
                    continue

                # Check if article already exists
                existing = db.execute(
                    text("SELECT id FROM articles WHERE link = :link"),
                    {"link": link}
                ).fetchone()

                if existing:
                    skipped += 1
                    continue

                # Get other fields
                description = entry.get('summary', entry.get('description', ''))
                author = entry.get('author', '')

                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6])
                    except:
                        pass

                # Insert article
                db.execute(
                    text("""
                        INSERT INTO articles
                        (feed_id, title, link, description, author, published_date)
                        VALUES (:feed_id, :title, :link, :description, :author, :published_date)
                    """),
                    {
                        "feed_id": feed_id,
                        "title": title[:500] if title else "No title",  # Limit length
                        "link": link,
                        "description": description[:1000] if description else "",
                        "author": author[:200] if author else "",
                        "published_date": published_date
                    }
                )
                added += 1

            db.commit()
            print(f"  ✅ Added: {added} articles, Skipped: {skipped}")
            total_added += added
            total_skipped += skipped

            # Be nice to servers
            time.sleep(0.5)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            db.rollback()

    print("\n" + "="*60)
    print(f"✅ Article fetch complete!")
    print(f"   Total added: {total_added} articles")
    print(f"   Total skipped: {total_skipped} articles (already existed)")
    print("="*60)

    # Show article count
    result = db.execute(text("SELECT COUNT(*) FROM articles"))
    total = result.fetchone()[0]
    print(f"\n📰 Total articles in database: {total}")

    print("\n💡 Refresh the frontend to see your articles!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
