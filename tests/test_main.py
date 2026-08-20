from fastapi.testclient import TestClient

from backend.database import Base, engine
from backend.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_list_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["completed"] is False
    assert "id" in data


def test_create_task_default_priority():
    response = client.post("/tasks", json={"title": "Learn Python"})
    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_task_with_priority():
    response = client.post(
        "/tasks",
        json={"title": "Learn RAG", "description": "Study retrieval augmented generation", "priority": "high"},
    )
    assert response.status_code == 201
    assert response.json()["priority"] == "high"


def test_create_task_invalid_priority():
    response = client.post(
        "/tasks",
        json={"title": "Learn MCP", "description": "Study MCP", "priority": "urgent"},
    )
    assert response.status_code == 422


def test_create_task_default_notes():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["notes"] == ""


def test_create_task_with_notes():
    response = client.post(
        "/tasks",
        json={"title": "Plan trip", "notes": "Remember passport"},
    )
    assert response.status_code == 201
    assert response.json()["notes"] == "Remember passport"


def test_create_task_default_due_date():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["due_date"] is None


def test_create_task_with_due_date():
    response = client.post(
        "/tasks",
        json={"title": "Plan trip", "due_date": "2026-09-01"},
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-09-01"


def test_create_task_default_category():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["category"] == "Other"


def test_create_task_with_category():
    response = client.post(
        "/tasks",
        json={"title": "Finish report", "category": "Work"},
    )
    assert response.status_code == 201
    assert response.json()["category"] == "Work"


def test_create_task_invalid_category():
    response = client.post(
        "/tasks",
        json={"title": "Bad category", "category": "Urgent"},
    )
    assert response.status_code == 422


def test_get_task():
    created = client.post("/tasks", json={"title": "Read book"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Read book"


def test_get_task_includes_notes():
    created = client.post(
        "/tasks", json={"title": "Read book", "notes": "Chapter 3"}
    ).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["notes"] == "Chapter 3"


def test_get_task_includes_category():
    created = client.post(
        "/tasks", json={"title": "Read book", "category": "Study"}
    ).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["category"] == "Study"


def test_get_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "Old title"


def test_update_task_priority():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"priority": "low"})
    assert response.status_code == 200
    assert response.json()["priority"] == "low"


def test_update_task_notes():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"notes": "New note"})
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "New note"
    assert data["title"] == "Old title"


def test_update_task_notes_does_not_affect_other_fields():
    created = client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc", "priority": "high"},
    ).json()
    response = client.put(f"/tasks/{created['id']}", json={"notes": "A note"})
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "A note"
    assert data["description"] == "Desc"
    assert data["priority"] == "high"
    assert data["completed"] is False


