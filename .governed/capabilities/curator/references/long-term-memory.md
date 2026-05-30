# GovKB Curator

## Working Agreement

- Operate as the project-level GovKB lifecycle maintainer, not as a domain implementation skill.
- Prefer governed reports, promotion digests, proposal metadata, candidates, validation output, and git status over raw transcripts.
- Never apply learning, proposals, candidates, or cleanup just because they exist; inspect safety and usefulness first.
- Keep local materialized skill memory and governed package memory aligned after accepted changes.

## Operating Flow

- Start with `git status --short --branch` in the governed project and in the GovKB repo when tools may change.
- Run `govkb-dev status <project-root> --codex-home <codex-home> --json` before deciding next action.
- If installed skills are stale, run `govkb-dev apply codex --project-root <project-root> --codex-home <codex-home>`.
- Use `govkb-dev review-memory --assistant codex --project-root <project-root> --inventory-json --lookback-days 90 --max-sessions 5` to see the next bounded learning batch.
- Use apply-mode review only when the user wants learning applied: `govkb-dev review-memory --assistant codex --project-root <project-root> --lookback-days 90 --max-sessions 5 --codex-timeout 180 --progress-jsonl`.
- After learning review, read the generated report before applying promotions, proposals, or candidates.
- For applied governed package changes, run `govkb-dev apply codex` again so local Codex skills match the package.

## Commands And Verification

- Use `govkb-dev promotions list <project-root> --codex-home <codex-home> --json` to find promotion lifecycle state.
- Use `govkb-dev promotions show <promotion> --project-root <project-root> --codex-home <codex-home>` or read the digest before accepting a promotion.
- Use `govkb-dev promotions mark-reviewed <promotion> --project-root <project-root> --codex-home <codex-home> --decision accepted --reason <reason> --json` only after reviewing the digest.
- Use `govkb-dev promotions apply <promotion> --project-root <project-root> --codex-home <codex-home> --json` to finalize accepted promotion changes into the active governed package.
- Use `govkb-dev proposals report <project-root> --json` and `govkb-dev proposals review <project-root> --json` before applying staged proposals.
- Use `govkb-dev proposals show <proposal-id> --project-root <project-root>` before any proposal apply.
- Use `govkb-dev proposals apply <proposal-id> --project-root <project-root>` only after explicit approval metadata exists and the proposal is safe.
- Use `govkb-dev candidates list <project-root> --json` to inspect candidates; use auto-create only when project policy and candidate maturity allow it.
- Run `govkb-dev validate <project-root> --strict` after governed package edits.

## Safety And Apply Policy

- Accept promotions when additions are append-only, scoped to the target capability, durable, evidence-backed, non-duplicative, and free of secrets or private transcript detail.
- Reject or hold promotions when additions depend on local state, one-off task status, unclear provenance, sensitive data, or broad assistant runtime facts.
- Apply docs-only proposals when they have clean sensitivity, adequate confidence, visible draft output, unique output paths, and strict validation passes.
- Hold script proposals unless draft code exists, the code is reviewed, the safety class matches behavior, and a focused verification command passes.
- Hold mutating proposals unless the runbook or tool has explicit preview or rollback behavior, approval requirements, and clear safety boundaries.
- Do not auto-create a governed capability from a one-occurrence candidate unless the user explicitly approves and the scope is obvious.
- Do not delete promotion worktrees or review artifacts without previewing cleanup and confirming they are non-actionable.

## State Interpretation

- `skillUpdates.state = current` means materialized skills match the governed package revision.
- `skillUpdates.state = apply-available` means run `apply codex` before relying on local skills.
- `skillUpdates.state = learned-updates` means local skill memory has useful learning that can be promoted after review.
- `skillUpdates.state = workspace-changes` means the governed package has active git changes that should be reviewed, validated, committed, or deliberately left staged.
- `pendingLocalMemory.safePromotionCount > 0` is a prompt to review promotion candidates, not permission to blindly apply.
- Validation warnings about historical migration source paths can be non-blocking when strict validation passes and the package has already been converted.

## Output Contract

- Report what was applied, what was held, and why.
- Include promotion run ids, proposal ids, candidate ids, and changed governed files.
- Include validation result and materialized skill apply result.
- State whether the project is ready to commit, still has review items, or needs cleanup.

## Code And Docs Map

- Governed capability definitions live under `.governed/capabilities/`.
- Adapter definitions live under `.governed/adapters/`.
- Project-level GovKB settings live in `.governed/project.toml`.
- GovKB lifecycle implementation lives under `src/govkb/`.
- VS Code UI integration lives under `vscode-extension/`.
