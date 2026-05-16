# Agentic Architecture Refactoring - Stakeholder Presentation

Status: Ready
Date: 2026-05-16

## 1. Executive Summary

GovKB had enough agentic workflow surface area that users could not reliably tell what state was source, derived, review-only, or stale. This feature adds the architecture map, CLI lifecycle guards, cleanup flow, and VS Code metadata/tests needed to make the everyday path understandable and safe to rerun.

## 2. Problem

- Users saw stale or duplicate promotion worktrees without a clear cleanup/finalization path.
- Conversion UX exposed already governed or GovKB-generated skills and sometimes forced unnecessary typing.
- Action labels, icons, and command ids could drift between Home, tree views, and the manifest.

## 3. Delivered Scope

| Area | Delivered |
|---|---|
| Product behavior | Clearer Home actions, governed skill summaries, conversion filtering, and cleanup prompts. |
| CLI/API behavior | Idempotent promotion reruns and `govkb promotions cleanup` preview/apply. |
| Documentation | State ownership map, phase summaries, parity review, release notes, and sign-off. |
| Tests | Python temp-dir lifecycle/cleanup tests and TypeScript registry, parser, flow, view, and packaging tests. |

## 4. Workflow

```text
unclear promotion/skill state -> CLI-backed preview or idempotent action -> explicit UI next step and preserved audit metadata
```

## 5. Use Case Coverage

| Scenario | Status | Evidence |
|---|---|---|
| UC-1 Ownership map | Covered | Smoke test and architecture doc. |
| UC-2 Action registry | Covered | Registry and packaging parity tests. |
| UC-3 Idempotent finalization | Covered | Promotion lifecycle regression tests. |
| UC-4 Cleanup preview | Covered | No-write cleanup preview test. |
| UC-5 Cleanup apply | Covered | Scoped removal, metadata preservation, and idempotent rerun tests. |
| UC-6 Conversion UX | Covered | Local skill filtering tests and Clearing helper QA. |
| UC-7 Governed skill summaries | Covered | Capability view tests. |
| UC-8 CLI mutation boundary | Covered | Registry mutation flags, flow tests, and temp-dir tests. |
| UC-9 Next action mapping | Covered | Home state tests. |

## 6. Verification

| Check | Evidence | Result |
|---|---|---|
| Test suite | `PYTHONPATH=src ... -m unittest discover -s tests -v` | Passed, 172 tests, 33 skipped. |
| Extension suite | `npm test`; `npm run test:host` | Passed, 115 tests and host exit 0. |
| CLI validation | `govkb.cli validate /Users/vasilevevgeny/code/govkb` | Passed with one existing non-blocking warning. |
| Clearing QA | Status, promotions list, cleanup preview, conversion filtering helper. | Passed read-only/controlled checks. |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes. |

## 7. Rollout And Rollback

Rollout:

- Merge the feature changes through normal repo review.
- Rebuild or reinstall the VS Code extension from the updated source.
- Use cleanup preview before applying cleanup in real projects.

Rollback:

- Revert the feature branch changes.
- Reinstall the prior extension build if needed.
- No metadata migration rollback is needed; cleanup preserves sidecar lifecycle metadata.

## 8. Decisions Or Follow-ups

| Item | Owner | Needed By |
|---|---|---|
| Full tree view metadata generation from registry | Engineering | Later only if drift returns. |
| Persisted governed skill summary field | Product/engineering | Later only if current status fields prove insufficient. |
| Unrelated untracked `prompt-engineering-kb` package disposition | Maintainer | Before committing if it should be part of this branch. |
