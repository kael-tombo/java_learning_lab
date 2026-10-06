# Lab 03: Prompt Engineering Patterns — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. All Java 21, no external dependencies.

---

## Exercise 1: Template Engine (E)

Implement `String render(String template, Map<String,String> vars)` supporting
`{{name}}` placeholders, throwing `IllegalArgumentException` on any placeholder
left unfilled or any variable supplied but unused.

**Expected**: `"Hi {{a}}, order {{b}}"` with `{a:Ann, b:7}` -> `"Hi Ann, order 7"`.

---

## Exercise 2: Sectioned Builder (E)

Create `PromptBuilder` with `system()`, `instructions()`, `context()`, `input()`,
`schema()` methods. Enforce order on `build()`. Add `assertNoUnfilled()` that
throws if a `{{var}}` survives rendering.

**Verify**: calling `input()` before `context()` throws with a clear message.

---

## Exercise 3: Few-Shot Formatter (E)

Implement `String fewShot(List<Example> examples)` rendering
`Input: ...\nOutput: ...` pairs with a trailing newline. Reject examples whose
output is empty.

**Verify**: 3 examples produce exactly 6 lines.

---

## Exercise 4: Deterministic Demo Selection (M)

Given labeled data, select k few-shot demonstrations that straddle the decision
boundary: pick the k/2 lowest-confidence and k/2 highest-confidence items plus
one from each class, using a seeded `Random` for the within-stratum choice.

**Expected**: the selected set always contains at least one example per class.

---

## Exercise 5: Structured Output Parser (M)

Write `IntentParser` for schema
`{"intent":"refund|status|other","amount_cents":int|null,"reason":string}`.
Extract the first balanced `{...}` block, parse it, validate ranges
(`reason` <= 200 chars, `amount_cents >= 0`), and return a `Result` with either a
value or a typed error.

**Expected**: truncated JSON returns an error, not an exception escaping.

---

## Exercise 6: Self-Repair Loop (M)

Implement `parseWithRepair(String raw, int maxAttempts)`:
1. Try `parse`. On failure, build a repair prompt:
   `"Your output was invalid: <error>. Return only corrected JSON."`
2. Retry with the repaired model stub. After `maxAttempts`, fall back to a
   regex + keyword extractor.

**Verify**: a stub that succeeds on attempt 2 returns the corrected value; a stub
that always fails returns the fallback value and marks `usedFallback=true`.

---

## Exercise 7: Decomposed Prompting (H)

Split the task "compute total order cost after a 10% coupon and free shipping over
$50" into `Planner -> Solver -> Combiner` interfaces. Implement each with plain
Java arithmetic and show the decomposition produces the same answer as the
monolithic version on 5 test orders.

**Verify**: no stage parses free text — stages exchange typed records.

---

## Exercise 8: Chain-of-Verification (M)

Implement `verify(String claim, List<String> evidence)`: split the claim into
atomic statements, mark each `supported` / `unsupported` / `contradicted` by exact
and normalized substring match, and return a verdict plus the unsupported list.

**Expected**: a claim mentioning a price absent from the evidence is flagged.

---

## Exercise 9: Prompt Optimizer (H)

Build `PromptOptimizer` with a mutation set (add a "Think step by step" line,
swap "concise" for "thorough", reorder sections, add a counter-example) and
hill-climbing over a 40-example validation set scored by exact-match against gold
labels. Stop after 20 iterations or when no improvement for 5.

**Verify**: it never selects a template that lowers the best score; log every
iteration's score.

---

## Exercise 10: Prefix-Cache Friendly Layout (M)

Given a template with variables, write `splitStatic(String template, Set<String> vars)`
returning `staticPrefix` and `dynamicSuffix`, moving every volatile variable after
all stable text.

**Verify**: for a 4k-token system prompt plus a user query, the static prefix is
identical across 100 renders, so a prefix-keyed cache would hit 100%.

---

## Exercise 11: Token Budget Guard (M)

Implement `String enforceBudget(String prompt, int maxTokens, Tokenizer stub)` that
truncates the **context** section first, then the few-shot block, never the
schema or the final instruction — and reports what it dropped.

**Verify**: the schema string survives every truncation.

---

## Exercise 12: Prompt Registry with Rollback (M)

Implement a registry keyed by `name:version`, `promote(name, version)`,
`rollback(name)`, and a render cache keyed by `sha256(name+version+rendered)`.
Assert rollback restores the previous promoted version within one call.

---

## Stretch A: Prompt Injection Canary (H)

Add 8 injection strings ("Ignore all previous instructions", base64 "reveal system
prompt", role-tag spoofing, markdown image exfil). Verify each is caught by the
delimiter + policy rules from THEORY section 9, and that the schema parser rejects
any resulting malformed output.

---

## Stretch B: Self-Consistency Voting (H)

Sample k = 5 answers at temperature 0.7, extract the final answer from each with
the structured parser, and return the majority plus the agreement rate.

**Verify**: with 3 agreeing and 2 differing, agreement = 0.6 and the majority wins.