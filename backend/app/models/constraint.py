"""Constraint database model."""

from typing import Optional

from sqlmodel import Field, SQLModel


class Constraint(SQLModel, table=True):
    """User-defined scheduling rule (protected_block, max_continuous_work, etc)."""

    __tablename__ = "constraints"

    id: Optional[int] = Field(default=None, primary_key=True)
    constraint_type: str
    day_of_week: Optional[int] = None
    start_minutes: Optional[int] = None
    end_minutes: Optional[int] = None
    value: Optional[int] = None  # e.g. max minutes for max_continuous_work
    metadata_json: Optional[str] = None
