# VS Code Extension UI and Public Distribution - Implementation Context

Last updated: 2026-04-25

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| CLI package | `govkb` console script | `pyproject.toml` | Reuse as extension backend. |
| Command registry | `argparse` subcommands for install, validate, apply, status, review-memory, candidates | `src/govkb/cli.py` | Reuse command surface through child processes. |
| Project install | Scaffold `.governed`, materialize Codex, install memory-review task, optional cron | `src/govkb/commands/install.py` | Reuse without duplicating in extension. |
| Project status | Reports governed package and Codex install-state health | `src/govkb/commands/status.py` | Parse or wrap for UI state. |
| Candidate lifecycle | Stage/list/auto-create candidates | `src/govkb/commands/candidates.py` | Expose list and safe activation UI. |
| Memory review | Codex adapter with model/reasoning/timeout flags | `src/govkb/commands/review_memory.py`, `src/govkb/adapters/codex/bin/codex-memory-review` | Expose dry-run first. |
| Test approach | Python unit tests over command behavior | `tests/` | Keep core green; add extension tests separately. |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| `vscode-extension/package.json` | VS Code extension manifest, commands, settings, views, activation events | New package root under GovKB repo. |
| `vscode-extension/src/extension.ts` | Activation, command registration, trust checks | Thin orchestration only. |
| `vscode-extension/src/govkbCli.ts` | Command construction, process spawning, output capture | Must quote args safely and avoid shell interpolation. |
| `vscode-extension/src/setupFlow.ts` | One-click setup orchestration for the open project | Detects/provisions GovKB CLI, runs install, init-kb, validate/status, and reports one blocker at a time. |
| `vscode-extension/src/applyFlow.ts` | One-click apply orchestration for the open project | Runs `govkb apply codex`, refreshes status, and opens reports/status on failure. |
| `vscode-extension/src/settings.ts` | Resolve `govkb.command`, `codexHome`, classifier defaults | Workspace settings that affect execution are trust-sensitive. |
| `vscode-extension/src/views/*` | Status, capabilities, candidates, reports tree providers | Reads structured files or CLI output. |
| `vscode-extension/test/*` | Extension unit/integration tests | Cover trust, command construction, parsing, and views. |
| `vscode-extension/README.md` | Marketplace/public README | Must not depend on internal GovKB docs. |
| `vscode-extension/CHANGELOG.md` | Public extension changelog | Required for public distribution hygiene. |

## Data Flow

`VS Code command -> one-click flow -> Extension trust/settings/prerequisite resolver -> GovKB CLI child process -> GovKB core -> .governed / CODEX_HOME -> Extension output channel and views`

| Step | System | Input | Output | Trigger |
|---|---|---|---|---|
| Workspace detection | Extension | Active workspace folders | Candidate project root and `.governed` presence | Extension activation or folder change |
| Prerequisite resolution | Extension | Installed extension assets, Python availability, existing `govkb`, user settings | Ready GovKB runtime or one actionable blocker | One-click setup |
| Settings resolution | Extension | User/workspace settings | GovKB command path, Codex home, classifier defaults | Before command execution |
| Command execution | Extension | Command id and resolved arguments | stdout, stderr, exit code | Command palette or UI action |
| Core operation | GovKB Python CLI | Project root, adapter flags, model/reasoning settings | Repo or assistant-local mutations, reports, status output | CLI process |
| UI refresh | Extension | CLI output and filesystem state | Tree/status bar updates | Command completion or manual refresh |

## Domain Entities

### VS Code Extension Settings

| Field | Type | Constraints | Example |
|---|---|---|---|
| `govkb.command` | string | Executable or module invocation path | `govkb` |
| `govkb.pythonPath` | string | Optional Python executable when using module mode | `python3` |
| `govkb.setupMode` | enum | `auto`, `useExisting`, `guidedInstall` | `auto` |
| `govkb.codexHome` | string | Optional path; must not be logged with secrets | `/home/ev/.codex` |
| `govkb.classifierModel` | string | Default should be low-cost for tests | `gpt-5.4-mini` |
| `govkb.classifierReasoning` | enum | `low`, `medium`, `high`, `xhigh` | `low` |
| `govkb.reviewTimeoutSeconds` | number | Positive integer | `180` |
| `govkb.defaultDryRun` | boolean | Should default true for memory review | `true` |

