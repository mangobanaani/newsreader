"""Simple tests that don't require database."""


def test_imports():
    """Test that main modules can be imported."""
    from app.core.config import settings

    # Test settings
    assert settings.PROJECT_NAME == "News Reader API"
    assert settings.VERSION == "1.0.0"


def test_schemas():
    """Test Pydantic schemas."""
    from app.schemas.user import UserCreate

    user_data = {"email": "test@example.com", "password": "testpass"}
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.password == "testpass"
