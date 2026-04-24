# govkb

Repo-native governed knowledge tooling for project AI collaboration.

## Documentation

- Product and implementation docs live under [docs/governed-skill-knowledge-framework](docs/governed-skill-knowledge-framework).
- The main starting points are:
  - [business.md](docs/governed-skill-knowledge-framework/business.md)
  - [implementation-plan.md](docs/governed-skill-knowledge-framework/implementation-plan.md)
  - [kb-quality-implementation-plan.md](docs/governed-skill-knowledge-framework/kb-quality-implementation-plan.md)
  - [aiapps-real-usage-test-plan.md](docs/governed-skill-knowledge-framework/aiapps-real-usage-test-plan.md)

## Current scope

This initial implementation covers:

- `govkb init` to scaffold a valid project `.governed/` package
- `govkb validate` to load and validate project manifests, capability contracts,
  adapter manifests, and release manifests
- `govkb create capability` to scaffold governed capability source files
- `govkb apply codex` to preview or materialize derived Codex skills
- `govkb install` to scaffold/apply a project and install the packaged Codex memory-review task
- `govkb review-memory --assistant codex` to run the project-scoped memory-review adapter
- local install-state tracking for Codex materialization
- governed learning classification, staging, auto-promotion, and audit reports

## Local development

```bash
cd govkb
python3 -m unittest discover -s tests -v
python3 -m govkb.cli --help
python3 -m govkb.cli apply codex --project-root /path/to/repo --codex-home /tmp/codex-home --preview
```
