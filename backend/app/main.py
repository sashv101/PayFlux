import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.agent_routes import router as agent_router
from app.api.routes import router


app = FastAPI(
    title="PayFlux API",
    description="Backend API for the PayFlux merchant-support agent.",
    version="0.1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(agent_router)


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