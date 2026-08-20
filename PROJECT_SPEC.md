# PROJECT_SPEC.md — Task Manager REST API (Project 2)

## 1. Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks` | List tasks (optional filtering/search/sort via query params, matching existing behavior: `search`, `completed`, `priority`, `category`, `sort_by`, `order`) |
| `GET` | `/tasks/{id}` | Fetch a single task by ID |
| `PUT` | `/tasks/{id}` | Partially update a task (only supplied fields change) |
| `DELETE` | `/tasks/{id}` | Delete a task by ID |

Note: the existing app mounts these at `/api/tasks`; this spec uses the bare `/tasks` prefix as instructed for Project 2. If this is meant to replace the existing API rather than run alongside it, the mount point should be reconciled during implementation planning.

## 2. Task Data Model

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `id` | integer | server-assigned | — | Auto-incremented primary key |
| `title` | string | yes | — | Non-empty after trimming |
| `description` | string | no | `""` | |
| `notes` | string | no | `""` | |
| `completed` | boolean | no | `false` | |
| `priority` | enum: `low`\|`medium`\|`high` | no | `medium` | |
| `due_date` | string (ISO `YYYY-MM-DD`) or `null` | no | `null` | |
| `category` | enum: `Work`\|`Study`\|`Personal`\|`Shopping`\|`Other` | no | `Other` | |
| `created_at` | datetime | server-assigned | — | New field, needed for persistence/ordering; not in current in-memory model |

This mirrors the existing `Task`/`TaskCreate`/`TaskUpdate` Pydantic models in `backend/main.py`, plus a `created_at` timestamp made necessary by moving off pure insertion-order-in-a-dict.

## 3. Validation Rules

- `title`: required on create, must be non-empty after stripping whitespace, max length 200.
- `description`, `notes`: optional strings, max length 2000 (avoid unbounded storage).
- `priority`: must be one of `low`/`medium`/`high` — invalid value → `422`.
- `category`: must be one of the 5 fixed values — invalid value → `422`.
- `due_date`: if provided, must parse as `YYYY-MM-DD`; invalid format → `422`.
- `id` in path params: must be a positive integer (FastAPI handles via type coercion); non-existent ID → `404`.
- `PUT`: partial update — omitted fields are untouched (existing `exclude_unset` behavior); an empty body is valid and is a no-op.

## 4. HTTP Status Codes

| Code | When |
|---|---|
| `200 OK` | Successful `GET` (list/single), successful `PUT` |
| `201 Created` | Successful `POST` |
| `204 No Content` | Successful `DELETE` |
| `404 Not Found` | `GET`/`PUT`/`DELETE` on a non-existent `id` |
| `422 Unprocessable Entity` | Invalid body/query params (bad enum value, bad due_date format, missing required field) |

## 5. Persistent Storage

- Replace the in-memory `dict[int, Task]` with **SQLite** via **SQLAlchemy** (already installed in this environment; add to `requirements.txt`).
- One table, `tasks`, mapping directly to the fields above.
- Rationale: the app is single-user, low-write-volume, and file-based storage avoids standing up an external DB server — SQLite is the natural next step up from in-memory for this project's scale, and SQLAlchemy is idiomatic with FastAPI/Pydantic.
- DB file (e.g. `backend/tasks.db`) should be gitignored, same treatment as the existing `__pycache__` artifacts.

## 6. Unit Tests (minimum 5)

1. `test_create_task` — `POST /tasks` returns `201` with assigned `id` and correct defaults.
2. `test_get_task` / `test_get_task_not_found` — `GET /tasks/{id}` returns the created task; returns `404` for a non-existent ID.
3. `test_update_task_partial` — `PUT /tasks/{id}` changes only the supplied field(s), leaves others untouched.
4. `test_delete_task` — `DELETE /tasks/{id}` returns `204`; subsequent `GET` returns `404`.
5. `test_create_task_invalid_priority` — invalid `priority` value returns `422`.
6. `test_persistence_across_restart` — data written to the DB is still retrievable after re-instantiating the app/session against the same DB file, proving it's not just in-memory.

(This reuses/extends the existing `tests/test_main.py` suite rather than starting from scratch — it already has ~40 tests covering most of this surface for the in-memory version.)

## 7. Out of Scope

- Authentication / authorization / multi-user support.
- Pagination (list endpoint returns all tasks, as today).
- Rate limiting.
- Task categories/priorities beyond the fixed enums (no user-defined categories).
- Real-time updates (WebSockets/SSE).
- Any changes to the existing frontend beyond what's needed to keep it working against the same API shape.
- Concurrent-write conflict resolution (SQLite's default locking is sufficient at this scale).

## 8. Recommended Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Web framework | **FastAPI** (existing) | Already in use; gives request validation, OpenAPI docs, and async support for free — no reason to switch. |
| Validation | **Pydantic** (existing) | Already integrated with FastAPI; enum/type validation maps directly to the rules above. |
| Persistence | **SQLite + SQLAlchemy** | Zero-ops file-based DB appropriate for this project's scale; SQLAlchemy gives an ORM layer that maps cleanly onto the existing Pydantic models without a heavier dependency (e.g., Postgres + driver + connection pooling) that this project doesn't need. |
| Server | **Uvicorn** (existing) | Already in use, standard ASGI server for FastAPI. |
| Testing | **pytest + httpx via FastAPI TestClient** (existing) | Already in use across 40+ tests; no reason to introduce a second test framework. |

This keeps the stack change minimal and additive (one new dependency: SQLAlchemy) rather than a rewrite, consistent with reusing the existing, already-tested API surface.
