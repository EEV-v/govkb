import * as vscode from "vscode";
import { CommandRunState } from "./commandState";
import { runCliCommand, statusJsonCommand, validateCommand } from "./govkbCli";
import { listCandidates, runMemoryReviewApply, runMemoryReviewDryRun, runOneClickApply, runOneClickSetup } from "./flows";
import { parseStatusPayload } from "./jsonParsers";
import { resolveProjectRoot } from "./projectSelection";
import { codexHomeForReports, discoverReportSummaries, reportRootForProject } from "./reports";
import { resolveSettings } from "./settings";
import { ensureWorkspaceTrusted } from "./trust";
import { Blocker, CliCommand, CliRunner, ReportSummary, StatusPayload } from "./types";
import { SimpleTreeProvider } from "./views/simpleTree";
import { capabilityRows } from "./views/capabilitiesView";
import { candidateRows } from "./views/candidatesView";
import { reportRows } from "./views/reportsView";
import { statusRows } from "./views/statusView";

const OPEN_OUTPUT_ACTION = "Open the GovKB output channel";
const RUN_SETUP_ACTION = "Run GovKB: One-Click Setup Current Project";
const RUN_STATUS_ACTION = "Run GovKB: Show Status";
const RUN_DRY_RUN_ACTION = "Run GovKB: Review Memory Dry Run";
const RUN_APPLY_REVIEW_ACTION = "Run GovKB: Review Memory Apply";
const REFRESH_REPORTS_ACTION = "GovKB: Refresh Reports";

function settingsFromVscode() {
  return resolveSettings(vscode.workspace.getConfiguration("govkb"));
}

async function handleAction(output: vscode.OutputChannel, selected: string | undefined): Promise<void> {
  if (!selected) {
    return;
  }
  if (selected === OPEN_OUTPUT_ACTION) {
    output.show(true);
    return;
  }
  if (selected === RUN_SETUP_ACTION) {
    await vscode.commands.executeCommand("govkb.oneClickSetup");
    return;
  }
  if (selected === RUN_STATUS_ACTION) {
    await vscode.commands.executeCommand("govkb.showStatus");
    return;
  }
  if (selected === RUN_DRY_RUN_ACTION) {
    await vscode.commands.executeCommand("govkb.reviewMemoryDryRun");
    return;
  }
  if (selected === RUN_APPLY_REVIEW_ACTION) {
    await vscode.commands.executeCommand("govkb.reviewMemoryApply");
    return;
  }
  if (selected === REFRESH_REPORTS_ACTION) {
    await vscode.commands.executeCommand("govkb.refreshReports");
    return;
  }
  if (selected.includes("govkb.command") || selected.includes("configure govkb.command")) {
    await vscode.commands.executeCommand("workbench.action.openSettings", "govkb.command");
    return;
  }
  if (selected.startsWith("Trust this workspace")) {
    await vscode.commands.executeCommand("workbench.trust.manage");
  }
}

async function showBlocker(output: vscode.OutputChannel, blocker: Blocker): Promise<void> {
  if (blocker.detail?.trim()) {
    output.appendLine(blocker.detail.trimEnd());
  }
  const actions = [blocker.action, OPEN_OUTPUT_ACTION].filter((action, index, all) => all.indexOf(action) === index);
  const selected = await vscode.window.showWarningMessage(blocker.title, ...actions);
  await handleAction(output, selected);
}

async function selectProjectRoot(output: vscode.OutputChannel): Promise<string | undefined> {
  const result = await resolveProjectRoot(vscode.workspace.workspaceFolders, async (roots) => {
    return vscode.window.showQuickPick(roots, {
      title: "Select GovKB project root"
    });
  });
  if (result.blocker) {
    await showBlocker(output, result.blocker);
    return undefined;
  }
  return result.projectRoot;
}

function createRunner(output: vscode.OutputChannel): CliRunner {
  return {
    async run(command: CliCommand) {
      output.appendLine(`$ ${command.executable} ${command.args.join(" ")}`);
      let lastChunkEndedWithNewline = true;
      const appendChunk = (chunk: string) => {
        output.append(chunk);
        lastChunkEndedWithNewline = chunk.endsWith("\n") || chunk.endsWith("\r");
      };
      const result = await runCliCommand(command, {
        onStdout: appendChunk,
        onStderr: appendChunk
      });
      if (!lastChunkEndedWithNewline) {
        output.appendLine("");
      }
      output.appendLine(`exit ${result.exitCode}`);
      return result;
    }
  };
}

async function requireTrusted(output: vscode.OutputChannel): Promise<boolean> {
  const workspaceTrust = vscode.workspace as unknown as {
    requestWorkspaceTrust?: () => Thenable<boolean | undefined>;
  };
  const trust = await ensureWorkspaceTrusted(vscode.workspace.isTrusted, async () => Boolean(await workspaceTrust.requestWorkspaceTrust?.()));
  if (!trust.trusted && trust.blocker) {
    await showBlocker(output, trust.blocker);
  }
  return trust.trusted;
}

