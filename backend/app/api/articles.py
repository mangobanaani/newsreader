"""Article endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.base import get_db
from app.models.feed import Article
from app.models.user import User
from app.schemas.feed import Article as ArticleSchema
from app.schemas.feed import ArticleLLMInsights, ArticleWithRecommendation
from app.services.nlp_processor import NLPProcessor
from app.services.recommendation_engine import RecommendationEngine
from app.services.llm_insights import (
    LLMContentError,
    LLMFeatureDisabledError,
    LLMInsightService,
)
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=list[ArticleSchema])
def list_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    bookmarked_only: bool = False,
    topic: str | None = None,
    min_sentiment: float | None = None,
    max_sentiment: float | None = None,
    sort_by: str = "date",  # date, sentiment
) -> list[Article]:
    """List user's articles with optional filtering."""
    from app.models.feed import UserPreference

    query = db.query(Article).join(Article.feed).filter(Article.feed.has(user_id=current_user.id))

    if unread_only:
        query = query.filter(Article.is_read.is_(False))

    if bookmarked_only:
        query = query.filter(Article.is_bookmarked.is_(True))

    # Sentiment filtering
    if min_sentiment is not None:
        query = query.filter(Article.sentiment_score >= min_sentiment)

    if max_sentiment is not None:
        query = query.filter(Article.sentiment_score <= max_sentiment)

    # Topic filtering (check if topic JSON contains the string)
    if topic:
        query = query.filter(Article.topics.like(f'%"{topic}"%'))

    # Sorting
    if sort_by == "sentiment":
        query = query.filter(Article.sentiment_score.isnot(None)).order_by(
            Article.sentiment_score.desc()
        )
    else:  # default to date
        query = query.order_by(Article.published_date.desc())

    articles = query.offset(skip).limit(limit).all()

    # Apply word filter from user preferences
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if prefs and prefs.excluded_words:
        filtered_articles = []
        for article in articles:
            text = f"{article.title} {article.description or ''}".lower()
            if not any(word.lower() in text for word in prefs.excluded_words):
                filtered_articles.append(article)
        return filtered_articles

    return articles


@router.get("/recommendations", response_model=list[ArticleWithRecommendation])
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
) -> list[ArticleWithRecommendation]:
    """Get personalized article recommendations."""
    engine = RecommendationEngine(db)
    recommendations = await engine.get_recommendations(current_user.id, limit)

    result = []
    for article, score, reason in recommendations:
        article_dict = ArticleSchema.model_validate(article).model_dump()
        article_dict["recommendation_score"] = score
        article_dict["recommendation_reason"] = reason
        result.append(ArticleWithRecommendation(**article_dict))

    return result


@router.get("/{article_id}", response_model=ArticleSchema)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Article:
    """Get article by ID."""
    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    return article


@router.get("/{article_id}/llm-insights", response_model=ArticleLLMInsights)
def get_article_llm_insights(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ArticleLLMInsights:
    """Get AI-generated insights for a specific article."""
    if not settings.ENABLE_LLM_FEATURES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="LLM features are disabled")

    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    service = LLMInsightService()
    try:
        payload = service.generate_insights(article)
    except LLMFeatureDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except LLMContentError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ArticleLLMInsights(**payload)


@router.post("/{article_id}/read", response_model=ArticleSchema)
def mark_as_read(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Article:
    """Mark article as read."""
    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.is_read = True
    db.commit()
    db.refresh(article)

    return article


@router.post("/{article_id}/bookmark", response_model=ArticleSchema)
def toggle_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Article:
    """Toggle article bookmark status."""
    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.is_bookmarked = not article.is_bookmarked
    db.commit()
    db.refresh(article)

    return article


@router.post("/{article_id}/rate", response_model=ArticleSchema)
def rate_article(
    article_id: int,
    rating: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Article:
    """Rate an article (0.0 - 5.0)."""
    if not 0.0 <= rating <= 5.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0.0 and 5.0",
        )

    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.user_rating = rating
    db.commit()
    db.refresh(article)

    return article


@router.post("/{article_id}/process", response_model=ArticleSchema)
def process_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Article:
    """Process article with NLP (generate embeddings, topics, etc.)."""
    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    processor = NLPProcessor(db)
    processor.process_article(article)

    db.refresh(article)
    return article


@router.post("/process-all", response_model=dict[str, int | str])
def process_all_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int | str]:
    """Process all articles with NLP (embeddings, sentiment, topics)."""
    processor = NLPProcessor(db)
    result = processor.process_all_articles(current_user.id)

    return result


