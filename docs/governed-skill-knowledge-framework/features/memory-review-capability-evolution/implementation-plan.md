# Memory Review Capability Evolution - Implementation Plan

Last updated: 2026-05-28

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | Main argparse surface | `src/govkb/cli.py` | Add a `proposals` subcommand family beside `candidates`; keep existing command names stable. |
| Public memory-review wrapper | Codex adapter launcher | `src/govkb/commands/review_memory.py` | Reuse existing model/reasoning, inventory, progress, session-file, and project-root forwarding. |
| Codex memory-review adapter | Classifier schema, prompt, validation, report, progress, staging | `src/govkb/adapters/codex/bin/codex-memory-review` | Extend current path instead of creating a parallel review engine. |
| Memory-review helper tests | Import packaged scheduler script with `SourceFileLoader` | `tests/test_memory_review.py` | Add proposal schema/report/process tests using the same import pattern. |
| Candidate commands | New capability candidate UX | `src/govkb/commands/candidates.py` | Leave scoped to `.governed/candidates`; do not add proposal behavior here. |
| Candidate core | New capability candidate staging and approval helpers | `src/govkb/core/candidates.py` | Reuse only patterns for TOML metadata, summaries, redaction, and temp-dir tests. |
| Project contracts | Project bundle and capability contract loading | `src/govkb/core/contracts.py` | Use `load_project_bundle` to verify target capability ids and capability roots. |
| Strict validation | Governed package/tool safety checks | `src/govkb/core/governed_skill.py`, `src/govkb/commands/validate.py` | Reuse after proposal apply; do not execute proposal-owned scripts during validation. |
| New proposal core | Proposal model, validation, list/show/apply helpers | New `src/govkb/core/proposals.py` | New file is justified because proposals are neither memory lessons nor new capability candidates. |
| New proposal command | `govkb proposals list/show/apply` | New `src/govkb/commands/proposals.py` | Match existing command-function pattern and JSON/text output style. |
| Tests | Proposal CLI/core/use-case tests | New `tests/test_proposals.py`, new `tests/test_memory_review_capability_evolution_use_cases.py`, new `tests/test_memory_review_capability_evolution_smoke.py` | Use `unittest`, `tempfile.TemporaryDirectory`, direct command functions, and synthetic classifier data. |
| Docs | Feature artifacts | `docs/governed-skill-knowledge-framework/features/memory-review-capability-evolution/**` | Keep traceability through use cases, PoC, plan review, and later parity review. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Spec handoff ready | Done | Product/Engineering |
| Blocking questions resolved | Done | Product/Engineering |
| Current command baseline captured | Done | Engineering |
| Targeted nearby tests pass | Done | Engineering |
| Raw transcript fixtures excluded | Required | Engineering |
| Production code changes approved by `review.md` | Required before implementation | Engineering |

## 1. Scope And Boundaries

Implement the first capability-evolution proposal lane:

- Add classifier contract support for `capability_evolution_proposals`.
- Validate and stage proposal metadata under `.governed/review-proposals/<proposal-id>/`.
- Add report/progress visibility for proposal counts and rows.
- Add `govkb proposals list`, `show`, and `apply`.
- Apply only approved proposals and only to `.governed/capabilities/<capability-id>/`.
- Preserve current memory lessons, semantic new-capability candidates, strict validation, cron behavior, and existing CLI contracts.

Out of scope:

