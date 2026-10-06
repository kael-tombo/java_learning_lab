# Lab 05: LLM Agent Frameworks — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps. Use a stub
`LlmClient` returning scripted responses so agent tests are deterministic.

---

## Exercise 1: Tool Registry with Schema Emission (E)

Implement `ToolRegistry` with `register`, `find`, `schemas()` returning a JSON
Schema array. Two tools: `getOrderStatus(orderId)`, `listOpenInvoices(customerId)`.

**Verify**: `schemas()` parses as valid JSON with exactly 2 entries.

---

## Exercise 2: Argument Validation Before Dispatch (M)

Add a hand-written validator per tool: type checks, required fields,
`additionalProperties: false` rejection, and a regex on `orderId`.

**Verify**: `getOrderStatus(orderId="DROP TABLE")` returns
`{"error":"INVALID_ARGUMENT"}` and the handler is **never** invoked (assert with a
counter).

---

## Exercise 3: Action Parser with Five Strategies (M)

Write `ActionParser.parse(String raw)` handling:
1. native tool-call JSON,
2. ```` ```json ```` fenced block,
3. bare JSON after `Action:`,
4. mini-language `Action: name(k=v, k2="v2")`,
5. anything else -> `FINAL` with the raw text.

**Verify**: 12 fixtures, one per branch and 2 adversarial; at most one action per
parse; unknown tool names become `UNKNOWN_TOOL` errors, not exceptions.

---

## Exercise 4: ReAct Loop with Budgets (M)

Implement `Agent.run(goal)` with `maxSteps`, `maxTokens`, `maxWallClockMs`. The
loop: build prompt -> call model -> parse -> dispatch tool -> append observation.

**Verify**: with a scripted model that never terminates, the loop stops exactly at
`maxSteps` and reports `budgetExhausted = true` with no leaked thread.

---

## Exercise 5: Tool Error Recovery (M)

Make the stub tool return `{"error":"TIMEOUT"}` on the first call and success after.
Assert the agent recovers on the next step and the trajectory records the failure.

**Verify**: recovery rate metric computed across 10 scenarios.

---

## Exercise 6: Loop Detection (M)

Detect a repeated `(tool, args)` pair within the last 6 steps. On detection,
inject an observation: `"You already called this tool with the same arguments.
Change approach or answer now."` and count the intervention.

**Verify**: a scripted loop of 4 identical steps is broken by step 3.

---

## Exercise 7: Observation Pruning (H)

Implement pruning that keeps the full history for the last 3 steps and replaces
older tool results with a one-line summary (`tool=NAME status=ok keys=a,b,c`),
respecting a token cap.

**Verify**: a 40-step trajectory's prompt stays under the cap; the final step still
sees every *distinct* tool result at least once.

---

## Exercise 8: Plan-Then-Act (M)

Add a `Planner` interface that emits a `List<PlanStep>` before the ReAct loop. The
loop may reorder or skip steps but must justify each deviation in one line.

**Verify**: 5 scenarios; deviations are logged and counted; a plan with 0 steps
immediately returns `FINAL`.

---

## Exercise 9: Hierarchical Orchestration (M)

Build `Supervisor` with specialists `Researcher`, `Analyst`, `Writer`. Supervisor
routes via a scripted router; each specialist is an agent with its own tool
subset. Synthesize a final answer.

**Verify**: specialists never receive tools outside their subset (assert with a
guarded registry); record tokens per specialist.

---

## Exercise 10: Parallel Fan-Out and Vote (M)

Run k=3 independent workers on the same task with different seeds, then vote.
Measure agreement rate and majority correctness on 20 tasks.

**Verify**: agreement rate correlates with correctness; document the correlation.

---

## Exercise 11: Human Approval Gate (M)

Mark tools `reversible` or `irreversible`. Before dispatching an irreversible tool,
emit an `ApprovalRequest` and block on a `CompletableFuture<Approval>` with a
timeout. On timeout, deny and record it.

**Verify**: with no approver, `refund` never executes; with an approver it does.

---

## Exercise 12: Trajectory Regression Suite (H)

Author 6 scenarios with expected tool sequences, e.g.
`["lookupCustomer", "listInvoices", "getOrderStatus"]`. Run them on every change and
fail on sequence mismatch (ignore natural-language differences).

**Verify**: deliberately break one tool's description and confirm the suite fails.

---

## Exercise 13: Trace Emitter (M)

Emit a JSONL trace: `{runId, step, thought, tool, argsHash, resultHash, latencyMs,
tokensIn, tokensOut}`. Hash long payloads instead of inlining them.

**Verify**: one line per step; hashes are stable across identical runs.

---

## Exercise 14: Token/Cost Accounting (M)

Track `tokensIn`, `tokensOut` per step with a price table per model. Emit
`costPerTask` and a per-tool attribution table.

**Verify**: sum of step costs equals `costPerTask`; the most expensive tool call
is identified.

---

## Stretch A: Workflow vs Agent Comparison (H)

Implement the same task (refund eligibility decision) twice: once as a written
workflow, once as a ReAct agent. Compare success rate, steps, cost, and variance
across 30 runs.

**Expected**: workflow wins on determinism and cost; document where the agent wins.

---

## Stretch B: Self-Correction Pass (H)

After the loop ends, run a `Critic` that inspects the trajectory for unsupported
claims (claims not present in any observation) and re-runs up to 2 repair steps.

**Verify**: unsupported-claim count drops to 0 after repair on the test set.

---

## Stretch C: Graph-Based Termination (H)

Replace the linear loop with a state machine: `PLAN -> ACT -> OBSERVE ->
REFLECT -> (back to ACT | COMPLETE | ESCALATE)`. Assert no state is unreachable
and every cycle decrements a budget.