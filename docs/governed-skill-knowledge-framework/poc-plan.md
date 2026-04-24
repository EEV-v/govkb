# PoC Plan - Governed Skill Knowledge Framework

Last updated: 2026-04-22

## 1. Objective And Hypotheses

Objective: prove before implementation that the current local skill set can be dry-run inventoried and mapped into the repo-first `govkb` migration model.

Hypotheses:
- Existing skills can be classified into `governed capability now`, `legacy keep until migrated`, or `adapter-local only` without mutating local installs.
- First-wave governed candidates are the current memory-bearing project knowledge keepers.
- Approval-gated memory policy can be detected from current skill content and preserved in generated contract candidates.
- The self-improving learning loop is out of this migration-inventory PoC and must be proven during Codex adapter implementation.
- The dry-run output is repeatable enough to use as a migration planning gate.

## 2. Data Scope

| Scope | Value |
|-------|-------|
| Source | `/mnt/c/Users/Ev/.codex/skills` |
| Read mode | local filesystem read-only |
| Included | direct local skills with `SKILL.md` plus `.system/*/SKILL.md` |
| Excluded | Slack plugin cache and other plugin-managed runtime skills |
| Output | feature-local `poc-artifacts/` only |

## 3. Source-Of-Truth Priority

1. Local `SKILL.md` frontmatter for skill id and description.
2. Local `references/*memory*.md` files for first-wave durable memory evidence.
3. Local references/scripts/agents presence for migration risk notes.
4. Generated PoC contract candidates under `poc-artifacts/proposed-contracts/`.

No database or API data is needed for this PoC.

## 4. Assertion Matrix

| Assertion ID | Requirement ID(s) | Assertion Description | Method | Pass Criteria | Artifact |
|--------------|-------------------|-----------------------|--------|---------------|----------|
| A-01 | REQ-TR-14, REQ-TR-16, REQ-AI-10, REQ-AI-12 | Inventory covers every local skill with `SKILL.md` and classifies each exactly once. | Script | Validation status is `passed`; `total_skills` is nonzero; no duplicate or unclassified skills. | `poc-artifacts/summary.json` |
| A-02 | REQ-TR-07, REQ-TR-16, REQ-AI-02 | Every memory-bearing project skill becomes a first-wave governed candidate. | Script | `memory_bearing_skills == generated_contracts == governed capability now count`. | `poc-artifacts/summary.json` |
| A-03 | REQ-TR-16, REQ-AI-12 | System and personal helper skills are not forced into project-governed source. | Script | `.system/*` and `ev-style-writer` classify as `adapter-local only`. | `poc-artifacts/skill-inventory.md` |
| A-04 | REQ-TR-14, REQ-TR-16, REQ-AI-10 | Project-specific skills without first-wave memory evidence remain operationally safe as legacy. | Script | Non-memory Clearing skills classify as `legacy keep until migrated`. | `poc-artifacts/skill-inventory.md` |
| A-05 | REQ-TR-01, REQ-TR-02, REQ-TR-03, REQ-AI-01, REQ-AI-02, REQ-AI-03, REQ-AI-11 | Contract candidates can be generated for first-wave governed skills. | Script | One `capability.contract.toml` candidate exists for each governed-now skill. | `poc-artifacts/proposed-contracts/` |
| A-06 | REQ-TR-09, REQ-AI-06 | Approval-gated capability policy is preserved in generated contract candidates. | Script | `clearing-feature-estimator` contract has `requires_explicit_acceptance = true`. | `poc-artifacts/proposed-contracts/clearing-feature-estimator/capability.contract.toml` |
| A-07 | REQ-TR-10, REQ-TR-12, REQ-AI-08 | Dry run does not mutate source skill installs. | Script inspection + output path check | Script writes only under `poc-artifacts/`; source paths are read-only inputs. | `poc/skill_inventory_dry_run.py` |
| A-08 | REQ-TR-06, REQ-AI-12 | Dry-run evidence is rerunnable with one command. | Shell script | `./regenerate-poc-data.sh` exits 0 and prints generated artifact paths; inventory hash remains stable across reruns. | `regenerate-poc-data.sh`, `poc-artifacts/summary.json` |

## 5. Execution Plan

Working directory:

```bash
cd "/home/ev/code/Clearing/Clearing-docs/docs/features/Governed Skill Knowledge Framework"
```

Run:

```bash
./regenerate-poc-data.sh
```

Optional override:

```bash
SKILLS_ROOT=/path/to/.codex/skills ./regenerate-poc-data.sh
```

## 6. Determinism Controls

- Source tree is passed as an explicit `SKILLS_ROOT`.
- Output is written under `poc-artifacts/`.
- Validation fails on duplicate ids, unclassified skills, unsafe proposed paths, or memory-bearing skills outside the governed track.
- `inventory_sha256` is computed from the classified skill inventory and contract mapping, not from runtime timestamp.

## 7. Known Limitations

- Routing hints are mechanically derived from existing descriptions and need human review before production use.
- Adapter manifests, release manifests, and scheduler integration are not implemented by this PoC.
- Session-to-repo resolution is covered by feature docs, not by this inventory script.
- The PoC includes system skills only to prove they stay adapter-local; they are not migration candidates.

## 8. Data-Evidence Strategy

This is a local filesystem/configuration feature, not a DB-backed data behavior feature. The actual evidence source is the current local skill tree. No PostgreSQL, MongoDB, MSSQL, API, or production data access is required.
