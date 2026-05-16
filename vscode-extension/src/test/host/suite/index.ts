import assert from "node:assert/strict";
import * as vscode from "vscode";

const expectedCommands = [
  "govkb.oneClickSetup",
  "govkb.oneClickApply",
  "govkb.validateProject",
  "govkb.showStatus",
  "govkb.refreshCapabilities",
  "govkb.openCapability",
  "govkb.convertSkillToGoverned",
  "govkb.renameGovernedSkill",
  "govkb.mergeGovernedSkills",
  "govkb.discoverLearning",
  "govkb.reviewLearningDryRun",
  "govkb.reviewLearningApply",
  "govkb.reviewMemoryDryRun",
  "govkb.reviewMemoryApply",
  "govkb.promoteAuto",
  "govkb.refreshPromotions",
  "govkb.openPromotion",
  "govkb.openPromotionWorktree",
  "govkb.showPromotion",
  "govkb.markPromotionAccepted",
  "govkb.applyPromotionToProject",
  "govkb.finalizeAcceptedPromotion",
  "govkb.markPromotionRejected",
  "govkb.archivePromotion",
  "govkb.listCandidates",
  "govkb.openCandidate",
  "govkb.refreshReports",
  "govkb.openLatestReport",
  "govkb.openReport",
  "govkb.openOutput"
];

export async function run(): Promise<void> {
  const extension = vscode.extensions.getExtension("govkb-local.govkb");
  assert.ok(extension, "GovKB extension should be registered in the extension host");

  await extension.activate();
  assert.equal(extension.isActive, true);

  const registeredCommands = await vscode.commands.getCommands(true);
  for (const command of expectedCommands) {
    assert.ok(registeredCommands.includes(command), `expected command to be registered: ${command}`);
  }

  const config = vscode.workspace.getConfiguration("govkb");
  assert.equal(config.get("autoRefreshOnStartup"), true);
  assert.equal(config.get("monitorIntervalSeconds"), 0);
}
