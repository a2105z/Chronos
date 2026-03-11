"""Chronos API - FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import createDbAndTables, getSession
from app.api import tasks, availability, schedule, constraints


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    createDbAndTables()
    yield


app = FastAPI(
    title="Chronos API",
    description="Constraint-aware time blocking engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(availability.router)
app.include_router(constraints.router)
app.include_router(schedule.router)


@app.get("/")
def root() -> dict:
    """Health check."""
    return {"service": "Chronos API", "status": "ok"}
