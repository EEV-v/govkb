export type SetupMode = "auto" | "useExisting" | "guidedInstall";
export type ReasoningEffort = "low" | "medium" | "high" | "xhigh";

export interface GovkbSettings {
  command: string;
  pythonPath: string;
  setupMode: SetupMode;
  codexHome?: string;
  classifierModel?: string;
  classifierReasoning?: ReasoningEffort;
  reviewTimeoutSeconds?: number;
  reviewMaxSessions: number;
  defaultDryRun: boolean;
}

export interface CliCommand {
  executable: string;
  args: string[];
  cwd?: string;
  env?: Record<string, string>;
}

export interface CliResult {
  command: CliCommand;
  exitCode: number;
  stdout: string;
  stderr: string;
}

export interface CliRunOptions {
  onStdout?: (chunk: string) => void;
  onStderr?: (chunk: string) => void;
}

export interface CliRunner {
  run(command: CliCommand, options?: CliRunOptions): Promise<CliResult>;
}

export interface Blocker {
  title: string;
  action: string;
  detail?: string;
}

export interface FlowResult {
  ok: boolean;
  commands: CliCommand[];
  blocker?: Blocker;
  statusJson?: StatusPayload;
}

export interface ValidationMessage {
  location: string;
  message: string;
}

export interface StatusPayload {
  schemaVersion: 1;
  projectRoot: string;
  governedRoot: string;
  project: {
    id: string | null;
    currentRelease: string;
  };
  validation: {
    status: "ok" | "error";
    warnings: ValidationMessage[];
    errors: ValidationMessage[];
  };
  kbHealth: {
    warnings: ValidationMessage[];
    suggestedRemediation: string | null;
  };
  capabilities: CapabilitySummary[];
  adapters: string[];
  releases: string[];
  installState: {
    codex: CodexInstallState;
  };
}

export interface CapabilitySummary {
  id: string;
  name: string;
  governed: boolean;
  description?: string;
  memoryEnabled?: boolean;
  requiresExplicitAcceptance?: boolean;
}

export interface CodexInstallState {
  status: "not-requested" | "unavailable" | "missing" | "present";
  statePath: string | null;
  appliedRevision: string | null;
  appliedRelease: string | null;
  appliedAt: string | null;
  materializedCapabilities: Array<{
    capabilityId: string | null;
    materializedSkillId: string | null;
  }>;
}

export interface CandidatesPayload {
  schemaVersion: 1;
  projectRoot: string;
  candidates: CandidateSummary[];
}

export interface CandidateSummary {
  id: string;
  status: string;
  occurrences: number;
  suggestedCapabilityId: string | null;
  activationState: "activated" | "not-activated";
  path: string;
}

export interface ReportSummaryPayload {
  schemaVersion: 1;
  codexHome: string;
  projectId: string;
  reports: ReportSummary[];
}

export interface ReportSummary {
  path: string;
  createdAt?: string;
  classifier: {
    model: string | null;
    reasoning: ReasoningEffort | null;
  };
  sessions: {
    failed: number;
    deferred: number;
    learned: number;
    stagedCandidates: number;
  };
  containsRawTranscript: false;
}

export interface TreeRow {
  label: string;
  description?: string;
  tooltip?: string;
  command?: {
    command: string;
    title: string;
    arguments?: unknown[];
  };
  contextValue?: string;
}
