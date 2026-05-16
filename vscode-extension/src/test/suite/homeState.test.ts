import test from "node:test";
import assert from "node:assert/strict";
import { buildHomeModel } from "../../homeState";
import { LearningInventoryPayload, LearningRunState, PromotionSummary, StatusPayload } from "../../types";

const status: StatusPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  governedRoot: "/repo/.governed",
  project: { id: "demo-project", currentRelease: "unreleased", gitRevision: "abc", governedDirty: false, governedStatus: [] },
  validation: { status: "ok", warnings: [], errors: [] },
  kbHealth: { warnings: [], suggestedRemediation: null },
  capabilities: [{ id: "project-knowledge-steward", name: "Project Knowledge Steward", governed: true }],
  adapters: ["codex"],
  releases: [],
  installState: {
    codex: {
      status: "present",
      statePath: "/tmp/state.json",
      appliedRevision: "abc",
      appliedRelease: "unreleased",
      appliedAt: null,
      materializedCapabilities: []
    }
  },
  skillUpdates: {
    state: "current",
    repoRevision: "abc",
    appliedRevision: "abc",
    governedDirty: false,
    pendingLocalMemory: {
      available: false,
      safePromotionCount: 0,
      rejectedCount: 0,
      pendingCount: 0,
      items: []
    }
  }
};

const inventory: LearningInventoryPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  codexHome: "/tmp/codex-home",
  lookbackDays: 90,
  maxSessions: 5,
  sessions: {
    totalDiscovered: 12,
    selectedForReview: 5,
    selectedBeforeLimit: 8,
    selectedIndexed: 4,
    selectedFileOnly: 1,
    alreadyProcessed: 3,
    indexedRows: 10,
    indexedMissingFiles: 1,
    fileOnlyRecentUnprocessed: 2
  },
  selectedSessions: [],
  memoryTargets: [],
  recommendedBatch: { lookbackDays: 90, maxSessions: 5, dryRun: true, reason: "Review a bounded batch." }
};

function promotion(state: string): PromotionSummary {
  return {
    runId: `run-${state}`,
    branch: "codex/govkb-auto-promote/demo/run",
    head: "abc",
    worktreeRoot: "/tmp/worktree",
    digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
    reportPaths: [],
    status: [" M .governed/capabilities/project-knowledge-steward/references/long-term-memory.md"],
    state,
    metadataPath: "/tmp/meta.json",
    review: state === "accepted" ? { decision: "accepted", reason: "Looks good." } : null,
    archive: null,
    apply:
      state === "applied"
        ? { appliedAt: "2026-05-16T00:00:00Z", projectRoot: "/repo", files: [".governed/capabilities/project-knowledge-steward/references/long-term-memory.md"] }
        : null
  };
}

test("buildHomeModel guides setup before status is loaded", () => {
  const model = buildHomeModel();
  assert.equal(model.primaryAction.id, "setup");
  assert.equal(model.primaryAction.command, "govkb.oneClickSetup");
  assert.equal(model.badges.find((badge) => badge.label === "Project")?.value, "not loaded");
});

test("buildHomeModel guides apply when materialized skills are stale", () => {
  const model = buildHomeModel({
    status: {
      ...status,
      skillUpdates: { ...status.skillUpdates, state: "apply-available", repoRevision: "def" }
    }
  });
  assert.equal(model.primaryAction.id, "apply");
  assert.equal(model.primaryAction.command, "govkb.oneClickApply");
});

test("buildHomeModel prioritizes promotion review before another batch", () => {
  const model = buildHomeModel({ status, inventory, promotions: [promotion("ready-for-review")] });
  assert.equal(model.primaryAction.id, "openPromotion");
  assert.equal(model.primaryAction.command, "govkb.openPromotion");
  assert.equal(model.sections.find((section) => section.id === "promotion")?.title, "Promotion Review");
});

test("buildHomeModel prioritizes finalizing accepted promotions", () => {
  const model = buildHomeModel({ status, inventory, promotions: [promotion("accepted")] });
  assert.equal(model.primaryAction.id, "finalizePromotion");
  assert.equal(model.primaryAction.command, "govkb.finalizeAcceptedPromotion");
});

test("buildHomeModel detects applied promotions that still need commit", () => {
  const model = buildHomeModel({
    status: {
      ...status,
      project: {
        ...status.project,
        governedDirty: true,
        governedStatus: [" M .governed/capabilities/project-knowledge-steward/references/long-term-memory.md"]
      }
    },
    promotions: [promotion("applied")]
  });
  assert.equal(model.primaryAction.id, "reviewWorkspaceChanges");
  assert.equal(model.primaryAction.label, "Commit governed updates");
});

test("buildHomeModel guides local memory promotion before ordinary review", () => {
  const model = buildHomeModel({
    status: {
      ...status,
      skillUpdates: {
        ...status.skillUpdates,
        state: "learned-updates",
        pendingLocalMemory: {
          available: true,
          safePromotionCount: 1,
          rejectedCount: 0,
          pendingCount: 1,
          items: [
            {
              capabilityId: "project-knowledge-steward",
              reason: "staged: review",
              additions: 1,
              repoPath: "/repo/.governed/capabilities/project-knowledge-steward/references/long-term-memory.md",
              localPath: "/tmp/codex-home/skills/govkb-demo-project-project-knowledge-steward/references/long-term-memory.md"
            }
          ]
        }
      }
    },
    inventory
  });
  assert.equal(model.primaryAction.id, "createReviewWorktree");
  assert.equal(model.primaryAction.command, "govkb.promoteAuto");
});

test("buildHomeModel guides another dry-run when project is current and inventory is loaded", () => {
  const model = buildHomeModel({ status, inventory });
  assert.equal(model.primaryAction.id, "reviewLearningDryRun");
  assert.equal(model.primaryAction.command, "govkb.reviewLearningDryRun");
  assert.equal(model.badges.find((badge) => badge.label === "Learning")?.value, "8 available");
});

test("buildHomeModel guides apply after a productive dry run", () => {
  const run: LearningRunState = {
    active: false,
    dryRun: true,
    sessions: [],
    artifacts: [],
    summary: {
      reviewed: 5,
      skipped: 0,
      deferred: 0,
      failed: 0,
      applied: 3,
      staged: 1,
      rejected: 0,
      existingSkillUpdates: 2,
      stagedCandidates: 1
    }
  };
  const model = buildHomeModel({ status, inventory, run });
  assert.equal(model.primaryAction.id, "reviewLearningApply");
  assert.equal(model.primaryAction.command, "govkb.reviewLearningApply");
});
