# Changelog

## 0.0.5

- Added read-only GovKB Doctor health refresh in Home and Status.
- Added staged proposal queue visibility backed by `govkb proposals review --json`.
- Surfaced cron, latest memory-review report, and proposal warning counts in the VS Code workflow.

## 0.0.4

- Ran memory-review Python adapters with the active GovKB interpreter instead of the system `python3` shebang.
- Added a bounded 180 second default classifier timeout for extension-triggered memory review.

## 0.0.3

- Resolved default GovKB runtime discovery for GUI-launched VS Code sessions with incomplete PATH.
- Updated the local repo launcher to require and select Python 3.11 or newer.

## 0.0.2

- Added Promotions view and promotion lifecycle commands.
- Added remembered-project startup refresh and optional read-only monitoring.
- Added Skill updates status row for applied Codex skill freshness and pending learned local memory.
- Added extension-host smoke test entry point.

## 0.0.1

- Initial local VSIX proof for GovKB setup, apply, status, candidates, and report views.
