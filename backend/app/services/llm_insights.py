"""LLM-powered content insights."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.models.feed import Article


class LLMFeatureDisabledError(RuntimeError):
    """Raised when LLM features are disabled."""


class LLMContentError(RuntimeError):
    """Raised when LLM generation fails."""


class LLMInsightService:
    """Generate AI insights for news articles."""

    def __init__(self) -> None:
        """Initialize the service."""
        self.enabled = settings.ENABLE_LLM_FEATURES and bool(settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL_OPENAI
        self.client: OpenAI | None = None

        if self.enabled:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _ensure_enabled(self) -> None:
        if not self.enabled:
            raise LLMFeatureDisabledError("LLM features are disabled")

    def generate_insights(self, article: Article) -> dict[str, Any]:
        """Generate structured insights for an article."""
        self._ensure_enabled()

        text_chunks = [f"Title: {article.title}"]
        if article.description:
            text_chunks.append(f"Description: {article.description}")
        if article.content:
            clean_content = article.content.replace("\n", " ").strip()
            if len(clean_content) > 1500:
                clean_content = clean_content[:1500] + "..."
            text_chunks.append(f"Body: {clean_content}")

        article_context = "\n".join(text_chunks)

        prompt = f"""
You are assisting a news analyst. Read the article below and respond in JSON.

Article:
{article_context}

Return JSON with the following fields:
- summary: A concise 3-4 sentence summary tailored for busy professionals.
- key_points: Array of 3-5 bullet points highlighting facts or implications.
- reliability_score: Float 0.0-1.0 indicating likely reliability.
- reliability_label: One of ["Highly Reliable", "Reliable", "Mixed Signals", "Unverified", "Questionable"].
- reliability_reason: Short justification referencing sourcing, tone, or factual grounding.
- tone: Qualitative assessment of tone (e.g., "neutral analysis", "strong opinion").
- suggested_actions: Array of up to 3 actionable follow-ups (can be empty).

Ensure the response is valid JSON.
"""

        try:
            if not self.client:
                raise LLMContentError("LLM client not initialized")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3,
            )
            content = response.choices[0].message.content if response.choices else None
        except Exception as exc:  # pragma: no cover - network failure
            return self._fallback_insights(article, error=str(exc))

        if not content:
            return self._fallback_insights(article, error="empty_response")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return self._fallback_insights(article, error="invalid_json")

        return {
            "summary": parsed.get("summary", "") or self._build_summary(article),
            "key_points": parsed.get("key_points", []) or self._build_key_points(article),
            "reliability_score": parsed.get(
                "reliability_score", self._estimate_reliability(article)
            ),
            "reliability_label": parsed.get("reliability_label")
            or self._reliability_label(self._estimate_reliability(article)),
            "reliability_reason": parsed.get("reliability_reason")
            or self._default_reliability_reason(article),
            "tone": parsed.get("tone") or self._estimate_tone(article),
            "suggested_actions": parsed.get("suggested_actions", [])
            or self._suggest_actions(article),
        }

    def _fallback_insights(self, article: Article, error: str | None = None) -> dict[str, Any]:
        score = self._estimate_reliability(article)
        return {
            "summary": self._build_summary(article),
            "key_points": self._build_key_points(article),
            "reliability_score": score,
            "reliability_label": self._reliability_label(score),
            "reliability_reason": self._default_reliability_reason(article, error),
            "tone": self._estimate_tone(article),
            "suggested_actions": self._suggest_actions(article),
        }

    def _build_summary(self, article: Article) -> str:
        text = article.description or article.content or article.title
        if not text:
            return "Summary unavailable."
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        return ". ".join(sentences[:3]) + ("." if sentences else "")

    def _build_key_points(self, article: Article) -> list[str]:
        text = article.description or article.content or ""
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        return sentences[:4]

    def _estimate_reliability(self, article: Article) -> float:
        score = 0.6
        if article.readability_label and article.readability_label in {
            "Standard",
            "Fairly Easy",
            "Easy",
            "Very Easy",
        }:
            score += 0.1
        if article.sentiment_score is not None:
            if abs(article.sentiment_score) <= 0.2:
                score += 0.1
            elif abs(article.sentiment_score) > 0.5:
                score -= 0.1
        return max(0.0, min(1.0, score))

    def _reliability_label(self, score: float) -> str:
        if score >= 0.85:
            return "Highly Reliable"
        if score >= 0.7:
            return "Reliable"
        if score >= 0.5:
            return "Mixed Signals"
        if score >= 0.3:
            return "Unverified"
        return "Questionable"

    def _estimate_tone(self, article: Article) -> str:
        if article.sentiment_score is None:
            return "Neutral/Informational"
        if article.sentiment_score > 0.35:
            return "Positive/Upbeat"
        if article.sentiment_score < -0.35:
            return "Critical/Concerned"
        return "Neutral analysis"

    def _default_reliability_reason(self, article: Article, error: str | None = None) -> str:
        parts = []
        if article.author:
            parts.append(f"Authored by {article.author}")
        if article.readability_label:
            parts.append(f"Readability: {article.readability_label}")
        if error:
            parts.append("Generated via offline heuristics")
        return "; ".join(parts) or "Heuristic assessment based on metadata"

    def _suggest_actions(self, article: Article) -> list[str]:
        actions: list[str] = []
        if article.cluster_id is not None:
            actions.append("Compare with other articles in this cluster")
        if article.sentiment_score is not None and abs(article.sentiment_score) > 0.5:
            actions.append("Check additional sources to balance sentiment")
        if article.readability_label in {"Very Difficult", "Difficult"}:
            actions.append("Consider a quick summary before deep reading")
        return actions
