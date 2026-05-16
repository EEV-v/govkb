import {
  CandidatesPayload,
  ConversionPayload,
  LearningInventoryPayload,
  PromotionCleanupPayload,
  PromotionsPayload,
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
