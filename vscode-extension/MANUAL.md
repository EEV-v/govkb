# GovKB VS Code Extension Manual

## Install Or Reinstall In WSL

From `/home/ev/code/govkb`:

```bash
code --remote wsl+Ubuntu-24.04 --install-extension /home/ev/code/govkb/vscode-extension/govkb-0.0.1.vsix --force
code --remote wsl+Ubuntu-24.04 --list-extensions --show-versions | rg -i 'govkb|govkb-local'
```

Expected installed id:

```text
govkb-local.govkb@0.0.1
```

## Shortest Successful Path

After installing the VSIX:

1. Open a WSL folder in VS Code.
2. Trust the workspace when VS Code asks.
3. Open the `GovKB` activity bar view.
4. Click `Show Status` in the Status view.
5. If status says the project is not initialized, click `One-Click Setup`.
6. Click `One-Click Apply` after setup succeeds.
7. Use `List Candidates` and `Refresh Reports` when you want candidate or report summaries.

Setup, apply, validation, candidate refresh, status refresh, and memory review show VS Code progress notifications. If one is already running, duplicate clicks are ignored and the GovKB output channel has the details. Memory review streams CLI/session progress into that channel while it runs.

## Runtime Setup For This Source Checkout

This WSL environment does not currently have `pip`, so the repo provides a local launcher:

```bash
/home/ev/code/govkb/scripts/govkb-dev --help
```

It is installed on PATH as:

```bash
/home/ev/.local/bin/govkb -> /home/ev/code/govkb/scripts/govkb-dev
```

The extension's default `GovKB: Command` value is `govkb`, so this launcher lets the extension find the GovKB runtime.

## First Use

1. Open a WSL folder in VS Code, for example `/home/ev/code/govkb` or another project that should use GovKB.
2. Trust the workspace when VS Code asks. Setup, apply, and memory-review commands require Workspace Trust.
3. Open the `GovKB` activity bar view and run `GovKB: Show Status` from the view title or command palette.
4. Keep the default `GovKB: Command` as `govkb` if it is available on PATH, or set:
   - `GovKB: Command` to `python-module`
   - `GovKB: Python Path` to `python3`
   - make sure that Python can import GovKB, for example by installing this repo in editable mode in the environment used by VS Code
5. Optionally set `GovKB: Codex Home` to a disposable path while testing, for example `/tmp/govkb-codex-home`. This setting is used for setup, apply, status, reports, and memory review.

If `pip` is later installed, this is the usual package-style runtime setup:

```bash
cd /home/ev/code/govkb
python3 -m pip install -e .
```

## Commands

Open the command palette with `Ctrl+Shift+P`, then run:

| Command | What It Does |
|---|---|
| `GovKB: One-Click Setup Current Project` | Checks GovKB runtime, runs `govkb install`, runs `govkb init-kb --all`, validates, and refreshes status. |
| `GovKB: One-Click Apply Current Project` | Runs `govkb apply codex --project-root <workspace>` and refreshes status. Requires a `.governed/` package; run setup first on a new project. |
| `GovKB: Validate Project` | Runs `govkb validate <workspace>`. |
| `GovKB: Show Status` | Runs `govkb status <workspace> --json` and updates status/capability views. |
| `GovKB: Review Memory Dry Run` | Runs memory review in dry-run mode with a one-session default cap. Classifier model, reasoning, and timeout use GovKB CLI defaults unless explicitly configured in extension settings. |
| `GovKB: Review Memory Apply` | Runs memory review in apply mode, updating eligible memory, staging candidates, refreshing reports/candidates, and streaming progress to the GovKB output channel. |
| `GovKB: List Candidates` | Runs `govkb candidates list <workspace> --json` and updates the candidates view. |
| `GovKB: Refresh Reports` | Reads aggregate memory-review report summaries from the configured Codex home. |
| `GovKB: Open Latest Report` | Opens the newest local report file for inspection. |
| `GovKB: Open Output` | Opens the `GovKB` output channel. |

## Views

Open the `GovKB` activity bar view:

- `Status`: project id, validation status, KB health, adapter state, Codex install state, and setup/apply/status shortcuts.
- `Capabilities`: governed capabilities from status JSON, with refresh/apply actions in the view title.
- `Candidates`: staged candidate summaries from `govkb candidates list --json`, including status, occurrences, and activation state.
- `Reports`: aggregate report summaries from project-scoped memory-review reports. Tree rows open local report files, but raw transcript content is not copied into extension state.

## Safe Test Flow

Use a disposable project first:

```bash
tmp="$(mktemp -d /tmp/govkb-vscode-manual.XXXXXX)"
PYTHONPATH=/home/ev/code/govkb/src python3 -m govkb.cli init --dest "$tmp/DemoProject" --project-id demo-project --project-name "Demo Project"
code --remote wsl+Ubuntu-24.04 "$tmp/DemoProject"
```

In VS Code:

1. Trust the workspace.
2. Run `GovKB: Show Status`.
3. Run `GovKB: One-Click Setup Current Project` if status says the project is not initialized.
4. Run `GovKB: One-Click Apply Current Project` with a disposable `GovKB: Codex Home` if you do not want to touch the real Codex home.
5. Run `GovKB: List Candidates` and `GovKB: Refresh Reports`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `GovKB runtime is not available` | Install GovKB on PATH, or set `GovKB: Command` to `python-module` and `GovKB: Python Path` to `python3`. |
| Runtime still unavailable after installing the launcher | Reload the VS Code window and confirm `GovKB: Command` is `govkb` or `/home/ev/.local/bin/govkb`. |
| Commands are blocked | Trust the workspace. |
| `GovKB apply failed` or `missing governed root` | Run `GovKB: One-Click Setup Current Project` first, or run `govkb install <workspace>` from the terminal. |
| A command appears to do nothing after a second click | The first run is still active; open the `GovKB` output channel to follow progress. |
| Multi-root workspace prompts for a project | Pick the one project root that owns `.governed/`. |
| Status view does not update | Run `GovKB: Show Status`; check the `GovKB` output channel. |
| Reports view is empty | Set `GovKB: Codex Home` if needed, run `GovKB: Review Memory Dry Run` or `GovKB: Review Memory Apply`, then run `GovKB: Refresh Reports`. |
| Memory review times out | Open the `GovKB` output channel or latest report. Timeout rows include the session id, session file, classifier workdir, classifier Codex home, model, reasoning, and any partial classifier output. Increase `GovKB: Review Timeout Seconds` if the selected session is legitimately large. |
| Apply or memory review uses the wrong Codex home | Set `GovKB: Codex Home` explicitly before running the command. |

## Current Limitations

- Local VSIX proof only; Marketplace publishing is not ready.
- WSL/Linux-first behavior only.
- No telemetry.
- Final publisher, repository metadata, branding, and public license are deferred.
