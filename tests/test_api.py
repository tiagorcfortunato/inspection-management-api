import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User

client = TestClient(app)


def unique_email():
    return f"{uuid.uuid4().hex[:8]}@example.com"


def register_and_login_as_admin(email: str = None, password: str = "Test123!") -> dict:
    if email is None:
        email = unique_email()
    client.post("/auth/register", json={"email": email, "password": password})
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.role = "admin"
        db.commit()
    finally:
        db.close()
    response = client.post("/auth/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def register_and_login(email: str = None, password: str = "Test123!") -> dict:
    if email is None:
        email = unique_email()
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def inspection_payload(
    location_code: str = "A9-KM-143",
    damage_type: str = "pothole",
    severity: str = "high",
    notes: str = "Large pothole near right lane",
):
    return {
        "location_code": location_code,
        "damage_type": damage_type,
        "severity": severity,
        "notes": notes,
    }


# --- Auth ---

def test_register_and_login():
    email = unique_email()
    response = client.post("/auth/register", json={"email": email, "password": "test123"})
    assert response.status_code == 201

    response = client.post("/auth/login", data={"username": email, "password": "test123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_register_duplicate_email():
    email = unique_email()
    client.post("/auth/register", json={"email": email, "password": "test123"})
    response = client.post("/auth/register", json={"email": email, "password": "test123"})
    assert response.status_code == 400


def test_login_wrong_password():
    email = unique_email()
    client.post("/auth/register", json={"email": email, "password": "test123"})
    response = client.post("/auth/login", data={"username": email, "password": "wrongpassword"})
    assert response.status_code == 401


def test_unauthenticated_access():
    response = client.get("/inspections")
    assert response.status_code == 401


# --- Inspection CRUD ---

def test_create_inspection():
    headers = register_and_login()
    response = client.post("/inspections", json=inspection_payload(), headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["location_code"] == "A9-KM-143"
    assert data["damage_type"] == "pothole"
    assert data["severity"] == "high"
    assert data["status"] == "reported"


def test_list_inspections():
    headers = register_and_login()
    client.post("/inspections", json=inspection_payload(), headers=headers)
    response = client.get("/inspections", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_get_inspection_by_id():
    headers = register_and_login()
    response = client.post("/inspections", json=inspection_payload(), headers=headers)
    inspection_id = response.json()["id"]

    response = client.get(f"/inspections/{inspection_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == inspection_id


def test_update_inspection():
    headers = register_and_login()
    response = client.post("/inspections", json=inspection_payload(), headers=headers)
    assert response.status_code == 201
    inspection_id = response.json()["id"]

    response = client.put(
        f"/inspections/{inspection_id}",
        json={"severity": "low", "notes": "temporary patch applied"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "low"
    assert data["notes"] == "temporary patch applied"


def test_delete_inspection():
    headers = register_and_login()
    response = client.post("/inspections", json=inspection_payload(location_code="C5-KM-200"), headers=headers)
    assert response.status_code == 201
    inspection_id = response.json()["id"]

    response = client.delete(f"/inspections/{inspection_id}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/inspections/{inspection_id}", headers=headers)
    assert response.status_code == 404


# --- Data isolation ---

def test_user_cannot_see_another_users_inspections():
    headers1 = register_and_login()
    headers2 = register_and_login()

    response = client.post("/inspections", json=inspection_payload(location_code="B2-KM-010"), headers=headers1)
    assert response.status_code == 201
    inspection_id = response.json()["id"]

    response = client.get("/inspections", headers=headers2)
    assert response.status_code == 200
    assert all(item["id"] != inspection_id for item in response.json()["items"])

    response = client.get(f"/inspections/{inspection_id}", headers=headers2)
    assert response.status_code == 404


def test_cannot_update_another_users_inspection():
    headers1 = register_and_login()
    headers2 = register_and_login()

    response = client.post("/inspections", json=inspection_payload(), headers=headers1)
    assert response.status_code == 201
    inspection_id = response.json()["id"]

    response = client.put(
        f"/inspections/{inspection_id}",
        json={"severity": "low"},
        headers=headers2,
    )
    assert response.status_code == 404


def test_cannot_delete_another_users_inspection():
    headers1 = register_and_login()
    headers2 = register_and_login()

    response = client.post("/inspections", json=inspection_payload(), headers=headers1)
    assert response.status_code == 201
    inspection_id = response.json()["id"]

    response = client.delete(f"/inspections/{inspection_id}", headers=headers2)
    assert response.status_code == 404


# --- Validation ---

def test_invalid_severity_value():
    headers = register_and_login()
    payload = inspection_payload()
    payload["severity"] = "extreme"
    response = client.post("/inspections", json=payload, headers=headers)
    assert response.status_code == 422


def test_invalid_damage_type_value():
    headers = register_and_login()
    payload = inspection_payload()
    payload["damage_type"] = "flood"
    response = client.post("/inspections", json=payload, headers=headers)
    assert response.status_code == 422


def test_missing_required_field():
    headers = register_and_login()
    response = client.post("/inspections", json={"severity": "high"}, headers=headers)
    assert response.status_code == 422


# --- Filtering ---

def test_filter_by_severity():
    headers = register_and_login()
    client.post("/inspections", json=inspection_payload(severity="high"), headers=headers)
    client.post("/inspections", json=inspection_payload(severity="low"), headers=headers)

    response = client.get("/inspections?severity=high", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(item["severity"] == "high" for item in data["items"])


def test_filter_by_damage_type():
    headers = register_and_login()
    client.post("/inspections", json=inspection_payload(damage_type="pothole"), headers=headers)
    client.post("/inspections", json=inspection_payload(damage_type="crack"), headers=headers)

    response = client.get("/inspections?damage_type=crack", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(item["damage_type"] == "crack" for item in data["items"])


def test_filter_by_status():
    headers = register_and_login()
    response = client.post("/inspections", json=inspection_payload(), headers=headers)
    inspection_id = response.json()["id"]
    client.put(f"/inspections/{inspection_id}", json={"status": "verified"}, headers=headers)

    response = client.get("/inspections?status=verified", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(item["status"] == "verified" for item in data["items"])


# --- Pagination ---

def test_pagination_limit():
    headers = register_and_login()
    for _ in range(3):
        client.post("/inspections", json=inspection_payload(), headers=headers)

    response = client.get("/inspections?limit=1&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] >= 3


def test_pagination_offset():
    headers = register_and_login()
    for i in range(3):
        client.post("/inspections", json=inspection_payload(location_code=f"X{i}-KM-000"), headers=headers)

    page1 = client.get("/inspections?limit=2&offset=0", headers=headers).json()["items"]
    page2 = client.get("/inspections?limit=2&offset=2", headers=headers).json()["items"]

    page1_ids = {item["id"] for item in page1}
    page2_ids = {item["id"] for item in page2}
    assert page1_ids.isdisjoint(page2_ids)


# --- Sorting ---

def test_sort_by_severity_asc():
    headers = register_and_login()
    client.post("/inspections", json=inspection_payload(severity="low"), headers=headers)
    client.post("/inspections", json=inspection_payload(severity="high"), headers=headers)
    client.post("/inspections", json=inspection_payload(severity="critical"), headers=headers)

    response = client.get("/inspections?sort_by=severity&order=asc", headers=headers)
    assert response.status_code == 200
    severities = [item["severity"] for item in response.json()["items"]]
    assert severities == sorted(severities)


def test_sort_by_severity_desc():
    headers = register_and_login()
    client.post("/inspections", json=inspection_payload(severity="low"), headers=headers)
    client.post("/inspections", json=inspection_payload(severity="high"), headers=headers)
    client.post("/inspections", json=inspection_payload(severity="critical"), headers=headers)

    response = client.get("/inspections?sort_by=severity&order=desc", headers=headers)
    assert response.status_code == 200
    severities = [item["severity"] for item in response.json()["items"]]
    assert severities == sorted(severities, reverse=True)


# --- Admin ---

def test_regular_user_cannot_access_admin_endpoint():
    headers = register_and_login()
    response = client.get("/admin/inspections", headers=headers)
    assert response.status_code == 403


def test_unauthenticated_cannot_access_admin_endpoint():
    response = client.get("/admin/inspections")
    assert response.status_code == 401


def test_admin_can_list_all_inspections():
    user_headers = register_and_login()
    admin_headers = register_and_login_as_admin()

    client.post("/inspections", json=inspection_payload(location_code="ADM-001"), headers=user_headers)

    response = client.get("/admin/inspections", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_admin_response_includes_user_email():
    user_headers = register_and_login()
    admin_headers = register_and_login_as_admin()

    client.post("/inspections", json=inspection_payload(location_code="ADM-002"), headers=user_headers)

    response = client.get("/admin/inspections", headers=admin_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert all("user_email" in item for item in items)


def test_admin_can_see_inspections_from_multiple_users():
    headers1 = register_and_login()
    headers2 = register_and_login()
    admin_headers = register_and_login_as_admin()

    client.post("/inspections", json=inspection_payload(location_code="ADM-U1"), headers=headers1)
    client.post("/inspections", json=inspection_payload(location_code="ADM-U2"), headers=headers2)

    response = client.get("/admin/inspections", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 2


def test_admin_can_update_any_inspection():
    user_headers = register_and_login()
    admin_headers = register_and_login_as_admin()

    response = client.post("/inspections", json=inspection_payload(location_code="ADM-UPD"), headers=user_headers)
    inspection_id = response.json()["id"]

    response = client.put(
        f"/admin/inspections/{inspection_id}",
        json={"status": "repaired"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "repaired"


def test_admin_can_delete_any_inspection():
    user_headers = register_and_login()
    admin_headers = register_and_login_as_admin()

    response = client.post("/inspections", json=inspection_payload(location_code="ADM-DEL"), headers=user_headers)
    inspection_id = response.json()["id"]

    response = client.delete(f"/admin/inspections/{inspection_id}", headers=admin_headers)
    assert response.status_code == 204


def test_regular_user_cannot_use_admin_update():
    headers1 = register_and_login()
    headers2 = register_and_login()

    response = client.post("/inspections", json=inspection_payload(), headers=headers1)
    inspection_id = response.json()["id"]

    response = client.put(
        f"/admin/inspections/{inspection_id}",
        json={"status": "repaired"},
        headers=headers2,
    )
    assert response.status_code == 403


def test_regular_user_cannot_use_admin_delete():
    headers1 = register_and_login()
    headers2 = register_and_login()

    response = client.post("/inspections", json=inspection_payload(), headers=headers1)
    inspection_id = response.json()["id"]

    response = client.delete(f"/admin/inspections/{inspection_id}", headers=headers2)
    assert response.status_code == 403