- Auto-applying proposals from cron.
- Auto-creating new governed capabilities through the proposal lane.
- A VS Code proposal review UI.
- External tracker changes.
- Full script generation from natural language without approved bounded output content.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-MRCE-01 | Add `capability_evolution_proposals` to classifier schema and result parsing. | `codex-memory-review` | Modify | Keep `candidates` and `semantic_candidate` backward-compatible. |
| REQ-MRCE-02 | Empty proposal arrays preserve current behavior. | `codex-memory-review`, tests | Modify/Test | Default to empty list when absent during transition if needed. |
| REQ-MRCE-03 | Stage valid proposals under `.governed/review-proposals/<proposal-id>/`. | `src/govkb/core/proposals.py`, `codex-memory-review` | New/Modify | Write repo-owned metadata only in non-dry-run review mode. |
| REQ-MRCE-04 | Keep new capability candidates on `.governed/candidates/`. | `src/govkb/commands/candidates.py`, `codex-memory-review` | Preserve/Modify | Missing target capability proposal rows reject or route to semantic candidate logic. |
| REQ-MRCE-05 | Add `govkb proposals list/show/apply`. | `src/govkb/cli.py`, `src/govkb/commands/proposals.py` | Modify/New | Provide text output first; add `--json` to list/show if useful for extension parity. |
| REQ-MRCE-06 | Always consider high-confidence proposal opportunities. | `prompt_for_session()` | Modify | Use existing `--codex-reasoning` for manual higher-reasoning runs. |
| REQ-MRCE-07 | Cron stages only and never writes executable files. | `codex-memory-review`, `src/govkb/core/proposals.py` | Modify/New | Proposal staging writes metadata/draft body, not final executable output. |
| REQ-MRCE-08 | Apply requires complete approval metadata. | `src/govkb/core/proposals.py`, `commands/proposals.py` | New | Required fields gate all file writes. |
| REQ-MRCE-09 | Output paths must stay under target capability package. | `src/govkb/core/proposals.py` | New | Resolve paths and reject absolute paths, parent traversal, symlinks outside root, and wrong capability roots. |
| REQ-MRCE-10 | Support `script`, `wrapper`, `prompt`, `runbook`, `instructions_update`. | `src/govkb/core/proposals.py`, tests | New | Unsupported types reject. |
| REQ-MRCE-11 | Mutating scripts/wrappers require preview or dry-run behavior. | `src/govkb/core/proposals.py` | New | Validate metadata and draft content before write. |
| REQ-MRCE-12 | Reject raw transcript, secrets, credentials, customer/prod evidence. | `codex-memory-review`, `src/govkb/core/proposals.py` | Modify/New | Reuse existing redaction/sensitive patterns where possible. |
| REQ-MRCE-13 | Reports include a proposal section. | `write_report()` | Modify | Include proposal rows and rejected proposal rows. |
| REQ-MRCE-14 | Reuse strict validation after apply. | `commands/proposals.py`, `core/proposals.py` | New | Run or invoke validation result before marking applied. |
| REQ-MRCE-15 | Maintain source review/session traceability without raw session storage. | `core/proposals.py`, report | New/Modify | Store source session id, thread name if safe, review run id, and evidence summary. |

## 3. Design

### Proposal Metadata

Store one proposal folder per proposal:

```text
<project-root>/.governed/review-proposals/<proposal-id>/
  proposal.toml
  proposal.md
  draft-output.md
```

`proposal.toml` should be the command source of truth:

```toml
schema_version = 1
id = "proposal-id"
status = "staged"
created_at = "2026-05-28T00:00:00Z"
source_run_id = "2026-05-28T000000Z"
source_session_id = "session-id"
target_capability = "clearing-bugfix-cookbook"
proposal_type = "script"
safety_class = "read_only"
output_paths = [".governed/capabilities/clearing-bugfix-cookbook/tools/scripts/example.py"]
verification_command = "PYTHONPATH=src python3 -m govkb.cli validate --strict <project-root> --json"

[approval]
status = "pending"
approver = ""
approved_at = ""
```

`proposal.md` contains review text only:

- Purpose.
- Inputs and outputs.
- Evidence summary.
- Safety notes.
- Why cron did not apply it.
- Suggested maintainer action.

`draft-output.md` can carry proposed text or script content for manual review. The first implementation should keep content explicit and bounded; it should not regenerate code at apply time from raw session text.

### Classifier Contract

Extend the schema with:

```json
"capability_evolution_proposals": [
  {
    "proposal_id": "string",
    "target_capability": "string",
    "proposal_type": "script|wrapper|prompt|runbook|instructions_update",
    "output_paths": ["string"],
    "purpose": "string",
    "inputs": ["string"],
    "outputs": ["string"],
    "safety_class": "read_only|mutating_with_dry_run|docs_only|prompt_only|instructions_only",
    "evidence": "string",
    "verification_command": "string",
    "confidence": 0.0,
    "sensitivity": "clean|sensitive|unknown",
    "cron_apply_reason": "string"
  }
]
```

The prompt should state that proposals are for existing capabilities only. If no existing capability owns the workflow, the classifier should use `semantic_candidate` and the existing candidate flow.

