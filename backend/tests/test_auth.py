"""Test authentication endpoints."""

from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration - should be disabled."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "newpassword"},
    )
    # Registration is disabled for security, should return 403
    assert response.status_code == 403
    data = response.json()
    assert "disabled" in data["detail"].lower()


def test_register_duplicate_user(client: TestClient, test_user):
    """Test registering duplicate user - should be disabled."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": test_user.email, "password": "password"},
    )
    # Registration is disabled for security, should return 403
    assert response.status_code == 403


def test_login(client: TestClient, test_user):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_wrong_password(client: TestClient, test_user):
    """Test login with correct email but wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_missing_credentials(client: TestClient):
    """Test login with missing credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={},
    )
    assert response.status_code == 422  # Validation error
