# AIApps Real Usage Test Plan

Goal

- prove GovKB works on fresh real project
- prove AIApps stays isolated from Clearing
- prove real work grows project KB
- prove learned stuff is reusable on second setup
- prove capture is AI-first and not dependent on English hint phrasing or coding-only evidence

Success means all 5 are true.

## 0. Cleanup

Before running this slice, reset prior governed AIApps test artifacts.

Cleanup target:

- `/home/ev/code/AIApps/.governed`
- local materialized `govkb-aiapps-*` skills in the active Codex home
- local AIApps install-state under `/home/ev/.codex/memories/govkb/install-state/aiapps--codex.json`
- local AIApps memory-review project state under `/home/ev/.codex/memories/govkb/projects/aiapps/`

Rule:

- do this as a clean-start test reset
- do not add backward-compatibility code for older GovKB-generated AIApps artifacts in this slice
- after cleanup, rerun install and real-session flow from zero

## 1. Install

- run:
  - `python3 -m govkb.cli install /home/ev/code/AIApps --project-id aiapps --project-name AIApps --codex-home /home/ev/.codex --cron`

Pass if:

- `/home/ev/code/AIApps/.governed` exists
- local skills are `govkb-aiapps-*`
- install state is `/home/ev/.codex/memories/govkb/install-state/aiapps--codex.json`
- cron/log path is under `/home/ev/.codex/memories/govkb/projects/aiapps/`

## 2. Isolation

Check:

- Clearing still uses `govkb-clearing-*`
- AIApps reports go only to `.../projects/aiapps/codex-memory-review/`
- no AIApps memory lands in Clearing `.governed`
- no Clearing memory lands in AIApps `.governed`

Pass if same capability ids like `project-knowledge-steward` coexist without overwrite.

## 3. Real sessions

Run 5 real Codex sessions from `/home/ev/code/AIApps`.

Session set:

- backend run/build/test flow
- frontend/dev/e2e flow
- repeat one area again so candidate detector gets second evidence
- one real small task: doc, test, fix, or debug note
- one mixed-language or non-coding session with durable outcome, for example:
  - Russian or mixed English/Russian review or delivery work
  - docs/spec update with durable repo facts
  - QA or deployment validation with stable commands/results

Rule:

- not fake prompts
- real repo work only
- for this slice use clean-start governed candidate artifacts; do not preserve older test candidate formats
- at least one session must rely on semantic evidence rather than English hint phrases or code diffs alone

## 4. Review-memory dry run

- run:
  - `python3 -m govkb.cli review-memory --assistant codex --project-root /home/ev/code/AIApps --dry-run --lookback-days 2 --max-sessions 1 --classifier-codex-home ~/.codex --codex-model gpt-5.4-mini --codex-reasoning low --codex-timeout 180`

Check:

- selected sessions are AIApps only
- report makes sense
- no junk lessons
- no secrets
- no self-referential noise
- at least one durable session reaches classification from semantic evidence rather than hint phrasing alone

## 5. Review-memory apply

- run same without `--dry-run`
- keep the same quota-safe classifier flags unless a documented diagnostic rerun requires a stronger model or higher reasoning

Pass if:

- `project-knowledge-steward` gets durable AIApps memory
- first unmatched durable work creates collecting candidate knowledge in `/home/ev/code/AIApps/.governed/candidates/`
- repeated unmatched work moves the same candidate to `ready-for-review`
- candidate artifact stores distilled reusable knowledge immediately, without raw or sanitized session excerpts
- nothing auto-creates new active capability from one session
- at least one mixed-language or non-coding durable session classifies without adding a new central hint rule

## 6. Reuse proof

- promote/apply learned AIApps package into second clean Codex home

Pass if:

- second setup gets same `govkb-aiapps-*` skills
- same learned memory is present
- follow-up AIApps session uses learned commands/conventions without re-discovery

## 7. Benefit check

Need at least one real win:

- less re-explaining project setup
- correct build/test/dev command reused from memory
- repeated workflow becomes staged capability candidate
- first durable unmatched session saves candidate knowledge; second confirming session is what makes it ready for review
- candidate knowledge is saved before promotion, but promotion is still required to make it active and distributable
- project KB becomes repo asset, not local chat residue
- one session proves semantic capture without depending on English hint phrasing

## MVP confirmation

MVP is confirmed only if all are true:

- one-command install works
- project separation works
- one real expertise update happens
- one real new-capability candidate is staged
- first unmatched durable session creates collecting knowledge and repeat evidence advances it
- candidate stage stores distilled knowledge without transcript-like repo content
- learned result can be reapplied on another local setup
- follow-up session is cheaper/faster because memory was reused
- at least one mixed-language or non-coding durable session classifies without custom hint additions

## Run order

1. install
2. 5 real sessions including one mixed-language or non-coding durable case
3. dry-run review
4. apply review
5. second-home reapply
6. follow-up session comparison
