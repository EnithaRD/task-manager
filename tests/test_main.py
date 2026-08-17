from fastapi.testclient import TestClient

from backend.main import app, tasks

client = TestClient(app)


def setup_function():
    tasks.clear()


def test_list_tasks_empty():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task():
    response = client.post("/api/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["completed"] is False
    assert "id" in data


def test_get_task():
    created = client.post("/api/tasks", json={"title": "Read book"}).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Read book"


def test_get_task_not_found():
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


def test_update_task():
    created = client.post("/api/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "Old title"


def test_update_task_not_found():
    response = client.put("/api/tasks/999", json={"completed": True})
    assert response.status_code == 404


def test_delete_task():
    created = client.post("/api/tasks", json={"title": "Temp"}).json()
    response = client.delete(f"/api/tasks/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found():
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404
