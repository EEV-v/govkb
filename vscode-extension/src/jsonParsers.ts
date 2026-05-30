import {
  CandidatesPayload,
  ConversionPayload,
  DoctorPayload,
  LearningInventoryPayload,
  PromotionCleanupPayload,
  PromotionsPayload,
  ProposalReviewPayload,
  ReportSummaryPayload,
  StatusPayload
} from "./types";

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function assertString(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new Error(`invalid ${label}: expected string`);
  }
  return value;
}

function assertNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`invalid ${label}: expected number`);
  }
  return value;
}

function assertArray(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new Error(`invalid ${label}: expected array`);
  }
  return value;
}

function assertBoolean(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") {
    throw new Error(`invalid ${label}: expected boolean`);
  }
  return value;
}

function assertStringOrNull(value: unknown, label: string): string | null {
  if (value !== null && typeof value !== "string") {
    throw new Error(`invalid ${label}: expected string or null`);
  }
  return value;
}

function assertNumberRecord(value: unknown, label: string): Record<string, number> {
  if (!isObject(value)) {
    throw new Error(`invalid ${label}: expected object`);
  }
  for (const [key, item] of Object.entries(value)) {
    assertNumber(item, `${label}.${key}`);
  }
  return value as Record<string, number>;
}

function assertStringRecord(value: unknown, label: string): Record<string, string> {
  if (!isObject(value)) {
    throw new Error(`invalid ${label}: expected object`);
  }
  for (const [key, item] of Object.entries(value)) {
    assertString(item, `${label}.${key}`);
  }
  return value as Record<string, string>;
}

export function parseStatusPayload(text: string): StatusPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid status payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid status payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  assertString(payload.governedRoot, "governedRoot");
  if (!isObject(payload.project) || !isObject(payload.validation) || !isObject(payload.kbHealth) || !isObject(payload.installState)) {
    throw new Error("invalid status payload: missing core sections");
  }
  if (!isObject(payload.skillUpdates)) {
    throw new Error("invalid status payload: missing skillUpdates");
  }
  assertArray(payload.capabilities, "capabilities");
  assertArray(payload.adapters, "adapters");
  return payload as unknown as StatusPayload;
}

