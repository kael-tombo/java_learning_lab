# Lab 10: LLM Safety & Alignment — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Unicode Normalization and Invisible Character Detection (E)

Implement NFKC normalization, strip zero-width characters (`U+200B..200D`, `U+FEFF`),
detect bidi control characters, and produce a report of what was removed.

**Verify**: `"ig\u200Bnore"` normalizes to `"ignore"` and the hidden character is
reported.

---

## Exercise 2: Encoding-Aware Normalization (M)

Decode segments that look like base64, hex, or ROT13; run classification on both the
raw and decoded forms; keep both in the audit record.

**Verify**: `base64("aWdub3JlIGFsbA==")` -> `"ignore all"` is caught.

---

## Exercise 3: Length and Rate Limits (E)

Implement an input length cap (token-based) and a per-user rate limiter with a token
bucket. Return typed errors: `INPUT_TOO_LONG`, `RATE_LIMITED`.

---

## Exercise 4: Instruction Collision Detection (M)

Given a document with a benign prefix and a trailing instruction block, detect the
collision: heuristic markers (`--- SYSTEM`, `assistant:`, `<|im_start|>`, "new
instructions:", "override") plus a position-based heuristic (instructions appearing
after the midpoint of retrieved content).

**Expected**: catches the natural-language version; documents the false-positive rate.

---

## Exercise 5: Delimiter and Labelling Defense (E)

Implement `renderContext(chunks)` that wraps untrusted content in explicit markers,
labels it as data, and appends a note that content inside is never instructions.
Compare the stub model's compliance rate with and without the delimiters.

**Expected**: delimiters reduce but do not eliminate compliance. Record both numbers.

---

## Exercise 6: Privilege Separation Test (H)

Build an agent where the system message contains policy and tool permissions, and a
retrieved document claims to grant new permissions. Assert:
1. the tool registry still only exposes the allowed tools,
2. the gate rejects any attempted unauthorized call,
3. the model narrating "permission granted" changes nothing.

**Verify**: zero unauthorized calls across 100 injected documents.

---

## Exercise 7: Argument Injection via Retrieved Content (M)

Deliver a tool argument value through a retrieved document (an "order id" containing
`A-1001'; DROP TABLE`). Assert pattern validation rejects it before dispatch.

**Verify**: handler invocation count is zero; observation is `INVALID_ARGUMENT`.

---

## Exercise 8: Output Guardrail Pipeline (M)

Implement the eight-stage output pipeline from THEORY section 7, with each stage
returning `PASS`, `BLOCK`, or `FAIL_CLOSED`. Verify that a classifier exception
produces `FAIL_CLOSED`.

---

## Exercise 9: PII and Secret Scrubbing (M)

Detect emails, phone numbers, credit-card-shaped digits, API keys (prefix patterns),
and account numbers in outputs. Redact with typed placeholders (`[EMAIL]`).

**Verify**: 20 fixture outputs; zero residual matches after re-scanning.

---

## Exercise 10: Refusal vs Over-Refusal (M)

Build 60 disallowed prompts and 60 benign lookalikes. Sweep the refusal threshold.
Plot refusal rate and over-refusal rate on one chart.

**Expected**: a clear Pareto trade-off; document the operating point and its cost.

---

## Exercise 11: Jailbreak Mutation Engine (H)

Implement 12 mutation operators from THEORY section 9. Apply each to 20 base prompts
and measure compliance rate before and after each defense layer.

**Deliverable**: a matrix of attack x layer with pass/fail.

---

## Exercise 12: Many-Shot Attack (M)

Construct a prompt with k benign Q/A pairs followed by one adversarial pair. Sweep
`k` in {0, 2, 5, 10}.

**Expected**: compliance rises with k; document the threshold where it breaks.

---

## Exercise 13: Multi-Turn Injection (H)

Split the payload across turns: turn 1 sets up innocuous context, turn 2 contains a
partial instruction, turn 3 completes it. Measure whether per-turn filters catch it.

**Expected**: neither turn alone triggers; stateful detection is required.

---

## Exercise 14: Image-Based Injection (H)

Render instruction text into an image and pass it as multimodal input. Assert the
image-text guardrail flags it and that the parser never treats image text as
instructions.

---

## Exercise 15: Red-Team Finding -> Regression Test (M)

Simulate a found bypass, write the permanent test, then verify that reverting the
fix makes the test fail. This proves the test has teeth.

---

## Exercise 16: Grounded Output Verification (M)

For answers generated with retrieved context, verify every atomic claim is supported
and that abstention is used when evidence is absent.

**Expected**: report faithfulness and abstention accuracy separately.

---

## Exercise 17: Category-Specific Thresholds (M)

Implement per-category refusal thresholds (security research, creative writing,
medical, legal, self-harm). Measure compliance on genuinely disallowed prompts per
category at each threshold.

**Expected**: self-harm thresholds differ sharply from security research ones.

---

## Exercise 18: Safe-Mode Degradation (M)

Implement a `safeMode` flag: strictest policy, tools disabled, retrieval off, output
classifier forced to block. Trigger it on an anomaly signal and verify the service
still answers safely.

---

## Exercise 19: Audit Log With Integrity (H)

Write an append-only audit log with a hash chain (`record_i` includes
`hash(record_{i-1})`). Verify tampering with any record breaks the chain.

---

## Exercise 20: Attack Suite Regression Runner (H)

Aggregate all cases into a suite with expected outcomes. Runner exits non-zero on
any violation and reports per-layer attribution (which layer failed).

---

## Stretch A: Representation Probing (H)

Analyze output embedding similarity between compliant and refusing responses to the
same prompt; test whether a linear probe separates them. Report accuracy and note
that a probe is a detector, not a control.

---

## Stretch B: Adversarial Fine-Tuning (H)

Generate an adversarial dataset from Exercise 11 outputs and train a small adapter
(Lab 06) on compliant responses. Measure attack success rate before and after, plus
benign accuracy to detect over-correction.

---

## Stretch C: Constitutional Critic (H)

Implement a critic model (rule-based) that checks outputs against 5 written
principles. Measure violation detection recall and false-positive rate versus a
single-classifier approach.

---

## Stretch D: Canary Leakage Detection (H)

Plant canary strings in the system prompt; verify they never appear in outputs across
1,000 requests including adversarial ones. Any leak is a hard failure.

---

## Stretch E: Rate-Limit Adaptive Attack (M)

Probe the rate limiter and document the detection signal for enumeration attacks.