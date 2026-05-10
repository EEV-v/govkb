import { CandidatesPayload, PromotionsPayload, ReportSummaryPayload, StatusPayload } from "./types";

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
