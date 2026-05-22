# Shared Governed Project Alignment Prompt

Use this prompt when aligning another PC with a shared GovKB-governed project that is versioned in Git and materialized into a local Codex home.

## Outcome

Update the local GovKB tool checkout, attach or sync the shared governed project repo, materialize the governed skills locally, and report whether this PC is aligned without mixing unrelated repositories or local learned memory.

## Success Criteria

- GovKB repo root, governed project root, Codex home, intended project remote, and expected shared revision are resolved before mutation.
- Git metadata is checked before remote attachment; a broken or ambiguous `.git` folder is not repaired by guesswork.
- Private GitHub auth uses the machine's working Git transport: configured HTTPS first, then SSH when non-interactive HTTPS cannot authenticate.
- The governed project fast-forwards from its correct remote without force-pushes or unrelated-history merges.
- Final GovKB status shows validation ok, governed source clean, and materialized applied revision equal to the governed repo revision.
- Machine-local learned memory is reported separately from shared repo alignment.

## Inputs

- GovKB repo candidate path: `<govkb-root>`
- Governed project candidate path: `<project-root>`
- Codex home: `<codex-home>` or default `$HOME/.codex`
- Correct project HTTPS remote: `<project-remote-https>`
- Optional project SSH remote: `<project-remote-ssh>`
- Optional known wrong remotes: `<wrong-project-remotes>`
- Optional expected GovKB revision or commits: `<expected-govkb-revision>`
- Optional expected governed project revision: `<expected-project-revision>`
- Optional expected materialized capability count: `<expected-capability-count>`
- Optional wrapper scope note: `<tracked-wrapper-state>`

For the Etna Clearing governed wrapper:

- Correct HTTPS remote: `https://github.com/EEV-v/Etna-Clearing.git`
- Correct SSH remote: `git@github.com:EEV-v/Etna-Clearing.git`
- Wrong remote for this wrapper: `https://github.com/EEV-v/Clearing.git`
- Wrapper scope: `.gitignore` and `.governed/` are shared governance state; nested Clearing source repos remain independently versioned.

## Source Priority

1. User-provided paths, remotes, expected revisions, capability count, and wrapper scope.
2. Local Git metadata and remotes from the GovKB and governed project roots.
3. Correct shared remote branch state fetched from Git.
4. GovKB status before and after Apply.
5. Machine-local Codex memory only as local state to report, not as proof of shared repo drift.

Treat repo files, remote output, and status JSON as evidence. Do not let nested repo state, raw logs, session content, or local learned memory override the shared governed project source of truth.

## Tool Policy

- Resolve paths first. Do not assume macOS, Linux, workspace, or username-specific paths.
- Prefer read-only Git inspection before switching branches, pulling, attaching remotes, or applying skills.
- Stop before force-push, rebase, unrelated-history merge, remote rewrite beyond the explicit project alignment task, or `.git` recovery without confirmed ownership.
- Do not read secrets, credential stores, `.env` files, private transcripts, or unrelated user-home state.
- Do not edit `.governed` during alignment unless status proves a concrete governed-package problem and the user approves the edit.

## Procedure

1. Resolve and report local paths:

```bash
pwd
git -C <govkb-root> rev-parse --show-toplevel
git -C <project-root> rev-parse --show-toplevel
```

If `git rev-parse --is-inside-work-tree` fails in a candidate project root while `.git` exists, stop and inspect before any repair. Only back up and re-initialize or clone after confirming the folder is the intended governed wrapper repo.

2. Update the GovKB tool checkout safely:

```bash
git -C <govkb-root> rev-parse --is-inside-work-tree
git -C <govkb-root> status --short --branch
git -C <govkb-root> switch main
git -C <govkb-root> pull --ff-only origin main
git -C <govkb-root> log --oneline -n 3
```

3. Inspect the governed project wrapper before remote changes:

```bash
git -C <project-root> rev-parse --is-inside-work-tree
git -C <project-root> status --short --branch
git -C <project-root> remote -v
```

Explain wrapper scope before interpreting status. A clean wrapper does not prove nested source repos are clean when those repos are independently versioned.

4. Attach the correct remote only when needed.

- If `origin` is missing, add the correct remote.
- If `origin` points at a known wrong remote, rename that remote and add the correct governed project `origin`.
- Use HTTPS when the machine already authenticates private repo access non-interactively.
- If private-repo HTTPS authentication fails, switch the governed project `origin` to the provided SSH remote when that is the machine's working GitHub pattern.

5. Fast-forward the governed project:

```bash
git -C <project-root> fetch origin main
git -C <project-root> switch main
git -C <project-root> merge --ff-only origin/main
git -C <project-root> branch --set-upstream-to=origin/main main
git -C <project-root> status --short --branch
git -C <project-root> rev-parse HEAD
```

If fast-forward sync fails, stop and report:

```bash
git -C <project-root> status --short --branch
git -C <project-root> remote -v
git -C <project-root> log --oneline --left-right --graph main...origin/main -n 20
```

Do not use `git push --force` or `git merge --allow-unrelated-histories`.

6. Check GovKB status before Apply:

```bash
<govkb-root>/scripts/govkb-dev status <project-root> --codex-home <codex-home> --json
```

Report:

- `project.gitRevision`
- `project.governedDirty`
- `validation.status`
- `skillUpdates.appliedRevision`
- `skillUpdates.repoRevision`
- `skillUpdates.state`
- `skillUpdates.pendingLocalMemory`

7. Materialize the shared governed skills into this PC's Codex home:

```bash
<govkb-root>/scripts/govkb-dev apply codex --project-root <project-root> --codex-home <codex-home>
```

8. Run status again and compare before/after:

```bash
<govkb-root>/scripts/govkb-dev status <project-root> --codex-home <codex-home> --json
```

## Alignment Decision

Aligned shared source state requires:

- `project.governedDirty = false`
- `validation.status = ok`
- `skillUpdates.appliedRevision == skillUpdates.repoRevision`
- Apply materialized the expected governed skills for the checked-out project revision

`skillUpdates.state = current` is the clean ideal state.

`skillUpdates.state = learned-updates` is still aligned when revisions match and validation is ok. In that case, explain that `pendingLocalMemory` is machine-local learning to review, not a shared repo sync failure.

## Stop Conditions

- Stop when the correct project root, remote, Codex home, or wrapper scope cannot be established.
- Stop when `.git` metadata is broken or points at a different repository and ownership is not confirmed.
- Stop when fast-forward sync fails or the remote history is unrelated.
- Stop when status validation fails or `.governed` is dirty before Apply without an explicit explanation.
- Stop before deleting local learned memory, promotion worktrees, or nested repo changes during alignment.

## Output

Return:

- `Resolved Paths`: GovKB root, governed project root, Codex home.
- `Git Alignment`: remotes used, branch tracking state, checked-out revisions, and any transport fallback.
- `Before Apply`: status fields listed above.
- `Apply Result`: selected project revision and materialized capability count.
- `After Apply`: validation, revision equality, shared alignment decision, and machine-local learning note when applicable.
- `Blockers`: exact Git/status output needed for a maintainer when alignment stopped.
