import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  parseCandidatesPayload,
  parseConversionPayload,
  parseLearningInventoryPayload,
  parsePromotionCleanupPayload,
  parsePromotionsPayload,
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
