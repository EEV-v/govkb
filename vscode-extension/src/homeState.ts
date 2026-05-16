import {
  CandidateSummary,
  LearningInventoryPayload,
  LearningRunState,
  PromotionSummary,
  ReportSummary,
  StatusPayload
} from "./types";
import { changedSkillCount, isPromotionPendingCommit, promotionGroups } from "./views/promotionsView";

export type HomeActionId =
  | "setup"
  | "apply"
  | "discoverLearning"
  | "reviewLearningDryRun"
  | "reviewLearningApply"
  | "createReviewWorktree"
  | "openPromotion"
  | "acceptPromotion"
  | "rejectPromotion"
  | "finalizePromotion"
  | "reviewWorkspaceChanges"
  | "openCapability"
  | "convertSkill"
  | "renameSkill"
  | "mergeSkills"
  | "openCandidates"
  | "openLatestReport"
  | "refreshReports"
  | "openOutput";

export interface HomeAction {
  id: HomeActionId;
  label: string;
  description: string;
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

function action(id: HomeActionId, label: string, description: string, command: string, icon: string, args?: unknown[]): HomeAction {
  return {
    id,
    label,
    description,
    command,
    icon,
    arguments: args
  };
}

function latestActionablePromotion(promotions?: PromotionSummary[]): PromotionSummary | undefined {
  return promotions && promotions.length > 0 ? promotionGroups(promotions)[0]?.promotion : undefined;
}

function primaryAction(input: HomeModelInput): HomeAction {
  const { status, inventory, promotions, run } = input;
  const promotion = latestActionablePromotion(promotions);

  if (!status) {
    return action("setup", "Set up GovKB", "Initialize or select a governed project.", "govkb.oneClickSetup", "rocket");
  }
  if (status.installState.codex.status === "missing" || status.skillUpdates.state === "not-applied") {
    return action("apply", "Apply governed skills", "Materialize governed skills into the configured Codex home.", "govkb.oneClickApply", "cloud-upload");
  }
  if (status.skillUpdates.state === "apply-available") {
    return action("apply", "Apply latest governed skills", "Repo and Codex materialized revisions differ.", "govkb.oneClickApply", "cloud-upload");
  }
  if (promotion?.state === "ready-for-review") {
    return action("openPromotion", "Review learning digest", `${changedSkillCount(promotion)} changed skill file(s).`, "govkb.openPromotion", "eye", [
      promotion
    ]);
  }
  if (promotion?.state === "accepted") {
    return action(
      "finalizePromotion",
      "Finalize accepted updates",
      "Copy reviewed governed updates into the active project without committing.",
      "govkb.finalizeAcceptedPromotion",
      "git-merge",
      [promotion]
    );
  }
  if (promotion?.state === "applied" && isPromotionPendingCommit(promotion, status)) {
    return action(
      "reviewWorkspaceChanges",
      "Commit governed updates",
      "A finalized promotion changed .governed files that still need normal Git review.",
      "govkb.showStatus",
      "repo-commit"
    );
  }
  if (run?.dryRun && run.summary && (run.summary.existingSkillUpdates > 0 || run.summary.stagedCandidates > 0 || run.summary.staged > 0)) {
    return action(
      "reviewLearningApply",
      "Apply reviewed learning",
      `${run.summary.existingSkillUpdates} existing update(s), ${run.summary.stagedCandidates} candidate(s).`,
      "govkb.reviewLearningApply",
      "play"
    );
  }
  if (status.skillUpdates.pendingLocalMemory.available) {
    return action(
      "createReviewWorktree",
      "Create learning review",
      `${status.skillUpdates.pendingLocalMemory.pendingCount} learned update(s) need review.`,
      "govkb.promoteAuto",
      "git-pull-request-create"
    );
  }
  if (status.skillUpdates.state === "workspace-changes") {
    return action(
      "reviewWorkspaceChanges",
      "Review governed workspace changes",
      "The active project has uncommitted .governed changes.",
      "govkb.showStatus",
      "diff"
    );
  }
  if (inventory && inventory.sessions.selectedForReview > 0) {
    return action(
      "reviewLearningDryRun",
      "Review next learning batch",
      `${inventory.sessions.selectedForReview} of ${inventory.sessions.selectedBeforeLimit} sessions selected.`,
      "govkb.reviewLearningDryRun",
      "debug-alt"
    );
  }
  return action(
    "discoverLearning",
    "Discover learning opportunities",
    "Load the next reviewable session batch and memory targets.",
    "govkb.discoverLearning",
    "search"
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
      action("discoverLearning", "Discover", "Refresh learning inventory.", "govkb.discoverLearning", "search"),
      action("reviewLearningDryRun", "Dry run", "Review a bounded batch without applying memory.", "govkb.reviewLearningDryRun", "debug-alt"),
      action("reviewLearningApply", "Apply", "Apply a bounded learning review through the CLI.", "govkb.reviewLearningApply", "play")
    ]
  });

  if (promotion) {
    const actions: HomeAction[] = [
      action("openPromotion", "Open digest", "Inspect reviewed governed changes.", "govkb.openPromotion", "eye", [promotion])
    ];
    if (promotion.state === "ready-for-review") {
      actions.push(
        action("acceptPromotion", "Accept", "Mark this learning review accepted after inspecting the digest.", "govkb.markPromotionAccepted", "pass", [
          promotion
        ]),
        action("rejectPromotion", "Reject", "Reject this learning review with a reason.", "govkb.markPromotionRejected", "error", [promotion])
      );
    }
    if (promotion.state === "accepted") {
      actions.unshift(
        action("finalizePromotion", "Finalize", "Apply accepted changes into the active project.", "govkb.finalizeAcceptedPromotion", "git-merge", [
          promotion
        ])
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
      action("openCapability", "Open skill", "Choose and inspect a governed skill package.", "govkb.openCapability", "go-to-file"),
      action("convertSkill", "Convert skill", "Convert one selected local Codex skill into governed source.", "govkb.convertSkillToGoverned", "new-folder"),
      action("renameSkill", "Rename", "Rename one governed skill package.", "govkb.renameGovernedSkill", "edit"),
      action("mergeSkills", "Merge", "Merge one governed skill into another.", "govkb.mergeGovernedSkills", "git-merge")
    ]
  });

  sections.push({
    id: "reports",
    title: "Reports",
    description: latestReport
      ? `${latestReport.sessions.learned} learned, ${latestReport.sessions.failed} failed, ${latestReport.sessions.deferred} deferred.`
      : "No latest report loaded.",
    actions: [
      action("openLatestReport", "Open latest", "Inspect the newest learning review report.", "govkb.openLatestReport", "go-to-file"),
      action("refreshReports", "Refresh", "Reload learning review reports.", "govkb.refreshReports", "refresh"),
      action("openOutput", "Open output", "Show full GovKB command output.", "govkb.openOutput", "output")
    ]
  });

  if (candidates && candidates.length > 0) {
    sections.push({
      id: "candidates",
      title: "New Skill Candidates",
      description: `${candidates.length} candidate(s) need triage.`,
      actions: [
        action("openCandidates", "Open candidates", "Review staged candidate packages.", "govkb.listCandidates", "list-tree")
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
