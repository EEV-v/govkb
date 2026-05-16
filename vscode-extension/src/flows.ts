import {
  applyCodexCommand,
  candidatesJsonCommand,
  convertSkillCommand,
  initKbCommand,
  installCommand,
  mergeCapabilitiesCommand,
  promoteAutoCommand,
  promotionApplyCommand,
  promotionArchiveCommand,
  promotionMarkReviewedCommand,
  promotionsListJsonCommand,
  renameCapabilityCommand,
  reviewMemoryApplyCommand,
  reviewMemoryCommand,
  reviewMemoryInventoryCommand,
  reviewMemoryProgressCommand,
  statusJsonCommand,
  validateCommand
} from "./govkbCli";
import {
  parseCandidatesPayload,
  parseConversionPayload,
  parseLearningInventoryPayload,
  parsePromotionsPayload,
  parseStatusPayload
} from "./jsonParsers";
import { initialLearningRunState, parseLearningProgressChunk, reduceLearningProgressEvents } from "./learningProgress";
import { checkGovkbRuntime, RuntimeProbe } from "./runtime";
import { CliCommand, CliRunner, FlowResult, GovkbSettings, LearningRunState } from "./types";

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

export async function discoverLearning(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner
): Promise<FlowResult> {
  const command = reviewMemoryInventoryCommand(settings, projectRoot);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      blocker: {
        title: "GovKB learning discovery failed",
        action: "Open the GovKB output channel",
        detail: result.stderr || result.stdout
      }
    };
  }
  return {
    ok: true,
    commands: [command],
    learningInventory: parseLearningInventoryPayload(result.stdout)
  };
}

export async function runLearningReviewBatch(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner,
  dryRun = settings.defaultDryRun,
  onState?: (state: LearningRunState) => void
): Promise<FlowResult> {
  const command = reviewMemoryProgressCommand(settings, projectRoot, dryRun);
  let state = initialLearningRunState();
  let remainder = "";
  const result = await runner.run(command, {
    onStdout: (chunk) => {
      const parsed = parseLearningProgressChunk(chunk, remainder);
      remainder = parsed.remainder;
      if (parsed.events.length > 0) {
        state = reduceLearningProgressEvents(state, parsed.events);
        onState?.(state);
      }
    }
  });
  if (remainder.trim()) {
    const parsed = parseLearningProgressChunk("\n", remainder);
    if (parsed.events.length > 0) {
      state = reduceLearningProgressEvents(state, parsed.events);
      onState?.(state);
    }
  }
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      learningRun: state,
      blocker: {
        title: `GovKB learning review ${dryRun ? "dry-run" : "apply"} failed`,
        action: "Open the GovKB output channel",
        detail: result.stderr || result.stdout
      }
    };
  }
  return { ok: true, commands: [command], learningRun: state };
}

export async function listCandidates(settings: GovkbSettings, projectRoot: string, runner: CliRunner) {
  const command = candidatesJsonCommand(settings, projectRoot);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout || "candidate listing failed");
  }
  return parseCandidatesPayload(result.stdout);
}

export async function convertSkillToGoverned(
  settings: GovkbSettings,
  projectRoot: string,
  skill: string,
  capabilityId: string | undefined,
  runner: CliRunner,
  write = false
): Promise<FlowResult> {
  const command = convertSkillCommand(settings, projectRoot, skill, capabilityId, write);
  const result = await runner.run(command);
  let conversion: FlowResult["conversion"];
  if (result.stdout.trim()) {
    try {
      conversion = parseConversionPayload(result.stdout);
    } catch {
      conversion = undefined;
    }
  }
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      conversion,
      blocker: {
        title: conversion?.strictStatus === "failed" ? "GovKB skill conversion is not strict-ready" : "GovKB skill conversion failed",
        action: "Open the GovKB output channel",
        detail: conversion ? conversionFailureDetail(conversion, result.stderr || result.stdout) : result.stderr || result.stdout
      }
    };
  }
  if (conversion?.strictStatus === "failed") {
    return {
      ok: false,
      commands: [command],
      conversion,
      blocker: {
        title: "GovKB skill conversion is not strict-ready",
        action: "Open the GovKB output channel",
        detail: conversionFailureDetail(conversion, result.stdout)
      }
    };
  }
  return { ok: true, commands: [command], conversion };
}

