import { GovkbSettings, ReasoningEffort, SetupMode } from "./types";

export interface ConfigurationReader {
  get<T>(key: string, defaultValue: T): T;
}

const reasoningValues = new Set(["low", "medium", "high", "xhigh"]);
const setupModeValues = new Set(["auto", "useExisting", "guidedInstall"]);

function asOptionalReasoning(value: string): ReasoningEffort | undefined {
  return reasoningValues.has(value) ? (value as ReasoningEffort) : undefined;
}

function asSetupMode(value: string): SetupMode {
  return setupModeValues.has(value) ? (value as SetupMode) : "guidedInstall";
}

export function defaultSettings(): GovkbSettings {
  return {
    command: "govkb",
    pythonPath: "python3",
    setupMode: "guidedInstall",
    codexHome: undefined,
    classifierModel: undefined,
    classifierReasoning: undefined,
    reviewTimeoutSeconds: 180,
    reviewLookbackDays: 90,
    reviewMaxSessions: 5,
    defaultDryRun: true,
    autoRefreshOnStartup: true,
    monitorIntervalSeconds: undefined
  };
}

export function resolveSettings(config: ConfigurationReader): GovkbSettings {
  const defaults = defaultSettings();
  const codexHome = config.get("codexHome", "");
  const classifierModel = config.get("classifierModel", "");
  const classifierReasoning = config.get("classifierReasoning", "");
  const timeout = config.get("reviewTimeoutSeconds", defaults.reviewTimeoutSeconds ?? 0);
  const lookbackDays = config.get("reviewLookbackDays", defaults.reviewLookbackDays);
  const maxSessions = config.get("reviewMaxSessions", defaults.reviewMaxSessions);
  const monitorInterval = config.get("monitorIntervalSeconds", 0);
  return {
    command: config.get("command", defaults.command).trim() || defaults.command,
    pythonPath: config.get("pythonPath", defaults.pythonPath).trim() || defaults.pythonPath,
    setupMode: asSetupMode(config.get("setupMode", defaults.setupMode)),
    codexHome: codexHome.trim() || undefined,
    classifierModel: classifierModel.trim() || undefined,
    classifierReasoning: asOptionalReasoning(classifierReasoning),
    reviewTimeoutSeconds: Number.isFinite(timeout) && timeout > 0 ? Math.floor(timeout) : undefined,
    reviewLookbackDays: Number.isFinite(lookbackDays) && lookbackDays > 0 ? Math.floor(lookbackDays) : defaults.reviewLookbackDays,
    reviewMaxSessions: Number.isFinite(maxSessions) && maxSessions > 0 ? Math.floor(maxSessions) : defaults.reviewMaxSessions,
    defaultDryRun: config.get("defaultDryRun", defaults.defaultDryRun),
    autoRefreshOnStartup: config.get("autoRefreshOnStartup", defaults.autoRefreshOnStartup),
    monitorIntervalSeconds: Number.isFinite(monitorInterval) && monitorInterval >= 30 ? Math.floor(monitorInterval) : undefined
  };
}
