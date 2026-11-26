from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for a to-do list.",
)

# ---------- In-memory "database" ----------
SEED_TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
]
tasks = [dict(t) for t in SEED_TASKS]


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """Wrong types / malformed JSON -> 400 with a JSON error (not FastAPI's default 422)."""
    return JSONResponse(
        status_code=400,
        content={"error": "invalid request: check field types and JSON syntax"},
    )


def error(status: int, message: str) -> JSONResponse:
    """Every error is JSON: {"error": "..."}"""
    return JSONResponse(status_code=status, content={"error": message})


def find_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


def next_id() -> int:
    return max((t["id"] for t in tasks), default=0) + 1


# ---------- Root and health ----------
@app.get("/", summary="API info")
def root():
    """Describes the API."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    """Used to check that the server is alive."""
    return {"status": "ok"}


# ---------- Read ----------
@app.get("/tasks", summary="List tasks")
def list_tasks():
    """Returns all tasks."""
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns one task, or 404 if it does not exist."""
    task = find_task(task_id)
    if task is None:
        return error(404, f"Task {task_id} not found")
    return task


# ---------- Create ----------
class TaskCreate(BaseModel):
    title: Optional[str] = None


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(body: Optional[TaskCreate] = None):
    """Creates a task. `title` is required and cannot be empty."""
    if body is None or not isinstance(body.title, str) or not body.title.strip():
        return error(400, "title is required and cannot be empty")
    task = {"id": next_id(), "title": body.title.strip(), "done": False}
    tasks.append(task)
    return JSONResponse(status_code=201, content=task)


# ---------- Update & Delete ----------
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, body: Optional[TaskUpdate] = None):
    """Updates `title` and/or `done`. Omitted fields stay unchanged."""
    task = find_task(task_id)
    if task is None:
        return error(404, f"Task {task_id} not found")
    if body is None or (body.title is None and body.done is None):
        return error(400, "request body must include title and/or done")
    if body.title is not None:
        if not body.title.strip():
            return error(400, "title cannot be empty")
        task["title"] = body.title.strip()
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Removes a task. Returns 204 with an empty body."""
    task = find_task(task_id)
    if task is None:
        return error(404, f"Task {task_id} not found")
    tasks.remove(task)
    return Response(status_code=204)