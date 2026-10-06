# Lab 04: AI Agent Frameworks — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps. Use a scripted
`LlmClient` so agent behaviour is deterministic.

---

## Exercise 1: Tool Registry with Schema Emission (E)

Register four tools; emit a JSON Schema array. Verify it parses and contains all four.

---

## Exercise 2: Argument Validation (M)

Type checks, `required`, `additionalProperties: false`, and a regex on `orderId`.

**Verify**: `getOrderStatus(orderId="DROP TABLE")` returns `INVALID_ARGUMENT` and the
handler is never invoked (assert with a counter).

---

## Exercise 3: Five-Strategy Parser (M)

Native call, fenced JSON, mini-language, bare JSON after `Action:`, fail-closed.

**Verify**: 15 fixtures; at most one action per parse; unknown tool -> `UNKNOWN_TOOL`
observation, not an exception.

---

## Exercise 4: ReAct Loop with Budgets (M)

`maxSteps`, `maxTokens`, `maxWallClockMs`, `maxToolCalls`. Loop until final answer.

**Verify**: a scripted model that never terminates stops exactly at `maxSteps` and
reports which budget fired.

---

## Exercise 5: Tool Error Recovery (M)

Tool returns `{"error":"TIMEOUT"}` once then succeeds. Assert recovery and trace
recording.

---

## Exercise 6: Loop Detection (M)

Detect repeated normalized `(tool, args)` within the last 6 steps; inject an
intervention observation.

**Verify**: a scripted 4-step identical loop is broken by step 3.

---

## Exercise 7: Observation Pruning (H)

Keep the last 3 steps verbatim; summarize older tool results to `tool=X status=ok
keys=...` under a token cap; drop oldest summaries first.

**Verify**: a 40-step trajectory stays under cap and every distinct tool result is
still represented.

---

## Exercise 8: Plan-Then-Act (M)

`Planner` emits typed `PlanStep`s; the loop may reorder or skip with a logged reason.

---

## Exercise 9: Router Agent (M)

Classify an intent into a fixed set and dispatch to a specialist; measure routing
accuracy on a labelled set.

---

## Exercise 10: Sequential Pipeline (M)

Fixed stages with typed handoffs; verify determinism across 20 identical runs.

---

## Exercise 11: Supervisor + Specialists (M)

Researcher/Analyst/Writer/Verifier behind a supervisor. Assert specialists never receive
tools outside their subset (guarded registry) and report tokens per specialist.

---

## Exercise 12: Parallel Fan-Out and Vote (M)

k=3 workers, different seeds, majority vote; measure agreement and correctness over 20
tasks.

---

## Exercise 13: Approval Gate (M)

Irreversible tools require `CompletableFuture<Approval>` with a timeout that denies.
Verify with no approver and with an approver.

---

## Exercise 14: Trajectory Regression Suite (H)

6 scenarios with expected tool sequences; ignore natural-language differences. Break a
tool description deliberately and confirm the suite fails.

---

## Exercise 15: Trace Emitter (M)

JSONL spans with hashed args/results; identical runs produce identical traces.

---

## Exercise 16: Token and Cost Accounting (M)

Per-step token counts with a price table; emit cost per task and per-tool attribution.

---

## Exercise 17: Injection via Tool Output (H)

A tool returns text containing "ignore previous instructions". Verify the guardrail
flags it and no unauthorized call results.

---

## Exercise 18: Step Efficiency Optimization (H)

Add a cost-aware tool selection step (skip an obviously unnecessary lookup); measure
the step-efficiency gain and the quality cost.

---

## Exercise 19: Self-Correction Critic (H)

A critic inspects the trajectory for claims unsupported by any observation; re-run up
to 2 repair steps. Measure the unsupported-claim count before and after.

---

## Exercise 20: Streaming Agent Output (M)

Stream plan and observations as they occur; measure time-to-first-user-visible-token.

---

## Stretch A: Agent State Machine (H)

Replace the loop with explicit states and transitions; assert no state is unreachable
and every cycle decrements a budget.

---

## Stretch B: Hierarchical Delegation (H)

Supervisor -> sub-supervisors -> workers with scoped registries at each level.

---

## Stretch C: Checkpoint and Resume (H)

Persist state mid-run and resume; verify the resumed trajectory matches the
uninterrupted one.

---

## Stretch D: Workflow vs Agent Comparison (H)

Same task implemented twice (written workflow vs ReAct agent); compare success, steps,
cost, and variance over 30 runs.

---

## Stretch E: Debate Pattern (H)

Two agents critique each other over 2 rounds; measure whether it beats single-pass and
whether errors are correlated.

---

## Stretch F: Idempotency Keys (M)

Deduplicate retried side effects by `(taskId, tool, normalizedArgs)`.