export function parseDoctorPayload(text: string): DoctorPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid doctor payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid doctor payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  assertString(payload.codexHome, "codexHome");
  assertString(payload.state, "state");
  if (!isObject(payload.project) || !isObject(payload.validation) || !isObject(payload.installState) || !isObject(payload.skillUpdates)) {
    throw new Error("invalid doctor payload: missing status sections");
  }
  if (!isObject(payload.proposalQueue) || !isObject(payload.proposalQueue.summary)) {
    throw new Error("invalid doctor payload: missing proposalQueue");
  }
  validateProposalReviewSummary(payload.proposalQueue.summary, "proposalQueue.summary");
  const reviewGroups = assertArray(payload.proposalQueue.reviewGroups, "proposalQueue.reviewGroups");
  for (const [index, group] of reviewGroups.entries()) {
    if (!isObject(group)) {
      throw new Error(`invalid proposalQueue.reviewGroups[${index}]: expected object`);
    }
    assertString(group.id, `proposalQueue.reviewGroups[${index}].id`);
    assertString(group.recommendedAction, `proposalQueue.reviewGroups[${index}].recommendedAction`);
    assertArray(group.proposalIds, `proposalQueue.reviewGroups[${index}].proposalIds`);
    assertArray(group.warningCodes, `proposalQueue.reviewGroups[${index}].warningCodes`);
  }
  if (!isObject(payload.memoryReview) || !isObject(payload.memoryReview.state) || !isObject(payload.memoryReview.latestRun)) {
    throw new Error("invalid doctor payload: missing memoryReview");
  }
  assertString(payload.memoryReview.stateDir, "memoryReview.stateDir");
  assertString(payload.memoryReview.statePath, "memoryReview.statePath");
  assertString(payload.memoryReview.reportDir, "memoryReview.reportDir");
  assertString(payload.memoryReview.state.status, "memoryReview.state.status");
  assertStringOrNull(payload.memoryReview.state.lastRunAt, "memoryReview.state.lastRunAt");
  assertStringOrNull(payload.memoryReview.state.lastSuccessfulUpdatedAt, "memoryReview.state.lastSuccessfulUpdatedAt");
  assertNumber(payload.memoryReview.state.processedSessionCount, "memoryReview.state.processedSessionCount");
  assertStringOrNull(payload.memoryReview.state.error, "memoryReview.state.error");
  assertString(payload.memoryReview.latestRun.status, "memoryReview.latestRun.status");
  assertStringOrNull(payload.memoryReview.latestRun.path, "memoryReview.latestRun.path");
  assertStringOrNull(payload.memoryReview.latestRun.runId, "memoryReview.latestRun.runId");
  assertNumberRecord(payload.memoryReview.latestRun.counts, "memoryReview.latestRun.counts");
  assertStringRecord(payload.memoryReview.latestRun.metadata, "memoryReview.latestRun.metadata");
  if (!isObject(payload.cron)) {
    throw new Error("invalid doctor payload: missing cron");
  }
  assertString(payload.cron.status, "cron.status");
  assertString(payload.cron.scriptPath, "cron.scriptPath");
  assertString(payload.cron.logPath, "cron.logPath");
  assertArray(payload.cron.matchingLines, "cron.matchingLines");
  assertStringOrNull(payload.cron.error, "cron.error");
  const recommendations = assertArray(payload.recommendations, "recommendations");
  for (const [index, recommendation] of recommendations.entries()) {
    if (!isObject(recommendation)) {
      throw new Error(`invalid recommendations[${index}]: expected object`);
    }
    assertString(recommendation.kind, `recommendations[${index}].kind`);
    assertString(recommendation.message, `recommendations[${index}].message`);
    if (recommendation.command !== undefined) {
      assertString(recommendation.command, `recommendations[${index}].command`);
    }
  }
  return payload as unknown as DoctorPayload;
}

function validateProposalReviewSummary(value: Record<string, unknown>, label: string): void {
  assertNumber(value.proposalCount, `${label}.proposalCount`);
  assertNumber(value.groupCount, `${label}.groupCount`);
  assertNumber(value.warningCount, `${label}.warningCount`);
  if (value.reviewGroupCount !== undefined) {
    assertNumber(value.reviewGroupCount, `${label}.reviewGroupCount`);
  }
  if (value.actionFilter !== undefined) {
    assertString(value.actionFilter, `${label}.actionFilter`);
  }
  if (!isObject(value.actionCounts)) {
    throw new Error(`invalid ${label}.actionCounts: expected object`);
  }
  for (const [key, count] of Object.entries(value.actionCounts)) {
    assertNumber(count, `${label}.actionCounts.${key}`);
  }
}

export function parseProposalReviewPayload(text: string): ProposalReviewPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid proposal review payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid proposal review payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  if (!isObject(payload.summary)) {
    throw new Error("invalid proposal review payload: missing summary");
  }
  validateProposalReviewSummary(payload.summary, "summary");
  const groups = assertArray(payload.groups, "groups");
  for (const [index, group] of groups.entries()) {
    if (!isObject(group)) {
      throw new Error(`invalid groups[${index}]: expected object`);
    }
    assertString(group.id, `groups[${index}].id`);
    assertNumber(group.priority, `groups[${index}].priority`);
    assertString(group.recommendedAction, `groups[${index}].recommendedAction`);
    assertArray(group.proposalIds, `groups[${index}].proposalIds`);
    assertArray(group.targetCapabilities, `groups[${index}].targetCapabilities`);
    assertArray(group.warningCodes, `groups[${index}].warningCodes`);
    assertArray(group.outputPaths, `groups[${index}].outputPaths`);
    assertString(group.reason, `groups[${index}].reason`);
    assertArray(group.nextSteps, `groups[${index}].nextSteps`);
    assertArray(group.commands, `groups[${index}].commands`);
  }
  return payload as unknown as ProposalReviewPayload;
}

