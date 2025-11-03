"""User schemas for API validation."""

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserUpdate(BaseModel):
    """User update schema."""

    email: EmailStr | None = None
    password: str | None = None


class UserInDB(UserBase):
    """User schema as stored in database."""

    id: int
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}


class User(UserInDB):
    """Public user schema."""

    pass


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: int | None = None
