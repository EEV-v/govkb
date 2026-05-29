# Memory Review Capability Evolution - Implementation Context

Last updated: 2026-05-28

## Objective

Extend GovKB's Codex memory-review path so it can stage structured capability-evolution proposals in addition to existing memory lessons and new capability candidates.

The implementation must preserve current safe memory behavior while making reusable tool/script/prompt/runbook opportunities explicit and reviewable.

## Source Artifacts

- `docs/governed-skill-knowledge-framework/features/memory-review-capability-evolution/business.md`
- `docs/governed-skill-knowledge-framework/features/memory-review-capability-evolution/business-context.md`
- `README.md`
- `docs/README.md`
- `docs/governed-skill-knowledge-framework/business.md`
- `docs/governed-skill-knowledge-framework/implementation-plan.md`
- `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/business.md`
- `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/context.md`
- `src/govkb/adapters/codex/bin/codex-memory-review`
- `src/govkb/commands/candidates.py`
- `src/govkb/commands/create_capability.py`
- `src/govkb/commands/review_memory.py`
- `src/govkb/commands/validate.py`
- `src/govkb/core/candidates.py`
- `tests/test_memory_review.py`

No repo-local `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, or `.cursorrules` file was found under `/home/ev/code/govkb`; active session instructions and project docs are the applicable guidance.

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| Memory-review classifier schema | `schema_text()` only supports `candidates` and `semantic_candidate`. | `src/govkb/adapters/codex/bin/codex-memory-review` | Extend with a new proposal array. |
| Classifier prompt | `prompt_for_session()` asks for append-only memory candidates and one semantic capability candidate. | `src/govkb/adapters/codex/bin/codex-memory-review` | Extend prompt without weakening rejection rules. |
| Memory validation | `validate_candidate()` enforces exact target, section, sensitivity, duplicate, confidence, and durability gates. | `src/govkb/adapters/codex/bin/codex-memory-review` | Add a separate validator for proposal rows. |
| Review report | `write_report()` emits Applied, Staged, Candidate Stage Requests, Auto-Create, Rejected, Deferred, and Failed sections. | `src/govkb/adapters/codex/bin/codex-memory-review` | Add a capability-evolution proposal section. |
| Candidate staging | `run_candidate_staging()` shells into `govkb candidates stage` with optional semantic seed. | `src/govkb/adapters/codex/bin/codex-memory-review`; `src/govkb/commands/candidates.py` | Keep for new capability candidates only; do not overload it for proposal review. |
| Candidate auto-create | `govkb candidates auto-create-ready` requires project policy and review approval before activation. | `src/govkb/commands/candidates.py`; `src/govkb/commands/create_capability.py` | Preserve review-gated activation behavior. |
| Strict validation | `govkb validate --strict` surfaces strict package issues. | `src/govkb/commands/validate.py`; strict validation tests | Reuse for generated package/tool safety. |
| Governed tool convention | `tools/scripts/`, `tools/fixtures/`, and `tools/README.md` are known package locations. | `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/business.md` | Reuse as allowed target locations for applied proposals. |
| Public review wrapper | `govkb review-memory --assistant codex` invokes the Codex memory-review adapter. | `src/govkb/commands/review_memory.py` | Preserve CLI compatibility. |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| Capability-evolution proposal schema | Represent proposed scripts, wrappers, prompts, runbooks, instruction updates, and candidate-capability proposals independently from memory lessons. | Likely added to `schema_text()` and classifier result handling. |
| Proposal validator | Enforce target capability, proposal type, repo-relative path, sensitivity, evidence, approval posture, and cron safety. | Should be separate from `validate_candidate()` because proposals are not memory bullets. |
| Proposal staging writer | Persist reviewable proposal metadata under repo-owned `.governed/` paths. | Use `.governed/review-proposals/<proposal-id>/` as the approved project-level inbox. |
| Report section | Show proposed capability evolution rows in the memory-review report. | Must include source session, target capability, path, purpose, safety, and verification. |
| Manual proposal apply command | Convert approved proposals into files or patches, then run validation/tests. | Use the approved `govkb proposals list/show/apply` command family. |
| Tests and fixtures | Cover no-proposal compatibility, proposal staging, safety rejection, and manual apply. | Likely in `tests/test_memory_review.py` plus new focused tests. |

## Data Flow

1. Session discovery selects eligible Codex sessions.
2. Memory review builds the existing semantic evidence package.
3. Classifier returns:
   - memory candidates for existing capability memory
   - optional semantic capability candidate
   - optional capability-evolution proposals
4. Memory candidates use existing auto-apply, stage, reject, and report logic.
5. Capability-evolution proposals are validated separately.
6. Valid proposals are staged as reviewable repo-owned artifacts.
7. The report lists proposal rows and their safety posture.
8. Maintainer reviews and approves a proposal.
9. Manual apply/generate command writes files or patches.
10. Strict validation and targeted tests verify the result.

## Domain Entities

| Entity | Existing Or New | Notes |
|---|---|---|
| Memory candidate | Existing | One append-only lesson for one valid target memory section. |
| Semantic capability candidate | Existing | One proposed new capability when no existing specialized capability owns the workflow. |
| Capability-evolution proposal | New | A structured proposal to improve an existing capability's assets. |
| Proposal type | New | First slice supports `script`, `wrapper`, `prompt`, `runbook`, and `instructions_update`. |
| Target capability | Existing/New link | Proposal should target an existing capability unless it is explicitly a new capability candidate. |
| Proposed path | New | Repo-relative path under an allowed `.governed/` location. |
| Safety profile | New | Read-only, mutating-with-dry-run, docs-only, or prompt/instruction-only. |
| Approval metadata | New | Required before generation or apply: approved status, approver, approved timestamp, target capability, proposal type, output paths, safety class, and verification command. |

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Run full Python tests | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Source checkout, Python 3 with `tomllib`. |
| Run memory-review tests | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_memory_review -v` | `/home/ev/code/govkb` | Use after schema/report/classifier changes. |
| Run candidate tests | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_candidates -v` | `/home/ev/code/govkb` | Use if proposal flow reuses or touches candidates. |
| Check CLI help | `PYTHONPATH=src python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Confirms command registration. |
| Validate a governed project | `PYTHONPATH=src python3 -m govkb.cli validate --strict <project-root> --json` | `/home/ev/code/govkb` | Use against a fixture or real governed package after applying proposal artifacts. |
| Run memory review wrapper | `PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root <project-root> --dry-run` | `/home/ev/code/govkb` | Requires a project with `.governed/` and Codex memory-review task. |

