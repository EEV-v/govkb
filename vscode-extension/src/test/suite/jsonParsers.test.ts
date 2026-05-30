import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  parseCandidatesPayload,
  parseConversionPayload,
  parseDoctorPayload,
  parseLearningInventoryPayload,
  parsePromotionCleanupPayload,
  parsePromotionsPayload,
  parseProposalReviewPayload,
  parseReportSummaryPayload,
  parseStatusPayload
} from "../../jsonParsers";

function fixture(name: string): string {
  return readFileSync(join(process.cwd(), "src", "test", "fixtures", name), "utf8");
}

test("parseStatusPayload accepts fixture contract", () => {
  const payload = parseStatusPayload(fixture("status.sample.json"));
  assert.equal(payload.project.id, "demo-project");
  assert.equal(payload.project.governedDirty, false);
  assert.equal(payload.installState.codex.status, "missing");
  assert.equal(payload.skillUpdates.state, "not-applied");
});

test("parseDoctorPayload accepts health and proposal summary contract", () => {
  const payload = parseDoctorPayload(
    JSON.stringify({
      schemaVersion: 1,
      projectRoot: "/repo",
      codexHome: "/tmp/codex-home",
      state: "attention",
      project: { id: "demo-project", currentRelease: "unreleased", gitRevision: "abc" },
      validation: { status: "ok", warnings: [], errors: [] },
      installState: { codex: { status: "present", statePath: "/tmp/state.json", appliedRevision: "abc", appliedRelease: null, appliedAt: null, materializedCapabilities: [] } },
      skillUpdates: { state: "current", repoRevision: "abc", appliedRevision: "abc", governedDirty: false, pendingLocalMemory: { available: false, safePromotionCount: 0, rejectedCount: 0, pendingCount: 0, items: [] } },
      proposalQueue: {
        summary: { proposalCount: 2, groupCount: 1, warningCount: 1, reviewGroupCount: 1, actionFilter: "all", actionCounts: { "inspect-safety": 1 } },
        reviewGroups: [{ id: "group-1", recommendedAction: "inspect-safety", proposalIds: ["p1", "p2"], warningCodes: ["weak-verification"] }]
      },
      memoryReview: {
        stateDir: "/tmp/state",
        statePath: "/tmp/state/state.json",
        reportDir: "/tmp/state/reports",
        state: { status: "present", lastRunAt: "2026-05-30T00:00:00Z", lastSuccessfulUpdatedAt: "2026-05-30T00:00:00Z", processedSessionCount: 12, error: null },
        latestRun: { status: "completed", path: "/tmp/state/reports/report.md", runId: "run", counts: { sessionsProcessed: 5 }, metadata: { mode: "dry-run" } }
      },
      cron: { status: "installed", scriptPath: "/tmp/codex-home/bin/codex-memory-review", logPath: "/tmp/cron.log", matchingLines: ["* * * * * codex-memory-review"], error: null },
      recommendations: [{ kind: "proposals", message: "Inspect proposals.", command: "govkb proposals review /repo" }]
    })
  );
  assert.equal(payload.state, "attention");
  assert.equal(payload.proposalQueue.summary.proposalCount, 2);
  assert.equal(payload.memoryReview.latestRun.status, "completed");
});

test("parseProposalReviewPayload accepts review groups", () => {
  const payload = parseProposalReviewPayload(
    JSON.stringify({
      schemaVersion: 1,
      projectRoot: "/repo",
      summary: { proposalCount: 1, groupCount: 1, warningCount: 0, reviewGroupCount: 1, actionFilter: "all", actionCounts: { "manual-review": 1 } },
      groups: [
        {
          id: "group-p1",
          priority: 3,
          recommendedAction: "manual-review",
          proposalIds: ["p1"],
          targetCapabilities: ["project-knowledge-steward"],
          warningCodes: [],
          outputPaths: [".governed/capabilities/project-knowledge-steward/references/tool.md"],
          reason: "proposal is unique in the current queue",
          nextSteps: ["Review the proposal body."],
          commands: ["govkb proposals show p1 --project-root /repo"]
        }
      ]
    })
  );
  assert.equal(payload.groups[0].recommendedAction, "manual-review");
  assert.equal(payload.groups[0].commands.length, 1);
});

