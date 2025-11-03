"""Authentication endpoints."""

from datetime import timedelta
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate

router = APIRouter()

# Initialize OAuth
oauth = OAuth()

# Configure Google OAuth
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register new user - DISABLED for security.

    Registration is disabled. Use the seed_db.py script to create users.
    This endpoint is kept for API compatibility but will always return 403.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Public registration is disabled. Contact administrator to create an account.",
    )


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> dict[str, str]:
    """Login user and return access token."""
    print(f"[DEBUG] Login attempt - username: {form_data.username}, password length: {len(form_data.password)}")

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        print(f"[DEBUG] User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"[DEBUG] User found: {user.email}, checking password...")
    password_ok = verify_password(form_data.password, user.hashed_password)
    print(f"[DEBUG] Password verification result: {password_ok}")

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/google/login")
async def google_login(request: Request) -> RedirectResponse:
    """Initiate Google OAuth login flow."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    """Handle Google OAuth callback."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )

        email = user_info.get("email")
        google_id = user_info.get("sub")
        picture = user_info.get("picture")

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Google ID not provided",
            )

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Update OAuth info if user exists
            user.oauth_provider = "google"
            user.oauth_id = google_id
            if picture:
                user.picture = picture
        else:
            # Create new user with OAuth
            user = User(
                email=email,
                hashed_password=None,  # OAuth users don't have passwords
                oauth_provider="google",
                oauth_id=google_id,
                picture=picture,
                is_active=True,
                is_superuser=False,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)

        # Redirect to frontend with token
        frontend_url = settings.BACKEND_CORS_ORIGINS[0]
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={access_token}")

    except Exception as e:
        print(f"[ERROR] Google OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}",
        )
