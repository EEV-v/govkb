"""Scaffold placeholder bullets that should never be treated as durable memory."""

from __future__ import annotations

import re


SCAFFOLD_BULLETS = {
    "- TODO: add durable guidance for this capability.",
    "- TODO: define the capability scope, users, default behavior, and boundaries.",
    "- TODO: add recurring workflow steps after bootstrap or repeated evidence.",
    "- TODO: add recurring workflow steps only after candidate facts, bootstrap, or repeated repo evidence support them.",
    "- TODO: add durable validation commands, working directories, and evidence expectations.",
    "- TODO: add repo-relative code, test, and docs locations after bootstrap or repeated evidence.",
    "- TODO: add repo-relative code, test, and docs locations that future sessions should inspect first.",
    "- TODO: add precedence rules for conflicts between governed files, docs, and local context.",
    "- TODO: add precedence rules for conflicts between governed files, docs, candidate facts, and local context.",
    "- Add recurring project workflows here after they prove reusable across sessions.",
    "- Add stable verification commands here when they are useful beyond one task.",
    "- Add project-specific conventions here when they affect how future work should be done.",
    "- Add repo-relative code, test, and docs locations here when they are useful beyond one task.",
    "- Add authority rules here when one governed file should win over broader docs.",
    "- Track repeated specialized work as a candidate governed capability instead of expanding this broad steward indefinitely.",
    "- Add stable workflow steps here after bootstrap or repeated evidence.",
    "- Add durable verification commands here after bootstrap or repeated evidence.",
    "- Add repo-relative code and docs locations here after bootstrap or repeated evidence.",
    "- Use this section for stable capability-specific operating rules after activation.",
    "- Use this section for recurring project workflow patterns observed across sessions.",
    "- Use this section for durable validation commands, evidence expectations, and safety checks.",
    "- Use this section for durable repo-relative code, test, and docs locations.",
    "- Use this section for durable authority rules when one governed source should win.",
}

SCAFFOLD_BULLET_PATTERNS = (
    re.compile(r"^-\s*TODO:", re.I),
    re.compile(r"^-\s*Use this section\b", re.I),
)


def is_scaffold_bullet(line: str) -> bool:
    """Return True when a bullet is template filler, not durable knowledge."""
    stripped = line.strip()
    return stripped in SCAFFOLD_BULLETS or any(pattern.search(stripped) for pattern in SCAFFOLD_BULLET_PATTERNS)
