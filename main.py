from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for a to-do list.",
)


@app.get("/", summary="API info")
def root():
    return {"message": "Hello, server!"}