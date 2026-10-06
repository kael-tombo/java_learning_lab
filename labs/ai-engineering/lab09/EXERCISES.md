# Lab 09: AI Security — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Unicode Normalization and Invisible Characters (E)

NFKC, strip zero-width and bidi controls, report findings.

**Verify**: `"ig\u200Bnore"` normalizes to `"ignore"` with a finding recorded.

---

## Exercise 2: Recursive Decode and Classify (M)

Decode base64, hex, ROT13, URL-encoding; classify raw and all decoded forms; bound the
depth.

**Verify**: a base64 payload is caught; depth is bounded so a decode bomb cannot run
away.

---

## Exercise 3: Length and Rate Limits (E)

Token-based input caps; token-bucket rate limiter per tenant; typed errors.

---

## Exercise 4: Instruction Collision Detection (M)

Heuristic markers plus a position heuristic; report confidence per finding; measure the
false-positive rate on legitimate documents.

---

## Exercise 5: Injection Detector (H)

Implement 12 attack signatures and 8 mutation operators; measure detection per family.

**Verify**: 100% detection on the internal suite; document the families the detector
misses.

---

## Exercise 6: Delimiter Effectiveness Measurement (M)

Render untrusted content with and without markers; measure compliance rate with a stub
model.

**Expected**: markers reduce compliance but do not eliminate it; report both numbers.

---

## Exercise 7: Privilege Separation Test (H)

An agent whose system message grants capabilities it should not have. Assert the
registry and gate deny regardless of what the model narrates.

**Verify**: zero unauthorized calls across 100 injected documents.

---

## Exercise 8: Argument Injection (M)

Deliver a malicious tool argument through retrieved content; assert pattern validation
rejects it before dispatch (handler invocation count stays zero).

---

## Exercise 9: Output Guardrail Chain (M)

Eight stages, each PASS/BLOCK/FAIL_CLOSED; verify an exception in any stage blocks.

---

## Exercise 10: PII and Secret Scrubbing (M)

Detect emails, phone numbers, card-shaped digits, API keys, account numbers; redact
with typed placeholders; re-scan after redaction.

**Verify**: zero residual matches.

---

## Exercise 11: Canary Leakage Test (M)

Plant canary strings in the system prompt; run 1,000 requests including adversarial
ones; scan outputs.

---

## Exercise 12: Cross-Tenant Cache Isolation (M)

Tenant-scoped cache keys; a leak test that fails when scoping is removed.

---

## Exercise 13: Retrieval Pre-Filter Isolation (M)

Index namespaces with pre-filtering; assert an unauthorized query returns zero chunks
from another tenant.

---

## Exercise 14: Approval Gate (M)

Argument-scoped approvals with expiry and timeout-denies; verify a different argument
set is not covered.

---

## Exercise 15: Side-Effect Caps and Idempotency (M)

Cap writes per task; dedupe retries by `(taskId, tool, normalizedArgs)`.

---

## Exercise 16: Refusal and Over-Refusal (M)

Disallowed and benign-lookalike sets; sweep the threshold; report both rates and choose
an operating point.

---

## Exercise 17: Category-Specific Thresholds (M)

Different thresholds per category; measure compliance on genuinely disallowed prompts
per category.

---

## Exercise 18: Multi-Turn Injection (H)

Split a payload across three turns; verify per-turn filters do not catch it and that
stateful accumulation does.

---

## Exercise 19: Image-Borne Injection (H)

Render instruction text into an image; assert the guardrail flags it and image text is
never treated as instructions.

---

## Exercise 20: Audit Log with Hash Chain (H)

Append-only log with `hash(record_i)` including `hash(record_{i-1})`; verify tampering
breaks verification.

---

## Exercise 21: Abuse Detection (M)

Detect burst patterns, systematic argument probing, and repeated long inputs; apply
throttling rather than hard blocking.

---

## Exercise 22: Supply Chain Verification (H)

Verify pinned model SHAs, adapter checksums, and dataset hashes; fail the build on a
mismatch.

---

## Stretch A: Adversarial Fine-Tuning (H)

Train an adapter on compliant responses to found attacks; measure attack success rate
before/after plus benign accuracy to detect over-correction.

---

## Stretch B: Representation Probe (H)

Train a linear probe to separate compliant from refusing responses; report accuracy and
note it is a detector, not a control.

---

## Stretch C: Constitutional Critic (H)

A rule-based critic checking outputs against five written principles; compare
detection recall and false positives against a single classifier.

---

## Stretch D: Rate-Limit Enumeration Detection (M)

Probe the limiter and document the detection signal.

---

## Stretch E: Golden Security Test Suite (M)

Aggregate all cases; runner exits non-zero on any violation with per-layer attribution.

---

## Stretch F: Secret Rotation Drill (M)

Rotate a leaked secret and verify the old value no longer works anywhere; measure
propagation time across caches and indexes.