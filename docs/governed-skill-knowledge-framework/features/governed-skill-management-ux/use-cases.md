# Governed Skill Management UX Use Cases

## Feature Type

VSCodeExtension plus CLI.

## Scenarios

### @smoke List Governed Skills

Given a GovKB project has governed capabilities, when the user refreshes the Governed Skills view, then the extension shows the governed skill list with openable rows and management actions.

### Convert One Existing Codex Skill

Given a user has local Codex skills, when the user runs Convert One Existing Skill To Governed, then GovKB shows a picker of discovered `CODEX_HOME/skills` packages plus a manual path fallback, previews only the chosen skill, asks for confirmation, writes one governed package, and leaves the source skill unchanged.

### Convert Skill-Owned Assets Safely

Given the chosen source skill references helper scripts, prompts, reference files, or repo documents, when GovKB builds the conversion preview, then it copies safe skill-owned assets into the governed package, rewrites moved package paths, rewrites absolute paths inside the target project to repo-relative paths, and blocks unresolved or unsafe references before write.

### Rename Governed Skill

Given a governed skill id no longer describes its scope, when the user renames it, then GovKB moves the capability package, updates the contract id and name, preserves the old id as an alias, and leaves a reviewable Git diff.

### Merge Duplicate Governed Skills

Given two governed skills overlap, when the user merges the source into the target, then GovKB copies reusable source guidance into the target, adds source aliases to target routing, writes a merge report, removes the source capability, and leaves a reviewable Git diff.

### CLI Parity

Given a user prefers terminal workflows or automation, when they run `govkb capabilities list`, `govkb capabilities rename`, or `govkb capabilities merge`, then the same capability-management operations are available outside VS Code.
