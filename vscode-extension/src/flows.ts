import {
  applyCodexCommand,
  candidatesJsonCommand,
  initKbCommand,
  installCommand,
  reviewMemoryApplyCommand,
  reviewMemoryCommand,
  statusJsonCommand,
  validateCommand
} from "./govkbCli";
import { parseCandidatesPayload, parseStatusPayload } from "./jsonParsers";
import { checkGovkbRuntime, RuntimeProbe } from "./runtime";
import { CliCommand, CliRunner, FlowResult, GovkbSettings } from "./types";

async function runAndCollect(runner: CliRunner, command: CliCommand, commands: CliCommand[]) {
  commands.push(command);
  return runner.run(command);
}

export async function runOneClickSetup(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner,
  runtimeProbe: RuntimeProbe
): Promise<FlowResult> {
  const commands: CliCommand[] = [];
  const runtime = await checkGovkbRuntime(settings, runtimeProbe);
  if (!runtime.ok) {
    return { ok: false, commands, blocker: runtime.blocker };
  }
  for (const command of [
    installCommand(settings, projectRoot),
    initKbCommand(settings, projectRoot),
    validateCommand(settings, projectRoot)
  ]) {
    const result = await runAndCollect(runner, command, commands);
    if (result.exitCode !== 0) {
      return {
        ok: false,
        commands,
        blocker: {
          title: "GovKB setup command failed",
          action: "Open the GovKB output channel",
          detail: result.stderr || result.stdout
        }
      };
    }
  }
  const status = await runAndCollect(runner, statusJsonCommand(settings, projectRoot), commands);
  if (status.exitCode !== 0) {
    return {
      ok: false,
      commands,
      blocker: {
        title: "GovKB status refresh failed",
        action: "Run GovKB: Show Status",
        detail: status.stderr || status.stdout
      }
    };
  }
  return {
    ok: true,
    commands,
    statusJson: parseStatusPayload(status.stdout)
  };
}

export async function runOneClickApply(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner
): Promise<FlowResult> {
  const commands: CliCommand[] = [];
  const preflight = await runAndCollect(runner, statusJsonCommand(settings, projectRoot), commands);
  if (preflight.exitCode !== 0) {
    return {
      ok: false,
      commands,
      blocker: {
        title: "GovKB project is not initialized",
        action: "Run GovKB: One-Click Setup Current Project",
        detail: preflight.stderr || preflight.stdout
      }
    };
  }
  const apply = await runAndCollect(runner, applyCodexCommand(settings, projectRoot), commands);
  if (apply.exitCode !== 0) {
    return {
      ok: false,
      commands,
      blocker: {
        title: "GovKB apply failed",
        action: "Open the GovKB output channel",
        detail: apply.stderr || apply.stdout
      }
    };
  }
  const status = await runAndCollect(runner, statusJsonCommand(settings, projectRoot), commands);
  if (status.exitCode !== 0) {
    return {
      ok: false,
      commands,
      blocker: {
        title: "GovKB status refresh failed",
        action: "Run GovKB: Show Status",
        detail: status.stderr || status.stdout
      }
    };
  }
  return {
    ok: true,
    commands,
    statusJson: parseStatusPayload(status.stdout)
  };
}

export async function runMemoryReviewDryRun(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner
): Promise<FlowResult> {
  return runMemoryReview(settings, projectRoot, runner, true);
}

export async function runMemoryReviewApply(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner
): Promise<FlowResult> {
  const command = reviewMemoryApplyCommand(settings, projectRoot);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      blocker: {
        title: "GovKB memory review apply failed",
        action: "Open the GovKB output channel",
        detail: result.stderr || result.stdout
      }
    };
  }
  return { ok: true, commands: [command] };
}

export async function runMemoryReview(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner,
  dryRun = settings.defaultDryRun
): Promise<FlowResult> {
  const command = reviewMemoryCommand(settings, projectRoot, dryRun);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      blocker: {
        title: `GovKB memory review ${dryRun ? "dry-run" : "apply"} failed`,
        action: "Open the GovKB output channel",
        detail: result.stderr || result.stdout
      }
    };
  }
  return { ok: true, commands: [command] };
}

export async function listCandidates(settings: GovkbSettings, projectRoot: string, runner: CliRunner) {
  const command = candidatesJsonCommand(settings, projectRoot);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout || "candidate listing failed");
  }
  return parseCandidatesPayload(result.stdout);
}
