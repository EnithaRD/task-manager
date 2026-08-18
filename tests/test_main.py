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


def test_create_task_default_priority():
    response = client.post("/api/tasks", json={"title": "Learn Python"})
    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_task_with_priority():
    response = client.post(
        "/api/tasks",
        json={"title": "Learn RAG", "description": "Study retrieval augmented generation", "priority": "high"},
    )
    assert response.status_code == 201
    assert response.json()["priority"] == "high"


def test_create_task_invalid_priority():
    response = client.post(
        "/api/tasks",
        json={"title": "Learn MCP", "description": "Study MCP", "priority": "urgent"},
    )
    assert response.status_code == 422


def test_create_task_default_notes():
    response = client.post("/api/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["notes"] == ""


def test_create_task_with_notes():
    response = client.post(
        "/api/tasks",
        json={"title": "Plan trip", "notes": "Remember passport"},
    )
    assert response.status_code == 201
    assert response.json()["notes"] == "Remember passport"


def test_create_task_default_due_date():
    response = client.post("/api/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["due_date"] is None


def test_create_task_with_due_date():
    response = client.post(
        "/api/tasks",
        json={"title": "Plan trip", "due_date": "2026-09-01"},
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-09-01"


def test_create_task_default_category():
    response = client.post("/api/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["category"] == "Other"


def test_create_task_with_category():
    response = client.post(
        "/api/tasks",
        json={"title": "Finish report", "category": "Work"},
    )
    assert response.status_code == 201
    assert response.json()["category"] == "Work"


def test_create_task_invalid_category():
    response = client.post(
        "/api/tasks",
        json={"title": "Bad category", "category": "Urgent"},
    )
    assert response.status_code == 422


def test_get_task():
    created = client.post("/api/tasks", json={"title": "Read book"}).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Read book"


def test_get_task_includes_notes():
    created = client.post(
        "/api/tasks", json={"title": "Read book", "notes": "Chapter 3"}
    ).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["notes"] == "Chapter 3"


def test_get_task_includes_category():
    created = client.post(
        "/api/tasks", json={"title": "Read book", "category": "Study"}
    ).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["category"] == "Study"


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


def test_update_task_priority():
    created = client.post("/api/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"priority": "low"})
    assert response.status_code == 200
    assert response.json()["priority"] == "low"


def test_update_task_notes():
    created = client.post("/api/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"notes": "New note"})
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "New note"
    assert data["title"] == "Old title"


def test_update_task_notes_does_not_affect_other_fields():
    created = client.post(
        "/api/tasks",
        json={"title": "Task", "description": "Desc", "priority": "high"},
    ).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"notes": "A note"})
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "A note"
    assert data["description"] == "Desc"
    assert data["priority"] == "high"
    assert data["completed"] is False


def test_update_other_fields_does_not_affect_notes():
    created = client.post(
        "/api/tasks", json={"title": "Task", "notes": "Keep me"}
    ).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["notes"] == "Keep me"


def test_update_task_notes_to_empty_string_clears_it():
    created = client.post(
        "/api/tasks", json={"title": "Task", "notes": "Something"}
    ).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"notes": ""})
    assert response.status_code == 200
    assert response.json()["notes"] == ""


def test_update_task_due_date():
    created = client.post("/api/tasks", json={"title": "Old title"}).json()
    response = client.put(
        f"/api/tasks/{created['id']}", json={"due_date": "2026-10-15"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"] == "2026-10-15"
    assert data["title"] == "Old title"


def test_update_task_due_date_does_not_affect_other_fields():
    created = client.post(
        "/api/tasks",
        json={"title": "Task", "description": "Desc", "priority": "high"},
    ).json()
    response = client.put(
        f"/api/tasks/{created['id']}", json={"due_date": "2026-11-01"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"] == "2026-11-01"
    assert data["description"] == "Desc"
    assert data["priority"] == "high"
    assert data["completed"] is False


def test_update_task_due_date_to_null_clears_it():
    created = client.post(
        "/api/tasks", json={"title": "Task", "due_date": "2026-09-01"}
    ).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"due_date": None})
    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_update_task_category():
    created = client.post("/api/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"category": "Personal"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Personal"
    assert data["title"] == "Old title"


def test_update_task_category_does_not_affect_other_fields():
    created = client.post(
        "/api/tasks",
        json={"title": "Task", "description": "Desc", "priority": "high"},
    ).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"category": "Shopping"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Shopping"
    assert data["description"] == "Desc"
    assert data["priority"] == "high"
    assert data["completed"] is False


def test_update_task_invalid_category():
    created = client.post("/api/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"category": "Nope"})
    assert response.status_code == 422


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


def test_list_tasks_no_params_unchanged():
    client.post("/api/tasks", json={"title": "First"})
    client.post("/api/tasks", json={"title": "Second"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["First", "Second"]


def test_search_case_insensitive_match():
    client.post("/api/tasks", json={"title": "Buy Milk"})
    client.post("/api/tasks", json={"title": "Read book"})
    response = client.get("/api/tasks", params={"search": "MILK"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Buy Milk"]


def test_search_no_match_returns_empty():
    client.post("/api/tasks", json={"title": "Buy Milk"})
    response = client.get("/api/tasks", params={"search": "xyz"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_ignores_notes_field():
    client.post("/api/tasks", json={"title": "Buy Milk", "notes": "xyz special note"})
    response = client.get("/api/tasks", params={"search": "xyz"})
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_completed():
    done = client.post("/api/tasks", json={"title": "Done task"}).json()
    client.post("/api/tasks", json={"title": "Not done task"})
    client.put(f"/api/tasks/{done['id']}", json={"completed": True})

    response = client.get("/api/tasks", params={"completed": "true"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Done task"]

    response = client.get("/api/tasks", params={"completed": "false"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Not done task"]


def test_filter_by_priority():
    client.post("/api/tasks", json={"title": "Low task", "priority": "low"})
    client.post("/api/tasks", json={"title": "High task", "priority": "high"})
    response = client.get("/api/tasks", params={"priority": "high"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["High task"]


def test_combined_search_and_completed_filter():
    milk_done = client.post("/api/tasks", json={"title": "Buy Milk"}).json()
    client.post("/api/tasks", json={"title": "Buy Bread"})
    client.put(f"/api/tasks/{milk_done['id']}", json={"completed": True})

    response = client.get("/api/tasks", params={"search": "buy", "completed": "true"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Buy Milk"]


def test_sort_by_title_ascending():
    client.post("/api/tasks", json={"title": "Banana"})
    client.post("/api/tasks", json={"title": "Apple"})
    response = client.get("/api/tasks", params={"sort_by": "title", "order": "asc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Apple", "Banana"]


def test_sort_by_title_descending():
    client.post("/api/tasks", json={"title": "Banana"})
    client.post("/api/tasks", json={"title": "Apple"})
    response = client.get("/api/tasks", params={"sort_by": "title", "order": "desc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Banana", "Apple"]


def test_sort_by_created_order():
    client.post("/api/tasks", json={"title": "First"})
    client.post("/api/tasks", json={"title": "Second"})
    response = client.get("/api/tasks", params={"sort_by": "created", "order": "asc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["First", "Second"]

    response = client.get("/api/tasks", params={"sort_by": "created", "order": "desc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Second", "First"]