def test_update_other_fields_does_not_affect_notes():
    created = client.post(
        "/tasks", json={"title": "Task", "notes": "Keep me"}
    ).json()
    response = client.put(f"/tasks/{created['id']}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["notes"] == "Keep me"


def test_update_task_notes_to_empty_string_clears_it():
    created = client.post(
        "/tasks", json={"title": "Task", "notes": "Something"}
    ).json()
    response = client.put(f"/tasks/{created['id']}", json={"notes": ""})
    assert response.status_code == 200
    assert response.json()["notes"] == ""


def test_update_task_due_date():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(
        f"/tasks/{created['id']}", json={"due_date": "2026-10-15"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"] == "2026-10-15"
    assert data["title"] == "Old title"


def test_update_task_due_date_does_not_affect_other_fields():
    created = client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc", "priority": "high"},
    ).json()
    response = client.put(
        f"/tasks/{created['id']}", json={"due_date": "2026-11-01"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"] == "2026-11-01"
    assert data["description"] == "Desc"
    assert data["priority"] == "high"
    assert data["completed"] is False


def test_update_task_due_date_to_null_clears_it():
    created = client.post(
        "/tasks", json={"title": "Task", "due_date": "2026-09-01"}
    ).json()
    response = client.put(f"/tasks/{created['id']}", json={"due_date": None})
    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_update_task_category():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"category": "Personal"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Personal"
    assert data["title"] == "Old title"


def test_update_task_category_does_not_affect_other_fields():
    created = client.post(
        "/tasks",
        json={"title": "Task", "description": "Desc", "priority": "high"},
    ).json()
    response = client.put(f"/tasks/{created['id']}", json={"category": "Shopping"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Shopping"
    assert data["description"] == "Desc"
    assert data["priority"] == "high"
    assert data["completed"] is False


def test_update_task_invalid_category():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"category": "Nope"})
    assert response.status_code == 422


def test_update_task_not_found():
    response = client.put("/tasks/999", json={"completed": True})
    assert response.status_code == 404


def test_delete_task():
    created = client.post("/tasks", json={"title": "Temp"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found():
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_list_tasks_no_params_unchanged():
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    response = client.get("/tasks")
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["First", "Second"]


def test_search_case_insensitive_match():
    client.post("/tasks", json={"title": "Buy Milk"})
    client.post("/tasks", json={"title": "Read book"})
    response = client.get("/tasks", params={"search": "MILK"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Buy Milk"]


def test_search_no_match_returns_empty():
    client.post("/tasks", json={"title": "Buy Milk"})
    response = client.get("/tasks", params={"search": "xyz"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_ignores_notes_field():
    client.post("/tasks", json={"title": "Buy Milk", "notes": "xyz special note"})
    response = client.get("/tasks", params={"search": "xyz"})
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_completed():
    done = client.post("/tasks", json={"title": "Done task"}).json()
    client.post("/tasks", json={"title": "Not done task"})
    client.put(f"/tasks/{done['id']}", json={"completed": True})

    response = client.get("/tasks", params={"completed": "true"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Done task"]

    response = client.get("/tasks", params={"completed": "false"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Not done task"]


def test_filter_by_priority():
    client.post("/tasks", json={"title": "Low task", "priority": "low"})
    client.post("/tasks", json={"title": "High task", "priority": "high"})
    response = client.get("/tasks", params={"priority": "high"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["High task"]


def test_combined_search_and_completed_filter():
    milk_done = client.post("/tasks", json={"title": "Buy Milk"}).json()
    client.post("/tasks", json={"title": "Buy Bread"})
    client.put(f"/tasks/{milk_done['id']}", json={"completed": True})

    response = client.get("/tasks", params={"search": "buy", "completed": "true"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Buy Milk"]


def test_filter_by_category():
    client.post("/tasks", json={"title": "Study task", "category": "Study"})
    client.post("/tasks", json={"title": "Work task", "category": "Work"})
    response = client.get("/tasks", params={"category": "Study"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Study task"]


def test_filter_by_category_no_match_returns_empty():
    client.post("/tasks", json={"title": "Work task", "category": "Work"})
    response = client.get("/tasks", params={"category": "Shopping"})
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_invalid_category_returns_422():
    response = client.get("/tasks", params={"category": "Nope"})
    assert response.status_code == 422


def test_combined_category_and_completed_filter():
    work_done = client.post(
        "/tasks", json={"title": "Finish slides", "category": "Work"}
    ).json()
    shopping_done = client.post(
        "/tasks", json={"title": "Buy milk", "category": "Shopping"}
    ).json()
    client.post("/tasks", json={"title": "Plan meeting", "category": "Work"})
    client.put(f"/tasks/{work_done['id']}", json={"completed": True})
    client.put(f"/tasks/{shopping_done['id']}", json={"completed": True})

    completed_response = client.get("/tasks", params={"completed": "true"})
    assert completed_response.status_code == 200
    completed_titles = [task["title"] for task in completed_response.json()]
    assert len(completed_titles) > 1

    response = client.get(
        "/tasks", params={"category": "Work", "completed": "true"}
    )
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Finish slides"]


def test_sort_by_title_ascending():
    client.post("/tasks", json={"title": "Banana"})
    client.post("/tasks", json={"title": "Apple"})
    response = client.get("/tasks", params={"sort_by": "title", "order": "asc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Apple", "Banana"]


def test_sort_by_title_descending():
    client.post("/tasks", json={"title": "Banana"})
    client.post("/tasks", json={"title": "Apple"})
    response = client.get("/tasks", params={"sort_by": "title", "order": "desc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Banana", "Apple"]


def test_sort_by_created_order():
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    response = client.get("/tasks", params={"sort_by": "created", "order": "asc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["First", "Second"]

    response = client.get("/tasks", params={"sort_by": "created", "order": "desc"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Second", "First"]


def test_create_task_empty_title_rejected():
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_missing_title_rejected():
    response = client.post("/tasks", json={"description": "No title given"})
    assert response.status_code == 422


def test_create_task_invalid_due_date_rejected():
    response = client.post(
        "/tasks", json={"title": "Bad date", "due_date": "09-01-2026"}
    )
    assert response.status_code == 422


def test_update_task_invalid_due_date_rejected():
    created = client.post("/tasks", json={"title": "Task"}).json()
    response = client.put(
        f"/tasks/{created['id']}", json={"due_date": "not-a-date"}
    )
    assert response.status_code == 422


def test_data_persists_across_new_db_session():
    created = client.post("/tasks", json={"title": "Persisted task"}).json()

    from backend.database import SessionLocal
    from backend.models import TaskORM

    session = SessionLocal()
    try:
        stored = session.get(TaskORM, created["id"])
        assert stored is not None
        assert stored.title == "Persisted task"
    finally:
        session.close()


def test_update_task_null_title_rejected():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"title": None})
    assert response.status_code == 422


def test_update_task_whitespace_title_rejected():
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_title_too_long_rejected():
    response = client.post("/tasks", json={"title": "x" * 201})
    assert response.status_code == 422


def test_create_task_description_too_long_rejected():
    response = client.post(
        "/tasks", json={"title": "Task", "description": "x" * 2001}
    )
    assert response.status_code == 422


def test_create_task_response_includes_created_at():
    response = client.post("/tasks", json={"title": "Track creation time"})
    assert response.status_code == 201
    assert "created_at" in response.json()


def test_sort_by_created_uses_created_at_not_id():
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})
    response = client.get("/tasks", params={"sort_by": "created", "order": "asc"})
    timestamps = [task["created_at"] for task in response.json()]
    assert timestamps == sorted(timestamps)


def test_get_task_non_positive_id_rejected():
    response = client.get("/tasks/0")
    assert response.status_code == 422

    response = client.get("/tasks/-1")
    assert response.status_code == 422
