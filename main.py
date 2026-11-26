from fastapi import FastAPI
from fastapi.responses import JSONResponse

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


def error(status: int, message: str) -> JSONResponse:
    """Every error is JSON: {"error": "..."}"""
    return JSONResponse(status_code=status, content={"error": message})


def find_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


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