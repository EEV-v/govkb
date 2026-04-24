### Governed Skill Knowledge Framework — Focused Use Cases (BDD)
Last updated: 2026-04-22

### Assumptions & Conventions
| Aspect | Convention |
|--------|------------|
| Timezone | scheduled run uses `Europe/Istanbul`; timestamps and reports stay in UTC where already established |
| Schedule | daily scheduler run at `08:15`; manual ad hoc runs allowed any time |
| Matching keys | governed capability identity is `capability.id`; session identity is session id; installed release identity is `repo + git revision + assistant` |
| Contract root | canonical project source is `<project-root>/.governed/` |
| Framework repo | reusable CLI/tooling source is a separate shareable `govkb` GitHub repo |
| Contract format | `capability.contract.toml` and adapter manifests are parsed via built-in Python support |
| Governance precedence | project package is authoritative; assistant adapters may add and tighten rules; stricter policy always wins |
| Duplicates | the same session id is processed once per successful state advancement |
| Reprocessing | backfilled missed sessions are processed once without moving the success watermark backwards |
| Auto-apply threshold | resolved threshold is at least `0.85` unless a stricter contract raises it |
| Self-development loop | real team work can update existing governed capability expertise automatically when confidence is high; brand-new capability creation is staged for review |

### Test Data Contract
| Entity | Key Fields | Sample Values | Setup |
|--------|------------|---------------|-------|
| CapabilityContract | `capability.id`, `routing.hints`, `memory.targets.main.path`, `memory.targets.main.sections` | `internal-account-review`, `["review", "severity:"]`, `references/long-term-memory.md` | repo `.governed` fixture |
| AdapterManifest | `assistant`, `materialization.targets`, `governance` | `codex`, `skills/internal-account-review`, `inherit+tighten` | repo adapter fixture |
| ReleaseManifest | `release_id`, `git_revision`, `assistant_targets` | `2026.04.21`, `abc1234`, `["codex"]` | repo release fixture |
| SessionTranscript | `session_id`, `user_message`, `assistant_message`, `task_complete` | `session-skill-001`, `review implementation plan for internal accounts`, `P1 findings...` | JSONL fixture |
| ApprovalGatedCapability | `capability.id`, `requires_explicit_acceptance`, `memory target` | `feature-estimator`, `true`, `references/long-term-memory.md` | repo capability fixture |
| InvalidContract | `capability.id`, malformed field/value | `bad-review`, missing `memory.targets` | repo capability fixture |
| FileOnlySession | `session_id`, session file exists, index row missing | `session-file-only-001` | JSONL fixture |
| FrameworkRepo | CLI package, templates, schemas, adapters, tests | `govkb`, `src/govkb`, `templates/project/.governed` | shareable GitHub repo fixture |
| LearningCandidate | `source_session`, `target_capability`, `lesson`, `confidence`, `reuse_scope` | `session-fix-001`, `clearing-bugfixer`, `Use prod replay fixture before patching reconciliation importer`, `0.93`, `project` | session + classifier fixture |
| CapabilityCandidate | `candidate_id`, `evidence_sessions`, `suggested_contract`, `decision` | `clearing-review-tax-lots`, `["session-a", "session-b"]`, `capability.contract.toml`, `Stage` | staged candidate fixture |

### Feature: Make project AI knowledge self-improving through governed repo-native capability growth

**Background:**
  Given the memory-review task runs daily at `08:15` in `Europe/Istanbul`
  And the project source of truth lives under `<project-root>/.governed/`
  And Codex is the first live adapter
  And conventions above are enforced

### Scenarios (13 total)

**Scenario: A developer can clone the shareable `govkb` repo and bootstrap a project governed package** `@smoke`
  Given the `govkb` framework is published as a reusable GitHub repo
  And the repo contains the CLI package, contract schemas, project templates, Codex adapter, and tests
  When a developer clones and installs `govkb`
  And runs `govkb init` inside a project repo
  Then the project repo receives a valid `.governed/` package scaffold
  And `govkb validate` passes against that scaffold
  And the project package can later be used by `govkb apply codex` without copying framework source into the project repo

**Scenario: Happy path — a new governed capability becomes routable without central script edits** `@smoke`
  Given repo capability `acct-reviewer` contains `capability.contract.toml`
  And the contract declares routing hints for `account activation` and `approval review`
  And no central Python allowlist or keyword map contains `acct-reviewer`
  When a recent session discusses account activation approval review
  Then the framework resolves `acct-reviewer` as an eligible governed capability
  And the classifier receives `acct-reviewer` as a target candidate
  And no framework code change is required for that capability to participate