test("parseCandidatesPayload accepts fixture contract", () => {
  const payload = parseCandidatesPayload(fixture("candidates.sample.json"));
  assert.equal(payload.candidates[0].id, "backend-workflow");
  assert.equal(payload.candidates[0].occurrences, 2);
});

test("parseConversionPayload accepts strict failure details", () => {
  const payload = parseConversionPayload(
    JSON.stringify({
      sourcePath: "/tmp/codex-home/skills/grading",
      sourceName: "grading",
      capabilityId: "grading",
      capabilityName: "Grading",
      packagePath: "/repo/.governed/capabilities/grading",
      parityLevel: "Exact content copy",
      strictStatus: "failed",
      strictIssues: [
        {
          location: "/repo/.governed/capabilities/grading/instructions.md:10",
          message: "repo-relative or package-relative path does not exist: missing.md",
          ruleId: "GSK-PATH-001",
          severity: "error"
        }
      ],
      createdPackage: "/repo/.governed/capabilities/grading",
      packageRemoved: true
    })
  );
  assert.equal(payload.strictStatus, "failed");
  assert.equal(payload.packageRemoved, true);
  assert.equal(payload.strictIssues[0].ruleId, "GSK-PATH-001");
});

test("parseReportSummaryPayload rejects raw transcript summaries", () => {
  const payload = JSON.parse(fixture("report-summary.sample.json"));
  payload.reports[0].containsRawTranscript = true;
  assert.throws(() => parseReportSummaryPayload(JSON.stringify(payload)), /raw transcript/);
});

test("parseReportSummaryPayload accepts sanitized fixture", () => {
  const payload = parseReportSummaryPayload(fixture("report-summary.sample.json"));
  assert.equal(payload.reports[0].containsRawTranscript, false);
});

test("parsePromotionsPayload accepts lifecycle fixture", () => {
  const payload = parsePromotionsPayload(fixture("promotions.sample.json"));
  assert.equal(payload.promotions[0].state, "ready-for-review");
  assert.equal(payload.promotions[0].status.length, 2);
});

test("parsePromotionCleanupPayload accepts preview/apply cleanup contract", () => {
  const payload = parsePromotionCleanupPayload(
    JSON.stringify({
      schemaVersion: 1,
      projectRoot: "/repo",
      codexHome: "/tmp/codex-home",
      projectId: "repo",
      promotionsRoot: "/tmp/codex-home/memories/govkb/worktrees/repo",
      mode: "apply",
      eligible: [
        {
          runId: "run-1",
          state: "applied",
          worktreeRoot: "/tmp/codex-home/memories/govkb/worktrees/repo/run-1",
          metadataPath: "/tmp/codex-home/memories/govkb/promotions/repo/run-1.json",
          eligible: true,
          reason: "applied promotion worktree is cleanup-eligible"
        }
      ],
      skipped: [],
      removed: ["/tmp/codex-home/memories/govkb/worktrees/repo/run-1"],
      metadataUpdated: ["/tmp/codex-home/memories/govkb/promotions/repo/run-1.json"],
      error: null
    })
  );
  assert.equal(payload.mode, "apply");
  assert.equal(payload.removed.length, 1);
});

test("parseLearningInventoryPayload accepts fixture contract", () => {
  const payload = parseLearningInventoryPayload(fixture("learning-inventory.sample.json"));
  assert.equal(payload.sessions.selectedForReview, 5);
  assert.equal(payload.memoryTargets[0].capabilityId, "project-knowledge-steward");
  assert.equal(payload.recommendedBatch.maxSessions, 5);
});
