# VS Code Guided Daily Workflow UI - Requirements Catalog

Last updated: 2026-05-16

| ID | Requirement | Source | Acceptance Evidence |
|---|---|---|---|
| REQ-VGDW-01 | Provide a GovKB Home surface that shows one primary next action with a short reason and consequence. | `business.md` Success Criteria | Home model tests and rendered webview smoke. |
| REQ-VGDW-02 | Preserve existing tree views as compact summaries rather than primary workflow surfaces. | `business.md` Success Criteria | View row tests for compact labels and inline actions. |
| REQ-VGDW-03 | Guide setup, apply, learning review, promotion review, finalization, commit, and rematerialization states. | `business.md` Daily flow | Table-driven next-action tests. |
| REQ-VGDW-04 | Use icons and clear labels for common actions. | `business.md` Success Criteria | Command contribution and TreeRow icon tests. |
| REQ-VGDW-05 | Show promotion digest and lifecycle state before opening a worktree. | `business.md` User-Visible Outcomes | Promotion card and command routing tests. |
| REQ-VGDW-06 | Provide picker-driven convert, rename, and merge flows with manual fallback only when chosen. | `business.md` Success Criteria | Local skill and capability picker tests. |
| REQ-VGDW-07 | Hide already governed or materialized skills from conversion choices. | `business.md` Success Criteria | Existing `localSkills` tests plus Home action coverage. |
| REQ-VGDW-08 | Collapse duplicate and finalized promotion worktrees away from the main next action. | `business.md` Success Criteria | Promotion grouping tests. |
| REQ-VGDW-09 | Keep all project and assistant-local mutations behind the GovKB CLI. | `business.md` Constraints | Flow tests assert command builder use; no direct write helpers in webview. |
| REQ-VGDW-10 | Avoid raw transcript and private local-state leakage in UI and tests. | `business.md` Constraints | Parser/model fixture tests and review checklist. |
| REQ-VGDW-11 | Keep everyday Home wording business-readable by hiding dry-run terminology from the primary learning path. | `business.md` Daily Flow Wording Refinement | Home model tests assert the primary review label and consequence text. |

## Out Of Scope Requirements

| ID | Non-Requirement | Reason |
|---|---|---|
| NR-VGDW-01 | Automatic Git commits | User review and project workflow remain external. |
| NR-VGDW-02 | Standalone app UI | VS Code extension is the delivery target. |
| NR-VGDW-03 | Raw session transcript viewer | Violates governance and privacy constraints. |
