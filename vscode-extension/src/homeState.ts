import { actionDefinition, GovkbActionId } from "./actionRegistry";
import {
  CandidateSummary,
  LearningInventoryPayload,
  LearningRunState,
  PromotionSummary,
  ReportSummary,
  StatusPayload
} from "./types";
import { changedSkillCount, isPromotionPendingCommit, promotionGroups } from "./views/promotionsView";

export type HomeActionId = GovkbActionId;

export interface HomeAction {
  id: HomeActionId;
  label: string;
  description: string;
  reason?: string;
  consequence?: string;
  command: string;
  icon: string;
  arguments?: unknown[];
}

export interface HomeBadge {
  label: string;
  value: string;
  tone: "normal" | "success" | "warning" | "error";
}

export interface HomeSection {
  id: string;
  title: string;
  description: string;
  actions: HomeAction[];
}

export interface HomeModelInput {
  status?: StatusPayload;
  inventory?: LearningInventoryPayload;
  run?: LearningRunState;
  reports?: ReportSummary[];
  candidates?: CandidateSummary[];
  promotions?: PromotionSummary[];
}

export interface HomeModel {
  title: string;
  subtitle: string;
  primaryAction: HomeAction;
  badges: HomeBadge[];
  sections: HomeSection[];
}

function action(
  id: HomeActionId,
  overrides: Partial<Pick<HomeAction, "label" | "description" | "reason" | "consequence" | "command" | "icon" | "arguments">> = {}
): HomeAction {
  const definition = actionDefinition(id);
  return {
    id,
    label: overrides.label ?? definition.label,
    description: overrides.description ?? definition.description,
    reason: overrides.reason,
    consequence: overrides.consequence,
    command: overrides.command ?? definition.command,
    icon: overrides.icon ?? definition.icon,
    arguments: overrides.arguments
  };
}

function latestActionablePromotion(promotions?: PromotionSummary[]): PromotionSummary | undefined {
  return promotions && promotions.length > 0 ? promotionGroups(promotions)[0]?.promotion : undefined;
}

function primaryAction(input: HomeModelInput): HomeAction {
  const { status, inventory, promotions, run } = input;
  const promotion = latestActionablePromotion(promotions);

  if (!status) {
    return action("setup", {
      reason: "GovKB has not loaded a governed project for this workspace yet.",
      consequence: "Runs the guided setup flow, then refreshes project status."
    });
  }
  if (status.installState.codex.status === "missing" || status.skillUpdates.state === "not-applied") {
    return action("apply", {
      reason: "Codex skills for this project are not installed in the configured Codex home.",
      consequence: "Materializes governed packages from `.governed` into local Codex skills without committing repo files."
    });
  }
  if (status.skillUpdates.state === "apply-available") {
    return action("apply", {
      label: "Apply governed skills",
      description: "Repo governed skills changed since the last Codex install.",
      reason: "The repository revision and the materialized Codex skill revision differ.",
      consequence: "Updates local Codex skills from `.governed`; it does not change or commit the project repository."
    });
  }
  if (promotion?.state === "ready-for-review") {
    return action("openPromotion", {
      label: "Review learning digest",
      description: `${changedSkillCount(promotion)} changed skill file(s).`,
      reason: "A learning review is ready and needs a human decision before it can affect governed source.",
      consequence: "Opens the digest for review; accepting or rejecting remains a separate explicit action.",
      arguments: [promotion]
    });
  }
  if (promotion?.state === "accepted") {
    return action(
      "finalizePromotion", {
        label: "Finalize accepted updates",
        description: "Copy reviewed governed updates into the active project without committing.",
        reason: "The digest was accepted, but its changes are still isolated from the active `.governed` package.",
        consequence: "Applies accepted updates into `.governed`; you still review and commit the repo changes normally.",
        arguments: [promotion]
      }
    );
  }
  if (promotion?.state === "applied" && isPromotionPendingCommit(promotion, status)) {
    return action(
      "reviewWorkspaceChanges", {
        label: "Commit governed updates",
        description: "A finalized promotion changed .governed files that still need normal Git review.",
        reason: "Accepted updates are already applied into `.governed`, but Git has not recorded them yet.",
        consequence: "Opens the project status handoff so you can review and commit through the normal Git workflow.",
        icon: "repo-commit"
      }
    );
  }
  if (run?.dryRun && run.summary && (run.summary.existingSkillUpdates > 0 || run.summary.stagedCandidates > 0 || run.summary.staged > 0)) {
    return action(
      "reviewLearningApply", {
        label: "Apply reviewed learning",
        description: `${run.summary.existingSkillUpdates} existing update(s), ${run.summary.stagedCandidates} candidate(s).`,
        reason: "The latest preview found useful governed-memory updates or candidate skills.",
        consequence: "Runs the apply review path so accepted local learning can become a reviewable promotion."
      }
    );
  }
  if (status.skillUpdates.pendingLocalMemory.available) {
    return action(
      "createReviewWorktree", {
        description: `${status.skillUpdates.pendingLocalMemory.pendingCount} learned update(s) need review.`,
        reason: "Local Codex skills contain learned memory that is not yet in governed source.",
        consequence: "Creates an isolated promotion worktree and digest for human review."
      }
    );
  }
  if (status.skillUpdates.state === "workspace-changes") {
    return action(
      "reviewWorkspaceChanges", {
        description: "The active project has uncommitted .governed changes.",
        reason: "GovKB sees workspace changes under the governed package.",
        consequence: "Refreshes status so you can inspect the exact files before continuing."
      }
    );
  }
  if (inventory && inventory.sessions.selectedForReview > 0) {
    return action(
      "reviewLearningDryRun", {
        label: "Review learning updates",
        description: `${inventory.sessions.selectedForReview} of ${inventory.sessions.selectedBeforeLimit} sessions selected for preview.`,
        reason: "GovKB found reviewable sessions that may contain reusable learning.",
        consequence: "Runs a bounded preview review and writes a report; no governed memory is applied by this click."
      }
    );
  }
  return action(
    "discoverLearning", {
      label: "Discover learning opportunities",
      description: "Load the next reviewable session batch and memory targets.",
      reason: "Learning inventory has not been loaded for this project state.",
      consequence: "Runs read-only discovery so Home can decide whether a review is useful."
    }
  );
}

