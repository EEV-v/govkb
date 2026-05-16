# Governed Skill Management UX

## Stakeholder Need

GovKB users need to manage governed skills after project adoption without hand-editing `.governed`. The expected workflow is that a user can inspect governed skills, convert an existing local Codex skill into a governed capability, rename a governed skill when the scope becomes clearer, and merge duplicate governed skills when learning or migration produces overlapping capabilities.

## Success Criteria

- A user can see governed skills as a first-class VS Code view, including names, descriptions, lifecycle hints, and openable package files.
- A user can convert an existing Codex skill by entering a skill name under `CODEX_HOME/skills`, an explicit skill folder path, or a direct `SKILL.md` path.
- A user can rename a governed skill while preserving the old id as a routing alias.
- A user can merge one governed skill into another, preserving reusable instructions and memory guidance in the target and recording a merge report.
- CLI commands exist for the same operations so the VS Code extension is not the only entry point.
- Operations leave Git changes visible for review and do not commit automatically.
