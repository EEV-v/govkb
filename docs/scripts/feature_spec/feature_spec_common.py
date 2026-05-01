from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

DEFAULT_FEATURE_ROOT = Path("docs/governed-skill-knowledge-framework/features")
DEFAULT_SPEC_COOKBOOK_ROOT = Path("docs/FEATURE_SPEC_COOKBOOK")
DEFAULT_SPEC_KB_FILE = DEFAULT_SPEC_COOKBOOK_ROOT / "spec-knowledge-base.md"
TRACKING_LINE_RE = re.compile(r"^- (?P<label>[^:]+): `?(?P<id>[^` ]+)`? (?P<url>https?://\S+)\s*$")
SECTION_RE_TEMPLATE = r"(?ms)^## {heading}\s*\n(?P<body>.*?)(?=^## |\Z)"
REVIEWED_DOC_RE = re.compile(r"\(Reviewed (?P<date>[^)]+)\)\.docx\.md$", re.IGNORECASE)
QUESTION_LINE_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(?P<text>.+?)\s*$")
DECISION_STATUS_VALUES = ("Open", "Approved", "Deferred", "Rejected")
QUESTION_STATUS_VALUES = ("Blocking", "Deferred", "Resolved", "Assumption")
ROUND_STATE_FILENAME = "reconciliation-state.json"

SOURCE_DOC_EXTENSIONS = (".md", ".txt", ".docx.md")
FEEDBACK_KIND_PRIORITIES = {
    "reviewed_doc": 300,
    "feedback_doc": 220,
    "feedback_summary": 140,
}
FEEDBACK_DOC_KEYWORDS = (
    "review",
    "reviewed",
    "feedback",
    "comment",
    "comments",
    "response",
    "responses",
    "question",
    "questions",
    "note",
    "notes",
)
FEEDBACK_SUMMARY_KEYWORDS = ("changes", "delta", "diff", "redline")
GENERATED_SPEC_FILENAMES = {
    "business.md",
    "business-context.md",
    "context.md",
    "spec-brief.md",
    "open-questions.md",
    "decision-log.md",
    "business-review-pack.md",
    "business-review-message.md",
    "scope-lock.md",
    "spec-handoff.md",
    "use-cases.md",
    "poc-output.md",
    "poc-output.sql",
    "requirements-catalog.md",
    "implementation-plan.md",
    "decomposition.md",
    "decomposition-backup.md",
}
RECONCILIATION_STATUS_LABELS = {
    "Classification complete": "classificationComplete",
    "Promote source document as canonical": "promoteSourceDocument",
    "Canonical business.md updated manually": "canonicalUpdatedManually",
    "Round processed": "roundProcessed",
}
DEFAULT_RECONCILIATION_STATUS = {
    "classificationComplete": False,
    "promoteSourceDocument": False,
    "canonicalUpdatedManually": False,
    "roundProcessed": False,
}


def resolve_repo_root(raw_value: Optional[str]) -> Path:
    if raw_value:
        path = Path(raw_value).expanduser().resolve()
        if not is_govkb_repo_root(path):
            raise RuntimeError(f"Repo root does not look like a GovKB checkout: {path}")
        return path

    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if is_govkb_repo_root(candidate):
            return candidate
    raise RuntimeError("Could not resolve GovKB repo root.")


def is_govkb_repo_root(path: Path) -> bool:
    return (
        (path / "pyproject.toml").exists()
        and ((path / "src/govkb").exists() or (path / DEFAULT_FEATURE_ROOT).exists())
    ) or (path / DEFAULT_FEATURE_ROOT).exists()


def resolve_feature_dir(repo_root: Path, feature_reference: str) -> Path:
    reference = Path(feature_reference).expanduser()
    if reference.is_absolute() or feature_reference.startswith(".") or "/" in feature_reference:
        path = reference.resolve()
    else:
        path = (repo_root / DEFAULT_FEATURE_ROOT / feature_reference).resolve()
    if not path.exists():
        raise RuntimeError(f"Feature folder not found: {path}")
    return path