export function parseCandidatesPayload(text: string): CandidatesPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid candidates payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid candidates payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  const candidates = assertArray(payload.candidates, "candidates");
  for (const [index, candidate] of candidates.entries()) {
    if (!isObject(candidate)) {
      throw new Error(`invalid candidates[${index}]: expected object`);
    }
    assertString(candidate.id, `candidates[${index}].id`);
    assertString(candidate.status, `candidates[${index}].status`);
    assertNumber(candidate.occurrences, `candidates[${index}].occurrences`);
    assertString(candidate.path, `candidates[${index}].path`);
  }
  return payload as unknown as CandidatesPayload;
}

export function parseConversionPayload(text: string): ConversionPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid conversion payload: expected object");
  }
  assertString(payload.sourcePath, "sourcePath");
  assertString(payload.sourceName, "sourceName");
  assertString(payload.capabilityId, "capabilityId");
  assertString(payload.capabilityName, "capabilityName");
  assertString(payload.packagePath, "packagePath");
  assertString(payload.parityLevel, "parityLevel");
  assertString(payload.strictStatus, "strictStatus");
  const strictIssues = assertArray(payload.strictIssues, "strictIssues");
  for (const [index, issue] of strictIssues.entries()) {
    if (!isObject(issue)) {
      throw new Error(`invalid strictIssues[${index}]: expected object`);
    }
    assertString(issue.location, `strictIssues[${index}].location`);
    assertString(issue.message, `strictIssues[${index}].message`);
    assertString(issue.ruleId, `strictIssues[${index}].ruleId`);
    assertString(issue.severity, `strictIssues[${index}].severity`);
  }
  if (payload.createdPackage !== undefined) {
    assertString(payload.createdPackage, "createdPackage");
  }
  if (payload.packageRemoved !== undefined) {
    assertBoolean(payload.packageRemoved, "packageRemoved");
  }
  return payload as unknown as ConversionPayload;
}

export function parseReportSummaryPayload(text: string): ReportSummaryPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid report summary payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid report summary payload: unsupported schemaVersion");
  }
  assertString(payload.codexHome, "codexHome");
  assertString(payload.projectId, "projectId");
  const reports = assertArray(payload.reports, "reports");
  for (const [index, report] of reports.entries()) {
    if (!isObject(report) || !isObject(report.sessions)) {
      throw new Error(`invalid reports[${index}]: missing sessions`);
    }
    assertString(report.path, `reports[${index}].path`);
    assertNumber(report.sessions.failed, `reports[${index}].sessions.failed`);
    assertNumber(report.sessions.deferred, `reports[${index}].sessions.deferred`);
    if (report.containsRawTranscript !== false) {
      throw new Error(`invalid reports[${index}]: raw transcript summaries are not allowed`);
    }
  }
  return payload as unknown as ReportSummaryPayload;
}

