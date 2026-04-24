# GovKB MVP+ Test Plan

Last updated: 2026-04-24

## Goal

Prove GovKB works as a standalone reusable product in fresh projects:

- semantic classification works through the Codex adapter
- candidate naming and facts come from durable task meaning, repo artifacts, and commands
- multilingual and non-coding sessions produce governed output
- learned knowledge can be redistributed into a second local setup
- scheduler reports distinguish product success from classifier environment blockers

## Quota-Safe Classifier Settings

Real validation runs should use the smallest acceptable nested classifier model and low reasoning unless the test case explicitly needs more.

Default real-test flags:

```bash
--classifier-codex-home ~/.codex --codex-model gpt-5.4-mini --codex-reasoning low --codex-timeout 180
```

Equivalent environment defaults for direct scheduler runs:

```bash
export GOVKB_CODEX_MODEL=gpt-5.4-mini
export GOVKB_CODEX_REASONING=low
export GOVKB_CLASSIFIER_CODEX_HOME="$HOME/.codex"
```

Rules:

- Use `gpt-5.4-mini` with `low` reasoning for routine smoke, fresh-project, and regression validations.
- Keep validation output isolated with disposable `CODEX_HOME`, but use `--classifier-codex-home ~/.codex` so nested `codex exec` has the same auth/config as a normal WSL terminal.
- Increase model or reasoning only for a named diagnostic rerun after a mini/low failure is inspected.
- Treat quota, timeout, auth, or transient transport failures as environment blockers, not product success.
- Treat shell-level DNS or websocket `Operation not permitted` failures as execution-environment blockers even when the interactive Codex app session itself works.
- Keep `--max-sessions 1` for first-pass real checks; scale only after the report is clean.

## Test Matrix

| Area | Required Evidence | Pass Criteria |
|------|-------------------|---------------|
| Fresh install | Disposable project and isolated `CODEX_HOME` | `.governed` exists, install-state exists, Codex skills are materialized |
| Semantic classifier | `review-memory` with mini/low settings | At least one durable session reaches classification or is explicitly deferred as an environment blocker |
| Candidate quality | Repeated unmatched work | Same candidate reaches `ready-for-review`; name is semantic, not copied from prompt wording |
| Fact quality | Candidate and capability facts | Facts include repo-relative paths and reusable commands; no raw transcript excerpts |
| Multilingual | Russian or mixed English/Russian session | Durable output is classified or staged without adding language-specific hint rules |
| Non-coding | Docs, QA, release, delivery, or spec workflow | Governed output is not dependent on code diffs |
| Redistribution | Second clean `CODEX_HOME` | `govkb apply codex` materializes learned governed memory into the second setup |
| Reports | Scheduler report under project-scoped memory-review dir | Report records model, reasoning, timeout, deferred sessions, failed sessions, and candidate activity |

## Disposable Fresh-Project Runbook

1. Create a temp project and temp Codex home.

```bash
tmp_root="$(mktemp -d /tmp/govkb-mvp-plus.XXXXXX)"
project_root="$tmp_root/FreshPolicy"
codex_home="$tmp_root/codex-home"
mkdir -p "$project_root" "$codex_home"
```

2. Add minimal real project files.

Required shape:

- `README.md`
- one source or policy file
- one test file or verification script
- one non-coding artifact, for example `docs/release/signoff.md`

3. Install GovKB into the project.

```bash
PYTHONPATH=src python3 -m govkb.cli install "$project_root" \
  --project-id fresh-policy \
  --project-name FreshPolicy \
  --codex-home "$codex_home" \
  --revision mvp-plus-test
```

4. Bootstrap starter KB.

```bash
PYTHONPATH=src python3 -m govkb.cli init-kb "$project_root" \
  --all \
  --codex-home "$codex_home"
```

5. Run a quota-safe dry-run classification against one explicit session.

```bash
CODEX_HOME="$codex_home" PYTHONPATH=src python3 -m govkb.cli review-memory \
  --assistant codex \
  --project-root "$project_root" \
  --dry-run \
  --session-file "$tmp_root/sessions/session-one.jsonl" \
  --max-sessions 1 \
  --classifier-codex-home ~/.codex \
  --codex-model gpt-5.4-mini \
  --codex-reasoning low \
  --codex-timeout 180
```

