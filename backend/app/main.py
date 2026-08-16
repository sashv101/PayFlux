from fastapi import FastAPI

app = FastAPI(
    title="PayFlux API",
    description="Backend API for the PayFlux merchant-support agent.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to PayFlux",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "payflux-api",
    }