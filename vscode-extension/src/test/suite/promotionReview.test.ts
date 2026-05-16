import test from "node:test";
import assert from "node:assert/strict";
import { defaultPromotionReviewReason, normalizePromotionReviewReason } from "../../promotionReview";

test("defaultPromotionReviewReason gives accepted reviews an editable default", () => {
  assert.match(defaultPromotionReviewReason("accepted"), /Accepted/);
  assert.equal(defaultPromotionReviewReason("rejected"), "");
});

test("normalizePromotionReviewReason rejects blank review reasons", () => {
  assert.equal(normalizePromotionReviewReason(undefined), undefined);
  assert.equal(normalizePromotionReviewReason("   "), undefined);
  assert.equal(normalizePromotionReviewReason(" Reviewed "), "Reviewed");
});
