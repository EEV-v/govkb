import test from "node:test";
import assert from "node:assert/strict";
import { ensureWorkspaceTrusted } from "../../trust";

test("trusted workspace passes", async () => {
  const result = await ensureWorkspaceTrusted(true);
  assert.equal(result.trusted, true);
});

test("untrusted workspace blocks when trust is not granted", async () => {
  const result = await ensureWorkspaceTrusted(false, async () => false);
  assert.equal(result.trusted, false);
  assert.equal(result.blocker?.action, "Trust this workspace before running GovKB commands");
});

test("untrusted workspace can continue after trust request succeeds", async () => {
  const result = await ensureWorkspaceTrusted(false, async () => true);
  assert.equal(result.trusted, true);
});