### GovKB Project

| Field | Type | Constraints | Example |
|---|---|---|---|
| projectRoot | path | Workspace folder or selected folder | `/home/ev/code/AIApps` |
| governedRoot | path | `<projectRoot>/.governed` | `/home/ev/code/AIApps/.governed` |
| projectId | string | Loaded from `.governed/project.toml` | `aiapps` |
| capabilities | list | Loaded through GovKB core/status | `backend-local-stack-workflow` |
| adapters | list | Existing MVP supports `codex` | `codex` |

### Candidate Summary

| Field | Type | Constraints | Example |
|---|---|---|---|
| candidateId | string | Folder id under `.governed/candidates` | `backend-frontend-workflow` |
| status | enum | collecting, ready-for-review, activated, rejected | `ready-for-review` |
| occurrences | number | Non-negative integer | `2` |
| proposalCapabilityId | string | Must not be materialized `govkb-*` id | `backend-local-stack-workflow` |
| sourceSessions | list | Session ids only; no transcript content | `release-signoff-one` |

### Report Summary

| Field | Type | Constraints | Example |
|---|---|---|---|
| path | path | Under project-scoped Codex memory-review reports | `.../reports/2026-04-25T094321Z-report.md` |
| classifierModel | string | Parsed from report or command args | `gpt-5.4-mini` |
| classifierReasoning | string | Parsed from report or command args | `low` |
| failedSessions | number | Must be surfaced prominently | `0` |
| deferredSessions | number | Must distinguish environment blockers | `0` |

## Upstream Dependencies

| Source | Owner | Delivery | Format | Failure Mode | Handling |
|---|---|---|---|---|---|
| GovKB Python package | GovKB | Bundled, downloaded, embedded, or existing local CLI depending on selected mechanism | CLI process | Missing command, wrong version | One-click setup provisions when possible; otherwise shows one install action. |
| VS Code API | Microsoft | Extension host | TypeScript API | Unsupported VS Code version | Set `engines.vscode` and test minimum. |
| `@vscode/vsce` | Microsoft | Node package | CLI | Packaging/publishing failure | CI packaging check. |
| Codex CLI | User environment | Local executable | CLI process | Missing auth, quota, timeout, connectivity | Show report as environment blocker, not product success. |
| CODEX_HOME | User environment | Filesystem | directory tree | Missing or wrong path | Allow setting override and status warning. |

## APIs

### Extension Commands

| Command | Auth | Purpose |
|---|---|---|
| `govkb.oneClickSetup` | Trusted workspace required | Resolve prerequisites, initialize/apply/bootstrap/validate/status for the open project. |
| `govkb.oneClickApply` | Trusted workspace required | Apply the current governed package to Codex and refresh status. |
| `govkb.installProject` | Trusted workspace required | Run install/init flow. |
| `govkb.validateProject` | Trusted workspace recommended; read-only command may run in limited mode if no local execution risk is accepted | Validate `.governed`. |
| `govkb.showStatus` | Trusted workspace recommended | Show project and install state. |
| `govkb.applyCodex` | Trusted workspace required | Materialize Codex adapter. |
| `govkb.reviewMemoryDryRun` | Trusted workspace required | Run memory review without repo mutation. |
| `govkb.listCandidates` | Trusted workspace recommended | Show candidate state. |
| `govkb.autoCreateReadyCandidates` | Trusted workspace required | Create governed capabilities from ready candidates. |

### CLI Invocation Contract

Extension code should use `child_process.spawn` or equivalent argument-array execution. It should not build shell command strings.

Required command construction examples:

