import test from "node:test";
import assert from "node:assert/strict";
import { candidateRows } from "../../views/candidatesView";
import { capabilityRows } from "../../views/capabilitiesView";
import { learningRows } from "../../views/learningView";
import { promotionRows } from "../../views/promotionsView";
import { reportRows } from "../../views/reportsView";
import { statusRows } from "../../views/statusView";
import { DoctorPayload, StatusPayload } from "../../types";

const status: StatusPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  governedRoot: "/repo/.governed",
  project: { id: "demo-project", currentRelease: "unreleased", gitRevision: "abc", governedDirty: false, governedStatus: [] },
  validation: { status: "ok", warnings: [], errors: [] },
  kbHealth: { warnings: [], suggestedRemediation: null },
  capabilities: [{ id: "project-knowledge-steward", name: "Project Knowledge Steward", governed: true, memoryEnabled: true }],
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

const doctor: DoctorPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  codexHome: "/tmp/codex-home",
  state: "attention",
  project: status.project,
  validation: status.validation,
  installState: status.installState,
  skillUpdates: status.skillUpdates,
  proposalQueue: {
    summary: { proposalCount: 3, groupCount: 2, warningCount: 1, reviewGroupCount: 2, actionFilter: "all", actionCounts: { "inspect-safety": 1, "manual-review": 1 } },
    reviewGroups: [{ id: "group-1", recommendedAction: "inspect-safety", proposalIds: ["p1"], warningCodes: ["weak-verification"] }]
  },
  memoryReview: {
    stateDir: "/tmp/state",
    statePath: "/tmp/state/state.json",
    reportDir: "/tmp/state/reports",
    state: { status: "present", lastRunAt: "2026-05-30T00:00:00Z", lastSuccessfulUpdatedAt: "2026-05-30T00:00:00Z", processedSessionCount: 12, error: null },
    latestRun: { status: "completed", path: "/tmp/state/reports/report.md", runId: "run", counts: { selectedBeforeLimit: 8 }, metadata: { mode: "dry-run" } }
  },
  cron: { status: "installed", scriptPath: "/tmp/codex-home/bin/codex-memory-review", logPath: "/tmp/cron.log", matchingLines: ["0 * * * * codex-memory-review"], error: null },
  recommendations: [{ kind: "proposals", message: "Inspect safety-sensitive staged proposals.", command: "govkb proposals review /repo --action inspect-safety" }]
};

test("statusRows summarize project health", () => {
  const rows = statusRows(status);
  assert.equal(rows[0].label, "demo-project");
  assert.equal(rows[0].description, "ok, 1 governed skill(s)");
  assert.equal(rows[0].icon, "project");
  assert.equal(rows.find((row) => row.label === "Learned updates")?.description, "current");
});

test("statusRows include read-only doctor and proposal queue rows", () => {
  const rows = statusRows(status, doctor);
  assert.equal(rows.find((row) => row.label === "Doctor")?.description, "attention");
  assert.equal(rows.find((row) => row.label === "Proposal queue")?.command?.command, "govkb.reviewProposals");
  assert.equal(rows.find((row) => row.label === "Memory review cron")?.description, "installed");
  assert.equal(rows.find((row) => row.label === "Doctor recommendations")?.description, "1");
});

test("statusRows provide first-open actions", () => {
  const rows = statusRows();
  assert.equal(rows[0].label, "Project status not loaded");
  assert.equal(rows[0].icon, "pulse");
  assert.equal(rows[0].command?.command, "govkb.showStatus");
  assert.equal(rows[1].command?.command, "govkb.oneClickSetup");
});

test("statusRows show apply action when materialized skills are stale", () => {
  const rows = statusRows({
    ...status,
    project: { ...status.project, gitRevision: "def" },
    skillUpdates: { ...status.skillUpdates, state: "apply-available", repoRevision: "def" }
  });
  const learned = rows.find((row) => row.label === "Learned updates");
  assert.equal(learned?.description, "apply available");
  assert.equal(learned?.command?.command, "govkb.oneClickApply");
});

test("statusRows show workspace changes when governed package is dirty", () => {
  const rows = statusRows({
    ...status,
    project: { ...status.project, governedDirty: true, governedStatus: [" M .governed/project.toml"] },
    skillUpdates: { ...status.skillUpdates, state: "workspace-changes", governedDirty: true }
  });
  const learned = rows.find((row) => row.label === "Learned updates");
  assert.equal(learned?.description, "workspace changes");
  assert.equal(learned?.command?.command, "govkb.showStatus");
});

