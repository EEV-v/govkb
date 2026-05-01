# Governed Skill Quality Gates - Open Questions

| ID | Question | Status | Owner | Notes |
|---|---|---|---|---|
| Q1 | When should strict validation become the default for normal `govkb validate`? | Deferred | Product/Engineering | First slice keeps normal validation backward-compatible. |
| Q2 | Should approval be represented as candidate metadata, capability metadata, or both? | Blocking | Engineering | Business requires explicit approval before activation; implementation representation is still open. |
| Q3 | Should deprecated capabilities be hidden from routing immediately or only prevented from receiving new learning? | Deferred | Product | Not needed for first strict validation gate. |
| Q4 | Which exact path patterns count as local credential-file references? | Blocking | Security/Governance | Needed for deterministic strict validation. |
