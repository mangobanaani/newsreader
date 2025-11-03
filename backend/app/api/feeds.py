"""Feed management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.base import get_db
from app.models.feed import Feed
from app.models.user import User
from app.schemas.feed import Feed as FeedSchema
from app.schemas.feed import FeedCreate, FeedUpdate
from app.services.rss_fetcher import RSSFetcher

router = APIRouter()


@router.get("/", response_model=list[FeedSchema])
def list_feeds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> list[Feed]:
    """List user's feeds."""
    feeds = db.query(Feed).filter(Feed.user_id == current_user.id).offset(skip).limit(limit).all()
    return feeds


@router.post("/", response_model=FeedSchema, status_code=status.HTTP_201_CREATED)
def create_feed(
    feed_in: FeedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Feed:
    """Create new feed."""
    # Check if feed already exists for this user
    existing = (
        db.query(Feed).filter(Feed.url == str(feed_in.url), Feed.user_id == current_user.id).first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feed already exists",
        )

    feed = Feed(
        url=str(feed_in.url),
        title=feed_in.title,
        description=feed_in.description,
        user_id=current_user.id,
    )
    db.add(feed)
    db.commit()
    db.refresh(feed)

    return feed


@router.get("/{feed_id}", response_model=FeedSchema)
def get_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Feed:
    """Get feed by ID."""
    feed = db.query(Feed).filter(Feed.id == feed_id, Feed.user_id == current_user.id).first()

    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    return feed


@router.put("/{feed_id}", response_model=FeedSchema)
def update_feed(
    feed_id: int,
    feed_in: FeedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Feed:
    """Update feed."""
    feed = db.query(Feed).filter(Feed.id == feed_id, Feed.user_id == current_user.id).first()

    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    update_data = feed_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feed, field, value)

    db.commit()
    db.refresh(feed)

    return feed


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete feed."""
    feed = db.query(Feed).filter(Feed.id == feed_id, Feed.user_id == current_user.id).first()

    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    db.delete(feed)
    db.commit()


@router.post("/{feed_id}/refresh", response_model=dict[str, int])
async def refresh_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int]:
    """Refresh feed and fetch new articles."""
    feed = db.query(Feed).filter(Feed.id == feed_id, Feed.user_id == current_user.id).first()

    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    fetcher = RSSFetcher(db)
    new_articles = await fetcher.update_feed(feed)

    return {"new_articles": len(new_articles)}


@router.post("/refresh-all", response_model=dict[str, int])
async def refresh_all_feeds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int]:
    """Refresh all user's feeds."""
    fetcher = RSSFetcher(db)
    result = await fetcher.update_all_feeds(current_user.id)

    return result
