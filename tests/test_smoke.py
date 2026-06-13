import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/inspection_demo.db")
os.environ.setdefault("SECRET_KEY", "smoke-test-secret")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def unique_email() -> str:
    return f"{uuid.uuid4().hex[:8]}@example.com"


def register_and_login(email: str | None = None, password: str = "Test123!") -> dict:
    email = email or unique_email()

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Smoke Test User",
        },
    )
    assert register_response.status_code in (200, 201), register_response.text

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json().get("access_token")
    assert token, login_response.text
    return {"email": email, "password": password, "token": token}


def inspection_payload(
    location_code: str = "A9-KM-143",
    damage_type: str = "pothole",
    severity: str = "high",
    notes: str = "Large pothole near right lane",
) -> dict:
    return {
        "location_code": location_code,
        "damage_type": damage_type,
        "severity": severity,
        "notes": notes,
    }


@pytest.mark.smoke
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.smoke
def test_auth_and_inspection_roundtrip():
    session = register_and_login()
    headers = {"Authorization": f"Bearer {session['token']}"}

    create_response = client.post(
        "/inspections",
        json=inspection_payload(),
        headers=headers,
    )
    assert create_response.status_code in (200, 201), create_response.text

    created = create_response.json()
    inspection_id = created.get("id")
    assert inspection_id, create_response.text

    list_response = client.get("/inspections", headers=headers)
    assert list_response.status_code == 200, list_response.text
    payload = list_response.json()
    assert isinstance(payload, dict) and "items" in payload
    assert any(item.get("id") == inspection_id for item in payload["items"])

    get_response = client.get(f"/inspections/{inspection_id}", headers=headers)
    assert get_response.status_code == 200, get_response.text
    assert get_response.json().get("id") == inspection_id
