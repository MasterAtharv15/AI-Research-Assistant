from fastapi import FastAPI

app = FastAPI(title="AI Research Assistant")


@app.get("/")
def read_root() -> dict[str, str]:
    """Return the API welcome message."""
    return {"message": "AI Research Assistant API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}