## APIs And CLI Surface

Existing relevant CLI:

- `govkb review-memory --assistant codex`
- `govkb candidates stage`
- `govkb candidates list --json`
- `govkb candidates auto-create-ready`
- `govkb create capability`
- `govkb validate --strict`

New CLI direction:

- `govkb proposals list`
- `govkb proposals show <proposal-id>`
- `govkb proposals apply <proposal-id>`

No separate `--include-capability-evolution` discovery flag is required for the first slice. Memory review should detect high-confidence proposal opportunities by default, while cron remains staging-only.

## Storage

Existing storage:

| Location | Meaning |
|---|---|
| `$CODEX_HOME/memories/govkb/projects/<project-id>/codex-memory-review/**` | Derived local review reports, patches, logs, and state. |
| `<project>/.governed/candidates/<candidate-id>/` | Repo-owned candidate capability staging. |
| `<project>/.governed/capabilities/<capability-id>/` | Repo-owned governed capability source. |
| `<project>/.governed/capabilities/<capability-id>/tools/scripts/` | Allowed governed helper script location by quality-gate precedent. |
| `<project>/.governed/capabilities/<capability-id>/tools/README.md` | Required documentation when a capability has tool scripts or fixtures. |

Approved storage:

- staged proposal inbox: `.governed/review-proposals/<proposal-id>/`
- approved output paths: `.governed/capabilities/<capability-id>/...`
- new capability candidates: `.governed/candidates/<candidate-id>/`

## Security And Governance

- Do not store raw session transcripts in repo proposal artifacts.
- Do not store secrets, credential paths, customer identifiers, production evidence, or token-like values.
- Cron must not write executable scripts or instruction changes directly.
- Mutating script proposals must require preview or dry-run behavior before apply.
- Proposed paths must stay repo-relative and under allowed governed package paths.
- Strict validation must remain the activation/materialization gate for package-owned tools.
- `$CODEX_HOME/**` output is derived evidence, not authoritative design.

## Tests

Existing test anchors:

- `tests/test_memory_review.py` already covers schema strictness, report generation, classifier behavior, candidate staging, auto-create interactions, classifier stdin behavior, and scheduler behavior.
- `tests/test_candidates.py` covers candidate staging and activation flow.
- `tests/test_governed_skill_quality_gates_use_cases.py` covers strict validation and governed tool package expectations.
- `tests/test_review_memory_command.py` covers the public review-memory command wrapper.

Likely new coverage:

- classifier output schema accepts `capability_evolution_proposals`.
- empty proposals preserve current reports and state behavior.
- proposal rows are rejected when they contain unsafe paths, sensitive content, missing target capability, missing safety profile, or executable auto-apply from cron.
- valid proposal rows appear in the report.
- apply mode stages proposal artifacts without creating executable scripts.
- manual apply/generate path writes expected files and then runs strict validation.

## Observability

Review reports should expose:

- proposal count
- target capability
- proposal type
- proposed path
- source session
- safety profile
- evidence summary
- validation decision
- next maintainer action

Progress JSONL and VS Code learning views may later display these counts separately from existing memory updates and capability candidates.

## Resolved Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|
| 1 | Should staged proposals live under `.governed/capabilities/<capability-id>/proposals/` or a project-level `.governed/review-proposals/` queue? | No | Product/Engineering |
| 2 | Should proposal application be a new command or part of `govkb candidates`? | No | Product/Engineering |
| 3 | Should the classifier always consider capability-evolution proposals, or only when a manual flag is set? | No | Product/Engineering |
| 4 | What is the minimum approval metadata required before a proposal can generate executable files? | No | Governance/Engineering |
| 5 | Which proposal types should be included in the first implementation slice? | No | Product/Engineering |
| 6 | Should proposal staging be visible in the existing VS Code Learning view in the first slice? | No | Product |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| 1 | This feature should extend the packaged adapter at `src/govkb/adapters/codex/bin/codex-memory-review`, not only the installed copy under a Codex home. | Installed scripts could drift if the packaged source is not changed. |
| 2 | Existing memory candidates and semantic candidates should remain backward-compatible. | Existing cron users could see changed behavior unexpectedly. |
| 3 | Proposal generation should be conservative by default and manually applied. | If fully automatic generation is desired, scope and safety rules need expansion. |
| 4 | Strict validation is enough to verify generated governed tool package shape after proposal application. | Additional proposal-specific validation may be needed. |

## Traceability

| Context Section | business.md Source |
|---|---|
| Objective | Summary, Product Goal |
| Proposed New Components | Product Goal, MVP Scope, Proposal Types |
| Data Flow | Desired Workflow |
| Storage | Desired Workflow, Safety Rules, Approved Decisions |
| Security And Governance | Safety Rules, Out of Scope |
| Tests | Acceptance Criteria |
| Resolved Questions | Approved Decisions |
