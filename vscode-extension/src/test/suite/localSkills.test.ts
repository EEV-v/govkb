import test from "node:test";
import assert from "node:assert/strict";
import { promises as fs } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { discoverLocalSkills, governedSkillNamesForConversion } from "../../localSkills";

async function tempCodexHome(): Promise<string> {
  return fs.mkdtemp(join(tmpdir(), "govkb-local-skills-"));
}

test("discoverLocalSkills lists one selectable skill per SKILL.md", async () => {
  const codexHome = await tempCodexHome();
  await fs.mkdir(join(codexHome, "skills", "release-helper"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", "release-helper", "SKILL.md"),
    [
      "---",
      "name: release-helper",
      "description: Prepare release notes.",
      "---",
      "# Release Helper"
    ].join("\n")
  );
  await fs.mkdir(join(codexHome, "skills", ".system", "skill-creator"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", ".system", "skill-creator", "SKILL.md"),
    "---\nname: skill-creator\n---\n# Skill Creator\n"
  );

  const skills = await discoverLocalSkills(codexHome);

  assert.deepEqual(
    skills.map((skill) => skill.name),
    ["release-helper"]
  );
  assert.equal(skills[0].relativePath, "release-helper");
  assert.equal(skills[0].description, "Prepare release notes.");
});

test("discoverLocalSkills hides materialized governed skills from conversion picker", async () => {
  const codexHome = await tempCodexHome();
  await fs.mkdir(join(codexHome, "skills", "govkb-clearing-clearing-feature-cookbook"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", "govkb-clearing-clearing-feature-cookbook", "SKILL.md"),
    "---\nname: govkb-clearing-clearing-feature-cookbook\n---\n# Clearing Feature Cookbook\n"
  );
  await fs.mkdir(join(codexHome, "skills", "govkb-feature-cookbook"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", "govkb-feature-cookbook", "SKILL.md"),
    "---\nname: govkb-feature-cookbook\n---\n# GovKB Feature Cookbook\n"
  );
  await fs.mkdir(join(codexHome, "memories", "govkb", "install-state"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "memories", "govkb", "install-state", "clearing--codex.json"),
    JSON.stringify({
      capabilities: [
        {
          materialized_skill_id: "govkb-clearing-clearing-feature-cookbook",
          target_path: join(codexHome, "skills", "govkb-clearing-clearing-feature-cookbook")
        }
      ]
    })
  );

  const skills = await discoverLocalSkills(codexHome);

  assert.deepEqual(
    skills.map((skill) => skill.name),
    []
  );
});

test("discoverLocalSkills can include GovKB-generated packages when explicitly requested", async () => {
  const codexHome = await tempCodexHome();
  await fs.mkdir(join(codexHome, "skills", "govkb-feature-cookbook"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", "govkb-feature-cookbook", "SKILL.md"),
    "---\nname: govkb-feature-cookbook\n---\n# GovKB Feature Cookbook\n"
  );

  const skills = await discoverLocalSkills(codexHome, 2, { includeGovernedPackages: true });

  assert.deepEqual(
    skills.map((skill) => skill.name),
    ["govkb-feature-cookbook"]
  );
});

test("discoverLocalSkills hides source skills already governed by the selected project", async () => {
  const codexHome = await tempCodexHome();
  await fs.mkdir(join(codexHome, "skills", "clearing-level3-comment-writer"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", "clearing-level3-comment-writer", "SKILL.md"),
    "---\nname: clearing-level3-comment-writer\n---\n# Clearing Level 3 Comment Writer\n"
  );
  await fs.mkdir(join(codexHome, "skills", "comparative-grade-screening"), { recursive: true });
  await fs.writeFile(
    join(codexHome, "skills", "comparative-grade-screening", "SKILL.md"),
    "---\nname: comparative-grade-screening\n---\n# Comparative Grade Screening\n"
  );

  const skills = await discoverLocalSkills(codexHome, 2, {
    excludeNames: ["clearing-level3-comment-writer", "clearing level 3 comment writer"]
  });

  assert.deepEqual(
    skills.map((skill) => skill.name),
    ["comparative-grade-screening"]
  );
});

test("governedSkillNamesForConversion includes derived materialized skill ids", () => {
  const exclusions = governedSkillNamesForConversion({
    schemaVersion: 1,
    projectRoot: "/repo",
    governedRoot: "/repo/.governed",
    project: { id: "clearing", currentRelease: "unreleased", gitRevision: "abc", governedDirty: false, governedStatus: [] },
    validation: { status: "ok", warnings: [], errors: [] },
    kbHealth: { warnings: [], suggestedRemediation: null },
    capabilities: [
      {
        id: "comparative-grade-screening",
        name: "Comparative Grade Screening",
        governed: true,
        aliases: ["comparative screening"]
      }
    ],
    adapters: ["codex"],
    releases: [],
    installState: {
      codex: {
        status: "present",
        statePath: "/tmp/state.json",
        appliedRevision: "abc",
        appliedRelease: "unreleased",
        appliedAt: null,
        materializedCapabilities: []
      }
    },
    skillUpdates: {
      state: "current",
      repoRevision: "abc",
      appliedRevision: "abc",
      governedDirty: false,
      pendingLocalMemory: {
        available: false,
        safePromotionCount: 0,
        rejectedCount: 0,
        pendingCount: 0,
        items: []
      }
    }
  });

  assert.equal(exclusions.includes("comparative-grade-screening"), true);
  assert.equal(exclusions.includes("Comparative Grade Screening"), true);
  assert.equal(exclusions.includes("comparative screening"), true);
  assert.equal(exclusions.includes("govkb-clearing-comparative-grade-screening"), true);
});

test("discoverLocalSkills returns empty when CODEX_HOME has no skills folder", async () => {
  const codexHome = await tempCodexHome();
  assert.deepEqual(await discoverLocalSkills(codexHome), []);
});
