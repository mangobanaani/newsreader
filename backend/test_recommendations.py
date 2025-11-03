#!/usr/bin/env python3
"""Test recommendations engine."""

import sys
import asyncio
sys.path.insert(0, '/Users/pekka/Documents/newsreader/backend')

from app.db.base import SessionLocal
from app.services.recommendation_engine import RecommendationEngine

async def main():
    db = SessionLocal()
    try:
        print("Testing recommendation engine...")

        # Initialize engine (will fail if no API key, but fallback should work)
        try:
            engine = RecommendationEngine(db)
            print("✓ Recommendation engine initialized")
        except ValueError as e:
            print(f"✗ Could not initialize: {e}")
            print("\nRecommendations require either ANTHROPIC_API_KEY or OPENAI_API_KEY")
            print("The engine will use fallback embedding-based similarity instead")
            return

        # Get recommendations for user 1
        print("\nFetching recommendations for user 1...")
        recommendations = await engine.get_recommendations(user_id=1, limit=10)

        print(f"\n✓ Found {len(recommendations)} recommendations")

        if recommendations:
            print("\nTop 3 recommendations:")
            for i, (article, score, reason) in enumerate(recommendations[:3], 1):
                print(f"\n{i}. {article.title}")
                print(f"   Score: {score:.2f}")
                print(f"   Reason: {reason}")
        else:
            print("\n⚠ No recommendations found")
            print("This could be because:")
            print("  - No unread articles with embeddings")
            print("  - User preferences disabled")
            print("  - Min relevance score too high")
            print("  - No LLM API key configured")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
