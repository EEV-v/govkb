"""Policy helpers for governed memory quality gates."""

from __future__ import annotations

import re


GENERIC_CAPABILITY_TOKENS = (
    "bugfix",
    "cookbook",
    "curator",
    "delivery",
    "devops",
    "guard",
    "matcher",
    "project-knowledge-steward",
    "qa",
    "replay",
    "review",
    "staging",
    "steward",
    "sync",
    "tracker",
    "workflow",
)


FEATURE_DECISION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\b(fields? such as|field lists?|acceptance criteria|request shape|operator fields such as)\b"),
    re.compile(
        r"(?i)\b(reason codes?|selected[- ]error|source-to-error|error-to-destination|cash[_ -]only|"
        r"shares[_ -]and[_ -]cash|position[_ -]only)\b"
    ),
    re.compile(
        r"(?i)\b(route securities|route positions?|post cash|persist .*lot|auto-close .*matching|"
        r"enable .*field|drive .*date)\b"
    ),
    re.compile(r"(?i)\b(Trade Error|Golden|OMS|CUSIP|ISIN|Corporate Action|CorporateAction|TransactionLot|TaxForm|Edocs|eDocs)\b"),
    re.compile(r"\b[A-Z0-9]{2,}_[A-Z0-9_]{2,}\b"),
    re.compile(r"\b(?:GS|CUSIP|ISIN)-?[A-Z0-9]{4,}\b"),
)


def is_generic_memory_capability(capability_id: str | None) -> bool:
    """Return true for broad workflow capabilities that should avoid mutable product decisions."""
    normalized = (capability_id or "").strip().lower()
    if not normalized:
        return True
    return any(token in normalized for token in GENERIC_CAPABILITY_TOKENS)


def feature_specific_decision_reason(lesson: str, capability_id: str | None = None) -> str | None:
    """Return a staging reason when generic memory looks like a mutable feature decision."""
    if not is_generic_memory_capability(capability_id):
        return None

    text = lesson.strip()
    if not text:
        return None

    for pattern in FEATURE_DECISION_PATTERNS:
        if pattern.search(text):
            return (
                "lesson appears to encode mutable feature or product behavior; "
                "rewrite as stable system/process guidance or route to a domain-specific capability"
            )
    return None
