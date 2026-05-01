import { promises as fs } from "node:fs";
import { homedir } from "node:os";
import { basename, join } from "node:path";
import { GovkbSettings, ReasoningEffort, ReportSummary, ReportSummaryPayload } from "./types";

function countPattern(text: string, pattern: RegExp): number {
  const matches = text.match(pattern);
  return matches ? matches.length : 0;
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function extractValue(text: string, label: string): string | null {
  const expression = new RegExp(`^\\s*-?\\s*${escapeRegExp(label)}\\s*:\\s*(.+?)\\s*$`, "im");
  return expression.exec(text)?.[1] ?? null;
}

function extractNumber(text: string, label: string): number | null {
  const value = extractValue(text, label);
  if (!value) {
    return null;
  }
  const number = Number.parseInt(value, 10);
  return Number.isFinite(number) ? number : null;
}

function extractRunId(path: string): string | undefined {
  const match = /^(.+)-report\.md$/i.exec(basename(path));
  return match?.[1];
}

function reasoningOrNull(value: string | null): ReasoningEffort | null {
  return value === "low" || value === "medium" || value === "high" || value === "xhigh" ? value : null;
}

export function summarizeReportMarkdown(path: string, text: string): ReportSummary {
  return {
    path,
    createdAt: extractValue(text, "Created at") ?? extractRunId(path),
    classifier: {
      model: extractValue(text, "Classifier model"),
      reasoning: reasoningOrNull(extractValue(text, "Classifier reasoning"))
    },
    sessions: {
      failed: extractNumber(text, "Failed sessions") ?? countPattern(text, /\bfailed\b/gi),
      deferred: extractNumber(text, "Deferred sessions") ?? countPattern(text, /\bdeferred\b/gi),
      learned: extractNumber(text, "Applied") ?? countPattern(text, /\blearned\b/gi),
      stagedCandidates: extractNumber(text, "Capability candidates") ?? countPattern(text, /\bstaged candidate\b/gi)
    },
    containsRawTranscript: false
  };
}

export function codexHomeForReports(
  settings: Pick<GovkbSettings, "codexHome">,
  env: NodeJS.ProcessEnv = process.env,
  home: string = homedir()
): string {
  return settings.codexHome ?? env.CODEX_HOME?.trim() ?? join(home, ".codex");
}

export function reportRootForProject(codexHome: string, projectId: string): string {
  return join(codexHome, "memories", "govkb", "projects", projectId, "codex-memory-review", "reports");
}

export async function discoverReportSummaries(reportRoot: string, maxReports = 20): Promise<ReportSummary[]> {
  let entries;
  try {
    entries = await fs.readdir(reportRoot, { withFileTypes: true });
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "ENOENT" || code === "ENOTDIR") {
      return [];
    }
    throw error;
  }
  const reportNames = entries
    .filter((entry) => entry.isFile() && entry.name.endsWith("-report.md"))
    .map((entry) => entry.name)
    .sort((left, right) => right.localeCompare(left))
    .slice(0, maxReports);
  const reports: ReportSummary[] = [];
  for (const reportName of reportNames) {
    const reportPath = join(reportRoot, reportName);
    reports.push(summarizeReportMarkdown(reportPath, await fs.readFile(reportPath, "utf8")));
  }
  return reports;
}

export function buildReportSummaryPayload(codexHome: string, projectId: string, reports: ReportSummary[]): ReportSummaryPayload {
  return {
    schemaVersion: 1,
    codexHome,
    projectId,
    reports
  };
}