function projectBadges(input: HomeModelInput): HomeBadge[] {
  const { status, inventory, candidates, promotions } = input;
  const promotion = latestActionablePromotion(promotions);
  return [
    {
      label: "Project",
      value: status?.project.id ?? "not loaded",
      tone: status ? "normal" : "warning"
    },
    {
      label: "Validation",
      value: status?.validation.status ?? "unknown",
      tone: status?.validation.status === "ok" ? "success" : "warning"
    },
    {
      label: "Codex skills",
      value: status?.skillUpdates.state ?? "unknown",
      tone: status?.skillUpdates.state === "current" ? "success" : "warning"
    },
    {
      label: "Learning",
      value: inventory ? `${inventory.sessions.selectedBeforeLimit} available` : "not discovered",
      tone: inventory ? "normal" : "warning"
    },
    {
      label: "Candidates",
      value: `${candidates?.length ?? 0}`,
      tone: candidates && candidates.length > 0 ? "warning" : "success"
    },
    {
      label: "Promotion",
      value: promotion?.state ?? "none",
      tone: promotion && promotion.state !== "applied" ? "warning" : "normal"
    }
  ];
}

function workflowSections(input: HomeModelInput): HomeSection[] {
  const { status, inventory, reports, candidates, promotions, run } = input;
  const promotion = latestActionablePromotion(promotions);
  const latestReport = reports?.[0];
  const sections: HomeSection[] = [];

  sections.push({
    id: "learning",
    title: "Learning",
    description: run?.active
      ? "Review is running."
      : inventory
        ? `${inventory.sessions.selectedForReview} selected, ${inventory.sessions.selectedBeforeLimit} available.`
        : "Inventory has not been loaded.",
    actions: [
      action("discoverLearning"),
      action("reviewLearningDryRun", {
        label: "Preview review",
        description: "Classify a bounded batch without applying memory."
      }),
      action("reviewLearningApply", {
        label: "Apply review",
        description: "Run the approved learning review path."
      })
    ]
  });

  if (promotion) {
    const actions: HomeAction[] = [
      action("openPromotion", { arguments: [promotion] })
    ];
    if (promotion.state === "ready-for-review") {
      actions.push(
        action("acceptPromotion", { arguments: [promotion] }),
        action("rejectPromotion", { arguments: [promotion] })
      );
    }
    if (promotion.state === "accepted") {
      actions.unshift(
        action("finalizePromotion", { arguments: [promotion] })
      );
    }
    sections.push({
      id: "promotion",
      title: "Promotion Review",
      description: `${promotion.state}, ${changedSkillCount(promotion)} changed skill file(s).`,
      actions
    });
  }

  sections.push({
    id: "skills",
    title: "Governed Skills",
    description: status ? `${status.capabilities.length} governed skill(s).` : "Status not loaded.",
    actions: [
      action("openCapability"),
      action("convertSkill"),
      action("renameSkill"),
      action("mergeSkills")
    ]
  });

  sections.push({
    id: "reports",
    title: "Reports",
    description: latestReport
      ? `${latestReport.sessions.learned} learned, ${latestReport.sessions.failed} failed, ${latestReport.sessions.deferred} deferred.`
      : "No latest report loaded.",
    actions: [
      action("openLatestReport"),
      action("refreshReports"),
      action("openOutput")
    ]
  });

  if (candidates && candidates.length > 0) {
    sections.push({
      id: "candidates",
      title: "New Skill Candidates",
      description: `${candidates.length} candidate(s) need triage.`,
      actions: [
        action("openCandidates")
      ]
    });
  }

  return sections;
}

export function buildHomeModel(input: HomeModelInput = {}): HomeModel {
  const status = input.status;
  return {
    title: "GovKB Home",
    subtitle: status?.project.id ? `${status.project.id} - guided daily workflow` : "Select or set up a governed project.",
    primaryAction: primaryAction(input),
    badges: projectBadges(input),
    sections: workflowSections(input)
  };
}
