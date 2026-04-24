# GovKB KB Quality Test Plan

Last updated: 2026-04-24

## Goal

Prove GovKB can create and maintain richer governed capability KB, not only scaffold text and short lesson bullets, while keeping transcript-like session content out of repo-governed source.

Also prove the capture model is transferable:

- not coding-only
- not English-only
- not dependent on per-project hint expansion

Test assumption for this slice:

- use a clean-start governed test setup
- do not require compatibility with older GovKB-generated candidate artifact formats

## Test Areas

1. bootstrap quality
2. candidate capture quality before promotion
3. candidate activation quality
4. thin-KB health reporting
5. AI-first semantic session classification
6. AIApps real-life memory quality
7. multilingual semantic capture
8. non-coding semantic capture
9. redistribution of richer KB to second local setup

## 1. Automated Tests

### CLI and bootstrap

Add tests for:

- `govkb init-kb --capability <id>` updates one capability
- `govkb init-kb --all` updates all eligible capabilities
- bootstrap output lists evidence files and validation result
- dry run leaves files unchanged if dry-run support is added

### Candidate activation

Add tests for:

- repeated unmatched sessions create candidate knowledge before activation or promotion
- first unmatched durable session creates `collecting`; second confirming session creates `ready-for-review`
- candidate repo artifacts contain no user/assistant transcript excerpts
- source session ids and timestamps are preserved without transcript content
- candidate facts are stored in structured form, not only markdown summary
- `create capability --from-candidate` creates scaffold plus initial KB
- `--no-init-kb` skips bootstrap explicitly
- thin evidence keeps capability minimal but valid
- candidate ids come from semantic topic synthesis, not raw imperative prompt wording

### Session classification and routing

Add tests for:

- meaningful verified implementation session reaches classification without matching an English hint phrase
- mixed-language session can reach classification when the outcome is durable
- non-coding session with durable outcome can reach classification without code changes
- self-referential GovKB maintenance session is still rejected deterministically
- routing hints act as optional accelerators and are not required for durable capture

### Validation and status

Add tests for:

- contract bootstrap metadata is required or validated as designed
- thin-KB checks use contract-driven expectations rather than project-specific hardcoding
- scaffold-only memory triggers thin-KB warning
- capability with durable entries does not warn
- workflow capability with no verification command warns

### Governance

Add tests for:

- bootstrap rejects secrets
- candidate staging rejects transcript-like repo persistence
- bootstrap rejects absolute local paths
- bootstrap rejects assistant-runtime artifacts
- explicit-acceptance capability rules are unchanged

### Multilingual and non-coding fixtures

Add tests for at least:

- Russian or mixed-language review or delivery outcome
- documentation or spec session with durable reusable commands or authority rules
- QA or deployment session with stable validation workflow facts

## 2. Manual AIApps Test

### Step 1. Baseline

Run:

```bash
python3 -m govkb.cli status /home/ev/code/AIApps --codex-home /home/ev/.codex
python3 -m govkb.cli candidates list /home/ev/code/AIApps
```

Record:

- current active capabilities
- current thin KB observations
- current promoted memory

Reset rule:

- if older candidate artifacts from prior testing exist, discard and regenerate them for this slice
- also clear prior AIApps local materialization, install-state, and project-scoped memory-review state before the fresh run

### Step 2. Candidate capture boundary

Use repeated unmatched AIApps work to create or refresh a candidate.

Pass if:

- candidate knowledge appears immediately in repo-governed candidate artifacts
- first unmatched durable session produces `collecting`
- second confirming session moves the same candidate to `ready-for-review`
- the repo candidate artifact stores distilled reusable facts, not transcript-like excerpts
- source session provenance is limited to ids, timestamps, and summary-level rationale
- candidate facts are stored in structured form suitable for later grouping or merge
- durable sessions do not require English hint phrasing to be classified

### Step 3. Bootstrap existing AIApps capabilities

Run:

```bash
python3 -m govkb.cli init-kb /home/ev/code/AIApps --capability project-knowledge-steward
python3 -m govkb.cli init-kb /home/ev/code/AIApps --capability backend-local-stack-workflow
python3 -m govkb.cli init-kb /home/ev/code/AIApps --capability auth-e2e-workflow
```

Pass if:

- memory now contains repo-relative facts
- at least one capability records code/docs/scripts/verification knowledge
- validation passes after each run
- bootstrap file selection follows governed contract metadata

### Step 4. Story workflow quality check

Use a real AIApps story task.

Pass if governed memory can capture facts such as:

- where story backend code lives
- where unit tests live
- where relevant docs/config live
- what the narrow verification command is

Fail if memory only stores generic guidance like “validate input” without repo grounding.

### Step 4b. Mixed-language check

Run one real AIApps session in Russian or mixed English/Russian.

Pass if:

- the session is classified when the outcome is durable
- resulting memory or candidate artifacts remain structured and repo-relative
- no new hardcoded language-specific hint rule is needed

### Step 5. Candidate activation quality

Create or reactivate a candidate-backed capability.

Pass if:

- created capability is not left scaffold-thin
- initial memory uses candidate knowledge plus repo inspection
- no local-only paths or one-off task notes are stored

### Step 6. Thin-KB reporting

Run:

```bash
python3 -m govkb.cli validate /home/ev/code/AIApps
python3 -m govkb.cli status /home/ev/code/AIApps --codex-home /home/ev/.codex
```

Pass if:

- thin capabilities are warned clearly
- non-thin capabilities are clean
- output points to `govkb init-kb`
- warning behavior follows contract-driven expectations

## 3. Non-Coding Scenario Test

Use one real or fixture-based session that is not a coding task, for example:

- review findings
- spec/docs update
- QA runbook capture
- delivery/deploy validation

Pass if:

- the session reaches classification through semantic evidence, not code-change detection
- durable facts land in steward or candidate artifacts correctly
- candidate naming reflects topic meaning rather than raw prompt wording
- governance filters still block transcript-like or runtime-local noise

## 4. Redistribution Test

Use a second clean Codex home.

Run:

```bash
python3 -m govkb.cli apply codex --project-root /home/ev/code/AIApps --codex-home <second-codex-home>
```

Pass if:

- second home receives the same `govkb-aiapps-*` skills
- richer memory is present in materialized outputs
- install state is separate from the first home
- candidate artifacts in repo remain distilled and transcript-free

## 5. Follow-Up Reuse Test

Run one real AIApps task from the second Codex home.

Pass if:

- the assistant reuses the governed repo facts without rediscovering them
- task setup is faster and more accurate
- relevant code/docs/scripts are named correctly from existing governed memory

## 6. Exit Criteria

This test plan passes only if all are true:

- candidate knowledge is captured before promotion
- repo candidate artifacts contain no transcript-like excerpts
- first unmatched durable session creates collecting state and second confirming session creates ready-for-review state
- durable capture does not depend on English hint phrases
- automated tests cover bootstrap, activation, thin-KB warnings, governance, multilingual capture, and non-coding capture
- AIApps capability KB is materially richer after bootstrap
- at least one specialized capability contains stable repo-map knowledge
- at least one mixed-language or non-coding scenario classifies correctly without custom hint additions
- second-home apply carries the richer KB
- follow-up work in the second setup shows practical reuse