### Validation Rules

Proposal validation should reject when:

- Target capability does not exist in `load_project_bundle(project_root)`.
- Type is not one of the approved first-slice types.
- Output path is absolute, contains `..`, resolves outside project root, or is outside `.governed/capabilities/<target-capability>/`.
- Sensitivity is not `clean`.
- Purpose, evidence, safety class, or verification command is missing.
- Evidence or draft content contains secret-like, credential-path, raw-transcript, customer, or production-evidence indicators.
- Script/wrapper proposal is mutating without dry-run/preview/confirmation metadata.

### Apply Rules

`govkb proposals apply <proposal-id> --project-root <project-root>` should:

1. Load and validate proposal metadata.
2. Require approval metadata with `status = "approved"`, approver, approved timestamp, target capability, approved output paths, safety class, and verification command.
3. Revalidate output paths.
4. Write only approved output paths under the target capability.
5. Run strict validation against the project or report the exact strict validation command if automated command execution is deferred.
6. Mark the proposal applied only after writes and validation succeed.

## 4. Integration Points

| Integration | Contract |
|---|---|
| `src/govkb/cli.py` | Import `run_proposals`; add `proposals` parser with `list`, `show`, `apply`; include `--project-root` and optional `--json`. |
| `src/govkb/commands/proposals.py` | Dispatch proposal actions and format text/JSON output. |
| `src/govkb/core/proposals.py` | Own proposal metadata, validation, staging, listing, loading, and apply file writes. |
| `src/govkb/adapters/codex/bin/codex-memory-review` | Extend schema, prompt, result parsing, proposal validation call, report rows, progress counts, and dry-run behavior. |
| `src/govkb/core/contracts.py` | No schema change expected; use existing project bundle to verify target capability. |
| `src/govkb/core/governed_skill.py` | Reuse strict validation after apply; no proposal-specific rule should execute scripts. |
| `tests/test_memory_review.py` | Extend existing scheduler tests for schema/report/progress behavior. |
| `tests/test_proposals.py` | Cover proposal list/show/apply and safety validation. |

## 5. Application Logic

1. Memory review classifies a session and reads `capability_evolution_proposals`.
2. Each proposal row receives the source session id and run id.
3. Proposal validator checks target capability, type, paths, safety metadata, sensitivity, evidence, and cron posture.
4. In dry-run mode, proposal rows appear in the report but do not write proposal folders.
5. In normal review mode, valid proposals are staged under `.governed/review-proposals/<proposal-id>/`.
6. The report lists staged and rejected proposal rows separately from memory candidates and new capability candidates.
7. `govkb proposals list` scans proposal folders and summarizes status.
8. `govkb proposals show` prints metadata and review text.
9. `govkb proposals apply` writes approved outputs and runs strict validation before marking applied.

## 6. Data Consistency And Safety

- `.governed/review-proposals/**` is project-owned review state.
- `$CODEX_HOME/**` report output remains derived state and must not be treated as proposal source of truth.
- Staging writes metadata and draft review artifacts only; it does not write final tool or instruction paths.
- Apply uses atomic-ish writes where practical: write to temp file in the target directory, then replace.
- Apply should refuse to overwrite an existing non-identical file unless metadata explicitly declares replace semantics or the command exposes a reviewed `--overwrite` option in a later slice.
- Strict validation must not execute proposed scripts.
- Rejected proposal rows should include safe reasons, not raw secret-like values.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Proposal smoke tests | `tests/test_memory_review_capability_evolution_smoke.py` | Empty proposal array compatibility and valid staged script proposal. |
| Proposal use-case tests | `tests/test_memory_review_capability_evolution_use_cases.py` | Types, path validation, cron stage-only behavior, unsafe rejection, mutating dry-run requirement. |
| Proposal command tests | `tests/test_proposals.py` | `list`, `show`, `apply`, approval metadata, output path bounds, strict validation call. |
| Memory-review regression tests | `tests/test_memory_review.py` | Schema text, report sections, progress counts, existing memory candidate behavior. |
| Candidate regression tests | `tests/test_candidates.py`, `tests/test_candidates_json.py` | New capability candidate flow remains unchanged. |
| Review wrapper tests | `tests/test_review_memory_command.py` | Existing model/reasoning flags continue to forward. |
| Strict validation tests | `tests/test_governed_skill_quality_gates_use_cases.py` | Package-owned tool safety remains available after apply. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Confirm CLI imports and new command appears. | Python 3.11+ |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals --help` | `/home/ev/code/govkb` | Confirm proposal command surface. | Phase 2 complete |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v` | `/home/ev/code/govkb` | Proposal core/CLI tests. | Test module added |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review_capability_evolution_smoke tests.test_memory_review_capability_evolution_use_cases -v` | `/home/ev/code/govkb` | Feature smoke/use-case tests. | Test modules added |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review tests.test_review_memory_command tests.test_candidates_json -v` | `/home/ev/code/govkb` | Nearby regression tests. | Source checkout |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli validate --strict <temp-project-root> --json` | `/home/ev/code/govkb` | Validate applied proposal package. | Temp governed project exists |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Final suite. | Production implementation complete |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

Add proposal metadata model, validation helpers, and proposal folder list/load primitives.

Files:

- New `src/govkb/core/proposals.py`
- New `tests/test_proposals.py`
- Optional fixtures/helpers inside `tests/test_proposals.py`

Verify:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v`

