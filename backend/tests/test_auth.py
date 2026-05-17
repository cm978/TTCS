from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings
from app.models.user import User


def register_payload(email: str = "moon@example.com") -> dict[str, str]:
    return {
        "email": email,
        "password": "SecurePass123!",
        "display_name": "Moon",
    }


def test_register_creates_user_and_hides_password(client, db_session):
    response = client.post("/api/v1/auth/register", json=register_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "moon@example.com"
    assert "password" not in body
    assert "hashed_password" not in body

    user = db_session.query(User).filter_by(email="moon@example.com").one()
    assert user.hashed_password != "SecurePass123!"
    assert user.hashed_password.startswith("$2")


def test_register_rejects_duplicate_email(client):
    assert client.post("/api/v1/auth/register", json=register_payload()).status_code == 201

    response = client.post("/api/v1/auth/register", json=register_payload())

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_register_rejects_invalid_payload(client):
    response = client.post("/api/v1/auth/register", json={"email": "bad", "password": "short"})

    assert response.status_code == 422


def test_login_returns_bearer_token_for_valid_credentials(client):
    client.post("/api/v1/auth/register", json=register_payload())

    response = client.post("/api/v1/auth/login", json={"email": "moon@example.com", "password": "SecurePass123!"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == 86400
    assert body["user"]["email"] == "moon@example.com"
    assert "hashed_password" not in body["user"]


def test_login_rejects_invalid_credentials(client):
    client.post("/api/v1/auth/register", json=register_payload())

    response = client.post("/api/v1/auth/login", json={"email": "moon@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_requires_valid_bearer_token(client):
    client.post("/api/v1/auth/register", json=register_payload())
    login = client.post("/api/v1/auth/login", json={"email": "moon@example.com", "password": "SecurePass123!"})
    token = login.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "moon@example.com"


def test_me_rejects_missing_or_malformed_token(client):
    missing = client.get("/api/v1/auth/me")
    malformed = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"})

    assert missing.status_code == 401
    assert malformed.status_code == 401


def test_me_rejects_expired_token(client):
    client.post("/api/v1/auth/register", json=register_payload())
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401

