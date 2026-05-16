import * as vscode from "vscode";
import * as path from "node:path";
import { CommandRunState } from "./commandState";
import { promotionShowCommand, runCliCommand, statusJsonCommand, validateCommand } from "./govkbCli";
import {
  applyPromotionToProject,
  archivePromotion,
  convertSkillToGoverned,
  discoverLearning,
  listCandidates,
  listPromotions,
  markPromotionReviewed,
  mergeGovernedSkills,
  renameGovernedSkill,
  runAutoPromote,
  runLearningReviewBatch,
  runOneClickApply,
  runOneClickSetup
} from "./flows";
import { parseStatusPayload } from "./jsonParsers";
import { discoverLocalSkills, LocalSkillSummary } from "./localSkills";
import { resolveProjectRoot } from "./projectSelection";
import { defaultPromotionReviewReason, normalizePromotionReviewReason } from "./promotionReview";
import { codexHomeForReports, discoverReportSummaries, reportRootForProject } from "./reports";
import { withResolvedGovkbRuntime } from "./runtimeDiscovery";
import { resolveSettings } from "./settings";
import { ensureWorkspaceTrusted } from "./trust";
import {
  Blocker,
  CandidateSummary,
  CapabilitySummary,
  CliCommand,
  CliRunOptions,
  CliRunner,
  LearningInventoryPayload,
  LearningRunState,
  PromotionSummary,
  ReportSummary,
  StatusPayload
} from "./types";
import { SimpleTreeProvider } from "./views/simpleTree";
import { capabilityRows } from "./views/capabilitiesView";
import { candidateRows } from "./views/candidatesView";
import { learningRows } from "./views/learningView";
import { promotionRows } from "./views/promotionsView";
import { promotionGroups } from "./views/promotionsView";
import { reportRows } from "./views/reportsView";
import { statusRows } from "./views/statusView";
import { LAST_PROJECT_ROOT_KEY, storedProjectRootForWorkspace } from "./workspaceProject";

const OPEN_OUTPUT_ACTION = "Open the GovKB output channel";
const RUN_SETUP_ACTION = "Run GovKB: One-Click Setup Current Project";
const RUN_STATUS_ACTION = "Run GovKB: Show Status";
const RUN_DRY_RUN_ACTION = "Run GovKB: Review Memory Dry Run";
const RUN_APPLY_REVIEW_ACTION = "Run GovKB: Review Memory Apply";
const REFRESH_REPORTS_ACTION = "GovKB: Refresh Reports";
const RUN_AUTO_PROMOTE_ACTION = "GovKB: Auto Promote Learned Updates";
const REFRESH_PROMOTIONS_ACTION = "GovKB: Refresh Promotions";
const MARK_PROMOTION_ACCEPTED_ACTION = "GovKB: Mark Promotion Accepted";
const CONVERT_SKILL_ACTION = "GovKB: Convert One Existing Skill To Governed";
const ENTER_SKILL_MANUALLY_ACTION = "Enter skill name or path manually";