**Scenario: Session resolves to the correct repo-governed package before governed routing begins** `@smoke`
  Given session metadata contains working directory `/home/ev/code/Clearing/ETNAClearingService`
  And repo root `/home/ev/code/Clearing` contains `.governed/`
  And another repo on the same machine also contains `.governed/`
  When the scheduled task starts processing that session
  Then the session resolves to repo package `/home/ev/code/Clearing/.governed/`
  And governed contracts are loaded from that package only
  And a session with no governed repo match is skipped with a health warning instead of using the wrong package

**Scenario: Project-only knowledge stays repo-native and is not constrained by Codex skills** `@regression`
  Given project capability `clearing-master-reviewer` is defined under `<project-root>/.governed/capabilities/clearing-master-reviewer/`
  And project-only knowledge for Internal Accounts lives under `<project-root>/.governed/knowledge/internal-accounts/`
  When a recent session is specific to the Internal Accounts feature in this repo
  Then the project-specific routing hint participates in classification
  And any project-only governed memory update lands in the repo package
  And the update is not constrained by Codex-only overlay structure
  And assistant-local artifacts remain derived outputs

**Scenario: Real team work grows an existing governed capability and redistributes it** `@smoke`
  Given teammate A completes a reusable bugfix workflow in the project
  And governed capability `clearing-bugfixer` allows memory updates under `.governed/capabilities/clearing-bugfixer/`
  And the classifier extracts reusable lesson `Use prod replay fixture before patching reconciliation importer` with confidence `0.93`
  When the scheduled Codex memory-review adapter validates the lesson
  Then the lesson is applied to the allowed repo-governed memory target in the governed automation worktree
  And the report records the learned project behavior as redistributable
  And promotion can create a repo-tracked release
  When teammate B runs `govkb apply codex --release 2026.04.22`
  Then teammate B's local Codex setup receives the updated bugfix expertise
  And no central scheduler code edit is required

**Scenario: Repeated unmatched work pattern stages a new governed capability candidate** `@regression`
  Given recent sessions repeatedly discuss a project workflow that does not match an existing governed capability
  And the evidence spans at least two completed project sessions
  When the memory-review adapter cannot map the pattern to an existing valid contract
  Then it stages a new governed capability candidate with suggested id, routing hints, memory targets, and evidence sessions
  And the candidate is not auto-created as an active capability
  And a reviewer can promote, edit, or reject the candidate explicitly

**Scenario: `govkb apply codex` materializes repo state into local assistant setup** `@regression`
  Given repo release manifest `2026.04.21` points to git revision `abc1234`
  And the release targets assistant `codex`
  And local install state does not yet match that revision
  When `govkb apply codex --release 2026.04.21` runs
  Then the local Codex setup is materialized from the repo package
  And the applied revision is recorded in local install state
  And future update checks compare local state to the repo-tracked release

**Scenario: High-confidence exact lesson auto-applies to a repo-governed memory target through the Codex adapter** `@regression`
  Given governed capability `clearing-master-reviewer` resolves with auto-apply threshold `0.85`
  And a session produces one reusable lesson for section `Repository Best Practices`
  And the classifier returns confidence `0.91`
  And the lesson is not sensitive, not duplicate, and not environment-local
  When local validation runs
  Then the lesson is auto-applied to the allowed repo-governed memory target in the governed automation worktree
  And the active developer working tree remains unchanged
  And the applied patch is written to the run artifacts
  And the run report records the applied change

**Scenario Outline: Approval-gated or low-confidence lessons stage instead of auto-applying** `@regression`
  Given governed capability `<CapabilityId>` resolves with threshold `<Threshold>` and explicit acceptance `<ExplicitAcceptance>`
  And the classifier returns a reusable lesson with confidence `<Confidence>`
  And the lesson is otherwise valid and non-sensitive
  When local validation runs
  Then the decision is `<Decision>`
  And no automatic memory mutation bypasses the resolved governance rules

  Examples:
  | CaseId | CapabilityId | Threshold | ExplicitAcceptance | Confidence | Decision |
  | GOV-01 | feature-estimator | 0.85 | true | 0.96 | Stage |
  | GOV-02 | clearing-master-reviewer | 0.85 | false | 0.78 | Stage |
  | GOV-03 | clearing-master-reviewer | 0.90 | false | 0.89 | Stage |

**Scenario: The same repo package can define future Claude and Copilot targets without redefining project knowledge** `@regression`
  Given the project package contains adapter definitions for `codex`, `claude`, and `copilot`
  And all three adapters point to the same governed capability and project knowledge source
  When adapter validation runs
  Then the project knowledge model is shared across assistants
  And no assistant requires its own separate project-only knowledge source
  And Codex remains the only live adapter in the first increment

**Scenario: File-only session is still discovered and processed** `@regression`
  Given session file `session-file-only-001.jsonl` exists under `~/.codex/sessions`
  And the same session id is absent from `session_index.jsonl`
  And the session falls inside the review window
  When the scheduled task selects sessions
  Then the file-only session is counted in discovery health
  And the session is processed once
  And successful processing does not move the watermark backwards

