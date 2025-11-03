#!/usr/bin/env python3
"""Add default RSS feeds for the admin user."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use dev database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create feeds table if needed
with engine.begin() as conn:
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url VARCHAR NOT NULL,
                title VARCHAR,
                description TEXT,
                last_fetched DATETIME,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, url)
            )
        """))
        print("✅ Feeds table created/verified")
    except Exception as e:
        print(f"Table creation note: {e}")

# Default feeds to add
DEFAULT_FEEDS = [
    {
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "title": "BBC News - Home",
        "description": "BBC News - Latest news and headlines from the UK and around the world"
    },
    {
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "title": "BBC News - World",
        "description": "World news from the BBC"
    },
    {
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "title": "BBC News - Technology",
        "description": "Technology news from the BBC"
    },
    {
        "url": "https://www.theguardian.com/world/rss",
        "title": "The Guardian - World News",
        "description": "Latest world news from The Guardian"
    },
    {
        "url": "https://techcrunch.com/feed/",
        "title": "TechCrunch",
        "description": "Technology news, startups, and venture capital"
    },
    {
        "url": "https://www.reddit.com/r/worldnews/.rss",
        "title": "Reddit - World News",
        "description": "World news from Reddit"
    },
    {
        "url": "https://hnrss.org/frontpage",
        "title": "Hacker News - Front Page",
        "description": "Top stories from Hacker News"
    },
]

db = SessionLocal()

try:
    # Get admin user ID
    result = db.execute(text("SELECT id FROM users WHERE email = :email"),
                       {"email": "admin@newsreader.local"})
    user = result.fetchone()

    if not user:
        print("❌ Admin user not found! Run 'make seed-db' first.")
        sys.exit(1)

    user_id = user[0]
    print(f"✅ Found admin user (ID: {user_id})")

    added_count = 0
    skipped_count = 0

    for feed_data in DEFAULT_FEEDS:
        # Check if feed already exists
        result = db.execute(
            text("SELECT id FROM feeds WHERE user_id = :uid AND url = :url"),
            {"uid": user_id, "url": feed_data["url"]}
        )
        existing = result.fetchone()

        if existing:
            print(f"⏭️  Skipped (already exists): {feed_data['title']}")
            skipped_count += 1
            continue

        # Add feed
        db.execute(
            text("""
                INSERT INTO feeds (user_id, url, title, description, is_active)
                VALUES (:uid, :url, :title, :desc, 1)
            """),
            {
                "uid": user_id,
                "url": feed_data["url"],
                "title": feed_data["title"],
                "desc": feed_data["description"]
            }
        )
        print(f"✅ Added: {feed_data['title']}")
        added_count += 1

    db.commit()

    print("\n" + "="*60)
    print(f"✅ Default feeds setup complete!")
    print(f"   Added: {added_count} feeds")
    print(f"   Skipped: {skipped_count} feeds (already existed)")
    print("="*60)
    print("\n📰 Available feeds:")

    # List all feeds
    result = db.execute(
        text("SELECT title, url FROM feeds WHERE user_id = :uid ORDER BY id"),
        {"uid": user_id}
    )
    for i, (title, url) in enumerate(result.fetchall(), 1):
        print(f"  {i}. {title}")
        print(f"     {url}")

    print("\n💡 Tip: Login at http://localhost:3001 to see your feeds!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
finally:
    db.close()
