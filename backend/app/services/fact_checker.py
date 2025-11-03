"""Fact-checking service using LLM and external APIs."""

import json
from typing import Any

import anthropic
import httpx
import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.feed import Article


class FactChecker:
    """Fact-checking service for articles."""

    def __init__(self, db: Session):
        """Initialize fact checker."""
        self.db = db
        self.provider = settings.DEFAULT_LLM_PROVIDER
        self.enabled = settings.ENABLE_LLM_FEATURES

        if not self.enabled:
            self.provider = "disabled"
            return

        if self.provider == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.LLM_MODEL_OPENAI
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.LLM_MODEL_ANTHROPIC

    async def extract_claims(self, article: Article) -> list[dict[str, Any]]:
        """Extract factual claims from article."""
        if not self.enabled or self.provider == "disabled":
            return []

        text = f"{article.title}\n\n{article.content or article.description or ''}"

        prompt = f"""Extract specific factual claims from this article that can be verified. Focus on:
- Statistics and numbers
- Dates and events
- Quotes from named sources
- Product launches or announcements
- Scientific findings

Article:
{text[:2000]}

Extract claims in JSON format:
[{{"claim": "...", "category": "statistic|date|quote|announcement|finding", "importance": "high|medium|low"}}]"""

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text
            else:  # openai
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3,
                )
                content = response.choices[0].message.content or "[]"

            claims = json.loads(content)
            return claims if isinstance(claims, list) else []

        except Exception as e:
            return [{"error": str(e)}]

    async def verify_claim(self, claim: str) -> dict[str, Any]:
        """Verify a single claim using LLM and web search."""
        result = {
            "claim": claim,
            "verdict": "unknown",  # true, false, misleading, unknown
            "confidence": 0.0,
            "explanation": "",
            "sources": [],
        }

        # Step 1: LLM pre-check
        if self.enabled and self.provider != "disabled":
            llm_assessment = await self._llm_fact_check(claim)
            result.update(llm_assessment)

        # Step 2: Web search verification (if available)
        # This would use Google Fact Check API, Bing, or other sources
        # web_results = await self._web_search_verification(claim)

        return result

    async def _llm_fact_check(self, claim: str) -> dict[str, Any]:
        """Use LLM for initial fact assessment."""
        if not self.enabled or self.provider == "disabled":
            return {
                "verdict": "needs_verification",
                "confidence": 0.0,
                "explanation": "LLM fact checking is disabled",
                "red_flags": [],
                "context_needed": [],
            }

        prompt = f"""Analyze this claim for factual accuracy. Consider:
1. Is the claim verifiable?
2. Does it align with known facts?
3. Are there any red flags or misleading elements?
4. What additional context is needed?

Claim: {claim}

Respond in JSON:
{{
    "verdict": "likely_true|likely_false|misleading|needs_verification|opinion",
    "confidence": 0.0-1.0,
    "explanation": "...",
    "red_flags": ["..."],
    "context_needed": ["..."]
}}"""

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text
            else:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3,
                )
                content = response.choices[0].message.content or "{}"

            return json.loads(content)

        except Exception as e:
            return {
                "verdict": "error",
                "confidence": 0.0,
                "explanation": f"Error: {str(e)}",
            }

    async def _web_search_verification(self, claim: str) -> list[dict[str, Any]]:
        """Search web for claim verification."""
        # This would integrate with:
        # - Google Fact Check Tools API
        # - News API
        # - Academic databases
        # - Wikipedia API

        sources = []

        # Example: Use DuckDuckGo or similar
        try:
            async with httpx.AsyncClient() as client:
                # Simplified search - in production use proper APIs
                search_url = f"https://api.duckduckgo.com/?q={claim}&format=json"
                response = await client.get(search_url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    # Parse and extract relevant information
                    sources.append(
                        {
                            "source": "DuckDuckGo",
                            "summary": data.get("Abstract", ""),
                            "url": data.get("AbstractURL", ""),
                        }
                    )
        except Exception:
            pass

        return sources

    async def check_article(self, article: Article) -> dict[str, Any]:
        """Comprehensive fact check of entire article."""
        # Extract claims
        claims = await self.extract_claims(article)

        # Verify each claim
        verified_claims = []
        for claim_data in claims:
            if "claim" in claim_data:
                verification = await self.verify_claim(claim_data["claim"])
                verified_claims.append({**claim_data, **verification})

        # Overall assessment
        total_claims = len(verified_claims)
        if total_claims == 0:
            return {
                "overall_verdict": "insufficient_claims",
                "reliability_score": 0.5,
                "claims": [],
            }

        # Calculate reliability score
        true_count = sum(1 for c in verified_claims if c.get("verdict") == "likely_true")
        false_count = sum(1 for c in verified_claims if c.get("verdict") == "likely_false")

        reliability_score = (true_count - false_count * 2) / total_claims
        reliability_score = max(0.0, min(1.0, (reliability_score + 1) / 2))

        return {
            "overall_verdict": self._calculate_overall_verdict(verified_claims),
            "reliability_score": reliability_score,
            "total_claims": total_claims,
            "verified_claims": verified_claims,
            "summary": self._generate_summary(verified_claims),
        }

    def _calculate_overall_verdict(self, claims: list[dict[str, Any]]) -> str:
        """Calculate overall verdict from individual claims."""
        verdicts = [c.get("verdict", "unknown") for c in claims]

        if not verdicts:
            return "unknown"

        false_count = verdicts.count("likely_false") + verdicts.count("misleading")
        total = len(verdicts)

        if false_count / total > 0.3:
            return "mostly_false"
        elif false_count > 0:
            return "mixed"
        elif verdicts.count("likely_true") / total > 0.7:
            return "mostly_true"
        else:
            return "uncertain"

    def _generate_summary(self, claims: list[dict[str, Any]]) -> str:
        """Generate summary of fact check results."""
        if not claims:
            return "No verifiable claims found."

        true_count = sum(1 for c in claims if c.get("verdict") == "likely_true")
        false_count = sum(1 for c in claims if c.get("verdict") == "likely_false")
        misleading_count = sum(1 for c in claims if c.get("verdict") == "misleading")

        return f"Found {len(claims)} claims: {true_count} likely true, {false_count} likely false, {misleading_count} misleading."