**Scenario: Invalid contract degrades only the affected capability and raises a health warning** `@edge-case`
  Given governed capability `clearing-review-bad` contains an invalid `capability.contract.toml`
  And other governed capabilities have valid contracts
  When the scheduled task loads governed contracts
  Then `clearing-review-bad` is excluded from governed participation
  And the report records an invalid-contract warning for that capability
  And unrelated governed capabilities continue processing normally

**Scenario: Maintenance chatter is rejected before it can become durable memory** `@regression`
  Given a recent session discusses `codex-memory-review`, report output, or `govkb` install debugging
  And the session does not contain project-domain work beyond framework maintenance
  When prescreen runs
  Then the session is marked self-referential or environment-local
  And the classifier is not called for durable memory extraction
  And the report records the skipped reason

### Notifications
| Status | Subject | Recipients | Timing |
|--------|---------|------------|--------|
| Processed | local report entry + log line | local operator | end of run |
| Inconsistencies | local report health warning | local operator | end of run |
| Skipped | local report entry | local operator | end of run |
| Error | local report entry + log line | local operator | immediate in run output |

Example line: `session-skill-001 | clearing-master-reviewer | Repository Best Practices | confidence 0.91 | Applied`

### In Scope / Out of Scope
- In:
  - contract-driven governed capability discovery
  - self-improving project knowledge from real team sessions
  - repo-native project-governed package under `.governed/`
  - `govkb apply codex` from git-tracked releases
  - Codex as the first live adapter
  - assistant-agnostic project knowledge ownership
  - conservative auto-apply/stage/reject behavior
  - health reporting for file-only sessions and invalid contracts
  - legacy fallback during migration
- Out:
  - default skill creator override
  - bulk migration of all remaining skills
  - runtime prompt composition from adapter-managed prompt files
  - UI for staged-memory review
  - fully working Claude and Copilot adapters
  - fully automatic activation of brand-new governed capabilities
  - proving exact chatbot cost reduction

### Traceability
| Req | Scenario(s) | Coverage |
|-----|-------------|----------|
| GSKF-01 Shareable framework repo can be cloned and used to scaffold project packages | A developer can clone the shareable `govkb` repo and bootstrap a project governed package | Full |
| GSKF-02 Dynamic governed capability discovery without hardcoded routing | Happy path — a new governed capability becomes routable without central script edits | Full |
| GSKF-03 Session must resolve to the correct repo-governed package or skip safely | Session resolves to the correct repo-governed package before governed routing begins | Full |
| GSKF-04 Project-only knowledge is repo-native and assistant-agnostic | Project-only knowledge stays repo-native and is not constrained by Codex skills | Full |
| GSKF-05 Existing governed capability expertise grows from real work and redistributes to teammates | Real team work grows an existing governed capability and redistributes it | Full |
| GSKF-06 Repeated unmatched patterns stage new governed capability candidates | Repeated unmatched work pattern stages a new governed capability candidate | Full |
| GSKF-07 `govkb apply codex` updates local setup from git-tracked repo source | `govkb apply codex` materializes repo state into local assistant setup | Full |
| GSKF-08 High-confidence reusable lessons can auto-apply safely without mutating the active developer working tree | High-confidence exact lesson auto-applies to a repo-governed memory target through the Codex adapter | Full |
| GSKF-09 Governance gates must still stage approval-gated or low-confidence lessons | Approval-gated or low-confidence lessons stage instead of auto-applying | Full |
| GSKF-10 Same repo package supports future assistant targets | The same repo package can define future Claude and Copilot targets without redefining project knowledge | Full |
| GSKF-11 Session discovery must not miss file-only sessions | File-only session is still discovered and processed | Full |
| GSKF-12 Invalid contracts must be visible without breaking unrelated capabilities | Invalid contract degrades only the affected capability and raises a health warning | Full |
| GSKF-13 Maintenance chatter must not become durable memory | Maintenance chatter is rejected before it can become durable memory | Full |

### Testability Checklist
- [ ] Every Given: setup via fixture or local files, not manual inspection
- [ ] Every When: single automatable scheduler or concrete `govkb` CLI trigger
- [ ] Every Then: specific state/report/file assertion
- [ ] Negative assertions explicit (`no framework code change`, `assistant-local artifacts remain derived outputs`)
- [ ] Domain-meaningful identifiers in examples

### Anti-Patterns
- ❌ Hardcoded project skill ids inside the scheduler
- ❌ Project-only knowledge modeled as Codex-only overlay source
- ❌ Adapter policy weakening project governance
- ❌ Invalid contracts silently falling back without a health warning
- ❌ Maintenance chatter becoming long-term memory
- ❌ Automatically creating active new capabilities from a single session without review
