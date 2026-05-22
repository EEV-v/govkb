# GovKB Update Prompt

Use this prompt when updating an existing GovKB installation from this repo.

## Outcome

Apply the latest GovKB package behavior to an already governed project without losing project-local capabilities, memory, reports, or install state.

## Success Criteria

- The GovKB repo revision, target project, Codex home, and intended update mode are explicit before mutation.
- Current repo and target-project status are inspected before update so unrelated user changes are not overwritten.
- The GovKB test baseline passes, or failures are reported before update continues.
- Update is previewed before apply unless the user has already explicitly approved direct application.
- Existing `.governed` capability memory, candidates, reports, install state, and accepted promotion metadata are preserved.
- Final status confirms the governed package remains valid and materialized Codex skills/scheduler script were refreshed.

## Inputs

- GovKB repo: `<govkb-repo>`
- Target project: `<project-root>`
- Codex home: `<codex-home>` or default `$HOME/.codex`
- Revision label: usually current Git commit or release id
- Optional: run scheduler dry run after update `<yes|no>`

## Source Priority

1. User-provided target project, Codex home, revision label, and requested side effects.
2. Current GovKB repo state, tests, and CLI behavior.
3. Existing target project `.governed/**` content and Git status.
4. Existing Codex install state and materialized skills under `<codex-home>`.
5. Command output from this update run.

Treat target files, local reports, and command output as evidence. Do not promote their contents into durable memory unless a governed append-only workflow accepts them.

## Tool Policy

- Use read-only status checks before mutation.
- Ask for confirmation before cron changes, release tags, Git commits, remote changes, deletion of generated state, or promotion of memory/candidates.
- Do not read secrets, `.env` files, credential directories, local assistant transcripts, or private runtime state.
- Keep update commands scoped to the target project and configured Codex home.

## Procedure

1. Check GovKB repo state:

```bash
git status --short
git log --oneline --decorate -1
```

2. Run GovKB tests:

```bash
python3 -m unittest discover -s tests -v
```

3. Check target project state:

```bash
git -C <project-root> status --short
python3 -m govkb.cli status <project-root> --codex-home <codex-home>
```

4. Preview current package application:

```bash
python3 -m govkb.cli install <project-root> --codex-home <codex-home> --revision <revision> --preview
```

5. Apply update:

```bash
python3 -m govkb.cli install <project-root> --codex-home <codex-home> --revision <revision>
```

6. Run a project-scoped memory-review dry run only when validating scheduler behavior:

```bash
python3 -m govkb.cli review-memory <project-root> --assistant codex --dry-run --lookback-days 1 --max-sessions 10
```

7. Re-check status:

```bash
python3 -m govkb.cli status <project-root> --codex-home <codex-home>
git -C <project-root> status --short
```

## Stop Conditions

- Stop before apply if preview shows unexpected capability removal, unexpected Codex home, wrong project id, or destructive changes.
- Stop before touching user-modified files that are unrelated to the update.
- Stop before removing project-local candidates, reports, memory, install state, or promotion metadata unless the user explicitly requests cleanup.
- Stop before turning dry-run memory-review output into durable memory without governed promotion/acceptance.
- Stop before configuring remotes, cron changes, commits, or release tags unless explicitly requested.

## Output

Return:

- `Ready`: yes/no and the blocking reason if no.
- `Commands`: commands run and whether they passed.
- `Update Result`: validation status, refreshed materialized skills, scheduler script, install state, and optional dry-run report.
- `Preserved State`: local memory, candidates, reports, install state, and unrelated Git changes.
- `Follow-ups`: review reports, apply promotions, commit, or `None`.