Rollback:

- Remove the new proposal core module and tests.

### Phase 1 - Core Behavior

Scope:

Implement staging and apply primitives with approval metadata, bounded output paths, sensitive-content rejection, mutating-script guard, and strict validation hook.

Files:

- `src/govkb/core/proposals.py`
- `tests/test_proposals.py`

Verify:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals tests.test_governed_skill_quality_gates_use_cases -v`

Rollback:

- Revert proposal core changes; no existing commands depend on the module before Phase 2.

### Phase 2 - Command Or Adapter Integration

Scope:

Add `govkb proposals list/show/apply` and wire argparse.

Files:

- `src/govkb/cli.py`
- New `src/govkb/commands/proposals.py`
- `tests/test_proposals.py`

Verify:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals --help`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v`

Rollback:

- Remove CLI parser entries, command module, and imports. Staged proposal folders remain inert metadata if any were created in temp tests only.

### Phase 3 - End-to-End Or Workflow Behavior

Scope:

Extend Codex memory-review schema, prompt, validation, report, progress counts, dry-run behavior, and staging calls.

Files:

- `src/govkb/adapters/codex/bin/codex-memory-review`
- `tests/test_memory_review.py`
- New `tests/test_memory_review_capability_evolution_smoke.py`
- New `tests/test_memory_review_capability_evolution_use_cases.py`

Verify:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review_capability_evolution_smoke tests.test_memory_review_capability_evolution_use_cases tests.test_memory_review -v`

Rollback:

- Revert scheduler schema/report/process changes and feature tests. Existing candidates and memory review resume prior behavior.

### Phase 4 - Docs, Packaging, Or Optional UI

Scope:

Update README/current-scope docs if command behavior is user-facing, then create parity/release artifacts after implementation.

Files:

- `README.md`
- Feature folder `poc-parity-review.md`, `release-notes.md`, and related closeout docs when implementation is complete

Verify:

- `git diff --check`
- Final full test suite

Rollback:

- Revert docs updates independently from production code.

## 10. Rollback Plan

- Proposal command rollback: remove `govkb proposals` parser and command module; proposal folders are ignored by existing GovKB.
- Adapter rollback: remove `capability_evolution_proposals` schema/prompt/report/staging changes; memory candidates and semantic candidates remain on existing paths.
- Apply rollback after a failed proposal apply: restore files from pre-write backups or refuse partial apply before status changes; leave proposal status as `apply-failed` with safe error text.
- Strict validation rollback is not needed; it is existing behavior and remains independent.

## 11. Open Questions

None blocking.

Implementation should choose a conservative first apply contract for verification command execution. If automated arbitrary verification commands are too risky, the first slice can run strict validation and print the proposal's verification command for manual execution, then record that as a residual limitation in parity review.

## 12. Ready Checklist

| Item | Status |
|---|---|
| Requirements mapped to scenarios | Done |
| PoC baseline identifies current gaps | Done |
| Existing code inventory names concrete files | Done |
| New files justified | Done |
| Tests mapped to use cases | Done |
| Verification commands listed with working dir | Done |
| Governance and raw-transcript safety covered | Done |
| Rollback explicit | Done |
