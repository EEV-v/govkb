# Clearing Governed Skill Remediation

## Summary

Use GovKB governed skill quality gates to repair the current Clearing governed package state.

This is an operational follow-up, not the first GovKB product implementation slice. It depends on `governed-skill-quality-gates`.

## Business Problem

The Clearing project currently has a governed package that validates syntactically but contains a weak active capability shape. The current `local-stack-workflow` capability was activated from Corporate Actions-related evidence, contains generic memory, and includes command paths that do not match the Clearing workspace root.

This undermines confidence that GovKB has learned the right reusable project behavior.

## Product Goal

Make the Clearing governed package trustworthy again by using strict validation output to guide cleanup.

Maintainers should be able to:

- identify weak active capabilities
- decide whether to demote, replace, rename, or deprecate them
- repair invalid memory commands and paths
- disable unsafe auto-activation while reviewing candidates
- keep existing useful Clearing project memory

## Dependencies

This work should happen after `governed-skill-quality-gates` can flag the weak package shape.

Engineering may plan this remediation before quality gates are implemented, but remediation writes must not happen until strict validation can produce actionable evidence for the Clearing package.

## Scope

In scope:

- run strict validation against `/home/ev/code/Clearing`
- review `local-stack-workflow`
- decide whether to replace it with a domain-specific capability
- fix invalid repo-relative commands and paths
- disable or constrain candidate auto-create if needed
- preserve durable project-knowledge-steward memory that is still valid

Out of scope:

- changing Clearing production code
- querying production systems
- migrating every existing Clearing local skill
- creating new GovKB product behavior beyond what quality gates provide

## Remediation Options

The maintainer should choose one path after strict validation:

| Option | Use When | Outcome |
|---|---|---|
| Repair in place | Capability id and scope are acceptable after review | Clean memory, paths, commands, and tool metadata |
| Rename or replace | Capability was activated under the wrong domain | Create a domain-specific capability and deactivate the weak one |
| Deprecate | Existing materialized users need compatibility but routing should stop | Keep package for history but remove active use |
| Demote to candidate | Evidence is not sufficient for active capability | Move back to reviewable candidate state |

## First Remediation Policy

The first engineering pass should use this safe default:

1. Run strict validation and produce a remediation report.
2. Disable or constrain Clearing candidate auto-create until strict gates are enforced.
3. Do not mutate Clearing production code.
4. Do not mutate Clearing governed package state until a maintainer approves the remediation option.
5. If `local-stack-workflow` is confirmed to be weak or wrong-domain, prefer demotion or deprecation over in-place repair.
6. Preserve useful project-knowledge-steward memory unless strict validation identifies a concrete safety issue.

Long-term `.governed` ownership should be the Git repository that owns Clearing project governance. If the working directory under review is not itself a Git repository, engineering must stop at a remediation report and identify the owning repository before writing durable governed package changes.

## Acceptance Criteria

1. Strict validation identifies the current weak Clearing governed package issues.
2. Maintainer has a reviewed remediation plan before files are changed.
3. Weak generic active capability is either repaired, renamed/replaced, deprecated, or demoted.
4. Invalid commands and repo paths are corrected or removed.
5. Candidate auto-create no longer silently activates weak Clearing capabilities.
6. Useful durable Clearing memory remains available after remediation.
7. Final Clearing package validates under strict mode or has an explicit documented exception list.