function conversionFailureDetail(conversion: NonNullable<FlowResult["conversion"]>, fallback: string): string {
  const errorIssues = conversion.strictIssues.filter((issue) => issue.severity === "error");
  const shown = errorIssues.slice(0, 8).map((issue) => `- ${issue.ruleId}: ${issue.message} (${issue.location})`);
  const more = errorIssues.length > shown.length ? `\n- ${errorIssues.length - shown.length} more strict error(s).` : "";
  const removed =
    conversion.packageRemoved === true
      ? "\nThe attempted package was removed; no failed governed skill package was kept."
      : "";
  return [
    `Selected skill: ${conversion.sourceName}`,
    `Target governed skill: ${conversion.capabilityId}`,
    `Strict validation: ${conversion.strictStatus}`,
    shown.length > 0 ? `Strict errors:\n${shown.join("\n")}${more}` : fallback.trim(),
    removed
  ]
    .filter((part) => part.trim())
    .join("\n\n");
}

export async function renameGovernedSkill(
  settings: GovkbSettings,
  projectRoot: string,
  oldCapabilityId: string,
  newCapabilityId: string,
  runner: CliRunner
): Promise<FlowResult> {
  const command = renameCapabilityCommand(settings, projectRoot, oldCapabilityId, newCapabilityId);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      blocker: {
        title: "GovKB governed skill rename failed",
        action: "Open the GovKB output channel",
        detail: result.stderr || result.stdout
      }
    };
  }
  return { ok: true, commands: [command] };
}

export async function mergeGovernedSkills(
  settings: GovkbSettings,
  projectRoot: string,
  sourceCapabilityId: string,
  targetCapabilityId: string,
  runner: CliRunner
): Promise<FlowResult> {
  const command = mergeCapabilitiesCommand(settings, projectRoot, sourceCapabilityId, targetCapabilityId);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    return {
      ok: false,
      commands: [command],
      blocker: {
        title: "GovKB governed skill merge failed",
        action: "Open the GovKB output channel",
        detail: result.stderr || result.stdout
      }
    };
  }
  return { ok: true, commands: [command] };
}

export async function runAutoPromote(
  settings: GovkbSettings,
  projectRoot: string,
  runner: CliRunner
): Promise<FlowResult> {
  const commands: CliCommand[] = [];
  const promote = await runAndCollect(runner, promoteAutoCommand(settings, projectRoot), commands);
  if (promote.exitCode !== 0) {
    return {
      ok: false,
      commands,
      blocker: {
        title: "GovKB automated promotion failed",
        action: "Open the GovKB output channel",
        detail: promote.stderr || promote.stdout
      }
    };
  }
  const promotions = await runAndCollect(runner, promotionsListJsonCommand(settings, projectRoot), commands);
  if (promotions.exitCode !== 0) {
    return {
      ok: false,
      commands,
      blocker: {
        title: "GovKB promotions refresh failed",
        action: "Open the GovKB output channel",
        detail: promotions.stderr || promotions.stdout
      }
    };
  }
  return {
    ok: true,
    commands,
    promotionsJson: parsePromotionsPayload(promotions.stdout)
  };
}

export async function listPromotions(settings: GovkbSettings, projectRoot: string, runner: CliRunner) {
  const command = promotionsListJsonCommand(settings, projectRoot);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout || "promotion listing failed");
  }
  return parsePromotionsPayload(result.stdout);
}

export async function markPromotionReviewed(
  settings: GovkbSettings,
  projectRoot: string,
  promotion: string,
  decision: "accepted" | "rejected",
  reason: string,
  runner: CliRunner,
  reviewer?: string
) {
  const command = promotionMarkReviewedCommand(settings, projectRoot, promotion, decision, reason, reviewer);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout || "promotion review update failed");
  }
  return listPromotions(settings, projectRoot, runner);
}

export async function applyPromotionToProject(
  settings: GovkbSettings,
  projectRoot: string,
  promotion: string,
  runner: CliRunner
) {
  const command = promotionApplyCommand(settings, projectRoot, promotion);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout || "promotion finalization failed");
  }
  return listPromotions(settings, projectRoot, runner);
}

export async function archivePromotion(
  settings: GovkbSettings,
  projectRoot: string,
  promotion: string,
  reason: string | undefined,
  runner: CliRunner
) {
  const command = promotionArchiveCommand(settings, projectRoot, promotion, reason);
  const result = await runner.run(command);
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout || "promotion archive failed");
  }
  return listPromotions(settings, projectRoot, runner);
}
