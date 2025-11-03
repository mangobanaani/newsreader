"""User preferences endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.base import get_db
from app.models.feed import UserPreference
from app.models.user import User
from app.schemas.feed import UserPreference as UserPreferenceSchema
from app.schemas.feed import UserPreferenceUpdate

router = APIRouter()


@router.get("/", response_model=UserPreferenceSchema)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserPreference:
    """Get user preferences."""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    if not preferences:
        # Create default preferences
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


@router.put("/", response_model=UserPreferenceSchema)
def update_preferences(
    preferences_in: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserPreference:
    """Update user preferences."""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    if not preferences:
        # Create new preferences
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)

    update_data = preferences_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)

    return preferences