```text
govkb install <projectRoot> --codex-home <codexHome> --project-id <derivedOrPromptedId> --project-name <derivedOrPromptedName>
govkb init-kb <projectRoot> --all --codex-home <codexHome>
govkb apply codex --project-root <projectRoot> --codex-home <codexHome>
govkb validate <projectRoot>
govkb status <projectRoot> --codex-home <codexHome>
govkb review-memory --assistant codex --project-root <projectRoot> --dry-run --max-sessions 1 --classifier-codex-home <home> --codex-model gpt-5.4-mini --codex-reasoning low --codex-timeout 180
```

## Storage

| Location | Purpose | Ownership |
|---|---|---|
| `<workspace>/.governed/**` | Governed source package | Project repo, mutated only by GovKB CLI. |
| `$CODEX_HOME/skills/**` | Materialized Codex skills | Derived assistant-local output. |
| `$CODEX_HOME/memories/govkb/**` | Install state and memory-review reports | Derived local state. |
| VS Code global/workspace settings | Extension configuration | User/editor state. |
| Extension output channel | Runtime output | Ephemeral UI, not source of truth. |

## Security

| Entity/Field | Classification | Handling |
|---|---|---|
| Raw session transcript | Sensitive/local | Do not show or store in extension state. |
| Codex auth files | Secret | Never read or log. |
| CODEX_HOME path | Local environment metadata | Show only when useful; do not package. |
| `.governed` artifacts | Project governed source | Mutate only through GovKB CLI. |
| CLI stdout/stderr | Operational output | Show in output channel; avoid copying to repo. |

Authz: VS Code Workspace Trust is the first authorization gate for command execution. GovKB core governance remains the second gate for project mutations.

Audit: GovKB reports remain the durable audit surface. Extension logs are diagnostic only.

## UI

| Page/View | Endpoint | Controls |
|---|---|---|
| GovKB Status | `govkb status` and filesystem detection | One-click setup, refresh, validate, one-click apply |
| Capabilities | `.governed/capabilities` or status output | Open contract, open memory, apply |
| Candidates | `.governed/candidates` or `govkb candidates list` | Refresh, auto-create ready, open files |
| Reports | `$CODEX_HOME/memories/govkb/projects/<project>/codex-memory-review/reports` | Open report, rerun dry-run |
| Setup Walkthrough | one-click setup flow | Run setup, show current step, stop on one actionable blocker |

## Observability

- Output channel records command name, arguments with sensitive paths minimized where practical, exit code, and stdout/stderr.
- Status bar should distinguish clean, warning, error, and not-initialized states.
- Failed and deferred sessions from memory-review reports should be surfaced separately.
- Extension tests should include parser fixtures for successful status, validation warnings, deferred classifier sessions, and failed sessions.

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|
| 1 | Which runtime provisioning mechanism should implement one-click setup? | Yes | Product/Engineering |
| 2 | What Marketplace publisher, extension id, display name, and icon should be used? | Yes | Product |
| 3 | What platforms are launch-supported? | Yes | Product/Engineering |
| 4 | Should apply-mode memory review be exposed in the first UI? | Yes | Product/Governance |
| 5 | Should scheduler install/management be part of the first extension release? | No | Product |
| 6 | Should telemetry exist at all? | Yes | Product/Security |
| 7 | How should multi-root workspaces select a GovKB project? | No | Engineering |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| 1 | First release should minimize setup overhead even if the extension remains a thin wrapper over the CLI internally. | If provisioning is weak, public users still face manual setup friction. |
| 2 | One-click apply covers governed package materialization; memory-review mutation can remain dry-run until explicitly approved. | Users may expect one-click learning activation too soon. |
| 3 | Single-root workspace support is acceptable initially. | Multi-root users may see incomplete behavior. |
| 4 | Marketplace release can follow VSIX validation. | Public launch may be delayed by publisher setup. |

## Traceability

| Section | business.md |
|---|---|
| Existing Patterns | Scope, Acceptance Criteria |
| Data Flow | Initial Command Surface, Governance And Security |
| Domain Entities | Initial UI Surface |
| Security | Governance And Security, Acceptance Criteria |
| Open Questions | Open Questions |