@router.post("/cluster", response_model=dict[str, int])
def cluster_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int]:
    """Cluster all articles using NLP."""
    processor = NLPProcessor(db)
    num_clusters = processor.cluster_articles(current_user.id)

    return {"clusters": num_clusters}


@router.get("/{article_id}/similar", response_model=list[ArticleSchema])
def get_similar_articles(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 10,
) -> list[Article]:
    """Get similar articles based on content similarity."""
    article = (
        db.query(Article)
        .join(Article.feed)
        .filter(Article.id == article_id, Article.feed.has(user_id=current_user.id))
        .first()
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    processor = NLPProcessor(db)
    similar = processor.find_similar_articles(article, limit)

    return [art for art, _ in similar]


@router.get("/topics/all", response_model=dict[str, int])
def get_all_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int]:
    """Get all topics with article counts."""
    articles = (
        db.query(Article)
        .join(Article.feed)
        .filter(
            Article.feed.has(user_id=current_user.id),
            Article.topics.isnot(None)
        )
        .all()
    )

    topic_counts: dict[str, int] = {}
    for article in articles:
        if article.topics:
            for topic in article.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # Sort by count descending
    sorted_topics = dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    return sorted_topics


@router.get("/analytics/sentiment", response_model=dict[str, int | dict[str, int]])
def get_sentiment_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int | dict[str, int]]:
    """Get sentiment distribution and trends over time."""
    articles = (
        db.query(Article)
        .join(Article.feed)
        .filter(
            Article.feed.has(user_id=current_user.id),
            Article.sentiment_score.isnot(None)
        )
        .all()
    )

    sentiment_counts = {
        "positive": 0,
        "slightly_positive": 0,
        "neutral": 0,
        "slightly_negative": 0,
        "negative": 0,
        "total": len(articles)
    }

    # Daily sentiment trends (last 7 days)
    from datetime import datetime, timedelta
    from collections import defaultdict

    daily_sentiment: dict[str, dict[str, int]] = defaultdict(lambda: {
        "positive": 0, "neutral": 0, "negative": 0
    })

    for article in articles:
        score = article.sentiment_score

        # Categorize sentiment
        if score >= 0.5:
            sentiment_counts["positive"] += 1
        elif score >= 0.05:
            sentiment_counts["slightly_positive"] += 1
        elif score <= -0.5:
            sentiment_counts["negative"] += 1
        elif score <= -0.05:
            sentiment_counts["slightly_negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

        # Daily trends
        if article.published_date:
            date_key = article.published_date.strftime("%Y-%m-%d")
            if score >= 0.05:
                daily_sentiment[date_key]["positive"] += 1
            elif score <= -0.05:
                daily_sentiment[date_key]["negative"] += 1
            else:
                daily_sentiment[date_key]["neutral"] += 1

    # Convert defaultdict to regular dict
    sentiment_counts["daily_trends"] = dict(daily_sentiment)

    return sentiment_counts


@router.get("/analytics/topics", response_model=dict[str, list[dict[str, str | int]]])
def get_topic_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 7,
) -> dict[str, list[dict[str, str | int]]]:
    """Get topic trends over time."""
    from datetime import datetime, timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    articles = (
        db.query(Article)
        .join(Article.feed)
        .filter(
            Article.feed.has(user_id=current_user.id),
            Article.topics.isnot(None),
            Article.published_date >= cutoff_date
        )
        .all()
    )

    # Track topics over time
    topic_timeline: dict[str, list[str]] = {}

    for article in articles:
        if article.topics and article.published_date:
            date_key = article.published_date.strftime("%Y-%m-%d")
            for topic in article.topics[:5]:  # Top 5 topics per article
                if topic not in topic_timeline:
                    topic_timeline[topic] = []
                topic_timeline[topic].append(date_key)

    # Calculate trending topics
    trending: list[dict[str, str | int]] = []
    for topic, dates in topic_timeline.items():
        trending.append({
            "topic": topic,
            "count": len(dates),
            "growth": len([d for d in dates if d >= (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")])
        })

    # Sort by recent growth
    trending.sort(key=lambda x: x["growth"], reverse=True)

    return {"trending_topics": trending[:20]}


@router.get("/analytics/clusters", response_model=dict[str, list[dict[str, int | list[int]]]])
def get_cluster_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, list[dict[str, int | list[int]]]]:
    """Get article cluster information."""
    articles = (
        db.query(Article)
        .join(Article.feed)
        .filter(
            Article.feed.has(user_id=current_user.id),
            Article.cluster_id.isnot(None)
        )
        .all()
    )

    # Group by cluster
    clusters: dict[int, list[int]] = {}
    for article in articles:
        cluster_id = article.cluster_id
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(article.id)

    # Format response
    cluster_data = [
        {"cluster_id": cid, "article_count": len(articles), "article_ids": articles[:10]}
        for cid, articles in clusters.items()
    ]

    cluster_data.sort(key=lambda x: x["article_count"], reverse=True)

    return {"clusters": cluster_data}


@router.get("/export/csv")
def export_articles_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    topic: str | None = None,
    min_sentiment: float | None = None,
    max_sentiment: float | None = None,
):
    """Export articles as CSV."""
    from fastapi.responses import StreamingResponse
    import csv
    from io import StringIO

    # Build query with same filters as list endpoint
    query = db.query(Article).join(Article.feed).filter(Article.feed.has(user_id=current_user.id))

    if min_sentiment is not None:
        query = query.filter(Article.sentiment_score >= min_sentiment)
    if max_sentiment is not None:
        query = query.filter(Article.sentiment_score <= max_sentiment)
    if topic:
        query = query.filter(Article.topics.like(f'%"{topic}"%'))

    articles = query.order_by(Article.published_date.desc()).all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["ID", "Title", "Link", "Author", "Published Date", "Sentiment Score", "Topics", "Is Read", "Is Bookmarked"])

    # Rows
    for article in articles:
        topics_str = "; ".join(article.topics) if article.topics else ""

        writer.writerow([
            article.id,
            article.title,
            article.link,
            article.author or "",
            article.published_date.isoformat() if article.published_date else "",
            article.sentiment_score if article.sentiment_score is not None else "",
            topics_str,
            article.is_read,
            article.is_bookmarked
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=articles.csv"}
    )


@router.get("/export/json")
def export_articles_json(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    topic: str | None = None,
    min_sentiment: float | None = None,
    max_sentiment: float | None = None,
):
    """Export articles as JSON."""
    from fastapi.responses import StreamingResponse

    # Build query with same filters
    query = db.query(Article).join(Article.feed).filter(Article.feed.has(user_id=current_user.id))

    if min_sentiment is not None:
        query = query.filter(Article.sentiment_score >= min_sentiment)
    if max_sentiment is not None:
        query = query.filter(Article.sentiment_score <= max_sentiment)
    if topic:
        query = query.filter(Article.topics.like(f'%"{topic}"%'))

    articles = query.order_by(Article.published_date.desc()).all()

    # Convert to dict
    articles_data = []
    for article in articles:
        articles_data.append({
            "id": article.id,
            "title": article.title,
            "link": article.link,
            "description": article.description,
            "author": article.author,
            "published_date": article.published_date.isoformat() if article.published_date else None,
            "sentiment_score": article.sentiment_score,
            "topics": article.topics,
            "is_read": article.is_read,
            "is_bookmarked": article.is_bookmarked
        })

    json_str = json.dumps({"articles": articles_data, "count": len(articles_data)}, indent=2)

    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=articles.json"}
    )
