"""Prompt rendering for governed capability KB initialization."""

from __future__ import annotations


def initialize_kb_prompt_text(
    *,
    capability_id: str,
    capability_name: str | None = None,
    summary: str | None = None,
    scope_summary: str | None = None,
    memory_path: str = "references/long-term-memory.md",
    candidate_id: str | None = None,
) -> str:
    """Render the active-session prompt used to initialize capability memory."""
    title = capability_name or capability_id.replace("-", " ").title()
    candidate_lines: list[str] = []
    if candidate_id:
        candidate_lines.extend(
            [
                f"- Candidate: `{candidate_id}`",
                f"- Candidate metadata: `.governed/candidates/{candidate_id}/candidate.toml`",
                f"- Candidate evidence: `.governed/candidates/{candidate_id}/evidence.md`",
            ]
        )
    else:
        candidate_lines.append("- Candidate evidence: none; initialize only from the current contract and repo facts.")

    summary_lines: list[str] = []
    if summary:
        summary_lines.append(f"- Summary: {summary}")
    if scope_summary:
        summary_lines.append(f"- Scope: {scope_summary}")

    return (
        f"# Initialize KB: {title}\n\n"
        "Use this prompt in an active assistant session after the governed capability is created.\n\n"
        "## Context\n\n"
        f"- Capability: `{capability_id}`\n"
        f"- Contract: `.governed/capabilities/{capability_id}/capability.contract.toml`\n"
        f"- Instructions: `.governed/capabilities/{capability_id}/instructions.md`\n"
        f"- Memory: `.governed/capabilities/{capability_id}/{memory_path}`\n"
        + ("\n".join(candidate_lines) + "\n")
        + ("\n".join(summary_lines) + "\n" if summary_lines else "")
        + "\n"
        "## Task\n\n"
        "1. Read the capability contract, instructions, current memory, and candidate evidence if it exists.\n"
        "2. Inspect only repo files directly needed to verify stable facts for this capability.\n"
        "3. Append the minimal durable KB entries that will improve future sessions.\n"
        "4. Keep each entry short, reusable, and scoped to this capability.\n"
        "5. Run `govkb validate` for the project after changes.\n\n"
        "## Governance\n\n"
        "- Do not store secrets, bearer tokens, API keys, passwords, or copied credential values.\n"
        "- Do not store local-only absolute paths unless they are part of the governed repo contract.\n"
        "- Do not store one-off task status, report output, or session narration.\n"
        "- Prefer append-only memory changes; do not rewrite accepted KB unless a fact is clearly wrong.\n"
        "- If evidence is thin, leave the KB minimal and report that no durable update was made.\n\n"
        "## Output\n\n"
        "- List memory bullets added or say `No KB update`.\n"
        "- List repo files used as evidence.\n"
        "- List validation command and result.\n"
    )
