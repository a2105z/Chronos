"""Shared utilities for API handlers."""


def applyPartialUpdate(model: object, data: dict) -> None:
    """Apply only the provided fields from data onto the model."""
    for key, value in data.items():
        setattr(model, key, value)
