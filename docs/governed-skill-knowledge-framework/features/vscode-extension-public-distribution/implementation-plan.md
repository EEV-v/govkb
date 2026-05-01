# VS Code Extension UI and Public Distribution - Implementation Plan

Last updated: 2026-04-25

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | Command and flag registration | `src/govkb/cli.py` | Extend `status` and `candidates list` with `--json`; keep existing human output as default. |
| Status command | Project summary, validation result, install-state, KB health output | `src/govkb/commands/status.py` | Extract a status payload builder and emit JSON only when requested. Preserve current text output. |
| Candidate command | Candidate staging/list/auto-create flows | `src/govkb/commands/candidates.py` | Extract candidate summary rows and add JSON output for `list` only. Leave staging and auto-create behavior unchanged. |
| Install flow | Project scaffold, validation, Codex materialization, memory-review task install | `src/govkb/commands/install.py` | Reuse from extension one-click setup through CLI invocation; do not duplicate in TypeScript. |
| Apply flow | Codex materialization and install-state tracking | `src/govkb/commands/apply.py`, `src/govkb/adapters/codex/materialize.py` | Reuse from extension one-click apply through CLI invocation. |
| KB bootstrap | Capability knowledge bootstrap and rematerialization | `src/govkb/commands/init_kb.py`, `src/govkb/core/kb_bootstrap.py` | Reuse during setup after install. |
| Memory review | Public CLI wrapper and packaged Codex task | `src/govkb/commands/review_memory.py`, `src/govkb/adapters/codex/bin/codex-memory-review` | Reuse for dry-run UI command; pass safe defaults from extension settings. |
| Bundle loading | Project, capability, adapter, release validation models | `src/govkb/core/contracts.py` | Use existing bundle and validation structures to populate status JSON. |
| Candidate model | Candidate file loading and listing | `src/govkb/core/candidates.py` | Use existing TOML source of truth for candidates JSON. |
| Install state | Codex state path and load helpers | `src/govkb/core/install_state.py` | Reuse for status JSON install-state section. |
| Python tests | CLI command-function tests using temp dirs | `tests/test_install.py`, `tests/test_apply.py`, `tests/test_init_kb.py`, `tests/test_candidates.py`, `tests/test_review_memory_command.py` | Follow existing `unittest.TestCase`, `TemporaryDirectory`, direct command-function patterns. |
| Docs | Product docs and feature artifacts | `README.md`, `docs/README.md`, `docs/governed-skill-knowledge-framework/**`, this feature folder | Update only docs needed for CLI JSON and extension local VSIX usage. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Spec handoff exists and is ready for the locked first slice. | Complete | Product/Engineering |
| Phase 3 PoC artifacts exist and targeted baseline tests pass. | Complete | Engineering |
| Marketplace publisher, icon, and public branding are required for public publish. | Deferred | Product |
| Node/npm and VS Code extension packaging tools are available locally or installable. | Verify during implementation | Engineering |
| Production code edits are allowed only after `review.md` says `Ready for Implementation: Yes`. | Pending review | Engineering |

## 1. Scope And Boundaries

In scope for the first engineering slice:

- Add JSON output for `govkb status` and `govkb candidates list`.
- Add `vscode-extension/` as an optional UI/orchestration package.
- Implement WSL/Linux-first local VSIX workflow with command palette commands, settings, status/candidates/reports views, output channel, and status bar.
- Implement one-click setup and one-click apply by invoking the GovKB CLI with argument arrays.
- Gate local execution and mutations behind VS Code Workspace Trust.
- Add Python tests for JSON CLI output and TypeScript tests for extension behavior.
- Package a local `.vsix`.

Out of scope for this slice:

