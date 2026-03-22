import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_email():
    return f"{uuid.uuid4().hex[:8]}@example.com"


def inspection_payload(
    location_code: str = "A9-KM-143",
    damage_type: str = "pothole",
    severity: str = "high",
    status: str = "reported",
    notes: str = "Large pothole near right lane",
):
    return {
        "location_code": location_code,
        "damage_type": damage_type,
        "severity": severity,
        "status": status,
        "notes": notes,
    }


def test_register_login_and_create_inspection():
    email = unique_email()
    password = "test123"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code in [200, 201]

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/inspections",
        json=inspection_payload(),
        headers=headers,
    )
    assert response.status_code == 201

    data = response.json()
    assert data["location_code"] == "A9-KM-143"
    assert data["damage_type"] == "pothole"
    assert data["severity"] == "high"
    assert data["status"] == "reported"

    response = client.get("/inspections", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_user_cannot_see_another_users_inspections():
    password = "test123"

    email1 = unique_email()
    email2 = unique_email()

    response = client.post(
        "/auth/register",
        json={
            "email": email1,
            "password": password,
        },
    )
    assert response.status_code in [200, 201]

    response = client.post(
        "/auth/login",
        data={
            "username": email1,
            "password": password,
        },
    )
    assert response.status_code == 200

    token1 = response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    response = client.post(
        "/inspections",
        json=inspection_payload(location_code="B2-KM-010"),
        headers=headers1,
    )
    assert response.status_code == 201

    inspection_id = response.json()["id"]

    response = client.post(
        "/auth/register",
        json={
            "email": email2,
            "password": password,
        },
    )
    assert response.status_code in [200, 201]

    response = client.post(
        "/auth/login",
        data={
            "username": email2,
            "password": password,
        },
    )
    assert response.status_code == 200

    token2 = response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    response = client.get("/inspections", headers=headers2)
    assert response.status_code == 200

    data = response.json()
    assert all(item["id"] != inspection_id for item in data["items"])

    response = client.get(f"/inspections/{inspection_id}", headers=headers2)
    assert response.status_code == 404


def test_update_inspection():
    email = unique_email()
    password = "test123"

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code in [200, 201]

    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/inspections",
        json=inspection_payload(),
        headers=headers,
    )
    assert response.status_code == 201

    inspection_id = response.json()["id"]

    response = client.put(
        f"/inspections/{inspection_id}",
        json={
            "location_code": "A9-KM-143",
            "damage_type": "pothole",
            "severity": "low",
            "status": "reported",
            "notes": "temporary patch applied",
        },
        headers=headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["severity"] == "low"
    assert data["notes"] == "temporary patch applied"


def test_delete_inspection():
    email = unique_email()
    password = "test123"

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code in [200, 201]

    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/inspections",
        json=inspection_payload(location_code="C5-KM-200"),
        headers=headers,
    )
    assert response.status_code == 201

    inspection_id = response.json()["id"]

    response = client.delete(
        f"/inspections/{inspection_id}",
        headers=headers,
    )
    assert response.status_code == 204

    response = client.get(f"/inspections/{inspection_id}", headers=headers)
    assert response.status_code == 404