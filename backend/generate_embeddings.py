#!/usr/bin/env python3
"""Generate embeddings for all articles."""

import os
import sys
import json

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./dev.db'
os.environ['SECRET_KEY'] = 'test-key'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer

# Create database session
DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Load sentence transformer model
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model loaded!")

# Get articles without embeddings
result = db.execute(
    text("""
        SELECT a.id, a.title, a.description
        FROM articles a
        JOIN feeds f ON a.feed_id = f.id
        WHERE f.user_id = 1 AND (a.embedding IS NULL OR a.embedding = '')
    """)
)

articles = result.fetchall()
print(f"\nGenerating embeddings for {len(articles)} articles...")

processed = 0
for article in articles:
    article_id, title, description = article
    text_content = f"{title}. {description or ''}"

    # Generate embedding
    embedding = model.encode(text_content)
    embedding_json = json.dumps(embedding.tolist())

    # Update database
    db.execute(
        text("""
            UPDATE articles
            SET embedding = :embedding
            WHERE id = :id
        """),
        {"embedding": embedding_json, "id": article_id}
    )

    processed += 1
    if processed % 10 == 0:
        db.commit()
        print(f"  Processed {processed}/{len(articles)} articles...")

# Final commit
db.commit()
print(f"\n✓ Successfully generated embeddings for {len(articles)} articles!")
db.close()