- Marketplace publishing and final public branding.
- Runtime bundling, silent download, or embedded GovKB distribution.
- macOS, Windows native, and VS Code Web support.
- Scheduler UI.
- Memory-review apply mode in the extension.
- Telemetry.
- Direct TypeScript mutation of `.governed/` or `$CODEX_HOME`.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-VSCODE-01 | Local extension package and VSIX packaging | `vscode-extension/**` | New | Provisional metadata until public branding is decided. |
| REQ-VSCODE-02 | Thin CLI orchestration | `vscode-extension/src/govkbCli.ts`, `src/govkb/**` | New/Modify | Extension calls CLI only; no governance duplication. |
| REQ-VSCODE-03 | One-click setup | `vscode-extension/src/setupFlow.ts` | New | Sequence: runtime check, `install`, `init-kb --all`, `validate`, `status --json`. |
| REQ-VSCODE-04 | Missing runtime blocker | `vscode-extension/src/runtime.ts`, `setupFlow.ts` | New | Return one actionable install/configuration step and stop. |
| REQ-VSCODE-05 | Workspace Trust gating | `vscode-extension/src/trust.ts`, command registrations | New | Block execution before spawning child process. |
| REQ-VSCODE-06 | One-click apply | `vscode-extension/src/applyFlow.ts` | New | Run `govkb apply codex`, then `status --json`; no memory-review mutation. |
| REQ-VSCODE-07 | Dry-run memory review defaults | `vscode-extension/src/settings.ts`, `memoryReviewFlow.ts` | New | Defaults: `gpt-5.4-mini`, `low`, `180`, dry-run true. |
| REQ-VSCODE-08 | Status JSON | `src/govkb/cli.py`, `src/govkb/commands/status.py`, `tests/test_status_json.py` | Modify/New | Use `poc-artifacts/status.sample.json` as contract seed. |
| REQ-VSCODE-09 | Candidates JSON | `src/govkb/cli.py`, `src/govkb/commands/candidates.py`, `tests/test_candidates.py` or `tests/test_candidates_json.py` | Modify/New | Preserve current text mode. |
| REQ-VSCODE-10 | Report summary view | `vscode-extension/src/reports.ts`, `views/reportsView.ts` | New | Aggregate only; no transcript text copied into state. |
| REQ-VSCODE-11 | Argument-array execution | `vscode-extension/src/govkbCli.ts` | New | Use `child_process.spawn` or `execFile`, never shell interpolation. |
| REQ-VSCODE-12 | Settings resolution | `vscode-extension/src/settings.ts` | New | Treat command path, Python path, Codex home, and model settings as trust-sensitive. |
| REQ-VSCODE-13 | Multi-root selection | `vscode-extension/src/projectSelection.ts` | New | Stop on ambiguity and prompt for one project root. |
| REQ-VSCODE-14 | VSIX exclusions | `vscode-extension/.vscodeignore` | New | Exclude reports, Codex homes, `.governed`, generated output, and private paths. |
| REQ-VSCODE-15 | Core tests remain green | `tests/**`, `vscode-extension/src/test/**` | Modify/New | Run targeted tests and full Python suite before completion. |

## 3. Design

Python CLI JSON layer:

- Add `--json` to `govkb status` and `govkb candidates list`.
- Keep current text output as the default to avoid breaking existing users and docs.
- Build JSON payloads from existing validated objects, not by parsing printed strings.
- Serialize paths as strings and validation messages as objects with `location` and `message`.
- Return the same exit codes as the human output path.

Extension package:

- `vscode-extension/package.json` declares commands, views, settings, activation events, scripts, and provisional VSIX metadata.
- `src/extension.ts` registers commands, status bar, tree views, and output channel.
- `src/govkbCli.ts` owns command construction and process execution with argument arrays.
- `src/settings.ts` resolves extension settings and defaults.
- `src/projectSelection.ts` resolves a single project root.
- `src/trust.ts` blocks local execution when Workspace Trust is missing.
- `src/setupFlow.ts`, `src/applyFlow.ts`, and `src/memoryReviewFlow.ts` orchestrate CLI commands.
- `src/jsonParsers.ts` validates status/candidate/report summary shapes before views consume them.
- `src/views/*` implements status, capabilities, candidates, and reports tree providers.

## 4. Integration Points

| Integration | Direction | Contract |
|---|---|---|
| VS Code command palette | User to extension | Commands under `govkb.*` invoke typed flow functions. |
| VS Code Workspace Trust | Extension to VS Code API | Mutation and local execution commands call trust guard before CLI execution. |
| GovKB CLI | Extension to Python package | Use executable plus arg array; support configured `govkb.command` or Python module mode. |
| `.governed/**` | GovKB CLI to project repo | Source-of-truth mutations remain in Python CLI only. |
| `$CODEX_HOME/**` | GovKB CLI and report parser | Derived assistant-local state; extension may read summaries and open files but not mutate directly. |
| Output channel | Extension to user | Show command labels, exit status, stdout/stderr; avoid secrets and raw transcript content. |

## 5. Application Logic

One-click setup:

1. Resolve exactly one trusted workspace/project root.
2. Resolve settings and GovKB runtime.
3. If runtime is missing, stop with one install/configuration action.
4. Run `govkb install <workspace> --codex-home <codexHome>` with optional project id/name only when needed.
5. Run `govkb init-kb <workspace> --all --codex-home <codexHome>`.
6. Run `govkb validate <workspace>`.
7. Run `govkb status <workspace> --codex-home <codexHome> --json`.
8. Refresh views and status bar from JSON.

