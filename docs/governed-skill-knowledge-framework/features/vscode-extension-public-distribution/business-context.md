# Business Context - VS Code Extension UI and Public Distribution

Last updated: 2026-04-25

## Business Purpose And Workflow

GovKB is moving from a local power-user CLI into a reusable standalone product. The next adoption bottleneck is not core governance behavior; it is discoverability, onboarding, and day-to-day operation.

The VS Code extension should give users a familiar way to:

- run one-click setup for the open project
- run one-click apply of the governed package to Codex for the open project
- initialize or validate a repo-governed knowledge package when the user chooses the lower-level commands
- inspect governed capabilities and candidate growth
- run memory-review dry-runs with safe defaults
- understand whether local Codex materialization is current
- package and distribute GovKB to public users without requiring them to read internal development notes

The extension is a distribution and operations surface. It is not the source of truth for governed knowledge.

## Domain Terms

| Term | Meaning |
|---|---|
| GovKB core | The Python package and CLI that owns validation, materialization, candidate management, and memory review. |
| `.governed/` package | Repo-native source of truth for project knowledge, capabilities, adapters, releases, and candidates. |
| Adapter materialization | Creating assistant-local files from governed repo source, currently for Codex. |
| Candidate | A repeated or unmatched semantic work pattern staged for possible capability creation. |
| VSIX | Installable VS Code extension package used for private or pre-Marketplace distribution. |
| Marketplace | Public VS Code extension distribution channel. |
| Workspace Trust | VS Code safety model that controls behavior when a workspace may execute local code or scripts. |

## Existing Product Context

Current GovKB docs define the product as a repo-native governed knowledge framework with a public CLI surface. The MVP explicitly excluded UI for memory governance. That makes this feature a post-MVP distribution layer rather than a change to the core product contract.

Relevant existing GovKB constraints:

- project-only knowledge lives in git under `.governed/`
- assistant-local files are derived outputs
- Codex is the first adapter, but the model must stay assistant-agnostic
- semantic classification and candidate creation must remain governed
- real-life validation should use low-cost nested classifier defaults unless a diagnostic rerun needs more

## External Distribution Context

Official VS Code documentation supports two distribution modes:

- package an extension as `.vsix` for local/private installation
- publish to the VS Code Marketplace using `@vscode/vsce`

Marketplace publishing requires a publisher identity and Personal Access Token flow. The extension package also needs public-facing metadata such as README, changelog, license handling, and icon/banner choices.

Official VS Code Workspace Trust guidance is directly relevant because this extension will execute local commands and read/write workspace files. Trust-sensitive behavior should be blocked or limited until the user trusts the workspace.

## Source-Backed Constraints

| Constraint | Source | Impact |
|---|---|---|
| VS Code extensions can be packaged as `.vsix` or published to Marketplace with `@vscode/vsce`. | VS Code Publishing Extensions docs, accessed 2026-04-25 | First release can ship as VSIX before public Marketplace release. |
| Marketplace publishing requires publisher setup and PAT-based publishing. | VS Code Publishing Extensions docs, accessed 2026-04-25 | Public release needs branding and publisher decisions before publish. |
| Extensions that execute workspace-derived code or commands need Workspace Trust handling. | VS Code Workspace Trust docs, accessed 2026-04-25 | GovKB commands that mutate or execute must be gated in untrusted workspaces. |
| Existing GovKB core is a Python package with a console script. | `pyproject.toml` | Extension should call the CLI instead of duplicating logic. |
| Existing GovKB memory-review supports model and reasoning flags. | `src/govkb/cli.py` | Extension can expose low-cost classifier settings without core changes. |

## Assumptions

| ID | Assumption | Risk If Wrong |
|---|---|---|
| A1 | One-click setup is the required public UX; the remaining decision is how the extension provisions or locates the GovKB runtime. | If provisioning is weak, users still face manual setup friction. |
| A2 | VSIX distribution is acceptable before Marketplace publication. | If Marketplace is required first, publisher and branding become launch blockers. |
| A3 | Workspace Trust gating is mandatory for a credible public extension. | If ignored, public users may run local mutations in unsafe workspaces. |
| A4 | Low-cost classifier defaults should be visible extension settings. | If hidden, public validation may burn quota or time unnecessarily. |
| A5 | The first UI can be single-workspace focused. | Multi-root users may see ambiguous project state. |

## Open Business Questions

| ID | Question | Why It Matters |
|---|---|---|
| BQ1 | What public publisher id, display name, and extension id should be used? | Marketplace identity is hard to rename later. |
| BQ2 | Which runtime provisioning mechanism should support one-click setup: bundled wheel, downloaded package, embedded source, or guided local install action? | Determines installation support burden and public onboarding quality. |
| BQ3 | Is telemetry allowed, and must it be opt-in? | Public extensions need an explicit privacy posture. |
| BQ4 | Which platforms are launch-supported: WSL/Linux only, macOS, Windows native, or all three? | Path handling and Codex home discovery differ by platform. |
| BQ5 | Should memory-review mutation be exposed immediately, or should the first release limit one-click apply to governed package materialization plus dry-run memory review? | Controls governance risk in first release. |

## Sources

| Source | Location | Accessed |
|---|---|---|
| GovKB product spec | `docs/governed-skill-knowledge-framework/business.md` | 2026-04-25 |
| GovKB implementation plan | `docs/governed-skill-knowledge-framework/implementation-plan.md` | 2026-04-25 |
| GovKB MVP+ test plan | `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md` | 2026-04-25 |
| GovKB CLI entrypoint | `src/govkb/cli.py` | 2026-04-25 |
| VS Code Publishing Extensions | https://code.visualstudio.com/api/working-with-extensions/publishing-extension | 2026-04-25 |
| VS Code Workspace Trust Extension Guide | https://code.visualstudio.com/api/extension-guides/workspace-trust | 2026-04-25 |
