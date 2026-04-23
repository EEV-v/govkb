# govkb

Repo-native governed knowledge tooling for project AI collaboration.

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
