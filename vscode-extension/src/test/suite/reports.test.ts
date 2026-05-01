import test from "node:test";
import assert from "node:assert/strict";
import { mkdir, mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildReportSummaryPayload, codexHomeForReports, discoverReportSummaries, reportRootForProject, summarizeReportMarkdown } from "../../reports";

test("summarizeReportMarkdown emits aggregate-only report summaries", () => {
  const summary = summarizeReportMarkdown(
    "/tmp/report.md",
    "Classifier model: gpt-5.4-mini\nClassifier reasoning: low\nfailed\ndeferred\nlearned\nstaged candidate\n"
  );
  assert.equal(summary.classifier.model, "gpt-5.4-mini");
  assert.equal(summary.classifier.reasoning, "low");
  assert.equal(summary.sessions.failed, 1);
  assert.equal(summary.sessions.deferred, 1);
  assert.equal(summary.containsRawTranscript, false);
});

test("summarizeReportMarkdown parses current memory-review report bullets", () => {
  const summary = summarizeReportMarkdown(
    "/tmp/2026-04-25T120000Z-report.md",
    [
      "# Codex Memory Review - 2026-04-25",
      "- Classifier model: gpt-5.4-mini",
      "- Classifier reasoning: low",
      "- Deferred sessions: 2",
      "- Applied: 1",
      "- Capability candidates: 3",
      "- Failed sessions: 4"
    ].join("\n")
  );
  assert.equal(summary.createdAt, "2026-04-25T120000Z");
  assert.equal(summary.sessions.failed, 4);
  assert.equal(summary.sessions.deferred, 2);
  assert.equal(summary.sessions.learned, 1);
  assert.equal(summary.sessions.stagedCandidates, 3);
});

test("buildReportSummaryPayload keeps reports under the selected project", () => {
  const report = summarizeReportMarkdown("/tmp/report.md", "failed\n");
  const payload = buildReportSummaryPayload("/tmp/codex-home", "demo-project", [report]);
  assert.equal(payload.projectId, "demo-project");
  assert.equal(payload.reports[0].containsRawTranscript, false);
});

test("reportRootForProject follows the project-scoped memory-review path", () => {
  assert.equal(
    reportRootForProject("/tmp/codex-home", "demo-project"),
    "/tmp/codex-home/memories/govkb/projects/demo-project/codex-memory-review/reports"
  );
});

test("codexHomeForReports prefers settings then environment then home default", () => {
  assert.equal(codexHomeForReports({ codexHome: "/tmp/settings-home" }, { CODEX_HOME: "/tmp/env-home" }, "/home/user"), "/tmp/settings-home");
  assert.equal(codexHomeForReports({ codexHome: undefined }, { CODEX_HOME: "/tmp/env-home" }, "/home/user"), "/tmp/env-home");
  assert.equal(codexHomeForReports({ codexHome: undefined }, {}, "/home/user"), "/home/user/.codex");
});

test("discoverReportSummaries reads newest report summaries without patch files", async () => {
  const root = await mkdtemp(join(tmpdir(), "govkb-reports-test-"));
  const reportRoot = join(root, "reports");
  await mkdir(reportRoot);
  await writeFile(join(reportRoot, "2026-04-24T120000Z-report.md"), "- Failed sessions: 1\n", "utf8");
  await writeFile(join(reportRoot, "2026-04-25T120000Z-report.md"), "- Failed sessions: 2\n", "utf8");
  await writeFile(join(reportRoot, "2026-04-25T120000Z-staged.patch"), "diff\n", "utf8");

  const reports = await discoverReportSummaries(reportRoot);
  assert.deepEqual(
    reports.map((report) => [report.createdAt, report.sessions.failed]),
    [
      ["2026-04-25T120000Z", 2],
      ["2026-04-24T120000Z", 1]
    ]
  );
});

test("discoverReportSummaries treats a missing report folder as empty", async () => {
  const reports = await discoverReportSummaries("/tmp/govkb-missing-report-folder-for-test");
  assert.deepEqual(reports, []);
});
