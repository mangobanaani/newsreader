"""RSS feed fetching and parsing service."""

import asyncio
import re
from datetime import datetime
from typing import Any

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.feed import Article, Feed


class RSSFetcher:
    """RSS feed fetcher service."""

    def __init__(self, db: Session) -> None:
        """Initialize RSS fetcher."""
        self.db = db

    def clean_html(self, text: str | None) -> str:
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

    async def fetch_feed(self, feed_url: str) -> dict[str, Any]:
        """Fetch and parse RSS feed."""
        async with aiohttp.ClientSession() as session:
            async with session.get(str(feed_url)) as response:
                content = await response.text()

        feed_data = feedparser.parse(content)
        return {
            "title": feed_data.feed.get("title", ""),
            "description": feed_data.feed.get("description", ""),
            "entries": feed_data.entries,
        }

    async def update_feed(self, feed: Feed) -> list[Article]:
        """Fetch and update articles for a feed."""
        try:
            feed_data = await self.fetch_feed(feed.url)

            # Update feed metadata
            if not feed.title and feed_data["title"]:
                feed.title = feed_data["title"]
            if not feed.description and feed_data["description"]:
                feed.description = feed_data["description"]

            feed.last_fetched = datetime.utcnow()
            self.db.commit()

            # Process articles
            new_articles = []
            for entry in feed_data["entries"]:
                # Check if article already exists
                existing = self.db.query(Article).filter(Article.link == entry.get("link")).first()

                if not existing:
                    # Clean HTML from description and content
                    description = self.clean_html(entry.get("summary", ""))
                    content = None
                    if entry.get("content"):
                        content = self.clean_html(entry.get("content", [{}])[0].get("value", ""))

                    article = Article(
                        feed_id=feed.id,
                        title=entry.get("title", ""),
                        link=entry.get("link", ""),
                        description=description,
                        content=content,
                        author=entry.get("author", ""),
                        published_date=self._parse_date(entry.get("published")),
                    )
                    self.db.add(article)
                    new_articles.append(article)

            self.db.commit()

            # Automatically process new articles with NLP
            if new_articles:
                from app.services.nlp_processor import NLPProcessor
                processor = NLPProcessor(self.db)
                for article in new_articles:
                    try:
                        processor.process_article(article)
                    except Exception as e:
                        print(f"Warning: Failed to process article {article.id} with NLP: {e}")

            return new_articles

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to fetch feed {feed.url}: {str(e)}")

    async def update_all_feeds(self, user_id: int) -> dict[str, int]:
        """Update all active feeds for a user."""
        feeds = self.db.query(Feed).filter(Feed.user_id == user_id, Feed.is_active.is_(True)).all()

        total_new = 0
        total_errors = 0

        tasks = [self.update_feed(feed) for feed in feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                total_errors += 1
            else:
                total_new += len(result)

        # Automatically run clustering after fetching new articles
        if total_new > 0:
            try:
                from app.services.nlp_processor import NLPProcessor
                processor = NLPProcessor(self.db)
                processor.cluster_articles(user_id)
            except Exception as e:
                print(f"Warning: Failed to cluster articles: {e}")

        return {"new_articles": total_new, "errors": total_errors, "feeds_updated": len(feeds)}

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None

        try:
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str)
        except Exception:
            return None
