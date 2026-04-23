# GovKB Install Prompt

Use this prompt when installing GovKB into a project for the first time.

## Goal

Install or refresh GovKB from this repo into the target project, materialize assistant capabilities, and optionally install the project-scoped memory-review schedule.

## Inputs

- GovKB repo: `<govkb-repo>`
- Target project: `<project-root>`
- Codex home: `<codex-home>` or default `$HOME/.codex`
- Project id: optional, stable lowercase id
- Project name: optional human name
- Cron schedule: optional, default `15 8 * * *`

## Procedure

1. Confirm the target project path and whether `.governed/` already exists.
2. Run GovKB tests from the GovKB repo:

```bash
python3 -m unittest discover -s tests -v
```

3. Preview install:

```bash
python3 -m govkb.cli install <project-root> --codex-home <codex-home> --preview
```

4. Apply install:

```bash
python3 -m govkb.cli install <project-root> --codex-home <codex-home> --revision <revision>
```

5. If a scheduled review job is wanted, apply with cron:

```bash
python3 -m govkb.cli install <project-root> --codex-home <codex-home> --revision <revision> --cron --schedule "15 8 * * *"
```

6. Verify status:

```bash
python3 -m govkb.cli status <project-root> --codex-home <codex-home>
```

## Safety Rules

- Do not read or commit secrets, `.env` files, local credentials, or assistant session transcripts.
- Do not add a Git remote unless the user explicitly asks for it.
- Keep project-local knowledge under `<project-root>/.governed`.
- Treat staged memory-review items as review material unless the policy explicitly auto-promotes them.

## Expected Result

- `<project-root>/.governed/` exists and validates.
- Codex skills are materialized under `<codex-home>/skills/`.
- The packaged `codex-memory-review` task is installed under `<codex-home>/bin/`.
- Install state exists under `<codex-home>/memories/govkb/install-state/`.
- If cron was requested, the project-scoped scheduled job is present.
