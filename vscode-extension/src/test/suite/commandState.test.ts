import test from "node:test";
import assert from "node:assert/strict";
import { CommandRunState } from "../../commandState";

test("CommandRunState prevents duplicate active command keys", async () => {
  const state = new CommandRunState();
  assert.equal(state.start("setup"), true);
  assert.equal(state.start("setup"), false);
  assert.equal(state.isRunning("setup"), true);
  state.finish("setup");
  assert.equal(state.start("setup"), true);
});

test("CommandRunState releases keys after async work", async () => {
  const state = new CommandRunState();
  const result = await state.run("apply", async () => "done");
  assert.equal(result.started, true);
  assert.equal(result.value, "done");
  assert.equal(state.isRunning("apply"), false);
});

test("CommandRunState releases keys after errors", async () => {
  const state = new CommandRunState();
  await assert.rejects(
    state.run("dry-run", async () => {
      throw new Error("failed");
    }),
    /failed/
  );
  assert.equal(state.isRunning("dry-run"), false);
});