One-click apply:

1. Resolve trusted workspace/project root and settings.
2. Run `govkb apply codex --project-root <workspace> --codex-home <codexHome>`.
3. Run `govkb status <workspace> --codex-home <codexHome> --json`.
4. Refresh views and do not run memory-review apply mode.

Memory review dry-run:

1. Resolve trusted project root and settings.
2. Run `govkb review-memory --assistant codex --project-root <workspace> --dry-run --codex-model <model> --codex-reasoning <reasoning> --codex-timeout <timeout>`.
3. Refresh report summaries after command completion.

## 6. Data Consistency And Safety

- `.governed/` remains the project-owned source of truth.
- `$CODEX_HOME/skills/**` and memory-review reports remain derived local state.
- Extension TypeScript code does not write `.governed/` or Codex skill files directly.
- Tests use `tempfile.TemporaryDirectory` for Python and temp workspace/Codex home fixtures for TypeScript.
- JSON status and candidate output excludes raw sessions and secrets.
- Report view keeps aggregate counts and file paths only; full report inspection is a local file open action.
- Public package ignores local reports, Codex homes, `.governed` data, and generated test output.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Python status JSON unit tests | `tests/test_status_json.py` | Valid project, validation warnings/errors, Codex install-state present/missing, KB health warnings, text mode unchanged. |
| Python candidates JSON tests | `tests/test_candidates.py` or `tests/test_candidates_json.py` | Empty candidates, collecting candidate, ready candidate with suggested capability, text mode unchanged. |
| Python regression suite | `tests/**` | Existing install/apply/init-kb/candidate/review-memory behavior stays green. |
| Extension command construction tests | `vscode-extension/src/test/suite/govkbCli.test.ts` | Argument arrays for install, init-kb, validate, status JSON, apply, candidates JSON, review-memory dry-run. |
| Extension settings tests | `vscode-extension/src/test/suite/settings.test.ts` | Defaults and overrides for command, Python path, Codex home, classifier model/reasoning, timeout, dry-run. |
| Extension trust tests | `vscode-extension/src/test/suite/trust.test.ts` | Untrusted workspaces block commands before CLI invocation. |
| Extension flow tests | `vscode-extension/src/test/suite/setupFlow.test.ts`, `applyFlow.test.ts`, `memoryReviewFlow.test.ts` | Setup sequence, missing runtime blocker, apply sequence, dry-run defaults. |
| Extension parser/view tests | `vscode-extension/src/test/suite/views.test.ts`, `reports.test.ts` | Status/candidates/report fixtures parse without transcript leakage. |
| Packaging check | `vscode-extension/.vscodeignore`, package command | VSIX excludes local/private/generated state. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests/test_status_json.py tests/test_candidates.py -v` | `/home/ev/code/govkb` | Verify JSON CLI tests and candidates regressions. | JSON tests added. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Verify full Python suite. | Python implementation complete. |
| `PYTHONPATH=src python3 -m govkb.cli status <temp-project> --codex-home <temp-codex-home> --json` | `/home/ev/code/govkb` | Manual JSON status smoke. | Temp project initialized with `govkb init`. |
| `PYTHONPATH=src python3 -m govkb.cli candidates list <temp-project> --json` | `/home/ev/code/govkb` | Manual JSON candidates smoke. | Temp project has staged or empty candidates. |
| `npm install` | `/home/ev/code/govkb/vscode-extension` | Install extension dev dependencies. | `package.json` exists; network available. |
| `npm test` | `/home/ev/code/govkb/vscode-extension` | Run extension tests. | Dependencies installed. |
| `npm run compile` | `/home/ev/code/govkb/vscode-extension` | Compile TypeScript. | Dependencies installed. |
| `npx @vscode/vsce package --no-dependencies` | `/home/ev/code/govkb/vscode-extension` | Build local VSIX. | Compile passes; package metadata present. |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

- Add JSON CLI contracts for `status` and `candidates list`.
- Add Python tests that assert contract fields and preserve current text output.

Files:

- `src/govkb/cli.py`
- `src/govkb/commands/status.py`
- `src/govkb/commands/candidates.py`
- `tests/test_status_json.py`
- `tests/test_candidates.py` or `tests/test_candidates_json.py`

Verify:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests/test_status_json.py tests/test_candidates.py -v`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v`

Rollback:

- Revert the JSON flags, payload helpers, and JSON-specific tests. Existing text commands remain unaffected.

### Phase 1 - Core Extension Package

Scope:

- Scaffold `vscode-extension/` with manifest, TypeScript config, scripts, command ids, settings, views, output channel, and parser fixtures.
- Implement settings, project selection, runtime resolution, trust guard, and CLI argument-array runner.

Files:

- `vscode-extension/package.json`
- `vscode-extension/tsconfig.json`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/settings.ts`
- `vscode-extension/src/projectSelection.ts`
- `vscode-extension/src/runtime.ts`
- `vscode-extension/src/trust.ts`
- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/jsonParsers.ts`
- `vscode-extension/src/test/suite/*.test.ts`

Verify:

- `npm install`
- `npm run compile`
- `npm test`

Rollback:

- Remove `vscode-extension/`; Python JSON CLI support can stay if already merged because it is backward-compatible.

### Phase 2 - Command And Workflow Behavior

Scope:

- Implement one-click setup, one-click apply, validate/status/candidates commands, and memory-review dry-run command.
- Wire commands to status refresh and output channel.

Files:

- `vscode-extension/src/setupFlow.ts`
- `vscode-extension/src/applyFlow.ts`
- `vscode-extension/src/memoryReviewFlow.ts`
- `vscode-extension/src/commands.ts`
- `vscode-extension/src/test/suite/setupFlow.test.ts`
- `vscode-extension/src/test/suite/applyFlow.test.ts`
- `vscode-extension/src/test/suite/memoryReviewFlow.test.ts`

Verify:

- `npm run compile`
- `npm test`

Rollback:

- Revert workflow modules and command registrations; keep package scaffold if Phase 1 remains useful.

### Phase 3 - Views And Report Summaries

Scope:

- Implement status, capabilities, candidates, and reports views from JSON/status fixtures and local report summaries.
- Ensure report summaries do not retain raw transcript content.

Files:

- `vscode-extension/src/views/statusView.ts`
- `vscode-extension/src/views/capabilitiesView.ts`
- `vscode-extension/src/views/candidatesView.ts`
- `vscode-extension/src/views/reportsView.ts`
- `vscode-extension/src/reports.ts`
- `vscode-extension/src/test/fixtures/*.json`
- `vscode-extension/src/test/suite/views.test.ts`
- `vscode-extension/src/test/suite/reports.test.ts`

Verify:

- `npm run compile`
- `npm test`

Rollback:

- Disable view contributions in `package.json` and remove view provider modules.

### Phase 4 - Docs, Packaging, And Local VSIX

Scope:

- Add extension README, changelog, license handling note, `.vscodeignore`, and local VSIX packaging script.
- Update GovKB docs with local VSIX install and WSL/Linux first-slice caveats.

Files:

- `vscode-extension/README.md`
- `vscode-extension/CHANGELOG.md`
- `vscode-extension/.vscodeignore`
- `README.md`
- `docs/README.md`
- `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/release-notes.md` later in closeout

Verify:

- `npm run compile`
- `npm test`
- `npx @vscode/vsce package --no-dependencies`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v`

Rollback:

- Remove extension package artifacts or revert docs/package metadata changes. Python CLI JSON remains backward-compatible and can stay unless user requests full rollback.

## 10. Rollback Plan

- Python JSON CLI changes are additive. If JSON mode fails, remove `--json` flags and JSON tests while preserving current text behavior.
- Extension package is isolated under `vscode-extension/`; full rollback is removing that folder and related README/docs entries.
- No migration or data rewrite is planned for existing `.governed/` packages.
- No TypeScript code directly mutates `$CODEX_HOME`; failed extension flows can be disabled by unregistering commands or shipping without the VSIX.

## 11. Open Questions

| Question | Blocking? | Handling |
|---|---|---|
| What final Marketplace publisher id, extension id, icon, and branding should be used? | No for local VSIX | Use provisional local metadata and mark public publish as deferred. |
| Should report summaries eventually come from a Python CLI command instead of extension-side parsing? | No | Start with aggregate local parser; add CLI command later only if duplication appears. |
| Which Node test runner should be final: VS Code extension host tests only or split plain unit tests plus extension host tests? | No | Use the standard VS Code test pattern first; split only if tests become slow or brittle. |

## 12. Ready Checklist

| Item | Status |
|---|---|
| Accepted first-slice scope is documented in `scope-lock.md` and `spec-handoff.md`. | Yes |
| Requirements map to use cases and PoC assertions. | Yes |
| Existing code inventory references concrete paths. | Yes |
| New files are justified and isolated. | Yes |
| Verification commands include targeted and full Python tests. | Yes |
| Extension tests and packaging commands are named with working directories. | Yes |
| Governance boundaries for `.governed/`, `$CODEX_HOME`, and raw transcripts are explicit. | Yes |
| Rollback is phase-specific. | Yes |
| Plan review completed. | Pending |