function settingsFromVscode() {
  const settings = withResolvedGovkbRuntime(resolveSettings(vscode.workspace.getConfiguration("govkb")));
  return {
    ...settings,
    codexHome: codexHomeForReports(settings)
  };
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
  if (selected === RUN_AUTO_PROMOTE_ACTION) {
    await vscode.commands.executeCommand("govkb.promoteAuto");
    return;
  }
  if (selected === REFRESH_PROMOTIONS_ACTION) {
    await vscode.commands.executeCommand("govkb.refreshPromotions");
    return;
  }
  if (selected === MARK_PROMOTION_ACCEPTED_ACTION) {
    await vscode.commands.executeCommand("govkb.markPromotionAccepted");
    return;
  }
  if (selected === CONVERT_SKILL_ACTION) {
    await vscode.commands.executeCommand("govkb.convertSkillToGoverned");
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
    async run(command: CliCommand, options?: CliRunOptions) {
      output.appendLine(`$ ${command.executable} ${command.args.join(" ")}`);
      let lastChunkEndedWithNewline = true;
      const appendChunk = (chunk: string) => {
        output.append(chunk);
        lastChunkEndedWithNewline = chunk.endsWith("\n") || chunk.endsWith("\r");
      };
      const result = await runCliCommand(command, {
        onStdout: (chunk) => {
          options?.onStdout?.(chunk);
          appendChunk(chunk);
        },
        onStderr: (chunk) => {
          options?.onStderr?.(chunk);
          appendChunk(chunk);
        }
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
  vscode.window.setStatusBarMessage(`GovKB: ${title} is already running`, 5000);
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
  const learningProvider = new SimpleTreeProvider();
  const candidatesProvider = new SimpleTreeProvider();
  const promotionsProvider = new SimpleTreeProvider();
  const reportsProvider = new SimpleTreeProvider();
  let latestStatus: StatusPayload | undefined;
  let latestPromotions: PromotionSummary[] = [];
  let latestPromotionsProjectRoot: string | undefined;
  let latestReports: ReportSummary[] = [];
  let latestReportRoot: string | undefined;
  let latestCandidates: CandidateSummary[] = [];
  let latestLearningInventory: LearningInventoryPayload | undefined;
  let latestLearningRun: LearningRunState | undefined;
  let monitor: NodeJS.Timeout | undefined;

  function rememberProjectRoot(projectRoot: string): void {
    void context.workspaceState.update(LAST_PROJECT_ROOT_KEY, projectRoot);
  }

  function refreshLearningView(): void {
    learningProvider.setRows(
      learningRows({
        status: latestStatus,
        inventory: latestLearningInventory,
        run: latestLearningRun,
        reports: latestReports,
        candidates: latestCandidates,
        promotions: latestPromotions
      })
    );
  }

  function refreshViews(status?: StatusPayload): void {
    latestStatus = status ?? latestStatus;
    statusProvider.setRows(statusRows(latestStatus));
    capabilitiesProvider.setRows(capabilityRows(latestStatus?.capabilities, latestStatus?.governedRoot));
    refreshLearningView();
  }

  function capabilityRoot(capability: CapabilitySummary): string | undefined {
    return capability.path ?? (latestStatus?.governedRoot ? path.join(latestStatus.governedRoot, "capabilities", capability.id) : undefined);
  }

  async function refreshCapabilitiesForProject(projectRoot?: string): Promise<void> {
    const root = projectRoot ?? latestStatus?.projectRoot ?? (await selectProjectRoot(output));
    if (!root) {
      return;
    }
    await refreshStatus(root, false);
  }

  async function selectCapability(
    capability?: CapabilitySummary | string,
    title = "Select governed skill"
  ): Promise<{ projectRoot: string; capability: CapabilitySummary } | undefined> {
    const projectRoot = latestStatus?.projectRoot ?? (await selectProjectRoot(output));
    if (!projectRoot) {
      return undefined;
    }
    if (!latestStatus || latestStatus.projectRoot !== projectRoot) {
      await refreshStatus(projectRoot, false);
    }
    if (typeof capability === "object" && capability?.id) {
      return { projectRoot, capability };
    }
    if (typeof capability === "string" && latestStatus) {
      const found = latestStatus.capabilities.find((item) => item.id === capability || item.name === capability || item.path === capability);
      if (found) {
        return { projectRoot, capability: found };
      }
    }
    const capabilities = latestStatus?.capabilities ?? [];
    if (capabilities.length === 0) {
      await showBlocker(output, {
        title: "No governed skills found",
        action: RUN_SETUP_ACTION
      });
      return undefined;
    }
    const picked = await vscode.window.showQuickPick(
      capabilities.map((item) => ({
        label: item.id,
        description: item.name,
        detail: item.description,
        capability: item
      })),
      { title }
    );
    return picked ? { projectRoot, capability: picked.capability } : undefined;
  }

  async function openCapability(capability?: CapabilitySummary | string): Promise<void> {
    const selected = await selectCapability(capability);
    if (!selected) {
      return;
    }
    const root = capabilityRoot(selected.capability);
    if (!root) {
      await showBlocker(output, {
        title: "Governed skill path is not available",
        action: RUN_STATUS_ACTION
      });
      return;
    }
    const preferred = vscode.Uri.file(selected.capability.instructionsPath ?? path.join(root, "instructions.md"));
    const fallback = vscode.Uri.file(path.join(root, "capability.contract.toml"));
    try {
      await vscode.window.showTextDocument(preferred, { preview: true });
    } catch {
      await vscode.window.showTextDocument(fallback, { preview: true });
    }
  }

  function normalizeCapabilityInput(value: string): string {
    return value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function governedSkillNamesForConversion(status?: StatusPayload): string[] {
    const names = new Set<string>();
    for (const capability of status?.capabilities ?? []) {
      names.add(capability.id);
      names.add(capability.name);
      for (const alias of capability.aliases ?? []) {
        names.add(alias);
      }
    }
    for (const materialized of status?.installState.codex.materializedCapabilities ?? []) {
      if (materialized.materializedSkillId) {
        names.add(materialized.materializedSkillId);
      }
    }
    return [...names].filter(Boolean);
  }

  async function enterSkillSourceManually(): Promise<string | undefined> {
    return vscode.window.showInputBox({
      title: "Enter one Codex skill",
      prompt: "Enter one skill name under CODEX_HOME/skills, an explicit skill folder path, or a SKILL.md path",
      placeHolder: "release-helper, /Users/me/.codex/skills/release-helper, or /Users/me/.codex/skills/release-helper/SKILL.md",
      ignoreFocusOut: true,
      validateInput: (value) => (value.trim() ? undefined : "Skill name or path is required.")
    });
  }

  async function chooseSkillSourceForConversion(
    settings: ReturnType<typeof settingsFromVscode>,
    status?: StatusPayload
  ): Promise<string | undefined> {
    let skills: LocalSkillSummary[];
    try {
      skills = await discoverLocalSkills(settings.codexHome, 2, {
        excludeNames: governedSkillNamesForConversion(status)
      });
    } catch (error) {
      output.appendLine(`GovKB: failed to list local Codex skills: ${(error as Error).message}`);
      skills = [];
    }
    const manualItem = {
      label: ENTER_SKILL_MANUALLY_ACTION,
      description: "Use a skill not shown here",
      detail: "Enter a skill name, folder path, or SKILL.md path.",
      alwaysShow: true,
      manual: true
    };
    const items = [
      ...skills.map((skill) => ({
        label: skill.name,
        description: skill.relativePath,
        detail: skill.description ?? skill.path,
        source: skill.path
      })),
      manualItem
    ];
    const picked = await vscode.window.showQuickPick(items, {
      title: "Choose one Codex skill to convert",
      placeHolder: skills.length > 0 ? "Only the selected skill will be converted." : "No CODEX_HOME/skills packages found.",
      matchOnDescription: true,
      matchOnDetail: true,
      ignoreFocusOut: true
    });
    if (!picked) {
      return undefined;
    }
    if ("manual" in picked && picked.manual) {
      return enterSkillSourceManually();
    }
    return "source" in picked ? picked.source : undefined;
  }

  async function runConvertSkillToGovernedCommand(skillInput?: string): Promise<void> {
    if (!(await requireTrusted(output))) {
      return;
    }
    const projectRoot = latestStatus?.projectRoot ?? (await selectProjectRoot(output));
    if (!projectRoot) {
      return;
    }
    const settings = settingsFromVscode();
    let status = latestStatus;
    if (!status || status.projectRoot !== projectRoot) {
      status = await refreshStatus(projectRoot, false);
    }
    const skill = skillInput ?? (await chooseSkillSourceForConversion(settings, status));
    if (!skill?.trim()) {
      return;
    }
    const trimmedSkill = skill.trim();
    const defaultName = path.basename(trimmedSkill) === "SKILL.md" ? path.basename(path.dirname(trimmedSkill)) : path.basename(trimmedSkill);
    const defaultId = normalizeCapabilityInput(defaultName) || undefined;
    const capabilityIdInput = await vscode.window.showInputBox({
      title: "Target governed skill id",
      prompt: "Leave the suggested id or enter a lower kebab-case capability id",
      value: defaultId,
      ignoreFocusOut: true,
      validateInput: (value) => (!value.trim() || normalizeCapabilityInput(value) === value.trim() ? undefined : "Use lower kebab-case.")
    });
    if (capabilityIdInput === undefined) {
      return;
    }
    const capabilityId = capabilityIdInput.trim() || undefined;
    await runWithProgress(commandState, output, "convertSkillToGoverned", "Convert One Existing Skill To Governed", async (progress) => {
      progress.report({ message: "Previewing conversion..." });
      const preview = await convertSkillToGoverned(settings, projectRoot, trimmedSkill, capabilityId, runner, false);
      if (!preview.ok) {
        if (preview.blocker) {
          await showBlocker(output, preview.blocker);
        }
        return;
      }
      const decision = await vscode.window.showInformationMessage(
        "Create this governed skill package? The source skill is left unchanged and the new package stays in Git for review.",
        "Create governed skill",
        "Cancel"
      );
      if (decision !== "Create governed skill") {
        output.appendLine("GovKB: governed skill conversion cancelled after preview.");
        return;
      }
      progress.report({ message: "Writing governed skill package..." });
      const written = await convertSkillToGoverned(settings, projectRoot, trimmedSkill, capabilityId, runner, true);
      if (!written.ok) {
        if (written.blocker) {
          await showBlocker(output, written.blocker);
        }
        return;
      }
      await refreshStatus(projectRoot, false);
      output.appendLine("GovKB: existing skill converted into a governed package.");
    });
  }

  async function runRenameGovernedSkillCommand(capability?: CapabilitySummary | string): Promise<void> {
    if (!(await requireTrusted(output))) {
      return;
    }
    const selected = await selectCapability(capability, "Select governed skill to rename");
    if (!selected) {
      return;
    }
    const newId = await vscode.window.showInputBox({
      title: "Rename governed skill",
      prompt: `New id for ${selected.capability.id}`,
      value: selected.capability.id,
      ignoreFocusOut: true,
      validateInput: (value) => {
        const normalized = normalizeCapabilityInput(value);
        if (!normalized) {
          return "New governed skill id is required.";
        }
        if (normalized !== value.trim()) {
          return "Use lower kebab-case.";
        }
        if (normalized === selected.capability.id) {
          return "Choose a different id.";
        }
        return undefined;
      }
    });
    if (!newId) {
      return;
    }
    await runWithProgress(commandState, output, "renameGovernedSkill", "Rename Governed Skill", async (progress) => {
      progress.report({ message: "Renaming governed skill..." });
      const result = await renameGovernedSkill(
        settingsFromVscode(),
        selected.projectRoot,
        selected.capability.id,
        newId.trim(),
        runner
      );
      if (!result.ok) {
        if (result.blocker) {
          await showBlocker(output, result.blocker);
        }
        return;
      }
      await refreshStatus(selected.projectRoot, false);
      output.appendLine(`GovKB: renamed governed skill ${selected.capability.id} -> ${newId.trim()}.`);
    });
  }

  async function runMergeGovernedSkillsCommand(source?: CapabilitySummary | string): Promise<void> {
    if (!(await requireTrusted(output))) {
      return;
    }
    const selectedSource = await selectCapability(source, "Select governed skill to merge");
    if (!selectedSource) {
      return;
    }
    const candidates = latestStatus?.capabilities.filter((item) => item.id !== selectedSource.capability.id) ?? [];
    if (candidates.length === 0) {
      await showBlocker(output, {
        title: "No merge target governed skill found",
        action: CONVERT_SKILL_ACTION
      });
      return;
    }
    const pickedTarget = await vscode.window.showQuickPick(
      candidates.map((item) => ({
        label: item.id,
        description: item.name,
        detail: item.description,
        capability: item
      })),
      { title: `Merge ${selectedSource.capability.id} into...` }
    );
    if (!pickedTarget) {
      return;
    }
    const decision = await vscode.window.showWarningMessage(
      `Merge ${selectedSource.capability.id} into ${pickedTarget.capability.id}? The source governed skill package is removed after its guidance is copied into the target.`,
      "Merge governed skills",
      "Cancel"
    );
    if (decision !== "Merge governed skills") {
      return;
    }
    await runWithProgress(commandState, output, "mergeGovernedSkills", "Merge Governed Skills", async (progress) => {
      progress.report({ message: "Merging governed skills..." });
      const result = await mergeGovernedSkills(
        settingsFromVscode(),
        selectedSource.projectRoot,
        selectedSource.capability.id,
        pickedTarget.capability.id,
        runner
      );
      if (!result.ok) {
        if (result.blocker) {
          await showBlocker(output, result.blocker);
        }
        return;
      }
      await refreshStatus(selectedSource.projectRoot, false);
      output.appendLine(`GovKB: merged governed skill ${selectedSource.capability.id} into ${pickedTarget.capability.id}.`);
    });
  }

  async function refreshStatus(projectRoot: string, warnOnNonZero = true): Promise<StatusPayload | undefined> {
    const result = await runner.run(statusJsonCommand(settingsFromVscode(), projectRoot));
    if (result.stdout.trim()) {
      try {
        const status = parseStatusPayload(result.stdout);
        rememberProjectRoot(status.projectRoot);
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
      latestCandidates = payload.candidates;
      candidatesProvider.setRows(candidateRows(latestCandidates));
      refreshLearningView();
    } catch (error) {
      await showBlocker(output, {
        title: "GovKB candidate refresh failed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function selectCandidate(candidate?: CandidateSummary | string): Promise<CandidateSummary | undefined> {
    if (typeof candidate === "object" && candidate?.id) {
      return candidate;
    }
    if (typeof candidate === "string") {
      const found = latestCandidates.find(
        (item) => item.id === candidate || item.suggestedCapabilityId === candidate || item.path === candidate
      );
      if (found) {
        return found;
      }
    }
    const projectRoot = latestStatus?.projectRoot ?? (await selectProjectRoot(output));
    if (!projectRoot) {
      return undefined;
    }
    if (latestCandidates.length === 0) {
      await refreshCandidatesForProject(projectRoot);
    }
    if (latestCandidates.length === 0) {
      await showBlocker(output, {
        title: "No GovKB candidates found",
        action: RUN_APPLY_REVIEW_ACTION
      });
      return undefined;
    }
    const picked = await vscode.window.showQuickPick(
      latestCandidates.map((item) => ({
        label: item.suggestedCapabilityId ?? item.id,
        description: `${item.status}, ${item.occurrences} occurrence${item.occurrences === 1 ? "" : "s"}`,
        detail: item.id === item.suggestedCapabilityId ? item.path : `${item.id} - ${item.path}`,
        candidate: item
      })),
      { title: "Select GovKB candidate" }
    );
    return picked?.candidate;
  }

  async function openCandidate(candidate?: CandidateSummary | string): Promise<void> {
    const selected = await selectCandidate(candidate);
    if (!selected) {
      return;
    }
    const preferred = vscode.Uri.file(path.join(selected.path, "draft-instructions.md"));
    const fallback = vscode.Uri.file(path.join(selected.path, "candidate.toml"));
    try {
      await vscode.window.showTextDocument(preferred, { preview: true });
    } catch {
      await vscode.window.showTextDocument(fallback, { preview: true });
    }
  }

  async function refreshPromotionsForProject(projectRoot?: string): Promise<void> {
    const root = projectRoot ?? latestPromotionsProjectRoot ?? latestStatus?.projectRoot ?? (await selectProjectRoot(output));
    if (!root) {
      return;
    }
    try {
      await refreshStatus(root, false);
      const payload = await listPromotions(settingsFromVscode(), root, runner);
      rememberProjectRoot(root);
      latestPromotions = payload.promotions;
      latestPromotionsProjectRoot = root;
      promotionsProvider.setRows(promotionRows(latestPromotions, latestStatus));
      refreshLearningView();
    } catch (error) {
      await showBlocker(output, {
        title: "GovKB promotions refresh failed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function selectPromotion(
    promotion?: PromotionSummary | string
  ): Promise<{ projectRoot: string; promotion: PromotionSummary } | undefined> {
    const projectRoot = latestPromotionsProjectRoot ?? latestStatus?.projectRoot ?? (await selectProjectRoot(output));
    if (!projectRoot) {
      return undefined;
    }
    if (typeof promotion === "object" && promotion?.runId) {
      return { projectRoot, promotion };
    }
    if (typeof promotion === "string") {
      const found = latestPromotions.find((item) => item.runId === promotion || item.branch === promotion || item.worktreeRoot === promotion);
      if (found) {
        return { projectRoot, promotion: found };
      }
    }
    if (latestPromotions.length === 0 || latestPromotionsProjectRoot !== projectRoot) {
      await refreshPromotionsForProject(projectRoot);
    }
    if (latestPromotions.length === 0) {
      await showBlocker(output, {
        title: "No GovKB promotions found",
        action: RUN_AUTO_PROMOTE_ACTION
      });
      return undefined;
    }
    const groupedPromotions = promotionGroups(latestPromotions).map((group) => group.promotion);
    const picked = await vscode.window.showQuickPick(
      groupedPromotions.map((item) => ({
        label:
          item.state === "accepted"
            ? "Next: finalize accepted learning updates"
            : item.state === "ready-for-review"
              ? "1. Open learning review"
              : item.runId,
        description: item.state,
        detail: item.review?.reason ?? item.branch ?? item.worktreeRoot,
        promotion: item
      })),
      { title: "Select GovKB promotion" }
    );
    return picked ? { projectRoot, promotion: picked.promotion } : undefined;
  }

  async function openPromotion(promotion?: PromotionSummary | string): Promise<void> {
    const selected = await selectPromotion(promotion);
    if (!selected) {
      return;
    }
    if (!selected.promotion.digestPath) {
      await showBlocker(output, {
        title: "Promotion digest is not available",
        action: OPEN_OUTPUT_ACTION
      });
      return;
    }
    await vscode.window.showTextDocument(vscode.Uri.file(selected.promotion.digestPath), { preview: true });
  }

  async function openPromotionWorktree(promotion?: PromotionSummary | string): Promise<void> {
    const selected = await selectPromotion(promotion);
    if (!selected) {
      return;
    }
    await vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(selected.promotion.worktreeRoot), true);
  }

  async function showPromotion(promotion?: PromotionSummary | string): Promise<void> {
    const selected = await selectPromotion(promotion);
    if (!selected) {
      return;
    }
    output.show(true);
    const result = await runner.run(promotionShowCommand(settingsFromVscode(), selected.projectRoot, selected.promotion.runId));
    if (result.exitCode !== 0) {
      await showBlocker(output, {
        title: "GovKB promotion details failed",
        action: OPEN_OUTPUT_ACTION,
        detail: result.stderr || result.stdout
      });
    }
  }

  async function markSelectedPromotion(
    decision: "accepted" | "rejected",
    promotion?: PromotionSummary | string
  ): Promise<void> {
    const selected = await selectPromotion(promotion);
    if (!selected) {
      output.appendLine("GovKB: promotion review cancelled; no promotion selected.");
      return;
    }
    const reasonInput = await vscode.window.showInputBox({
      title: `Mark GovKB promotion ${decision}`,
      prompt: "Review reason",
      value: defaultPromotionReviewReason(decision),
      ignoreFocusOut: true,
      validateInput: (value) => (normalizePromotionReviewReason(value) ? undefined : "Review reason is required.")
    });
    const reason = normalizePromotionReviewReason(reasonInput);
    if (!reason) {
      output.appendLine("GovKB: promotion review cancelled; no review reason entered.");
      return;
    }
    try {
      const payload = await markPromotionReviewed(
        settingsFromVscode(),
        selected.projectRoot,
        selected.promotion.runId,
        decision,
        reason,
        runner
      );
      latestPromotions = payload.promotions;
      latestPromotionsProjectRoot = selected.projectRoot;
      promotionsProvider.setRows(promotionRows(latestPromotions, latestStatus));
      refreshLearningView();
      output.appendLine(`GovKB: promotion ${selected.promotion.runId} marked ${decision}.`);
    } catch (error) {
      await showBlocker(output, {
        title: "GovKB promotion review update failed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function archiveSelectedPromotion(promotion?: PromotionSummary | string): Promise<void> {
    const selected = await selectPromotion(promotion);
    if (!selected) {
      return;
    }
    const reason = await vscode.window.showInputBox({
      title: "Archive GovKB promotion",
      prompt: "Archive reason",
      ignoreFocusOut: true
    });
    if (reason === undefined) {
      return;
    }
    try {
      const payload = await archivePromotion(
        settingsFromVscode(),
        selected.projectRoot,
        selected.promotion.runId,
        reason || undefined,
        runner
      );
      latestPromotions = payload.promotions;
      latestPromotionsProjectRoot = selected.projectRoot;
      promotionsProvider.setRows(promotionRows(latestPromotions, latestStatus));
      refreshLearningView();
    } catch (error) {
      await showBlocker(output, {
        title: "GovKB promotion archive failed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function preparePromotionFinalization(
    promotion?: PromotionSummary | string
  ): Promise<{ projectRoot: string; promotion: PromotionSummary } | undefined> {
    const selected = await selectPromotion(promotion);
    if (!selected) {
      return undefined;
    }
    await refreshPromotionsForProject(selected.projectRoot);
    const current =
      latestPromotions.find((item) => item.runId === selected.promotion.runId) ?? selected.promotion;
    if (current.state === "applied") {
      refreshLearningView();
      const action = await vscode.window.showInformationMessage(
        "GovKB learning updates are already finalized. Review and commit the active .governed changes when ready.",
        RUN_STATUS_ACTION
      );
      await handleAction(output, action);
      return undefined;
    }
    if (current.state !== "accepted") {
      await showBlocker(output, {
        title: "Accept the GovKB promotion before finalizing it",
        action: MARK_PROMOTION_ACCEPTED_ACTION
      });
      return undefined;
    }
    const decision = await vscode.window.showInformationMessage(
      "Finalize accepted GovKB learning updates? This copies reviewed .governed changes into the active project, marks the promotion applied, and leaves Git uncommitted.",
      "Finalize changes",
      "Open digest"
    );
    if (decision === "Open digest") {
      await openPromotion(current);
      return undefined;
    }
    if (decision !== "Finalize changes") {
      output.appendLine("GovKB: promotion finalization cancelled.");
      return undefined;
    }
    return { projectRoot: selected.projectRoot, promotion: current };
  }

  async function applySelectedPromotionToProject(selected: { projectRoot: string; promotion: PromotionSummary }): Promise<void> {
    try {
      const payload = await applyPromotionToProject(
        settingsFromVscode(),
        selected.projectRoot,
        selected.promotion.runId,
        runner
      );
      latestPromotions = payload.promotions;
      latestPromotionsProjectRoot = selected.projectRoot;
      await refreshStatus(selected.projectRoot, false);
      promotionsProvider.setRows(promotionRows(latestPromotions, latestStatus));
      refreshLearningView();
      output.appendLine(`GovKB: promotion ${selected.promotion.runId} finalized in active project without committing.`);
    } catch (error) {
      await showBlocker(output, {
        title: "GovKB promotion finalization failed",
        action: OPEN_OUTPUT_ACTION,
        detail: errorDetail(error)
      });
    }
  }

  async function runFinalizeAcceptedPromotionCommand(promotion?: PromotionSummary | string): Promise<void> {
    if (commandState.isRunning("finalizeAcceptedPromotion")) {
      await showAlreadyRunning(output, "Finalize Accepted Learning Updates");
      return;
    }
    if (!(await requireTrusted(output))) {
      return;
    }
    const selected = await preparePromotionFinalization(promotion);
    if (!selected) {
      return;
    }
    await runWithProgress(commandState, output, "finalizeAcceptedPromotion", "Finalize Accepted Learning Updates", async () => {
      await applySelectedPromotionToProject(selected);
    });
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
      refreshLearningView();
    } catch (error) {
      latestReports = [];
      reportsProvider.setRows(reportRows([], latestReportRoot));
      refreshLearningView();
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

  async function refreshLearningForProject(projectRoot: string, warnOnFailure = true): Promise<void> {
    try {
      const result = await discoverLearning(settingsFromVscode(), projectRoot, runner);
      if (result.learningInventory) {
        latestLearningInventory = result.learningInventory;
        refreshLearningView();
      }
      if (!result.ok && result.blocker && warnOnFailure) {
        await showBlocker(output, result.blocker);
      }
    } catch (error) {
      if (warnOnFailure) {
        await showBlocker(output, {
          title: "GovKB learning discovery failed",
          action: OPEN_OUTPUT_ACTION,
          detail: errorDetail(error)
        });
      }
    }
  }

  context.subscriptions.push(
    output,
    vscode.window.registerTreeDataProvider("govkb.status", statusProvider),
    vscode.window.registerTreeDataProvider("govkb.capabilities", capabilitiesProvider),
    vscode.window.registerTreeDataProvider("govkb.learning", learningProvider),
    vscode.window.registerTreeDataProvider("govkb.candidates", candidatesProvider),
    vscode.window.registerTreeDataProvider("govkb.promotions", promotionsProvider),
    vscode.window.registerTreeDataProvider("govkb.reports", reportsProvider)
  );

  const runner = createRunner(output);
  const commandState = new CommandRunState();

  context.subscriptions.push(
    vscode.commands.registerCommand("govkb.openOutput", () => output.show(true)),
    vscode.commands.registerCommand("govkb.refreshCapabilities", async () => {
      await runWithProgress(commandState, output, "refreshCapabilities", "Refresh Governed Skills", async (progress) => {
        progress.report({ message: "Refreshing governed skills..." });
        await refreshCapabilitiesForProject();
      });
    }),
    vscode.commands.registerCommand("govkb.openCapability", async (capability?: CapabilitySummary | string) => {
      await openCapability(capability);
    }),
    vscode.commands.registerCommand("govkb.convertSkillToGoverned", async (skill?: string) => {
      await runConvertSkillToGovernedCommand(skill);
    }),
    vscode.commands.registerCommand("govkb.renameGovernedSkill", async (capability?: CapabilitySummary | string) => {
      await runRenameGovernedSkillCommand(capability);
    }),
    vscode.commands.registerCommand("govkb.mergeGovernedSkills", async (capability?: CapabilitySummary | string) => {
      await runMergeGovernedSkillsCommand(capability);
    }),
    vscode.commands.registerCommand("govkb.openReport", async (reportPath?: string) => {
      await openReport(reportPath);
    }),
    vscode.commands.registerCommand("govkb.openCandidate", async (candidate?: CandidateSummary | string) => {
      await openCandidate(candidate);
    }),
    vscode.commands.registerCommand("govkb.openPromotion", async (promotion?: PromotionSummary | string) => {
      await openPromotion(promotion);
    }),
    vscode.commands.registerCommand("govkb.openPromotionWorktree", async (promotion?: PromotionSummary | string) => {
      await openPromotionWorktree(promotion);
    }),
    vscode.commands.registerCommand("govkb.showPromotion", async (promotion?: PromotionSummary | string) => {
      await runWithProgress(commandState, output, "showPromotion", "Show Promotion Details", async () => {
        await showPromotion(promotion);
      });
    }),
    vscode.commands.registerCommand("govkb.markPromotionAccepted", async (promotion?: PromotionSummary | string) => {
      await runWithProgress(commandState, output, "markPromotionAccepted", "Mark Promotion Accepted", async () => {
        if (!(await requireTrusted(output))) {
          return;
        }
        await markSelectedPromotion("accepted", promotion);
      });
    }),
    vscode.commands.registerCommand("govkb.markPromotionRejected", async (promotion?: PromotionSummary | string) => {
      await runWithProgress(commandState, output, "markPromotionRejected", "Mark Promotion Rejected", async () => {
        if (!(await requireTrusted(output))) {
          return;
        }
        await markSelectedPromotion("rejected", promotion);
      });
    }),
    vscode.commands.registerCommand("govkb.archivePromotion", async (promotion?: PromotionSummary | string) => {
      await runWithProgress(commandState, output, "archivePromotion", "Archive Promotion", async () => {
        if (!(await requireTrusted(output))) {
          return;
        }
        await archiveSelectedPromotion(promotion);
      });
    }),
    vscode.commands.registerCommand("govkb.applyPromotionToProject", async (promotion?: PromotionSummary | string) => {
      await runFinalizeAcceptedPromotionCommand(promotion);
    }),
    vscode.commands.registerCommand("govkb.finalizeAcceptedPromotion", async (promotion?: PromotionSummary | string) => {
      await runFinalizeAcceptedPromotionCommand(promotion);
    }),
    vscode.commands.registerCommand("govkb.refreshPromotions", async () => {
      await runWithProgress(commandState, output, "refreshPromotions", "Refresh Promotions", async (progress) => {
        progress.report({ message: "Refreshing promotions..." });
        await refreshPromotionsForProject();
      });
    }),
    vscode.commands.registerCommand("govkb.promoteAuto", async () => {
      await runWithProgress(commandState, output, "promoteAuto", "Auto Promote Learned Updates", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        progress.report({ message: "Creating isolated promotion review..." });
        const result = await runAutoPromote(settingsFromVscode(), projectRoot, runner);
        if (result.promotionsJson) {
          latestPromotions = result.promotionsJson.promotions;
          latestPromotionsProjectRoot = projectRoot;
          promotionsProvider.setRows(promotionRows(latestPromotions, latestStatus));
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
        }
      });
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
    vscode.commands.registerCommand("govkb.discoverLearning", async () => {
      await runWithProgress(commandState, output, "discoverLearning", "Discover Learning Opportunities", async (progress) => {
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        rememberProjectRoot(projectRoot);
        progress.report({ message: "Reading learning inventory..." });
        await refreshLearningForProject(projectRoot);
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
        rememberProjectRoot(projectRoot);
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
        rememberProjectRoot(projectRoot);
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
        rememberProjectRoot(projectRoot);
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
        rememberProjectRoot(projectRoot);
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
        rememberProjectRoot(projectRoot);
        progress.report({ message: "Running bounded dry-run review..." });
        const result = await runLearningReviewBatch(settingsFromVscode(), projectRoot, runner, true, (state) => {
          latestLearningRun = state;
          refreshLearningView();
        });
        if (result.learningRun) {
          latestLearningRun = result.learningRun;
          refreshLearningView();
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
          return;
        }
        progress.report({ message: "Refreshing learning outputs..." });
        await refreshReportsForProject(projectRoot);
        await refreshCandidatesForProject(projectRoot);
        await refreshLearningForProject(projectRoot, false);
      });
    }),
    vscode.commands.registerCommand("govkb.reviewLearningDryRun", async () => {
      await runWithProgress(commandState, output, "reviewLearningDryRun", "Review Learning Dry Run", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        output.show(true);
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        rememberProjectRoot(projectRoot);
        progress.report({ message: "Running bounded dry-run review..." });
        const result = await runLearningReviewBatch(settingsFromVscode(), projectRoot, runner, true, (state) => {
          latestLearningRun = state;
          refreshLearningView();
        });
        if (result.learningRun) {
          latestLearningRun = result.learningRun;
          refreshLearningView();
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
          return;
        }
        progress.report({ message: "Refreshing learning outputs..." });
        await refreshReportsForProject(projectRoot);
        await refreshCandidatesForProject(projectRoot);
        await refreshLearningForProject(projectRoot, false);
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
        rememberProjectRoot(projectRoot);
        progress.report({ message: "Running bounded apply review..." });
        const result = await runLearningReviewBatch(settingsFromVscode(), projectRoot, runner, false, (state) => {
          latestLearningRun = state;
          refreshLearningView();
        });
        if (result.learningRun) {
          latestLearningRun = result.learningRun;
          refreshLearningView();
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
          return;
        }
        progress.report({ message: "Refreshing learning outputs..." });
        await refreshReportsForProject(projectRoot);
        await refreshCandidatesForProject(projectRoot);
        await refreshPromotionsForProject(projectRoot);
        await refreshStatus(projectRoot, false);
        await refreshLearningForProject(projectRoot, false);
      });
    }),
    vscode.commands.registerCommand("govkb.reviewLearningApply", async () => {
      await runWithProgress(commandState, output, "reviewLearningApply", "Review Learning Apply", async (progress) => {
        if (!(await requireTrusted(output))) {
          return;
        }
        output.show(true);
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        rememberProjectRoot(projectRoot);
        progress.report({ message: "Running bounded apply review..." });
        const result = await runLearningReviewBatch(settingsFromVscode(), projectRoot, runner, false, (state) => {
          latestLearningRun = state;
          refreshLearningView();
        });
        if (result.learningRun) {
          latestLearningRun = result.learningRun;
          refreshLearningView();
        }
        if (!result.ok && result.blocker) {
          await showBlocker(output, result.blocker);
          return;
        }
        progress.report({ message: "Refreshing learning outputs..." });
        await refreshReportsForProject(projectRoot);
        await refreshCandidatesForProject(projectRoot);
        await refreshPromotionsForProject(projectRoot);
        await refreshStatus(projectRoot, false);
        await refreshLearningForProject(projectRoot, false);
      });
    }),
    vscode.commands.registerCommand("govkb.listCandidates", async () => {
      await runWithProgress(commandState, output, "listCandidates", "List Candidates", async (progress) => {
        const projectRoot = await selectProjectRoot(output);
        if (!projectRoot) {
          return;
        }
        rememberProjectRoot(projectRoot);
        progress.report({ message: "Refreshing candidates..." });
        await refreshCandidatesForProject(projectRoot);
      });
    })
  );

  statusProvider.setRows(statusRows());
  capabilitiesProvider.setRows(capabilityRows());
  learningProvider.setRows(learningRows());
  candidatesProvider.setRows(candidateRows());
  promotionsProvider.setRows(promotionRows());
  reportsProvider.setRows(reportRows());

  async function refreshProjectSurface(projectRoot: string): Promise<void> {
    const status = await refreshStatus(projectRoot, false);
    if (!status?.project.id) {
      return;
    }
    await refreshCandidatesForProject(projectRoot);
    await refreshPromotionsForProject(projectRoot);
    await refreshReportsForProject(projectRoot);
    await refreshLearningForProject(projectRoot, false);
  }

  async function autoRefreshOnStartup(): Promise<void> {
    const settings = settingsFromVscode();
    if (!settings.autoRefreshOnStartup) {
      return;
    }
    const storedRoot = context.workspaceState.get<string>(LAST_PROJECT_ROOT_KEY);
    const projectRoot = storedProjectRootForWorkspace(vscode.workspace.workspaceFolders, storedRoot);
    if (!projectRoot) {
      return;
    }
    output.appendLine(`GovKB: auto-refreshing ${projectRoot}`);
    await refreshProjectSurface(projectRoot);
  }

  function startMonitoring(): void {
    const intervalSeconds = settingsFromVscode().monitorIntervalSeconds;
    if (!intervalSeconds) {
      return;
    }
    monitor = setInterval(() => {
      const storedRoot = context.workspaceState.get<string>(LAST_PROJECT_ROOT_KEY);
      const projectRoot = latestStatus?.projectRoot ?? storedProjectRootForWorkspace(vscode.workspace.workspaceFolders, storedRoot);
      if (!projectRoot) {
        return;
      }
      output.appendLine(`GovKB: monitoring refresh for ${projectRoot}`);
      void refreshProjectSurface(projectRoot);
    }, intervalSeconds * 1000);
    context.subscriptions.push({
      dispose: () => {
        if (monitor) {
          clearInterval(monitor);
        }
      }
    });
  }

  void autoRefreshOnStartup();
  startMonitoring();
}

export function deactivate(): void {
  // VS Code disposes registered subscriptions.
}
