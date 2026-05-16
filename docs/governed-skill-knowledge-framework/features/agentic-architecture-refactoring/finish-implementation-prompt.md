# Agentic Architecture Refactoring - Finish Implementation Prompt

Use this prompt in a fresh Codex session from the GovKB repository root.

```text
You are Codex working in `/Users/vasilevevgeny/code/govkb`.

Use the `govkb-feature-cookbook` skill. Your task is to finish the `agentic-architecture-refactoring` feature to an acceptable merge-ready state, not to start a new design pass.

Feature folder:
`docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/`

First read:
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/business.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/context.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/use-cases.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/requirements-catalog.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/poc-plan.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/poc-output.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/implementation-plan.md`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/review.md`
- all existing `implementation-summary-phase-*.md` files in the feature folder
- `docs/COOKBOOK/POC_PARITY_REVIEW_PROMPT.MD`

Then inspect the current implementation before editing:
- `git status --short`
- `git diff --stat`
- `git diff -- src/govkb/cli.py src/govkb/commands/promotions.py src/govkb/core/promotion_lifecycle.py src/govkb/core/skill_conversion.py`
- `git diff -- vscode-extension/src vscode-extension/package.json`
- `git diff -- tests/test_promotions.py tests/test_agentic_architecture_refactoring_smoke.py tests/test_agentic_architecture_refactoring_use_cases.py`

Important working-tree rule:
- Do not revert unrelated user changes. In particular, inspect any modified file that is not already covered by the phase summaries, such as `src/govkb/core/skill_conversion.py`, and either incorporate it into the feature evidence if it is related or leave it untouched and call it out in the final status.
- Do not modify `.governed/capabilities/prompt-engineering-kb/` unless the user explicitly asks; it is currently unrelated untracked project state.

Current completed scope, based on existing summaries:
- Phase 0: architecture ownership doc and smoke test.
- Phase 1: VS Code action registry, Home model registry consumption, and registry/manifest parity tests.
- Phase 2: idempotent promotion accept/reject/archive/apply no-op behavior and Python regression coverage.
- Phase 3: promotion cleanup preview/apply, metadata preservation, CLI/VS Code wiring, and cleanup tests.
- Phase 4: governed skill summary rows, conversion picker filtering, one-click default target id, and extension tests.

Remaining goal:
Finish Phase 5 and the merge gate. This means the feature is understandable, verified, manually checked where necessary, and documented with no loose implementation/story gaps.

Required work:
1. Confirm every requirement in `requirements-catalog.md` maps to implementation evidence, tests, or explicit accepted deviation.
2. Confirm every use case in `use-cases.md` is covered by automated tests, extension tests, CLI verification, or manual QA evidence.
3. Inspect whether Phase 1 follow-up "tree view command metadata consolidation" is still necessary for this feature. If behavior is already acceptable, document it as a non-blocking follow-up; if there is a small safe cleanup, implement it with tests.
4. Inspect whether Phase 4 needs a persisted governed skill summary contract. If existing status fields are sufficient, keep the no-new-contract decision and document it in parity review; only add storage if there is a concrete failing requirement.
5. Run manual QA on the Clearing project in read-only or controlled mode:
   - status for `/Users/vasilevevgeny/code/Etna/Clearing`
   - promotions list and cleanup preview
   - local skill conversion picker filtering via the extension helper or compiled JS
   - do not apply destructive cleanup unless the preview shows only applied/archived/rejected/cleaned eligible artifacts and the user has already asked for cleanup
6. Create `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/poc-parity-review.md` using `docs/COOKBOOK/POC_PARITY_REVIEW_PROMPT.MD`.
7. Create final feature artifacts if missing:
   - `implementation-summary-phase-5.md`
   - `release-notes.md`
   - `sign-off.md`
   - `presentation.md` only if it adds useful stakeholder-facing summary; keep it concise.
8. Update `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/implementation-plan.md` only for truthful status changes, not to rewrite history.
9. Update `docs/governed-skill-knowledge-framework/features/README.md` only if the feature link is missing.

Verification commands to run before declaring done:
- `git diff --check`
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `npm test` from `vscode-extension`
- `npm run test:host` from `vscode-extension`
- `PYTHONPATH=src python3 -m govkb.cli validate /Users/vasilevevgeny/code/govkb`

If local `python3` is not Python 3.11+ or fails on `tomllib`, use the bundled runtime already used in this workspace:
`/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`

Acceptable completion criteria:
- `poc-parity-review.md` says `Ready for Merge: Yes`, or clearly lists exact remaining blockers.
- All required verification commands have run, with exact results recorded in the Phase 5 summary.
- Any validation warnings are identified as existing/non-blocking or fixed.
- No generated scratch directories remain, for example `vscode-extension/.vscode-test/`.
- Promotion cleanup behavior remains preview-first and root-contained.
- Repeated promotion lifecycle actions remain idempotent and do not rewrite metadata on no-op.
- Conversion picker hides already governed and GovKB-generated skills by default while preserving manual entry.
- VS Code UI commands remain contributed in `package.json` and covered by registry parity tests.
- No raw session transcript content, secrets, production data, or accidental local assistant state are added to repo artifacts.

Final response shape:
- Summarize completed remaining work.
- List files created or materially changed.
- List verification commands and results.
- Call out unrelated dirty files or untracked state left untouched.
- Do not stage or commit unless explicitly asked.
```
