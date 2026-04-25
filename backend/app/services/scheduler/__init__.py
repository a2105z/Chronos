from typing import Any

__all__ = ["SchedulingEngine"]


def __getattr__(name: str) -> Any:
    if name == "SchedulingEngine":
        from app.services.scheduler.engine import SchedulingEngine

        return SchedulingEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
