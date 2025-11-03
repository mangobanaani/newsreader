"""Fuzzy matching for duplicate article detection."""

import re
from difflib import SequenceMatcher
from typing import Any

from sqlalchemy.orm import Session

from app.models.feed import Article


class FuzzyMatcher:
    """Fuzzy matching service for duplicate detection."""

    def __init__(self, db: Session):
        """Initialize fuzzy matcher."""
        self.db = db

    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Convert to lowercase
        text = text.lower()

        # Remove special characters and extra whitespace
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        # Remove common filler words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
        }
        words = text.split()
        words = [w for w in words if w not in stop_words]

        return " ".join(words).strip()

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)."""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)

        # Use SequenceMatcher for fuzzy comparison
        return SequenceMatcher(None, norm1, norm2).ratio()

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def find_similar_headlines(
        self, article: Article, threshold: float = 0.8, limit: int = 10
    ) -> list[tuple[Article, float]]:
        """Find articles with similar headlines."""
        # Get recent articles from the same user
        recent_articles = (
            self.db.query(Article)
            .join(Article.feed)
            .filter(
                Article.id != article.id,
                Article.feed.has(user_id=article.feed.user_id),
            )
            .order_by(Article.created_at.desc())
            .limit(1000)  # Check last 1000 articles
            .all()
        )

        similar_articles = []

        for other_article in recent_articles:
            similarity = self.calculate_similarity(article.title, other_article.title)

            if similarity >= threshold:
                similar_articles.append((other_article, similarity))

        # Sort by similarity
        similar_articles.sort(key=lambda x: x[1], reverse=True)

        return similar_articles[:limit]

    def find_duplicates(
        self, article: Article, title_threshold: float = 0.85, content_threshold: float = 0.9
    ) -> list[dict[str, Any]]:
        """Find potential duplicate articles."""
        duplicates = []

        # Check title similarity
        similar_by_title = self.find_similar_headlines(article, threshold=title_threshold)

        for other_article, title_similarity in similar_by_title:
            # Also check content similarity if both have content
            content_similarity = 0.0
            if article.content and other_article.content:
                content_similarity = self.calculate_similarity(
                    article.content[:500], other_article.content[:500]
                )

            # Determine if it's a duplicate
            is_duplicate = (
                title_similarity >= title_threshold or content_similarity >= content_threshold
            )

            if is_duplicate:
                duplicates.append(
                    {
                        "article_id": other_article.id,
                        "article_title": other_article.title,
                        "title_similarity": title_similarity,
                        "content_similarity": content_similarity,
                        "feed_id": other_article.feed_id,
                        "published_date": other_article.published_date,
                    }
                )

        return duplicates

    def deduplicate_articles(self, user_id: int, keep_strategy: str = "oldest") -> dict[str, Any]:
        """Deduplicate articles for a user."""
        # Get all articles
        articles = (
            self.db.query(Article)
            .join(Article.feed)
            .filter(Article.feed.has(user_id=user_id))
            .order_by(Article.created_at.asc())
            .all()
        )

        marked_for_removal = set()
        duplicate_groups = []

        # Find duplicate groups
        for i, article in enumerate(articles):
            if article.id in marked_for_removal:
                continue

            duplicates = self.find_duplicates(article)
            if duplicates:
                group = {"primary": article.id, "duplicates": []}

                for dup in duplicates:
                    dup_id = dup["article_id"]
                    if dup_id not in marked_for_removal:
                        group["duplicates"].append(dup)
                        marked_for_removal.add(dup_id)

                if group["duplicates"]:
                    duplicate_groups.append(group)

        # Mark duplicates based on strategy
        removed_count = 0
        if keep_strategy == "oldest":
            # Keep oldest, mark others as read
            for article in articles:
                if article.id in marked_for_removal:
                    article.is_read = True
                    removed_count += 1
        elif keep_strategy == "newest":
            # Keep newest, mark others as read
            for group in duplicate_groups:
                primary_article = (
                    self.db.query(Article).filter(Article.id == group["primary"]).first()
                )
                if primary_article:
                    primary_article.is_read = True
                    removed_count += 1

        self.db.commit()

        return {
            "duplicate_groups": len(duplicate_groups),
            "articles_marked": removed_count,
            "total_articles": len(articles),
        }

    def extract_keywords(self, text: str) -> set[str]:
        """Extract keywords for comparison."""
        normalized = self.normalize_text(text)
        words = normalized.split()

        # Filter words longer than 3 characters
        keywords = {w for w in words if len(w) > 3}

        return keywords

    def keyword_overlap(self, text1: str, text2: str) -> float:
        """Calculate keyword overlap between two texts."""
        keywords1 = self.extract_keywords(text1)
        keywords2 = self.extract_keywords(text2)

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        return intersection / union if union > 0 else 0.0
