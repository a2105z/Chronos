from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, auth, availability, constraints, schedule, tasks
from app.core.config import getSettings
from app.db import createDbAndTables, seedDemoUserIfNeeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables, migrate columns, and seed demo user on startup."""
    createDbAndTables()
    seedDemoUserIfNeeded()
    yield


settings = getSettings()

app = FastAPI(
    title="Chronos API",
    description="AI-native constraint-aware time blocking for internship recruiting",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(availability.router)
app.include_router(constraints.router)
app.include_router(schedule.router)
app.include_router(ai.router)


@app.get("/")
def root() -> dict:
    """Health check."""
    return {"service": "Chronos API", "status": "ok", "version": "1.0.0"}
