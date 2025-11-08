import os
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

# Point the application to an isolated test database before importing the app.
os.environ.setdefault("COMPANIONAI_DATABASE_URL", "sqlite+aiosqlite:///./test_companionai.db")

from backend.app.main import app  # noqa: E402  (import after env var set)

TEST_DB_PATH = Path("test_companionai.db")


@pytest.fixture
def client():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    with TestClient(app) as client:
        yield client
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def register_and_login(client: TestClient, email: str = "user@example.com", password: str = "Secret123!") -> str:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "display_name": "Test User"},
    )
    assert response.status_code == 201, response.text

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    return token


def test_full_chat_flow_persists_history_and_mood(client: TestClient) -> None:
    token = register_and_login(client)
    auth_header = {"Authorization": f"Bearer {token}"}

    profile_response = client.get("/users/me", headers=auth_header)
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "user@example.com"

    chat_payload = {"message": "Hello friend, I am feeling great today!"}
    chat_response = client.post("/chat/respond", json=chat_payload, headers=auth_header)
    assert chat_response.status_code == 200
    chat_data = chat_response.json()
    assert chat_data["reply"]
    assert chat_data["sentiment"] == "positive"
    assert chat_data["mood"] == "uplifted"

    history_response = client.get("/chat/history", headers=auth_header)
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 2  # user message + AI reply
    assert history[0]["sender"] == "user"
    assert history[1]["sender"] == "ai"

    mood_response = client.get("/mood/entries", headers=auth_header)
    assert mood_response.status_code == 200
    moods = mood_response.json()
    assert len(moods) == 1
    assert moods[0]["mood"] == "uplifted"


def test_chat_when_history_disabled(client: TestClient) -> None:
    token = register_and_login(client, email="guest@example.com")
    auth_header = {"Authorization": f"Bearer {token}"}

    settings_response = client.patch("/users/me", json={"history_enabled": False}, headers=auth_header)
    assert settings_response.status_code == 200
    assert settings_response.json()["history_enabled"] is False

    chat_response = client.post(
        "/chat/respond",
        json={"message": "This is a neutral update."},
        headers=auth_header,
    )
    assert chat_response.status_code == 200
    chat_data = chat_response.json()
    assert chat_data["mood"] == "calm"

    history_response = client.get("/chat/history", headers=auth_header)
    assert history_response.status_code == 200
    assert history_response.json() == []

    mood_response = client.get("/mood/entries", headers=auth_header)
    assert mood_response.status_code == 200
    assert mood_response.json() == []
