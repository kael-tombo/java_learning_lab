# Lab 04: AI Agent Frameworks — Mini Project

## Project: Agent Framework with Trajectory Tests and Safety Gates

Build an agent framework in Java 21 — registry, validation, parser, loop with budgets,
loop detection, pruning, approvals, tracing, and metrics — plus a supervisor and a
pipeline for comparison.

## Goal

A framework where a scripted agent terminates on every budget, unsafe tool calls are
blocked, a trajectory suite catches regressions, and the workflow-vs-agent trade is
measured rather than assumed.

## Requirements

### Phase 1: Tool Layer
- [ ] `ToolRegistry` with duplicate detection, revocation, and `scopedTo`.
- [ ] Six tools: three read-only, one reversible write, two irreversible.
- [ ] JSON Schema emission; valid output.
- [ ] Hand-written validators including a pattern on an order id and an email.

### Phase 2: Parser
- [ ] Five strategies, fail closed.
- [ ] 20 fixtures including malformed JSON, prose-only, and 5 injection attempts.
- [ ] At most one action per parse.

### Phase 3: Agent Loop
- [ ] `AgentConfig` with `maxSteps=8`, `maxTokens=24000`, `maxToolCalls=12`,
      `maxWallClockMs=5000`, `maxCostUsd=0.25`, `loopWindow=6`, `keepVerbatim=3`.
- [ ] All four budgets exercised in tests.
- [ ] Loop detection with normalized keys.

### Phase 4: Memory and Pruning
- [ ] Keep the last 3 verbatim; summarize older tool results.
- [ ] Token cap enforced; oldest summary dropped first.
- [ ] Verify every distinct tool result remains represented.

### Phase 5: Safety
- [ ] Approval gate: argument-scoped, timeout denies.
- [ ] Circuit breaker per tool.
- [ ] Side-effect cap per task.
- [ ] 100 injected documents / tool results; zero unauthorized calls.

### Phase 6: Trace and Metrics
- [ ] JSONL spans with hashed payloads; identical runs produce identical traces.
- [ ] Metrics: success rate, step efficiency, recovery rate, cost per task, cost by tool.

### Phase 7: Trajectory Suite
- [ ] 8 scenarios with expected tool sequences.
- [ ] Assertions on sequence and absence of unexpected `ERROR:` observations.
- [ ] Break-on-purpose test: corrupt a tool description; suite must fail.

### Phase 8: Orchestration Comparison
- [ ] Sequential pipeline with typed handoffs (deterministic).
- [ ] Supervisor with 3 specialists behind scoped registries.
- [ ] Fan-out k=3 with vote; measure agreement and accuracy.
- [ ] Report cost and variance for all three versus the single agent.

### Phase 9: Robustness
- [ ] Injection via tool output; verify it is flagged and harmless.
- [ ] Critic pass flagging unsupported claims; measure before/after.
- [ ] Client/cancellation path freeing resources.

### Phase 10: Reporting
- [ ] Five rendered trajectory timelines.
- [ ] Metrics table with variance across seeds.
- [ ] `REPORT.md` with the workflow-vs-agent conclusion.

## Directory Layout

```
lab04/
  src/com/aiengineering/lab04/{tool,parse,agent,memory,plan,orchestrator,trace,eval}/
  scenarios/trajectories.jsonl
  out/traces.jsonl
  out/metrics.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — registry + validators; handler counters prove invalid args never dispatch.
2. **M2** — parser passes 20 fixtures, fail-closed.
3. **M3** — agent runs a scripted 3-step trajectory exactly.
4. **M4** — each of the four budgets fires at least once in tests.
5. **M5** — loop detector breaks a scripted identical loop.
6. **M6** — pruning under cap; cited results preserved.
7. **M7** — approvals deny without an approver; permit with one.
8. **M8** — 100 injections; zero unauthorized calls.
9. **M9** — trajectory suite green; deliberately broken agent fails it.
10. **M10** — pipeline, supervisor, fan-out implemented and measured.
11. **M11** — critic pass reduces unsupported claims to zero.
12. **M12** — report written.

## Acceptance Criteria

- [ ] Invalid arguments never reach a handler (counter-verified).
- [ ] Unparseable output never throws out of the loop.
- [ ] All four budgets enforced and individually tested.
- [ ] Loop detector breaks a 4-step identical loop by step 3.
- [ ] Pruned prompt stays under cap with every distinct result represented.
- [ ] Irreversible tools never execute without a recorded approval.
- [ ] Zero unauthorized tool calls across 100 injections.
- [ ] Trajectory suite fails on a deliberately corrupted agent.
- [ ] Traces byte-identical across two runs with the same seed.
- [ ] Workflow-vs-agent comparison includes variance, not just means.

## Stretch Goals

- [ ] Hierarchical supervisor with sub-supervisors and nested scoping.
- [ ] Checkpoint/resume; verify the resumed trajectory matches.
- [ ] Debate pattern; measure against single-pass and check error correlation.
- [ ] Reflection loop using failures as few-shot examples.
- [ ] Cost-aware tool selection skipping unnecessary lookups.
- [ ] Streaming plan and observations; measure time-to-first-visible-token.
- [ ] Contract tests for tool providers.
- [ ] Chaos: tool providers failing intermittently; verify recovery.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Handler exception kills the run | Tool throws past the loop |
| Loop not detected | Args not normalized in the key |
| Approval succeeds with nobody | Approval not scoped or no timeout |
| Specialist writes | Shared registry instead of `scopedTo` |
| Context explodes | No pruning |
| Suite passes on a broken agent | Suite has no teeth |
| Traces differ run to run | Nondeterministic serialization |
| Fan-out helps nothing | Correlated errors across workers |
| Planner failure aborts | No degradation to a reactive step |

## Definition of Done

`REPORT.md` contains: the loop diagram, the tool catalogue with schemas, three
rendered trajectory timelines, the budget test results, the loop-detection example, the
pruning measurement, the safety test summary, the trajectory suite with the
break-on-purpose evidence, the orchestration comparison table with variance, the critic
pass results, and a "workflow or agent, per task type" conclusion.