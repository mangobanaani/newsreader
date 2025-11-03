"""MCP (Model Context Protocol) integration for enhanced context."""

from typing import Any

from pydantic import BaseModel


class MCPContext(BaseModel):
    """MCP context for LLM interactions."""

    user_id: int
    reading_history: list[dict[str, Any]]
    preferences: dict[str, Any]
    current_trends: list[str]
    semantic_clusters: dict[int, list[dict[str, Any]]]


class MCPContextBuilder:
    """Build rich context for LLM using MCP protocol."""

    def __init__(self) -> None:
        """Initialize MCP context builder."""
        pass

    def build_context(
        self,
        user_id: int,
        reading_history: list[Any],
        preferences: Any,
        articles: list[Any],
    ) -> MCPContext:
        """Build comprehensive context for LLM recommendations."""
        # Extract reading patterns
        history_data = [
            {
                "title": article.title,
                "topics": article.topics or [],
                "rating": article.user_rating,
                "sentiment": article.sentiment_score,
            }
            for article in reading_history
        ]

        # Build preference map
        preference_data = {
            "preferred_topics": preferences.preferred_topics if preferences else [],
            "excluded_topics": preferences.excluded_topics if preferences else [],
            "min_relevance": preferences.min_relevance_score if preferences else 0.5,
        }

        # Identify trending topics from recent articles
        all_topics: list[str] = []
        for article in articles:
            if article.topics:
                all_topics.extend(article.topics)

        # Get top 10 most common topics
        from collections import Counter

        topic_counts = Counter(all_topics)
        trending = [topic for topic, _ in topic_counts.most_common(10)]

        # Group articles by cluster
        clusters: dict[int, list[dict[str, Any]]] = {}
        for article in articles:
            if article.cluster_id is not None:
                if article.cluster_id not in clusters:
                    clusters[article.cluster_id] = []
                clusters[article.cluster_id].append(
                    {"title": article.title, "topics": article.topics or []}
                )

        return MCPContext(
            user_id=user_id,
            reading_history=history_data,
            preferences=preference_data,
            current_trends=trending,
            semantic_clusters=clusters,
        )

    def format_for_llm(self, context: MCPContext) -> str:
        """Format MCP context for LLM consumption."""
        parts = [
            f"User ID: {context.user_id}",
            "\nReading History:",
        ]

        for item in context.reading_history[:5]:  # Top 5 articles
            parts.append(f"  - {item['title']} (Rating: {item['rating']})")

        parts.append("\nPreferences:")
        if context.preferences["preferred_topics"]:
            parts.append(f"  Interested in: {', '.join(context.preferences['preferred_topics'])}")
        if context.preferences["excluded_topics"]:
            parts.append(
                f"  Not interested in: {', '.join(context.preferences['excluded_topics'])}"
            )

        if context.current_trends:
            parts.append(f"\nTrending Topics: {', '.join(context.current_trends[:5])}")

        if context.semantic_clusters:
            parts.append(f"\nIdentified {len(context.semantic_clusters)} semantic clusters")

        return "\n".join(parts)