function errorDetail(error: unknown): string {
  return error instanceof Error ? error.stack ?? error.message : String(error);
}

async function showAlreadyRunning(output: vscode.OutputChannel, title: string): Promise<void> {
  output.appendLine(`GovKB: ${title} is already running; ignoring duplicate request.`);
  const selected = await vscode.window.showInformationMessage(`GovKB: ${title} is already running`, OPEN_OUTPUT_ACTION);
  await handleAction(output, selected);
}

async function runWithProgress(
  state: CommandRunState,
  output: vscode.OutputChannel,
  key: string,
  title: string,
  task: (progress: vscode.Progress<{ message?: string; increment?: number }>) => Promise<void>
): Promise<void> {
  if (!state.start(key)) {
    await showAlreadyRunning(output, title);
    return;
  }
  output.appendLine(`GovKB: ${title} started`);
  try {
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `GovKB: ${title}`,
        cancellable: false
      },
      async (progress) => {
        progress.report({ message: "Running..." });
        await task(progress);
      }
    );
  } catch (error) {
    output.appendLine(errorDetail(error));
    const selected = await vscode.window.showErrorMessage(`GovKB: ${title} failed`, OPEN_OUTPUT_ACTION);
    await handleAction(output, selected);
  } finally {
    output.appendLine(`GovKB: ${title} finished`);
    state.finish(key);
  }
}

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel("GovKB");
  const statusProvider = new SimpleTreeProvider();
  const capabilitiesProvider = new SimpleTreeProvider();
  const candidatesProvider = new SimpleTreeProvider();
  const reportsProvider = new SimpleTreeProvider();
  let latestStatus: StatusPayload | undefined;
  let latestReports: ReportSummary[] = [];
  let latestReportRoot: string | undefined;

  function refreshViews(status?: StatusPayload): void {
    latestStatus = status ?? latestStatus;
    statusProvider.setRows(statusRows(latestStatus));
    capabilitiesProvider.setRows(capabilityRows(latestStatus?.capabilities));
  }

  async function refreshStatus(projectRoot: string, warnOnNonZero = true): Promise<StatusPayload | undefined> {
    const result = await runner.run(statusJsonCommand(settingsFromVscode(), projectRoot));
    if (result.stdout.trim()) {
      try {
        const status = parseStatusPayload(result.stdout);
        refreshViews(status);
        if (result.exitCode !== 0 && warnOnNonZero) {
          await showBlocker(output, {
            title: "GovKB status reports validation errors",
            action: OPEN_OUTPUT_ACTION,
            detail: result.stderr || `govkb status exited ${result.exitCode}`
          });
        }
        return status;
      } catch (error) {
        await showBlocker(output, {
          title: "GovKB status output could not be read",
          action: OPEN_OUTPUT_ACTION,
          detail: errorDetail(error)
        });
        return undefined;
      }
    }
    if (result.exitCode !== 0) {
      await showBlocker(output, {
        title: "GovKB status refresh failed",
        action: OPEN_OUTPUT_ACTION,
        detail: result.stderr || result.stdout
      });
    }
    return undefined;
  }

  async function refreshCandidatesForProject(projectRoot: string): Promise<void> {
    try {
      const payload = await listCandidates(settingsFromVscode(), projectRoot, runner);
      candidatesProvider.setRows(candidateRows(payload.candidates));
    } catch (error) {
      await showBlocker(output, {
        title: "GovKB candidate refresh failed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function refreshReportsForProject(projectRoot?: string): Promise<void> {
    const settings = settingsFromVscode();
    let status = latestStatus;
    if (!status || (projectRoot && status.projectRoot !== projectRoot)) {
      const root = projectRoot ?? (await selectProjectRoot(output));
      if (!root) {
        return;
      }
      status = await refreshStatus(root, false);
    }
    if (!status?.project.id) {
      latestReports = [];
      latestReportRoot = undefined;
      reportsProvider.setRows(reportRows([], latestReportRoot));
      await showBlocker(output, {
        title: "GovKB project id is not available",
        action: RUN_STATUS_ACTION
      });
      return;
    }
    latestReportRoot = reportRootForProject(codexHomeForReports(settings), status.project.id);
    try {
      latestReports = await discoverReportSummaries(latestReportRoot);
      reportsProvider.setRows(reportRows(latestReports, latestReportRoot));
    } catch (error) {
      latestReports = [];
      reportsProvider.setRows(reportRows([], latestReportRoot));
      await showBlocker(output, {
        title: "GovKB reports could not be refreshed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function openReport(reportPath: string | undefined): Promise<void> {
    if (!reportPath) {
      await showBlocker(output, {
        title: "No GovKB report is selected",
        action: REFRESH_REPORTS_ACTION
      });
      return;
    }
    await vscode.window.showTextDocument(vscode.Uri.file(reportPath), { preview: true });
  }

  async function openLatestReport(): Promise<void> {
    if (latestReports.length === 0) {
      await refreshReportsForProject();
    }
    const latest = latestReports[0];
    if (!latest) {
      await showBlocker(output, {
        title: "No GovKB reports found",
        action: RUN_DRY_RUN_ACTION
      });
      return;
    }
    await openReport(latest.path);
  }

  context.subscriptions.push(
    output,
    vscode.window.registerTreeDataProvider("govkb.status", statusProvider),
    vscode.window.registerTreeDataProvider("govkb.capabilities", capabilitiesProvider),
    vscode.window.registerTreeDataProvider("govkb.candidates", candidatesProvider),
    vscode.window.registerTreeDataProvider("govkb.reports", reportsProvider)
  );

  const runner = createRunner(output);
  const commandState = new CommandRunState();

  context.subscriptions.push(
    vscode.commands.registerCommand("govkb.openOutput", () => output.show(true)),
    vscode.commands.registerCommand("govkb.openReport", async (reportPath?: string) => {
      await openReport(reportPath);
    }),
    vscode.commands.registerCommand("govkb.openLatestReport", async () => {
      await runWithProgress(commandState, output, "openLatestReport", "Open Latest Report", async () => {
        await openLatestReport();
      });
    }),
    vscode.commands.registerCommand("govkb.refreshReports", async () => {
      await runWithProgress(commandState, output, "refreshReports", "Refresh Reports", async (progress) => {
        progress.report({ message: "Reading report summaries..." });
        await refreshReportsForProject();
      });
    }),
    vscode.commands.registerCommand("govkb.oneClickSetup", async () => {
      await runWithProgress(commandState, output, "oneClickSetup", "One-Click Setup", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        const settings = settingsFromVscode();
        progress.report({ message: "Running setup sequence..." });
        const result = await runOneClickSetup(settings, projectRoot, runner, async (command) => {
          const probe = await runner.run(command);
          return probe.exitCode === 0;
        });
        if (result.statusJson) {
          refreshViews(result.statusJson);
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
        }
      });
    }),
    vscode.commands.registerCommand("govkb.oneClickApply", async () => {
      await runWithProgress(commandState, output, "oneClickApply", "One-Click Apply", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Applying governed package..." });
        const result = await runOneClickApply(settingsFromVscode(), projectRoot, runner);
        if (result.statusJson) {
          refreshViews(result.statusJson);
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
        }
      });
    }),
    vscode.commands.registerCommand("govkb.validateProject", async () => {
      await runWithProgress(commandState, output, "validateProject", "Validate Project", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Validating project..." });
        const result = await runner.run(validateCommand(settingsFromVscode(), projectRoot));
        await refreshStatus(projectRoot, false);
        if (result.exitCode !== 0) {
          await showBlocker(output, {
            title: "GovKB validation failed",
            action: OPEN_OUTPUT_ACTION,
            detail: result.stderr || result.stdout
          });
        }
      });
    }),
    vscode.commands.registerCommand("govkb.showStatus", async () => {
      await runWithProgress(commandState, output, "showStatus", "Show Status", async (progress) => {
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Refreshing status..." });
        await refreshStatus(projectRoot);
      });
    }),
    vscode.commands.registerCommand("govkb.reviewMemoryDryRun", async () => {
      await runWithProgress(commandState, output, "reviewMemoryDryRun", "Review Memory Dry Run", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        output.show(true);
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Running dry-run review..." });
        const result = await runMemoryReviewDryRun(settingsFromVscode(), projectRoot, runner);
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
          return;
        }
        progress.report({ message: "Refreshing reports and candidates..." });
        await refreshReportsForProject(projectRoot);
        await refreshCandidatesForProject(projectRoot);
      });
    }),
    vscode.commands.registerCommand("govkb.reviewMemoryApply", async () => {
      await runWithProgress(commandState, output, "reviewMemoryApply", "Review Memory Apply", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        output.show(true);
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Running apply review..." });
        const result = await runMemoryReviewApply(settingsFromVscode(), projectRoot, runner);
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
          return;
        }
        progress.report({ message: "Refreshing reports and candidates..." });
        await refreshReportsForProject(projectRoot);
        await refreshCandidatesForProject(projectRoot);
        await refreshStatus(projectRoot, false);
      });
    }),
    vscode.commands.registerCommand("govkb.listCandidates", async () => {
      await runWithProgress(commandState, output, "listCandidates", "List Candidates", async (progress) => {
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Refreshing candidates..." });
        await refreshCandidatesForProject(projectRoot);
      });
    })
  );

  statusProvider.setRows(statusRows());
  capabilitiesProvider.setRows(capabilityRows());
  candidatesProvider.setRows(candidateRows());
  reportsProvider.setRows(reportRows());
}

export function deactivate(): void {
  // VS Code disposes registered subscriptions.
}
