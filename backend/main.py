from datetime import date, datetime
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Path as PathParam
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import TaskORM

app = FastAPI(title="Task Manager API")

Base.metadata.create_all(bind=engine)

Priority = Literal["low", "medium", "high"]
Category = Literal["Work", "Study", "Personal", "Shopping", "Other"]


def _validate_title(value: str | None) -> str:
    stripped = (value or "").strip()
    if not stripped:
        raise ValueError("title must not be empty")
    return stripped


def _validate_due_date(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError("due_date must be in YYYY-MM-DD format") from None
    return value


class TaskCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    notes: str = Field(default="", max_length=2000)
    completed: bool = False
    priority: Priority = "medium"
    due_date: str | None = None
    category: Category = "Other"

    _validate_title = field_validator("title")(_validate_title)
    _validate_due_date = field_validator("due_date")(_validate_due_date)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None
    priority: Priority | None = None
    due_date: str | None = None
    category: Category | None = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str | None) -> str:
        return _validate_title(value)

    _validate_due_date = field_validator("due_date")(_validate_due_date)


class Task(TaskCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    search: str | None = None,
    completed: bool | None = None,
    priority: Priority | None = None,
    category: Category | None = None,
    sort_by: Literal["title", "created"] | None = None,
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
):
    query = db.query(TaskORM)

    if completed is not None:
        query = query.filter(TaskORM.completed == completed)
    if priority is not None:
        query = query.filter(TaskORM.priority == priority)
    if category is not None:
        query = query.filter(TaskORM.category == category)

    result = query.all()

    if search is not None:
        result = [task for task in result if search.lower() in task.title.lower()]

    if sort_by == "title":
        result.sort(key=lambda task: task.title.lower(), reverse=order == "desc")
    elif sort_by == "created":
        result.sort(key=lambda task: task.created_at, reverse=order == "desc")

    return result


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = TaskORM(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int = PathParam(gt=0), db: Session = Depends(get_db)):
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int = PathParam(gt=0),
    updates: TaskUpdate = ...,
    db: Session = Depends(get_db),
):
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int = PathParam(gt=0), db: Session = Depends(get_db)):
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
