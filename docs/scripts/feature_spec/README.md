# GovKB Feature Spec Scripts

Repo-local helpers for `docs/FEATURE_SPEC_COOKBOOK/`.

## Main Workflow

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/scripts/feature_spec/run_feature_spec_workflow.py <FeatureSlug> --json
```

`<FeatureSlug>` resolves under `docs/governed-skill-knowledge-framework/features/`. You can also pass an absolute feature folder path.

The workflow refreshes local spec artifacts when its child scripts run with `--write`; review generated diffs before committing.

## Optional Tracker/Reference

GovKB does not require an external tracker. To record one in local artifacts:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/scripts/feature_spec/reconcile_feature_tracking.py <FeatureSlug> \
  --tracker-label "Reference" \
  --tracker-id "<ID>" \
  --tracker-url "<URL>" \
  --write-artifacts \
  --json
```

Use `--require-tracker` only when a feature must not proceed without a reference.
