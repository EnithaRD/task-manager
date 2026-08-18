from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import Literal

app = FastAPI(title="Task Manager API")

Priority = Literal["low", "medium", "high"]
Category = Literal["Work", "Study", "Personal", "Shopping", "Other"]


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    notes: str = ""
    completed: bool = False
    priority: Priority = "medium"
    due_date: str | None = None
    category: Category = "Other"


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    notes: str | None = None
    completed: bool | None = None
    priority: Priority | None = None
    due_date: str | None = None
    category: Category | None = None


class Task(TaskCreate):
    id: int


tasks: dict[int, Task] = {}
next_id = 1


@app.get("/api/tasks", response_model=list[Task])
def list_tasks(
    search: str | None = None,
    completed: bool | None = None,
    priority: Priority | None = None,
    category: Category | None = None,
    sort_by: Literal["title", "created"] | None = None,
    order: Literal["asc", "desc"] = "asc",
):
    result = list(tasks.values())

    if search is not None:
        result = [task for task in result if search.lower() in task.title.lower()]

    if completed is not None:
        result = [task for task in result if task.completed == completed]

    if priority is not None:
        result = [task for task in result if task.priority == priority]

    if category is not None:
        result = [task for task in result if task.category == category]

    if sort_by == "title":
        result.sort(key=lambda task: task.title.lower(), reverse=order == "desc")
    elif sort_by == "created":
        result.sort(key=lambda task: task.id, reverse=order == "desc")

    return result


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    global next_id
    new_task = Task(id=next_id, **task.model_dump())
    tasks[next_id] = new_task
    next_id += 1
    return new_task


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updates: TaskUpdate):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = task.model_copy(update=updates.model_dump(exclude_unset=True))
    tasks[task_id] = updated
    return updated


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