test("statusRows show promotion action when learned memory is pending", () => {
  const rows = statusRows({
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
            reason: "staged: auto promotion skipped active worktree mutation",
            additions: 1,
            repoPath: "/repo/.governed/capabilities/project-knowledge-steward/references/long-term-memory.md",
            localPath: "/tmp/codex-home/skills/govkb-demo-project-project-knowledge-steward/references/long-term-memory.md"
          }
        ]
      }
    }
  });
  const learned = rows.find((row) => row.label === "Learned updates");
  assert.equal(learned?.description, "1 learned update(s)");
  assert.equal(learned?.command?.command, "govkb.promoteAuto");
});

test("capabilityRows summarize capabilities with readable names", () => {
  const rows = capabilityRows([
    {
      id: "project-knowledge-steward",
      name: "Project Knowledge Steward",
      governed: true,
      memoryEnabled: true,
      lifecycleState: "active",
      migrationStatus: null,
      aliases: ["project knowledge steward"],
      description: "Cold-start project knowledge keeper.",
      memoryTargets: [
        {
          name: "main",
          path: "references/long-term-memory.md",
          absolutePath: "/repo/.governed/capabilities/project-knowledge-steward/references/long-term-memory.md",
          sections: ["Stable Workflows"]
        }
      ]
    }
  ]);
  assert.equal(rows[0].label, "Governed skills");
  assert.equal(rows[0].icon, "book");
  assert.equal(rows[1].command?.command, "govkb.convertSkillToGoverned");
  assert.equal(rows[2].label, "Project Knowledge Steward");
  assert.equal(rows[2].description, "project-knowledge-steward, active, memory");
  assert.match(rows[2].tooltip ?? "", /Cold-start project knowledge keeper/);
  assert.match(rows[2].tooltip ?? "", /Memory targets:/);
  assert.equal(rows[2].icon, "symbol-method");
  assert.equal(rows[2].command?.command, "govkb.openCapability");
  assert.equal(rows[2].contextValue, "govkb.capability");
});

test("capabilityRows provide refresh actions before status loads", () => {
  const rows = capabilityRows();
  assert.equal(rows[0].command?.command, "govkb.showStatus");
  assert.equal(rows[1].command?.command, "govkb.convertSkillToGoverned");
});

test("candidateRows summarize candidates", () => {
  const rows = candidateRows([
    {
      id: "backend-workflow",
      status: "ready-for-review",
      occurrences: 2,
      suggestedCapabilityId: "backend-local-stack-workflow",
      activationState: "not-activated",
      path: "/repo/.governed/candidates/backend-workflow"
    }
  ]);
  assert.equal(rows[0].label, "Candidates need triage");
  assert.equal(rows[0].description, "1 staged");
  assert.equal(rows[0].icon, "warning");
  assert.equal(rows[1].label, "Review candidate: backend-local-stack-workflow");
  assert.equal(rows[1].description, "ready-for-review, 2 occurrences");
  assert.equal(rows[1].command?.command, "govkb.openCandidate");
});

test("candidateRows provide discovery action when empty", () => {
  const rows = candidateRows([]);
  assert.equal(rows[0].label, "No new skill candidates");
  assert.equal(rows[0].command, undefined);
});

test("reportRows summarize report counts", () => {
  const rows = reportRows([
    {
      path: "/tmp/report.md",
      classifier: { model: "gpt-5.4-mini", reasoning: "low" },
      sessions: { failed: 1, deferred: 0, learned: 0, stagedCandidates: 0 },
      containsRawTranscript: false
    }
  ]);
  assert.equal(rows[0].description, "learned 0, failed 1, deferred 0, candidates 0");
  assert.equal(rows[0].icon, "warning");
  assert.equal(rows[0].command?.command, "govkb.openReport");
  assert.equal(rows[0].contextValue, "govkb.report");
});

test("reportRows provide refresh actions before reports load", () => {
  const rows = reportRows();
  assert.equal(rows[0].command?.command, "govkb.refreshReports");
  assert.equal(rows[1].command?.command, "govkb.reviewLearningDryRun");
});

test("learningRows show discovery action before inventory loads", () => {
  const rows = learningRows({ status });
  assert.equal(rows[0].label, "Learning");
  assert.equal(rows[0].icon, "lightbulb");
  assert.equal(rows[1].command?.command, "govkb.discoverLearning");
});

