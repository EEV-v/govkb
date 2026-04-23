"""Identifier helpers for governed objects."""

from __future__ import annotations

import re


def normalize_identifier(value: str) -> str:
    """Normalize a user-facing name into a governed identifier."""
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "project"
