import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { initialLearningRunState, parseLearningProgressChunk, reduceLearningProgressEvents } from "../../learningProgress";

function fixture(name: string): string {
  return readFileSync(join(process.cwd(), "src", "test", "fixtures", name), "utf8");
}

test("parseLearningProgressChunk handles chunked JSONL events", () => {
  const text = fixture("learning-progress.sample.jsonl");
  const split = Math.floor(text.length / 2);
  const first = parseLearningProgressChunk(text.slice(0, split));
  const second = parseLearningProgressChunk(text.slice(split), first.remainder);
  assert.equal(second.remainder, "");
  assert.equal(first.events.length + second.events.length, 6);
});

test("parseLearningProgressChunk ignores raw transcript events", () => {
  const parsed = parseLearningProgressChunk(
    '{"event":"session_classified","sessionId":"session-1","rawTranscript":"hidden"}\n'
  );
  assert.equal(parsed.events.length, 0);
});

test("reduceLearningProgressEvents summarizes run state", () => {
  const parsed = parseLearningProgressChunk(fixture("learning-progress.sample.jsonl"));
  const state = reduceLearningProgressEvents(initialLearningRunState(), parsed.events);
  assert.equal(state.active, false);
  assert.equal(state.runId, "run-1");
  assert.equal(state.sessions[0].status, "classified");
  assert.equal(state.sessions[0].appliedCount, 1);
  assert.equal(state.artifacts[0].kind, "report");
  assert.equal(state.summary?.existingSkillUpdates, 1);
});