Pass if:

- report is written under `$codex_home/memories/govkb/projects/fresh-policy/codex-memory-review/reports/`
- report shows classifier model `gpt-5.4-mini`, reasoning `low`, and timeout `180`
- failed sessions are zero
- deferred sessions are zero, unless the report clearly names quota/connectivity/timeout as an environment blocker

6. Stage repeated unmatched work.

```bash
PYTHONPATH=src python3 -m govkb.cli candidates stage \
  --project-root "$project_root" \
  --assistant codex \
  --session-file "$tmp_root/sessions/session-one.jsonl"

PYTHONPATH=src python3 -m govkb.cli candidates stage \
  --project-root "$project_root" \
  --assistant codex \
  --session-file "$tmp_root/sessions/session-two.jsonl"
```

Pass if:

- one semantic candidate is updated twice rather than split into prompt-wording variants
- `candidate.toml` reaches `status = "ready-for-review"` and `occurrences = 2`
- `candidate-facts.toml` includes repo-relative paths and commands
- no raw user or assistant transcript text is stored

7. Activate and materialize the ready candidate.

```bash
PYTHONPATH=src python3 -m govkb.cli candidates auto-create-ready \
  --project-root "$project_root" \
  --assistant codex \
  --codex-home "$codex_home"
```

Pass if:

- a governed capability is created under `.governed/capabilities/`
- the capability has non-empty initial memory grounded in candidate facts
- a corresponding `govkb-<project-id>-<capability-id>` Codex skill is materialized

8. Validate package quality.

```bash
PYTHONPATH=src python3 -m govkb.cli validate "$project_root"
PYTHONPATH=src python3 -m govkb.cli status "$project_root" --codex-home "$codex_home"
```

Pass if:

- validation exits zero
- status lists expected capabilities and materialized skills
- any KB-health warnings are specific and actionable

9. Prove redistribution into a second clean local setup.

```bash
second_home="$tmp_root/second-codex-home"
PYTHONPATH=src python3 -m govkb.cli apply codex \
  --project-root "$project_root" \
  --codex-home "$second_home" \
  --revision mvp-plus-redistribution
```

Pass if:

- second home gets the same governed skills
- materialized memory contains distilled governed facts from the first setup
- no raw session content is present

## AIApps Real-Project Runbook

Use the same quota-safe classifier flags for AIApps:

```bash
PYTHONPATH=src python3 -m govkb.cli review-memory \
  --assistant codex \
  --project-root /home/ev/code/AIApps \
  --dry-run \
  --lookback-days 2 \
  --max-sessions 1 \
  --classifier-codex-home ~/.codex \
  --codex-model gpt-5.4-mini \
  --codex-reasoning low \
  --codex-timeout 180
```

Required real session set:

- one backend or local-stack session
- one frontend, test, or e2e session
- one repeated workflow session for candidate convergence
- one docs/spec/QA/release session
- one Russian or mixed-language durable session

Pass if:

- selected sessions are AIApps only
- at least one durable session classifies without an English hint phrase
- at least one non-coding or mixed-language session produces governed output or a clean candidate
- learned output can be applied into a second clean Codex home

## Failure Handling

Do not mark MVP+ validation as passed when:

- nested Codex times out before producing classifier output
- quota or auth prevents classification
- shell-launched `codex exec` cannot resolve or connect to OpenAI from the current execution sandbox
- the report has failed sessions
- candidates store transcript-like content
- repeated work splits into multiple weakly named candidates
- second-home apply does not reproduce learned governed memory

If mini/low classification fails but the environment is healthy:

1. inspect the sanitized classifier input only in the local report/log area
2. rerun the same session once with the same mini/low settings
3. only then run a diagnostic pass with a stronger model or higher reasoning
4. record the reason stronger settings were required

## Result Record Template

```text
Date:
Project:
Codex home:
GovKB commit:
Classifier model:
Classifier reasoning:
Classifier timeout:
Sessions tested:
Report path:
Validation commands:
Created/updated capabilities:
Created/updated candidates:
KB quality notes:
Environment blockers:
MVP+ result:
Exact next fix:
```
