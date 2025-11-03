#!/usr/bin/env python3
"""Fix articles missing NLP processing."""

import sys
sys.path.insert(0, '/Users/pekka/Documents/newsreader/backend')

from app.db.base import SessionLocal
from app.services.nlp_processor import NLPProcessor
from app.models.feed import Article

def main():
    db = SessionLocal()
    try:
        processor = NLPProcessor(db)

        # Reprocess ALL articles to apply improved topic filtering
        print("Reprocessing all articles with improved topic extraction...")
        articles = (
            db.query(Article)
            .join(Article.feed)
            .filter(Article.feed.has(user_id=1))
            .all()
        )

        processed = 0
        for article in articles:
            try:
                processor.process_article(article)
                processed += 1
                if processed % 50 == 0:
                    print(f"  Processed {processed}/{len(articles)} articles...")
            except Exception as e:
                print(f"Error processing article {article.id}: {e}")
                continue

        print(f"✓ Reprocessed {processed} articles with improved topic extraction")

        # Also run clustering
        num_clusters = processor.cluster_articles(user_id=1)
        print(f"✓ Created {num_clusters} article clusters")

    finally:
        db.close()

if __name__ == "__main__":
    main()
