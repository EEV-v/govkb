import { spawn } from "node:child_process";
import { CliCommand, CliResult, CliRunOptions, GovkbSettings } from "./types";

export function buildGovkbCommand(settings: GovkbSettings, args: string[], cwd?: string): CliCommand {
  if (settings.command === "python-module") {
    return {
      executable: settings.pythonPath,
      args: ["-m", "govkb.cli", ...args],
      cwd
    };
  }
  return {
    executable: settings.command,
    args,
    cwd
  };
}

function withCodexHome(args: string[], codexHome?: string): string[] {
  return codexHome ? [...args, "--codex-home", codexHome] : args;
}

export function installCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, withCodexHome(["install", projectRoot], settings.codexHome));
}

export function initKbCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, withCodexHome(["init-kb", projectRoot, "--all"], settings.codexHome));
}

export function validateCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, ["validate", projectRoot]);
}

export function statusJsonCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, [...withCodexHome(["status", projectRoot], settings.codexHome), "--json"]);
}

export function applyCodexCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, withCodexHome(["apply", "codex", "--project-root", projectRoot], settings.codexHome));
}

export function convertSkillCommand(
  settings: GovkbSettings,
  projectRoot: string,
  skill: string,
  capabilityId?: string,
  write = false
): CliCommand {
  const args = ["convert", "skill", skill, "--project-root", projectRoot];
  if (settings.codexHome) {
    args.push("--codex-home", settings.codexHome);
  }
  if (capabilityId) {
    args.push("--capability-id", capabilityId);
  }
  if (write) {
    args.push("--write");
  }
  args.push("--json");
  return buildGovkbCommand(settings, args);
}

export function renameCapabilityCommand(
  settings: GovkbSettings,
  projectRoot: string,
  oldCapabilityId: string,
  newCapabilityId: string
): CliCommand {
  return buildGovkbCommand(settings, [
    "capabilities",
    "rename",
    oldCapabilityId,
    newCapabilityId,
    "--project-root",
    projectRoot,
    "--json"
  ]);
}

export function mergeCapabilitiesCommand(
  settings: GovkbSettings,
  projectRoot: string,
  sourceCapabilityId: string,
  targetCapabilityId: string
): CliCommand {
  return buildGovkbCommand(settings, [
    "capabilities",
    "merge",
    sourceCapabilityId,
    targetCapabilityId,
    "--project-root",
    projectRoot,
    "--json"
  ]);
}

export function promoteAutoCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, withCodexHome(["promote", projectRoot, "--auto"], settings.codexHome));
}

export function promotionsListJsonCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, [...withCodexHome(["promotions", "list", projectRoot], settings.codexHome), "--json"]);
}

export function promotionShowCommand(settings: GovkbSettings, projectRoot: string, promotion: string): CliCommand {
  return buildGovkbCommand(settings, withCodexHome(["promotions", "show", promotion, "--project-root", projectRoot], settings.codexHome));
}

export function promotionMarkReviewedCommand(
  settings: GovkbSettings,
  projectRoot: string,
  promotion: string,
  decision: "accepted" | "rejected",
  reason: string,
  reviewer?: string
): CliCommand {
  const args = [
    "promotions",
    "mark-reviewed",
    promotion,
    "--project-root",
    projectRoot,
    "--decision",
    decision,
    "--reason",
    reason
  ];
  if (reviewer) {
    args.push("--reviewer", reviewer);
  }
  return buildGovkbCommand(settings, [...withCodexHome(args, settings.codexHome), "--json"]);
}

export function promotionApplyCommand(settings: GovkbSettings, projectRoot: string, promotion: string): CliCommand {
  return buildGovkbCommand(
    settings,
    [...withCodexHome(["promotions", "apply", promotion, "--project-root", projectRoot], settings.codexHome), "--json"]
  );
}

export function promotionArchiveCommand(
  settings: GovkbSettings,
  projectRoot: string,
  promotion: string,
  reason?: string
): CliCommand {
  const args = ["promotions", "archive", promotion, "--project-root", projectRoot];
  if (reason) {
    args.push("--reason", reason);
  }
  return buildGovkbCommand(settings, [...withCodexHome(args, settings.codexHome), "--json"]);
}

export function candidatesJsonCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return buildGovkbCommand(settings, ["candidates", "list", projectRoot, "--json"]);
}

export function reviewMemoryCommand(settings: GovkbSettings, projectRoot: string, dryRun = settings.defaultDryRun): CliCommand {
  const args = [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    projectRoot
  ];
  if (dryRun) {
    args.push("--dry-run");
  }
  args.push("--lookback-days", String(settings.reviewLookbackDays));
  args.push("--max-sessions", String(settings.reviewMaxSessions));
  if (settings.classifierModel) {
    args.push("--codex-model", settings.classifierModel);
  }
  if (settings.classifierReasoning) {
    args.push("--codex-reasoning", settings.classifierReasoning);
  }
  if (settings.reviewTimeoutSeconds) {
    args.push("--codex-timeout", String(settings.reviewTimeoutSeconds));
  }
  const command = buildGovkbCommand(settings, args);
  return settings.codexHome ? { ...command, env: { CODEX_HOME: settings.codexHome } } : command;
}

export function reviewMemoryInventoryCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  const args = [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    projectRoot,
    "--inventory-json",
    "--lookback-days",
    String(settings.reviewLookbackDays),
    "--max-sessions",
    String(settings.reviewMaxSessions)
  ];
  const command = buildGovkbCommand(settings, args);
  return settings.codexHome ? { ...command, env: { CODEX_HOME: settings.codexHome } } : command;
}

export function reviewMemoryProgressCommand(
  settings: GovkbSettings,
  projectRoot: string,
  dryRun = settings.defaultDryRun
): CliCommand {
  const command = reviewMemoryCommand(settings, projectRoot, dryRun);
  return { ...command, args: [...command.args, "--progress-jsonl"] };
}

export function reviewMemoryDryRunCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return reviewMemoryCommand(settings, projectRoot, true);
}

export function reviewMemoryApplyCommand(settings: GovkbSettings, projectRoot: string): CliCommand {
  return reviewMemoryCommand(settings, projectRoot, false);
}

export function runCliCommand(command: CliCommand, options: CliRunOptions = {}): Promise<CliResult> {
  return new Promise((resolve) => {
    const child = spawn(command.executable, command.args, {
      cwd: command.cwd,
      env: command.env ? { ...process.env, ...command.env } : process.env,
      stdio: ["ignore", "pipe", "pipe"],
      shell: false
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      stdout += text;
      options.onStdout?.(text);
    });
    child.stderr.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      stderr += text;
      options.onStderr?.(text);
    });
    child.on("error", (error) => {
      resolve({
        command,
        exitCode: 127,
        stdout,
        stderr: stderr + error.message
      });
    });
    child.on("close", (code) => {
      resolve({
        command,
        exitCode: code ?? 1,
        stdout,
        stderr
      });
    });
  });
}
