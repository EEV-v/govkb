# GovKB Update Prompt

Use this prompt when updating an existing GovKB installation from this repo.

## Goal

Apply the latest GovKB package behavior to an already governed project without losing project-local capabilities, memory, reports, or install state.

## Inputs

- GovKB repo: `<govkb-repo>`
- Target project: `<project-root>`
- Codex home: `<codex-home>` or default `$HOME/.codex`
- Revision label: usually current Git commit or release id

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

6. Run a project-scoped memory-review dry run when validating scheduler behavior:

```bash
python3 -m govkb.cli review-memory <project-root> --assistant codex --dry-run --lookback-days 1 --max-sessions 10
```

7. Re-check status:

```bash
python3 -m govkb.cli status <project-root> --codex-home <codex-home>
git -C <project-root> status --short
```

## Safety Rules

- Do not overwrite `.governed` capability memory except through append-only governed flows.
- Do not remove project-local candidates or reports unless explicitly requested.
- Do not promote environment-local assistant runtime facts into durable project knowledge.
- Do not configure remotes, cron changes, or release tags unless explicitly requested.

## Expected Result

- Target project remains valid.
- Local Codex skills are refreshed from repo contracts.
- The packaged scheduler is refreshed in `<codex-home>/bin/`.
- Any memory-review output is auditable through reports and patches.
