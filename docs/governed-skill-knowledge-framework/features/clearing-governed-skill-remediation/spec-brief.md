# Spec Brief — Clearing Governed Skill Remediation

Last updated: 2026-05-01

## Objective
Use GovKB governed skill quality gates to repair the current Clearing governed package state.

This is an operational follow-up, not the first GovKB product implementation slice. It depends on `governed-skill-quality-gates`.

## Source Artifacts
- `business.md`
- `business-context.md`
- `context.md`

## Problem Statement
The Clearing project currently has a governed package that validates syntactically but contains a weak active capability shape. The current `local-stack-workflow` capability was activated from Corporate Actions-related evidence, contains generic memory, and includes command paths that do not match the Clearing workspace root.

This undermines confidence that GovKB has learned the right reusable project behavior.

## Business Value Snapshot
- identify weak active capabilities
- decide whether to demote, replace, rename, or deprecate them
- repair invalid memory commands and paths
- disable unsafe auto-activation while reviewing candidates
- keep existing useful Clearing project memory

## Scope Snapshot
- run strict validation against `/home/ev/code/Clearing`
- review `local-stack-workflow`
- decide whether to replace it with a domain-specific capability
- fix invalid repo-relative commands and paths
- disable or constrain candidate auto-create if needed
- preserve durable project-knowledge-steward memory that is still valid

## Acceptance Snapshot
- Strict validation identifies the current weak Clearing governed package issues.
- Maintainer has a reviewed remediation plan before files are changed.
- Weak generic active capability is either repaired, renamed/replaced, deprecated, or demoted.
- Invalid commands and repo paths are corrected or removed.
- Candidate auto-create no longer silently activates weak Clearing capabilities.
- Useful durable Clearing memory remains available after remediation.
- Final Clearing package validates under strict mode or has an explicit documented exception list.

## Review Readiness
- Open questions captured: 0
- Feedback source documents found: 0
- Tracker/reference status: not configured
- Pending feedback reconciliation: No
