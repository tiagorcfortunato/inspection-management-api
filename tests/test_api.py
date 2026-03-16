import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def unique_email():
    return f"{uuid.uuid4().hex[:8]}@example.com"


def test_register_login_and_create_task():

    email = unique_email()
    password = "test123"

    # register user
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code in [200, 201]

    # login
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # create task
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Testing API",
            "completed": False
        },
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Test Task"

    # get tasks
    response = client.get("/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1


def test_user_cannot_see_another_users_tasks():

    password = "test123"

    email1 = unique_email()
    email2 = unique_email()

    # user 1 register
    response = client.post(
        "/auth/register",
        json={
            "email": email1,
            "password": password
        }
    )
    assert response.status_code in [200, 201]

    # user 1 login
    response = client.post(
        "/auth/login",
        data={
            "username": email1,
            "password": password
        }
    )
    assert response.status_code == 200
    token1 = response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # user 1 creates task
    response = client.post(
        "/tasks",
        json={
            "title": "User1 Task",
            "description": "private task",
            "completed": False
        },
        headers=headers1
    )
    assert response.status_code == 200
    task_id = response.json()["id"]

    # user 2 register
    response = client.post(
        "/auth/register",
        json={
            "email": email2,
            "password": password
        }
    )
    assert response.status_code in [200, 201]

    # user 2 login
    response = client.post(
        "/auth/login",
        data={
            "username": email2,
            "password": password
        }
    )
    assert response.status_code == 200
    token2 = response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # user 2 should not see user 1 task in list
    response = client.get("/tasks", headers=headers2)
    assert response.status_code == 200
    data = response.json()
    assert all(task["id"] != task_id for task in data["items"])

    # user 2 should not access user 1 task directly
    response = client.get(f"/tasks/{task_id}", headers=headers2)
    assert response.status_code == 404

def test_update_task():

    email = unique_email()
    password = "test123"

    # register
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )

    # login
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create task
    response = client.post(
        "/tasks",
        json={
            "title": "Initial Task",
            "description": "before update",
            "completed": False,
        },
        headers=headers,
    )

    task_id = response.json()["id"]

    # update task
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "after update",
            "completed": True,
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Task"
    assert data["completed"] is True

def test_delete_task():

    email = unique_email()
    password = "test123"

    # register
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )

    # login
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create task
    response = client.post(
        "/tasks",
        json={
            "title": "Task to delete",
            "description": "delete test",
            "completed": False,
        },
        headers=headers,
    )

    task_id = response.json()["id"]

    # delete task
    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 200

    # ensure task is gone
    response = client.get(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 404
