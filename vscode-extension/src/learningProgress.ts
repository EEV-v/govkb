import { LearningProgressEvent, LearningRunState, LearningSessionProgress } from "./types";

export interface ProgressParseResult {
  events: LearningProgressEvent[];
  remainder: string;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

export function initialLearningRunState(): LearningRunState {
  return {
    active: false,
    sessions: [],
    artifacts: []
  };
}

export function parseLearningProgressChunk(chunk: string, previousRemainder = ""): ProgressParseResult {
  const text = previousRemainder + chunk;
  const lines = text.split(/\r?\n/);
  const remainder = text.endsWith("\n") || text.endsWith("\r") ? "" : lines.pop() ?? "";
  const events: LearningProgressEvent[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }
    try {
      const payload = JSON.parse(trimmed) as unknown;
      if (isObject(payload) && typeof payload.event === "string") {
        if ("rawTranscript" in payload || "transcript" in payload) {
          continue;
        }
        events.push(payload as unknown as LearningProgressEvent);
      }
    } catch {
      continue;
    }
  }
  return { events, remainder };
}

function upsertSession(
  sessions: LearningSessionProgress[],
  sessionId: string,
  update: Partial<LearningSessionProgress>
): LearningSessionProgress[] {
  const index = sessions.findIndex((session) => session.sessionId === sessionId);
  const current: LearningSessionProgress =
    index >= 0
      ? sessions[index]
      : {
          sessionId,
          status: "queued",
          targetSkills: [],
          lessonCount: 0,
          appliedCount: 0,
          stagedCount: 0,
          rejectedCount: 0,
          candidateCount: 0
        };
  const next = { ...current, ...update };
  if (index < 0) {
    return [...sessions, next];
  }
  return [...sessions.slice(0, index), next, ...sessions.slice(index + 1)];
}

export function reduceLearningProgressEvent(state: LearningRunState, event: LearningProgressEvent): LearningRunState {
  if (event.event === "run_started") {
    return {
      ...state,
      runId: event.runId,
      active: true,
      dryRun: Boolean(event.dryRun),
      lookbackDays: typeof event.lookbackDays === "number" ? event.lookbackDays : null,
      maxSessions: typeof event.maxSessions === "number" ? event.maxSessions : null,
      sessions: [],
      artifacts: [],
      summary: undefined
    };
  }
  if (event.event === "inventory") {
    return {
      ...state,
      inventory: event as unknown as LearningRunState["inventory"]
    };
  }
  if (event.event === "artifact_written" && typeof event.kind === "string" && typeof event.path === "string") {
    return {
      ...state,
      artifacts: [...state.artifacts, { kind: event.kind, path: event.path }]
    };
  }
  if (event.event === "run_finished") {
    return {
      ...state,
      active: false,
      summary: {
        reviewed: asNumber(event.reviewed),
        skipped: asNumber(event.skipped),
        deferred: asNumber(event.deferred),
        failed: asNumber(event.failed),
        applied: asNumber(event.applied),
        staged: asNumber(event.staged),
        rejected: asNumber(event.rejected),
        existingSkillUpdates: asNumber(event.existingSkillUpdates),
        stagedCandidates: asNumber(event.stagedCandidates)
      }
    };
  }
  if (event.sessionId) {
    return {
      ...state,
      sessions: upsertSession(state.sessions, event.sessionId, {
        threadName: event.threadName,
        updatedAt: event.updatedAt,
        status: event.status ?? event.event.replace(/^session_/, ""),
        reason: event.reason,
        targetSkills: asStringArray(event.targetSkills),
        lessonCount: asNumber(event.lessonCount),
        appliedCount: asNumber(event.appliedCount),
        stagedCount: asNumber(event.stagedCount),
        rejectedCount: asNumber(event.rejectedCount),
        candidateCount: asNumber(event.candidateCount)
      })
    };
  }
  return state;
}

export function reduceLearningProgressEvents(
  state: LearningRunState,
  events: LearningProgressEvent[]
): LearningRunState {
  return events.reduce(reduceLearningProgressEvent, state);
}