def read_text_if_exists(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def tokenize(value: str) -> List[str]:
    return [token for token in re.findall(r"[A-Za-z0-9]{3,}", value.casefold()) if token]


def slug_to_title(slug: str) -> str:
    spaced = re.sub(r"[_-]+", " ", slug)
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", spaced)
    spaced = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", spaced)
    words = [part for part in spaced.split() if part]
    normalized: List[str] = []
    for word in words:
        normalized.append(word if word.isupper() else word.capitalize())
    return " ".join(normalized)


def extract_heading_title(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if re.fullmatch(r"\*\*.+\*\*", stripped):
            return stripped.strip("*").strip()
    return None


def extract_summary_paragraph(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    lines = [line.rstrip() for line in text.splitlines()]
    after_title = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            after_title = True
            continue
        if not after_title or not stripped or stripped.startswith("## "):
            continue
        return stripped
    return None


def get_standard_paths(feature_dir: Path) -> Dict[str, Path]:
    review_rounds = feature_dir / "review-rounds"
    return {
        "business": feature_dir / "business.md",
        "business_context": feature_dir / "business-context.md",
        "context": feature_dir / "context.md",
        "spec_brief": feature_dir / "spec-brief.md",
        "open_questions": feature_dir / "open-questions.md",
        "decision_log": feature_dir / "decision-log.md",
        "review_pack": feature_dir / "business-review-pack.md",
        "review_message": feature_dir / "business-review-message.md",
        "scope_lock": feature_dir / "scope-lock.md",
        "spec_handoff": feature_dir / "spec-handoff.md",
        "review_rounds": review_rounds,
        "round_state": review_rounds / ROUND_STATE_FILENAME,
    }


def ensure_tracking_block(content: str, tracking_lines: Sequence[str]) -> str:
    tracking_block = "## Tracking\n" + "\n".join(tracking_lines)
    pattern = re.compile(r"(?ms)^## Tracking\s*\n.*?(?=^## |\Z)")
    if pattern.search(content):
        updated = pattern.sub(tracking_block + "\n\n", content, count=1)
        return re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"

    title_match = re.search(r"(?m)^# .+$", content)
    if title_match:
        insert_at = title_match.end()
        updated = content[:insert_at] + "\n\n" + tracking_block + "\n\n" + content[insert_at:].lstrip("\n")
        return re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"

    return tracking_block + "\n\n" + content.lstrip()


def parse_tracking_block(content: Optional[str]) -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}
    if not content:
        return result
    for line in content.splitlines():
        match = TRACKING_LINE_RE.match(line.strip())
        if not match:
            continue
        result[match.group("label")] = {"id": match.group("id"), "url": match.group("url")}
    return result


def list_reviewed_docs(feature_dir: Path) -> List[Path]:
    files = [path for path in feature_dir.iterdir() if path.is_file() and REVIEWED_DOC_RE.search(path.name)]
    return sorted(files, key=lambda path: feedback_sort_key(build_feedback_candidate(feature_dir, path)))


def latest_reviewed_doc(feature_dir: Path) -> Optional[Path]:
    docs = list_reviewed_docs(feature_dir)
    return docs[0] if docs else None


def reviewed_doc_label(path: Path) -> str:
    match = REVIEWED_DOC_RE.search(path.name)
    if match:
        return match.group("date")
    return path.stem


def latest_change_log(feature_dir: Path) -> Optional[Path]:
    review_rounds = get_standard_paths(feature_dir)["review_rounds"]
    if not review_rounds.exists():
        return None
    files = sorted(review_rounds.glob("*-changes.md"), key=lambda path: path.stat().st_mtime, reverse=True)
    return files[0] if files else None


def extract_section_body(content: Optional[str], heading: str) -> Optional[str]:
    if not content:
        return None
    pattern = re.compile(SECTION_RE_TEMPLATE.format(heading=re.escape(heading)))
    match = pattern.search(content)
    return match.group("body").strip() if match else None


def extract_question_lines(content: Optional[str]) -> List[str]:
    body = extract_section_body(content, "Open Questions")
    if not body:
        return []
    questions: List[str] = []
    raw_lines = body.splitlines()
    top_level_numbered = [line for line in raw_lines if re.match(r"^\d+\.\s+", line.strip()) and line == line.lstrip()]
    top_level_bullets = [line for line in raw_lines if re.match(r"^[-*]\s+", line.strip()) and line == line.lstrip()]
    candidate_lines = top_level_numbered or top_level_bullets
    for line in candidate_lines:
        match = QUESTION_LINE_RE.match(line)
        if not match:
            continue
        text = match.group("text").strip()
        if text:
            questions.append(text)
    return questions


def clean_inline_markdown(text: str) -> str:
    cleaned = re.sub(r"`([^`]+)`", r"\1", text)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def derive_feature_title(feature_dir: Path, explicit_title: Optional[str] = None) -> str:
    if explicit_title:
        return explicit_title.strip()
    business_text = read_text_if_exists(feature_dir / "business.md")
    title = extract_heading_title(business_text)
    if title:
        return clean_inline_markdown(title)
    return slug_to_title(feature_dir.name)


def split_markdown_row(line: str) -> List[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    inner = stripped[1:]
    if inner.endswith("|"):
        inner = inner[:-1]

    cells: List[str] = []
    current: List[str] = []
    escaped = False
    for char in inner:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def parse_markdown_table(text: Optional[str]) -> List[Dict[str, str]]:
    if not text:
        return []
    lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return []
    headers = split_markdown_row(lines[0])
    if not headers:
        return []
    rows: List[Dict[str, str]] = []
    for line in lines[2:]:
        values = split_markdown_row(line)
        if len(values) != len(headers):
            continue
        if values == headers:
            continue
        if all(re.fullmatch(r":?-+:?", value.replace(" ", "")) for value in values):
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def table_id_number(raw_value: str, prefix: str) -> Optional[int]:
    match = re.fullmatch(rf"{re.escape(prefix)}(?P<number>\d+)", (raw_value or "").strip())
    if not match:
        return None
    return int(match.group("number"))


def next_table_id(rows: Sequence[Dict[str, str]], prefix: str) -> str:
    numbers = [
        table_id_number(row.get("ID", ""), prefix)
        for row in rows
    ]
    next_number = max((number for number in numbers if number is not None), default=0) + 1
    return f"{prefix}{next_number}"


def merge_source_values(existing: str, new_value: str) -> str:
    parts: List[str] = []
    for candidate in [existing, new_value]:
        if not candidate:
            continue
        for piece in [part.strip() for part in candidate.split(";")]:
            if piece and piece not in parts:
                parts.append(piece)
    return "; ".join(parts)


def build_question_table(feature_title: str, questions: Sequence[str], source_path: str) -> str:
    lines = [
        f"# Open Questions — {feature_title}",
        "",
        f"Last updated: {today_iso()}",
        "",
        "| ID | Question | Status | Blocking | Owner | Source | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    if not questions:
        lines.append("| Q1 | No explicit open questions captured yet. | Assumption | No | TBD | Generated | Add questions during the next review round. |")
    else:
        for index, question in enumerate(questions, start=1):
            lines.append(
                f"| Q{index} | {escape_table(question)} | Blocking | Yes | TBD | {escape_table(source_path)} | Needs business answer or deferral. |"
            )
    return "\n".join(lines) + "\n"


def build_decision_table(feature_title: str, candidate_decisions: Sequence[str]) -> str:
    lines = [
        f"# Decision Log — {feature_title}",
        "",
        f"Last updated: {today_iso()}",
        "",
        "| ID | Decision / Candidate | Status | Owner | Source | Notes |",
        "|---|---|---|---|---|---|",
    ]
    if not candidate_decisions:
        lines.append("| D1 | No explicit decisions recorded yet. | Open | TBD | Generated | Use this file to capture approved scope decisions between business rounds. |")
    else:
        for index, decision in enumerate(candidate_decisions, start=1):
            lines.append(
                f"| D{index} | {escape_table(decision)} | Open | TBD | business.md | Promote to Approved / Deferred / Rejected during review. |"
            )
    return "\n".join(lines) + "\n"


def extract_decision_candidates(content: Optional[str]) -> List[str]:
    if not content:
        return []
    headings = [
        "Effective Value Logic",
        "Admission and Update Logic",
        "Non-goals",
        "Override Governance",
        "Lifecycle Management",
    ]
    candidates: List[str] = []
    for heading in headings:
        body = extract_section_body(content, heading)
        if not body:
            continue
        for line in body.splitlines():
            match = QUESTION_LINE_RE.match(line)
            if not match:
                continue
            text = clean_inline_markdown(match.group("text"))
            if text:
                candidates.append(f"{heading}: {text}")
    return candidates[:12]


def escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def today_iso() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def build_tracking_lines(trackers: Sequence[Dict[str, str]]) -> List[str]:
    lines: List[str] = []
    for tracker in trackers:
        label = (tracker.get("label") or "Tracker").strip()
        identifier = (tracker.get("id") or "").strip()
        url = (tracker.get("url") or "").strip()
        if not identifier or not url:
            continue
        lines.append(f"- {label}: `{identifier}` {url}")
    return lines


def append_or_replace_section(content: str, heading: str, body: str) -> str:
    section = f"## {heading}\n{body.strip()}"
    pattern = re.compile(SECTION_RE_TEMPLATE.format(heading=re.escape(heading)))
    if pattern.search(content):
        updated = pattern.sub(section + "\n\n", content, count=1)
        return re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"
    return content.rstrip() + "\n\n" + section + "\n"


def parse_date_hint(value: str) -> Optional[str]:
    value = value.strip()
    if not value:
        return None

    iso_match = re.search(r"(?P<year>20\d{2})[-_. /](?P<month>\d{1,2})[-_. /](?P<day>\d{1,2})", value)
    if iso_match:
        try:
            return date(
                int(iso_match.group("year")),
                int(iso_match.group("month")),
                int(iso_match.group("day")),
            ).isoformat()
        except ValueError:
            pass

    us_match = re.search(r"(?P<month>\d{1,2})[._/ -](?P<day>\d{1,2})[._/ -](?P<year>\d{2,4})", value)
    if us_match:
        year = int(us_match.group("year"))
        if year < 100:
            year += 2000
        try:
            return date(year, int(us_match.group("month")), int(us_match.group("day"))).isoformat()
        except ValueError:
            pass
    return None


def review_round_label(path: Path) -> str:
    stem = path.stem.replace(".docx", "")
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").casefold()
    return stem or "review-round"


def fingerprint_path(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def build_review_round_paths(feature_dir: Path, source_path: Path) -> Dict[str, Path]:
    review_rounds = get_standard_paths(feature_dir)["review_rounds"]
    label = review_round_label(source_path)
    if source_path.name.lower().endswith(".docx.md"):
        snapshot_name = f"{label}-reviewed.docx.md"
    else:
        snapshot_name = f"{label}-feedback{source_path.suffix or '.md'}"
    return {
        "snapshot": review_rounds / snapshot_name,
        "change_log": review_rounds / f"{label}-changes.md",
        "reconciliation": review_rounds / f"{label}-reconciliation.md",
        "label": review_rounds / f"{label}",
    }


def default_review_state() -> Dict[str, Any]:
    return {"rounds": {}}


def read_review_state(feature_dir: Path) -> Dict[str, Any]:
    state_path = get_standard_paths(feature_dir)["round_state"]
    if not state_path.exists():
        return default_review_state()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_review_state()
    if not isinstance(data, dict) or not isinstance(data.get("rounds"), dict):
        return default_review_state()
    return data


def write_review_state(feature_dir: Path, state: Dict[str, Any]) -> None:
    state_path = get_standard_paths(feature_dir)["round_state"]
    write_text(state_path, json.dumps(state, indent=2, ensure_ascii=False))


def parse_reconciliation_status(content: Optional[str]) -> Dict[str, bool]:
    status = dict(DEFAULT_RECONCILIATION_STATUS)
    if not content:
        return status
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        label, raw_value = stripped[2:].split(":", 1)
        mapped = RECONCILIATION_STATUS_LABELS.get(label.strip())
        if not mapped:
            continue
        status[mapped] = raw_value.strip().lower().startswith("yes")
    return status


def get_round_state_entry(feature_dir: Path, round_key: str) -> Optional[Dict[str, Any]]:
    return read_review_state(feature_dir).get("rounds", {}).get(round_key)


def get_round_state_for_source(feature_dir: Path, source_path: Path) -> Optional[Dict[str, Any]]:
    round_key = review_round_label(source_path)
    state = get_round_state_entry(feature_dir, round_key)
    if not state:
        return None
    return state


def update_round_state(feature_dir: Path, round_key: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    state = read_review_state(feature_dir)
    rounds = state.setdefault("rounds", {})
    rounds[round_key] = entry
    write_review_state(feature_dir, state)
    return entry


def detect_feedback_kind(path: Path) -> Optional[str]:
    lowered = path.name.casefold()
    if path.name in GENERATED_SPEC_FILENAMES:
        return None
    if lowered.endswith(ROUND_STATE_FILENAME.casefold()):
        return None
    if path.name.lower().endswith(".sql"):
        return None
    if not any(path.name.lower().endswith(ext) for ext in SOURCE_DOC_EXTENSIONS):
        return None
    if REVIEWED_DOC_RE.search(path.name):
        return "reviewed_doc"
    if any(keyword in lowered for keyword in FEEDBACK_DOC_KEYWORDS):
        return "feedback_doc"
    if any(keyword in lowered for keyword in FEEDBACK_SUMMARY_KEYWORDS):
        return "feedback_summary"
    return None


def build_feedback_candidate(feature_dir: Path, path: Path) -> Dict[str, Any]:
    kind = detect_feedback_kind(path)
    if kind is None:
        raise RuntimeError(f"Path is not a feedback candidate: {path}")

    round_key = review_round_label(path)
    round_paths = build_review_round_paths(feature_dir, path)
    state_entry = get_round_state_for_source(feature_dir, path) or {}
    reconciliation_text = read_text_if_exists(round_paths["reconciliation"])
    reconciliation_status = parse_reconciliation_status(reconciliation_text)
    date_hint = None
    reviewed_match = REVIEWED_DOC_RE.search(path.name)
    if reviewed_match:
        date_hint = parse_date_hint(reviewed_match.group("date"))
    if not date_hint:
        date_hint = parse_date_hint(path.name)

    return {
        "path": str(path),
        "name": path.name,
        "kind": kind,
        "roundKey": round_key,
        "dateHint": date_hint,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "priority": FEEDBACK_KIND_PRIORITIES.get(kind, 0),
        "snapshotPath": str(round_paths["snapshot"]),
        "changeLogPath": str(round_paths["change_log"]),
        "reconciliationPath": str(round_paths["reconciliation"]),
        "stateStatus": state_entry.get("status", "new"),
        "reconciliationStatus": reconciliation_status,
        "processed": bool(reconciliation_status.get("roundProcessed") or state_entry.get("status") == "reconciled"),
        "canonicalUpdated": bool(
            reconciliation_status.get("promoteSourceDocument")
            or reconciliation_status.get("canonicalUpdatedManually")
            or state_entry.get("canonicalUpdated")
        ),
    }


def feedback_sort_key(candidate: Dict[str, Any]) -> Tuple[int, int, int, float, str]:
    processed_rank = 1 if candidate.get("processed") else 0
    date_hint = candidate.get("dateHint") or "0000-00-00"
    timestamp = datetime.fromisoformat(candidate["mtime"]).timestamp()
    return (
        processed_rank,
        -int(date_hint.replace("-", "")) if date_hint and date_hint != "0000-00-00" else 0,
        -timestamp,
        -int(candidate.get("priority", 0)),
        candidate.get("name", ""),
    )


def list_feedback_candidates(feature_dir: Path, *, include_processed: bool = True) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for path in feature_dir.iterdir():
        if not path.is_file():
            continue
        kind = detect_feedback_kind(path)
        if kind is None:
            continue
        candidate = build_feedback_candidate(feature_dir, path)
        if not include_processed and candidate.get("processed"):
            continue
        candidates.append(candidate)
    return sorted(candidates, key=feedback_sort_key)


def latest_feedback_candidate(feature_dir: Path, *, include_processed: bool = False) -> Optional[Dict[str, Any]]:
    candidates = list_feedback_candidates(feature_dir, include_processed=include_processed)
    return candidates[0] if candidates else None


def latest_feedback_doc(feature_dir: Path) -> Optional[Path]:
    candidate = latest_feedback_candidate(feature_dir, include_processed=False)
    if candidate:
        return Path(candidate["path"])
    candidate = latest_feedback_candidate(feature_dir, include_processed=True)
    return Path(candidate["path"]) if candidate else None


def review_round_status(feature_dir: Path, source_path: Path) -> Dict[str, Any]:
    candidate = build_feedback_candidate(feature_dir, source_path)
    return {
        "roundKey": candidate["roundKey"],
        "sourcePath": candidate["path"],
        "changeLogPath": candidate["changeLogPath"],
        "reconciliationPath": candidate["reconciliationPath"],
        "processed": candidate["processed"],
        "canonicalUpdated": candidate["canonicalUpdated"],
        "reconciliationStatus": candidate["reconciliationStatus"],
        "stateStatus": candidate["stateStatus"],
    }


def set_reconciliation_status(content: str, **overrides: bool) -> str:
    updated = content
    for label, key in RECONCILIATION_STATUS_LABELS.items():
        if key not in overrides:
            continue
        value = "Yes" if overrides[key] else "No"
        pattern = re.compile(rf"(?m)^- {re.escape(label)}: (?:Yes|No)\s*$")
        replacement = f"- {label}: {value}"
        if pattern.search(updated):
            updated = pattern.sub(replacement, updated, count=1)
        else:
            updated = updated.rstrip() + f"\n{replacement}\n"
    return updated