export function parseLearningInventoryPayload(text: string): LearningInventoryPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid learning inventory payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid learning inventory payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  assertString(payload.codexHome, "codexHome");
  if (!isObject(payload.sessions)) {
    throw new Error("invalid learning inventory payload: missing sessions");
  }
  for (const key of [
    "totalDiscovered",
    "selectedForReview",
    "selectedBeforeLimit",
    "selectedIndexed",
    "selectedFileOnly",
    "alreadyProcessed",
    "indexedRows",
    "indexedMissingFiles",
    "fileOnlyRecentUnprocessed"
  ]) {
    assertNumber(payload.sessions[key], `sessions.${key}`);
  }
  const selectedSessions = assertArray(payload.selectedSessions, "selectedSessions");
  for (const [index, session] of selectedSessions.entries()) {
    if (!isObject(session)) {
      throw new Error(`invalid selectedSessions[${index}]: expected object`);
    }
    assertString(session.sessionId, `selectedSessions[${index}].sessionId`);
    assertString(session.threadName, `selectedSessions[${index}].threadName`);
    assertString(session.updatedAt, `selectedSessions[${index}].updatedAt`);
    assertBoolean(session.indexed, `selectedSessions[${index}].indexed`);
  }
  const memoryTargets = assertArray(payload.memoryTargets, "memoryTargets");
  for (const [index, target] of memoryTargets.entries()) {
    if (!isObject(target)) {
      throw new Error(`invalid memoryTargets[${index}]: expected object`);
    }
    assertString(target.skillId, `memoryTargets[${index}].skillId`);
    assertString(target.capabilityId, `memoryTargets[${index}].capabilityId`);
    assertString(target.memoryPath, `memoryTargets[${index}].memoryPath`);
    assertArray(target.sections, `memoryTargets[${index}].sections`);
  }
  if (!isObject(payload.recommendedBatch)) {
    throw new Error("invalid learning inventory payload: missing recommendedBatch");
  }
  assertNumber(payload.recommendedBatch.lookbackDays, "recommendedBatch.lookbackDays");
  assertNumber(payload.recommendedBatch.maxSessions, "recommendedBatch.maxSessions");
  assertBoolean(payload.recommendedBatch.dryRun, "recommendedBatch.dryRun");
  assertString(payload.recommendedBatch.reason, "recommendedBatch.reason");
  return payload as unknown as LearningInventoryPayload;
}

export function parsePromotionsPayload(text: string): PromotionsPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid promotions payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid promotions payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  assertString(payload.codexHome, "codexHome");
  assertString(payload.projectId, "projectId");
  assertString(payload.promotionsRoot, "promotionsRoot");
  const promotions = assertArray(payload.promotions, "promotions");
  for (const [index, promotion] of promotions.entries()) {
    if (!isObject(promotion)) {
      throw new Error(`invalid promotions[${index}]: expected object`);
    }
    assertString(promotion.runId, `promotions[${index}].runId`);
    assertString(promotion.worktreeRoot, `promotions[${index}].worktreeRoot`);
    assertString(promotion.state, `promotions[${index}].state`);
    assertString(promotion.metadataPath, `promotions[${index}].metadataPath`);
    assertArray(promotion.reportPaths, `promotions[${index}].reportPaths`);
    assertArray(promotion.status, `promotions[${index}].status`);
  }
  return payload as unknown as PromotionsPayload;
}

export function parsePromotionCleanupPayload(text: string): PromotionCleanupPayload {
  const payload = JSON.parse(text) as unknown;
  if (!isObject(payload)) {
    throw new Error("invalid promotion cleanup payload: expected object");
  }
  if (payload.schemaVersion !== 1) {
    throw new Error("invalid promotion cleanup payload: unsupported schemaVersion");
  }
  assertString(payload.projectRoot, "projectRoot");
  assertString(payload.codexHome, "codexHome");
  assertString(payload.projectId, "projectId");
  assertString(payload.promotionsRoot, "promotionsRoot");
  assertString(payload.mode, "mode");
  const eligible = assertArray(payload.eligible, "eligible");
  const skipped = assertArray(payload.skipped, "skipped");
  for (const [section, items] of [["eligible", eligible], ["skipped", skipped]] as const) {
    for (const [index, item] of items.entries()) {
      if (!isObject(item)) {
        throw new Error(`invalid ${section}[${index}]: expected object`);
      }
      assertString(item.runId, `${section}[${index}].runId`);
      assertString(item.state, `${section}[${index}].state`);
      assertString(item.worktreeRoot, `${section}[${index}].worktreeRoot`);
      assertString(item.metadataPath, `${section}[${index}].metadataPath`);
      assertBoolean(item.eligible, `${section}[${index}].eligible`);
      assertString(item.reason, `${section}[${index}].reason`);
    }
  }
  const removed = assertArray(payload.removed, "removed");
  for (const [index, item] of removed.entries()) {
    assertString(item, `removed[${index}]`);
  }
  const metadataUpdated = assertArray(payload.metadataUpdated, "metadataUpdated");
  for (const [index, item] of metadataUpdated.entries()) {
    assertString(item, `metadataUpdated[${index}]`);
  }
  return payload as unknown as PromotionCleanupPayload;
}
