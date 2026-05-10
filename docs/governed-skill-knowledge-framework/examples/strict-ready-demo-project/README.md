# Strict Ready Demo Project

This project is a sanitized customer-demo fixture for GovKB strict validation and Codex materialization.

Use it to show the happy path:

```bash
govkb validate --strict docs/governed-skill-knowledge-framework/examples/strict-ready-demo-project
govkb apply codex --project-root docs/governed-skill-knowledge-framework/examples/strict-ready-demo-project --codex-home /tmp/govkb-demo-codex-home
govkb status docs/governed-skill-knowledge-framework/examples/strict-ready-demo-project --codex-home /tmp/govkb-demo-codex-home --json
```

