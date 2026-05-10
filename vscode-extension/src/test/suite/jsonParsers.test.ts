import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parseCandidatesPayload, parsePromotionsPayload, parseReportSummaryPayload, parseStatusPayload } from "../../jsonParsers";

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
