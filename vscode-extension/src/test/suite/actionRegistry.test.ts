import test from "node:test";
import assert from "node:assert/strict";
import { actionDefinition, allActionDefinitions } from "../../actionRegistry";

test("action registry provides stable command metadata for home workflow actions", () => {
  assert.equal(actionDefinition("setup").command, "govkb.oneClickSetup");
  assert.equal(actionDefinition("apply").icon, "cloud-upload");
  assert.equal(actionDefinition("finalizePromotion").command, "govkb.finalizeAcceptedPromotion");
  assert.equal(actionDefinition("cleanupPromotions").mutates, "promotionWorktreeAndMetadata");
});

test("action registry command ids are unique", () => {
  const commands = allActionDefinitions().map((definition) => definition.command);
  assert.equal(new Set(commands).size, commands.length);
});

test("mutating action registry entries stay CLI-backed", () => {
  for (const definition of allActionDefinitions()) {
    if (definition.mutates !== "none") {
      assert.equal(definition.cliBacked, true, `${definition.id} must stay CLI-backed`);
    }
  }
});
