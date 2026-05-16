import { promises as fs } from "node:fs";
import { basename, join, relative, resolve } from "node:path";
import type { StatusPayload } from "./types";

export interface LocalSkillSummary {
  name: string;
  path: string;
  skillFile: string;
  relativePath: string;
  description?: string;
}

export interface LocalSkillDiscoveryOptions {
  excludeNames?: Iterable<string>;
  includeGovernedPackages?: boolean;
  includeSystemSkills?: boolean;
}

function frontmatterValue(text: string, key: string): string | undefined {
  const match = new RegExp(`^${key}:\\s*(.+?)\\s*$`, "im").exec(text);
  return match?.[1]?.trim();
}

async function isDirectory(path: string): Promise<boolean> {
  try {
    return (await fs.stat(path)).isDirectory();
  } catch {
    return false;
  }
}

async function readSkill(skillPath: string, root: string): Promise<LocalSkillSummary | undefined> {
  const skillFile = join(skillPath, "SKILL.md");
  let text: string;
  try {
    text = await fs.readFile(skillFile, "utf8");
  } catch {
    return undefined;
  }
  return {
    name: frontmatterValue(text, "name") ?? basename(skillPath),
    path: skillPath,
    skillFile,
    relativePath: relative(root, skillPath) || basename(skillPath),
    description: frontmatterValue(text, "description")
  };
}

interface MaterializedGovernedSkills {
  ids: Set<string>;
  paths: Set<string>;
}

function addString(value: unknown, target: Set<string>): void {
  if (typeof value === "string" && value.trim()) {
    target.add(value.trim());
  }
}

async function materializedGovernedSkills(codexHome: string): Promise<MaterializedGovernedSkills> {
  const installStateRoot = join(codexHome, "memories", "govkb", "install-state");
  const result: MaterializedGovernedSkills = { ids: new Set(), paths: new Set() };
  let entries;
  try {
    entries = await fs.readdir(installStateRoot, { withFileTypes: true });
  } catch {
    return result;
  }
  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith(".json")) {
      continue;
    }
    let parsed: unknown;
    try {
      parsed = JSON.parse(await fs.readFile(join(installStateRoot, entry.name), "utf8"));
    } catch {
      continue;
    }
    if (!parsed || typeof parsed !== "object" || !Array.isArray((parsed as { capabilities?: unknown }).capabilities)) {
      continue;
    }
    for (const capability of (parsed as { capabilities: unknown[] }).capabilities) {
      if (!capability || typeof capability !== "object") {
        continue;
      }
      const row = capability as Record<string, unknown>;
      addString(row.materialized_skill_id ?? row.materializedSkillId, result.ids);
      const targetPath = row.target_path ?? row.targetPath;
      if (typeof targetPath === "string" && targetPath.trim()) {
        result.paths.add(resolve(targetPath.trim()));
      }
    }
  }
  return result;
}

function isMaterializedGovernedSkill(skill: LocalSkillSummary, governed: MaterializedGovernedSkills): boolean {
  return governed.ids.has(skill.name) || governed.ids.has(basename(skill.path)) || governed.paths.has(resolve(skill.path));
}

function skillKeys(skill: LocalSkillSummary): string[] {
  return [skill.name, basename(skill.path), skill.relativePath].map((value) => value.trim().toLowerCase()).filter(Boolean);
}

function normalizeCapabilityToken(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function isGovkbMaterializedPackage(skill: LocalSkillSummary): boolean {
  return skillKeys(skill).some((key) => key === "govkb" || key.startsWith("govkb-") || key.includes("/govkb-"));
}

export function governedSkillNamesForConversion(status?: StatusPayload): string[] {
  const names = new Set<string>();
  const projectId = normalizeCapabilityToken(status?.project.id ?? "");
  for (const capability of status?.capabilities ?? []) {
    for (const value of [capability.id, capability.name, ...(capability.aliases ?? [])]) {
      if (value) {
        names.add(value);
      }
    }
    const capabilityId = normalizeCapabilityToken(capability.id);
    if (projectId && capabilityId) {
      names.add(`govkb-${projectId}-${capabilityId}`);
    }
  }
  for (const materialized of status?.installState.codex.materializedCapabilities ?? []) {
    if (materialized.materializedSkillId) {
      names.add(materialized.materializedSkillId);
    }
  }
  return [...names].filter(Boolean);
}

export async function discoverLocalSkills(
  codexHome: string,
  maxDepth = 2,
  options: LocalSkillDiscoveryOptions = {}
): Promise<LocalSkillSummary[]> {
  const root = join(codexHome, "skills");
  if (!(await isDirectory(root))) {
    return [];
  }
  const governed = await materializedGovernedSkills(codexHome);
  const excludedNames = new Set([...(options.excludeNames ?? [])].map((value) => value.trim().toLowerCase()).filter(Boolean));
  const discovered = new Map<string, LocalSkillSummary>();
  async function visit(directory: string, depth: number): Promise<void> {
    const skill = await readSkill(directory, root);
    if (skill) {
      const excludedByProject = skillKeys(skill).some((key) => excludedNames.has(key));
      const excludedGovernedPackage = !options.includeGovernedPackages && isGovkbMaterializedPackage(skill);
      if (!excludedByProject && !excludedGovernedPackage && !isMaterializedGovernedSkill(skill, governed)) {
        discovered.set(skill.path, skill);
      }
      return;
    }
    if (depth >= maxDepth) {
      return;
    }
    let entries;
    try {
      entries = await fs.readdir(directory, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.isDirectory() && (options.includeSystemSkills || !entry.name.startsWith("."))) {
        await visit(join(directory, entry.name), depth + 1);
      }
    }
  }
  await visit(root, 0);
  return [...discovered.values()].sort((left, right) => left.name.localeCompare(right.name));
}
