# GovKB Feature Spec Knowledge Base

Cross-feature reusable learning for GovKB business-spec convergence.

## Common Review Patterns

- Ask for first-slice scope and deferred public-launch scope separately when the feature mixes internal proof and public distribution.
- Keep product decisions, engineering implementation choices, and public branding decisions in separate rows when they have different owners.
- If the feature changes local execution or assistant-local state, ask about trust, source of truth, and mutation boundaries in the same round.
- If an extension or UI wraps CLI behavior, explicitly decide whether the CLI needs machine-readable output before implementation planning.

## Recurring Open-question Categories

- first supported platform
- runtime provisioning mechanism
- source of truth versus derived local output
- mutation boundaries
- Workspace Trust or local execution authorization
- telemetry/privacy posture
- public packaging and branding
- multi-root or multi-project behavior
- JSON or structured output needed for UI surfaces

## Stable Owners By Domain

- Product/Governance: public behavior, telemetry, publish readiness, mutation risk.
- Engineering: CLI contracts, package layout, parser/output shape, tests.
- Security/Privacy: local execution, secrets, transcript handling, telemetry.

## Standard Decision Heuristics

- Prefer a small named first slice over trying to lock a full public-release scope at once.
- Treat no telemetry as the default until an explicit privacy decision exists.
- Treat assistant-local files as derived outputs unless the product spec explicitly changes source-of-truth ownership.
- Prefer CLI-owned mutations over UI-owned filesystem writes.
- Prefer structured CLI output over parsing human-formatted text in a UI.

## Common Acceptance-criteria Templates

- A trusted workspace can run the workflow through the UI and see a clear status outcome.
- An untrusted workspace blocks local execution before invoking commands.
- The UI calls the core CLI with argument arrays rather than shell strings.
- Raw transcript content is not copied into repo artifacts or extension state.
- Local packaging excludes private paths, generated reports, and user assistant state.

## Recurring Scope Traps

- Public Marketplace readiness can block public release without blocking a local VSIX proof.
- Runtime bundling/download decisions can overcomplicate a first slice; guided setup may be enough for proof.
- Multi-root support can hide project selection ambiguity if not treated explicitly.
- Memory-review dry-run and memory-review mutation are separate governance surfaces.
- Extension views need stable machine-readable data; human CLI output is not a durable UI contract.

## Learned Patterns

- After manual curation, treat builder reruns as destructive until diffed; do not blindly accept boilerplate regressions.
- Derived outbound artifacts should normalize internal draft suffixes unless the business explicitly wants the internal label carried through.
- Tracker matching or external-public readiness should not block local engineering unless the locked slice depends on it.

## Examples of good review-pack wording
- Review packs work better when they ask business to approve scope, answer blockers, and mark deferred items explicitly.
