# Spec Brief — Codex Skill Governed Conversion

Last updated: 2026-05-01

## Objective
Add a preview-first workflow for converting one existing local Codex skill into a GovKB governed capability package.

This feature depends on `governed-skill-quality-gates`. Conversion must target the strict governed-skill package shape and must not write unsafe content into repo-governed memory.

## Source Artifacts
- `business.md`
- `business-context.md`
- `context.md`

## Problem Statement
Useful Codex skills already exist outside GovKB. Some contain durable project knowledge, prompts, scripts, or memory that should become repo-owned and reviewable. Today there is no guided path to convert one of those skills into `.governed/` without manually copying files and risking unsafe or local-only content.

## Business Value Snapshot
- preview what would be created before any write
- see what content is copied, transformed, rejected, or left adapter-local
- approve a target capability id and scope
- keep source local skills unchanged
- write a strict-valid governed package when the conversion is acceptable
- materialize the converted package back to Codex through normal GovKB apply

## Scope Snapshot
- convert one local Codex skill at a time
- source can be a skill directory path or a skill name resolved from a Codex home
- preview mode is the default safe path
- write mode creates a new governed capability package only
- conversion classifies source content before writing
- safe helper scripts and fixtures may be copied into standard governed locations
- source local skill is never mutated

## Acceptance Snapshot
- Maintainer can preview conversion for one local Codex skill without writing files.
- Preview clearly shows target package, copied content, rejected content, manual-review content, and validation status.
- Write mode creates a new governed capability package when preview is acceptable.
- Write mode fails if the target package already exists.
- Source local skill remains unchanged.
- Safe long-term memory, prompts, and helper scripts can be preserved in governed locations.
- Unsafe content is rejected and not copied into repo-governed memory.
- Converted package passes strict validation before write succeeds.

## Review Readiness
- Open questions captured: 0
- Feedback source documents found: 0
- Tracker/reference status: not configured
- Pending feedback reconciliation: No
