# app/main.py
from fastapi import FastAPI
from .api import router as api_router

app = FastAPI(
    title="Autonomous Code Review Agent",
    description="API for analyzing GitHub Pull Requests using AI.",
    version="1.0.0"
)

app.include_router(api_router)