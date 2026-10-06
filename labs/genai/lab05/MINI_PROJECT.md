# Lab 05: LLM Agent Frameworks — Mini Project

## Project: Support-Triage Agent with Tool Use, Budgets, and Traces

Build a production-shaped ReAct agent in Java 21 that triages customer support
tickets using a set of typed tools, with deterministic tests, budget enforcement,
trajectory assertions, and a full trace emitter.

## Goal

An agent that, given a ticket, decides: refund / status / escalate — using lookup
tools only, never inventing an order id, and always citing the tool output it used.
Measure success rate, step efficiency, cost, and recovery rate over 50 tickets.

## Requirements

### Phase 1: Tool Layer
- [ ] `ToolRegistry` with duplicate detection, revocation, and role scoping.
- [ ] Six tools: `findCustomerByEmail`, `getOrderStatus`, `listRecentOrders`,
      `checkRefundPolicy`, `createEscalationTicket`, `sendStatusReply`.
- [ ] Each tool: typed schema, `additionalProperties: false`, patterns on ids/email.
- [ ] Handlers return JSON strings; every failure path returns
      `{"error": "CODE", "detail": "..."}` — no exceptions escape.
- [ ] Mark `createEscalationTicket` and `sendStatusReply` irreversible.
- [ ] Simulated latency per tool (20-300 ms) to expose latency interactions.

### Phase 2: Parser
- [ ] All five parse strategies from THEORY / Exercise 3.
- [ ] A `ScriptedLlmClient` that throws when its script is exhausted.
- [ ] 20 fixtures: happy paths, fenced blocks, mini-language, malformed JSON,
      prose-only, and 4 injection attempts in the argument blob.

### Phase 3: The Loop
- [ ] `AgentConfig`: `maxSteps=8`, `maxTokens=24000`, `maxWallClockMs=5000`,
      `maxCostUsd=0.20`, `loopWindow=6`, `keepVerbatim=3`.
- [ ] Token counting via a whitespace/char-ratio estimator stub.
- [ ] Loop detection on normalized `(tool, args)`.
- [ ] Observation pruning with the oldest-summary-first drop order.
- [ ] Approval gate: `CompletableFuture<Approval>` with a 50 ms timeout -> deny.

### Phase 4: Evaluation Harness
- [ ] 50 tickets with gold labels and required evidence fields.
- [ ] Scored: `taskSuccess`, `stepEfficiency`, `toolCallPrecision/Recall`,
      `recoveryRate`, `costPerTask`, `p95Latency`.
- [ ] 8 fault-injection scenarios (tool timeout, empty result, ambiguous customer,
      missing order id, duplicate escalation, injection attempt, budget squeeze).

### Phase 5: Observability
- [ ] JSONL traces: `{runId, step, thought, tool, argsHash, resultHash, latencyMs,
      tokensIn, tokensOut, costUsd}`.
- [ ] A `TraceReport` printer rendering one trajectory in a readable timeline.
- [ ] Aggregate metrics to `out/metrics.json`.

### Phase 6: Regression Suite
- [ ] 8 scenarios with expected tool sequences.
- [ ] Assertions: sequence matches, no unexpected `ERROR:` observations, budget
      respected, approval enforced.
- [ ] Negative test: corrupt a tool description and assert the suite fails.

## Suggested Trajectories

| Ticket | Expected tool sequence | Notes |
|--------|------------------------|-------|
| "Where is order A-1001?" | `getOrderStatus` | single step |
| "I want a refund" (email known) | `findCustomerByEmail`, `listRecentOrders`, `checkRefundPolicy` | 3 steps, needs evidence |
| "Cancel my order" (id unknown) | `findCustomerByEmail`, `listRecentOrders`, `createEscalationTicket` | approval required |
| Ambiguous email (2 customers) | `findCustomerByEmail`, `sendStatusReply` | must ask, not guess |

## Directory Layout

```
lab05/
  src/com/genai/lab05/{agent,llm,tool,parse,memory,trace,eval}/
  tickets/tickets.jsonl
  out/traces.jsonl
  out/metrics.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — tools + registry + validators; handler-invocation counters in tests.
2. **M2** — parser passes all 20 fixtures, fail-closed on unparseable output.
3. **M3** — agent runs a scripted 3-step trajectory exactly.
4. **M4** — budgets enforced; loop detector breaks a scripted 4-step loop.
5. **M5** — pruning keeps prompt under cap while preserving every distinct result.
6. **M6** — 50-ticket eval written; baseline metrics recorded.
7. **M7** — fault injection: all 8 scenarios produce the expected safe behavior.
8. **M8** — trajectory suite green; deliberately-broken variant fails.

## Acceptance Criteria

- [ ] Task success >= 0.80 on the 50-ticket set.
- [ ] Step efficiency >= 0.70.
- [ ] Zero fabricated order ids — every id in an answer appears in a tool result.
- [ ] Recovery rate >= 0.80 on injected tool errors.
- [ ] No irreversible tool executes without an approval decision recorded.
- [ ] `maxSteps`, `maxTokens`, and wall clock each trigger at least once in tests.
- [ ] Traces are byte-identical across two runs with the same seed.

## Stretch Goals

- [ ] Add `checkInventory` and demonstrate a 5-step recovery path.
- [ ] Self-consistency: 3 trajectories, majority vote on the label.
- [ ] Critic pass that flags claims absent from any observation.
- [ ] Supervisor + specialists (researcher/analyst/writer) for the escalation flow.
- [ ] Replay a trace with a modified tool response to test robustness.
- [ ] Cost-aware tool selection: skip `listRecentOrders` when `getOrderStatus`
      already answers the question (saves ~40% of steps).
- [ ] Token-accurate counting by wiring a real tokenizer interface.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Agent invents an order id | Observation pruned before the answer step |
| Infinite loop on one tool | Loop detector key not normalizing args |
| Validation skipped | Handler called directly instead of via registry |
| Escalations sent unreviewed | Approval flag not set on the tool |
| Script exhausted | Loop not converging — the script length is the spec |
| Traces differ run to run | `HashMap` iteration order in serialization |
| Cost explodes with long history | Pruning dropping nothing (cap not enforced) |

## Definition of Done

`REPORT.md` contains: tool catalog with schemas, 3 rendered trajectory timelines,
the metrics table, fault-injection results, cost breakdown by tool, and a
"where would I put the model-chosen control flow and where I would not" section.