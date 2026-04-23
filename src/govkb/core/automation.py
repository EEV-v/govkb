"""Project automation policy helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AutomationPolicy:
    """Project-level governed automation controls."""

    auto_create_capabilities: bool = False
    auto_create_min_occurrences: int = 2


def automation_policy_from_manifest(project_manifest: dict[str, Any] | None) -> AutomationPolicy:
    """Return normalized automation policy from a governed project manifest."""
    if not isinstance(project_manifest, dict):
        return AutomationPolicy()
    automation = project_manifest.get("automation")
    if not isinstance(automation, dict):
        return AutomationPolicy()

    enabled = automation.get("auto_create_capabilities")
    min_occurrences = automation.get("auto_create_min_occurrences")

    normalized_enabled = enabled if isinstance(enabled, bool) else False
    normalized_min_occurrences = (
        min_occurrences
        if isinstance(min_occurrences, int) and not isinstance(min_occurrences, bool) and min_occurrences >= 2
        else 2
    )
    return AutomationPolicy(
        auto_create_capabilities=normalized_enabled,
        auto_create_min_occurrences=normalized_min_occurrences,
    )