test("learningRows separate existing updates from candidates", () => {
  const rows = learningRows({
    status: {
      ...status,
      skillUpdates: {
        ...status.skillUpdates,
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
    inventory: {
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
    },
    candidates: []
  });
  assert.equal(rows.find((row) => row.label === "Promote learned updates")?.description, "1 pending");
  assert.equal(rows.find((row) => row.label === "New skill candidates")?.description, "none");
});

test("learningRows promote accepted promotion apply as next step", () => {
  const rows = learningRows({
    status,
    promotions: [
      {
        runId: "run-2",
        branch: "codex/govkb-auto-promote/demo-project/run-2",
        head: "abc123",
        worktreeRoot: "/tmp/worktree-2",
        digestPath: "/tmp/worktree-2/.governed/reports/promotions/latest-promotion-digest.md",
        reportPaths: [],
        status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
        state: "ready-for-review",
        metadataPath: "/tmp/promotions/run-2.json",
        review: null,
        archive: null
      },
      {
        runId: "run-1",
        branch: "codex/govkb-auto-promote/demo-project/run-1",
        head: "abc123",
        worktreeRoot: "/tmp/worktree-1",
        digestPath: "/tmp/worktree-1/.governed/reports/promotions/latest-promotion-digest.md",
        reportPaths: [],
        status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
        state: "accepted",
        metadataPath: "/tmp/promotions/run-1.json",
        review: { decision: "accepted", reason: "Reviewed." },
        archive: null
      }
    ]
  });
  const applyRow = rows.find((row) => row.label === "Next: finalize accepted learning updates");
  assert.equal(applyRow?.command?.command, "govkb.finalizeAcceptedPromotion");
  assert.match(applyRow?.description ?? "", /skill file/);
  const reviewRow = rows.find((row) => row.label === "Learning review");
  assert.match(reviewRow?.description ?? "", /duplicate worktree/);
});

test("promotionRows summarize promotion lifecycle state", () => {
  const rows = promotionRows([
    {
      runId: "run-1",
      branch: "codex/govkb-auto-promote/demo-project/run-1",
      head: "abc123",
      worktreeRoot: "/tmp/worktree",
      digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
      state: "ready-for-review",
      metadataPath: "/tmp/promotions/run-1.json",
      review: null,
      archive: null
    }
  ]);
  assert.equal(rows[0].label, "1. Open learning review");
  assert.equal(rows[0].description, "1 skill file ready");
  assert.equal(rows[0].icon, "eye");
  assert.equal(rows[0].command?.command, "govkb.openPromotion");
  assert.equal(rows[0].contextValue, "govkb.promotion.ready");
  assert.equal(rows[1].label, "2. Accept reviewed updates");
  assert.equal(rows[1].command?.command, "govkb.markPromotionAccepted");
  assert.equal(rows[2].label, "Reject this review");
  assert.equal(rows[2].command?.command, "govkb.markPromotionRejected");
});

test("promotionRows show accepted promotions as ready to finalize", () => {
  const rows = promotionRows([
    {
      runId: "run-1",
      branch: "codex/govkb-auto-promote/demo-project/run-1",
      head: "abc123",
      worktreeRoot: "/tmp/worktree",
      digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
      state: "accepted",
      metadataPath: "/tmp/promotions/run-1.json",
      review: { decision: "accepted", reason: "Reviewed." },
      archive: null
    }
  ]);
  assert.equal(rows[0].label, "Next: finalize accepted learning updates");
  assert.match(rows[0].description ?? "", /applies without commit/);
  assert.equal(rows[0].icon, "git-merge");
  assert.equal(rows[0].command?.command, "govkb.finalizeAcceptedPromotion");
  assert.equal(rows[0].contextValue, "govkb.promotion.accepted");
});

test("promotionRows show applied promotions as pending commit", () => {
  const promotion = {
    runId: "run-1",
    branch: "codex/govkb-auto-promote/demo-project/run-1",
    head: "abc123",
    worktreeRoot: "/tmp/worktree",
    digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
    reportPaths: [],
    status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
    state: "applied",
    metadataPath: "/tmp/promotions/run-1.json",
    review: { decision: "accepted", reason: "Reviewed." },
    archive: null,
    apply: {
      appliedAt: "2026-05-12T19:00:00Z",
      projectRoot: "/repo",
      files: [".governed/capabilities/workflow-review/references/long-term-memory.md"]
    }
  };
  const rows = promotionRows([promotion], {
    ...status,
    project: {
      ...status.project,
      governedDirty: true,
      governedStatus: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"]
    },
    skillUpdates: { ...status.skillUpdates, state: "workspace-changes", governedDirty: true }
  });
  assert.equal(rows[0].label, "Next: commit governed changes");
  assert.match(rows[0].description ?? "", /pending commit/);
  assert.equal(rows[0].contextValue, "govkb.promotion.applied");
});

test("promotionRows show committed applied promotions as finalized", () => {
  const rows = promotionRows(
    [
      {
        runId: "run-1",
        branch: "codex/govkb-auto-promote/demo-project/run-1",
        head: "abc123",
        worktreeRoot: "/tmp/worktree",
        digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
        reportPaths: [],
        status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
        state: "applied",
        metadataPath: "/tmp/promotions/run-1.json",
        review: { decision: "accepted", reason: "Reviewed." },
        archive: null,
        apply: {
          appliedAt: "2026-05-12T19:00:00Z",
          projectRoot: "/repo",
          files: [".governed/capabilities/workflow-review/references/long-term-memory.md"]
        }
      }
    ],
    status
  );
  assert.equal(rows[0].label, "Learning updates finalized");
  assert.match(rows[0].description ?? "", /finalized/);
  assert.equal(rows[0].contextValue, "govkb.promotion.applied");
});

test("learningRows skip commit step after applied promotion is committed", () => {
  const rows = learningRows({
    status,
    promotions: [
      {
        runId: "run-1",
        branch: "codex/govkb-auto-promote/demo-project/run-1",
        head: "abc123",
        worktreeRoot: "/tmp/worktree",
        digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
        reportPaths: [],
        status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
        state: "applied",
        metadataPath: "/tmp/promotions/run-1.json",
        review: { decision: "accepted", reason: "Reviewed." },
        archive: null,
        apply: {
          appliedAt: "2026-05-12T19:00:00Z",
          projectRoot: "/repo",
          files: [".governed/capabilities/workflow-review/references/long-term-memory.md"]
        }
      }
    ]
  });
  assert.equal(rows.find((row) => row.label === "Next: commit governed updates"), undefined);
  assert.equal(rows[1].label, "Next: review another session batch");
  assert.equal(rows.find((row) => row.label === "Learning review")?.description, "finalized");
});

test("promotionRows keep applied promotions finalized when unrelated governed files are dirty", () => {
  const rows = promotionRows([
    {
      runId: "run-1",
      branch: "codex/govkb-auto-promote/demo-project/run-1",
      head: "abc123",
      worktreeRoot: "/tmp/worktree",
      digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
      state: "applied",
      metadataPath: "/tmp/promotions/run-1.json",
      review: { decision: "accepted", reason: "Reviewed." },
      archive: null,
      apply: {
        appliedAt: "2026-05-12T19:00:00Z",
        projectRoot: "/repo",
        files: [".governed/capabilities/workflow-review/references/long-term-memory.md"]
      }
    }
  ], {
    ...status,
    project: {
      ...status.project,
      governedDirty: true,
      governedStatus: ["?? .governed/candidates/new-skill/"]
    },
    skillUpdates: { ...status.skillUpdates, state: "workspace-changes", governedDirty: true }
  });
  assert.equal(rows[0].label, "Learning updates finalized");
  assert.match(rows[0].description ?? "", /finalized/);
});

test("promotionRows collapse equivalent promotion worktrees", () => {
  const rows = promotionRows([
    {
      runId: "run-2",
      branch: "codex/govkb-auto-promote/demo-project/run-2",
      head: "abc123",
      worktreeRoot: "/tmp/worktree-2",
      digestPath: "/tmp/worktree-2/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
      state: "ready-for-review",
      metadataPath: "/tmp/promotions/run-2.json",
      review: null,
      archive: null
    },
    {
      runId: "run-1",
      branch: "codex/govkb-auto-promote/demo-project/run-1",
      head: "abc123",
      worktreeRoot: "/tmp/worktree-1",
      digestPath: "/tmp/worktree-1/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
      state: "accepted",
      metadataPath: "/tmp/promotions/run-1.json",
      review: { decision: "accepted", reason: "Reviewed." },
      archive: null
    }
  ]);
  assert.equal(rows[0].label, "Next: finalize accepted learning updates");
  assert.match(rows[0].description ?? "", /1 duplicate hidden/);
  assert.equal(rows[1].label, "Duplicate review worktrees");
});

test("promotionRows provide refresh and auto-promote actions before load", () => {
  const rows = promotionRows();
  assert.equal(rows[0].command?.command, "govkb.refreshPromotions");
  assert.equal(rows[1].command?.command, "govkb.promoteAuto");
});
