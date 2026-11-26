from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for a to-do list.",
)


@app.get("/", summary="API info")
def root():
    """Describes the API."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    """Used to check that the server is alive."""
    return {"status": "ok"}