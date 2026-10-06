# Lab 05: LLM Agent Frameworks — Real-World Project

## Project: Autonomous Operations Agent for an Internal Platform

Design and build an agent that runs real operational tasks against internal
systems — provisioning, access review, incident triage, cost analysis — with the
safety, observability, evaluation, and human-approval machinery a production
deployment demands.

## Context

This is the shape of every serious internal agent: a model choosing among typed
tools that touch real infrastructure. The hard parts are not the loop — they are
(a) not letting the model take an irreversible action by accident, (b) proving the
agent actually works, and (c) operating it at 3am with a runbook.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., submitted
  28 Oct 2022; v3 8 Mar 2023) — https://arxiv.org/abs/2210.03629 — takeaway for this
  lab: interleaving thought, action, and observation improves interpretability and
  task success over act-only or reason-only baselines — the loop structure implemented
  in `Agent.java` and measured by the trajectory suite.
- "Constitutional AI: Harmlessness from AI Feedback" (Bai et al., submitted 1 Dec 2022;
  rev. 21 Dec 2024) — https://arxiv.org/abs/2212.08073 — takeaway for this lab: the
  policy layer that constrains agent behaviour can be a written set of principles
  checked at decision time, which is how `PolicyGate` enforces the refusal and
  escalation rules below without retraining the model.

## System Architecture

```
   operator / on-call / scheduled job
                |
       +--------v---------+     identity + approval token
       |  Control Plane   |
       |  (Java service)  |
       +--------+---------+
                |
     +----------v-----------+
     |  Task Router        |  task type -> agent profile (tool set, budgets)
     +----------+-----------+
                |
     +----------v-----------+
     |  Agent Runtime      |
     |  +---------------+  |
     |  | policy (LLM)  |  |  model + system policy + approval context
     |  +-------+-------+  |
     |          | action   |
     |  +-------v-------+  |  allowlist, arg schema, pattern, side-effect class,
     |  | Policy Gate   |  |  budget, rate limit, approval token
     |  +-------+-------+  |
     |          | approved |
     |  +-------v-------+  |
     |  | Tool Executor |  |  typed handlers, idempotency keys, retries,
     |  +-------+-------+  |  timeouts, circuit breakers
     |          | result   |
     |  +-------v-------+  |  prune, sanitize, truncate
     |  |  Memory       |  |
     |  +-------+-------+  |
     |          |          |
     |     budget check ----+--> exhausted -> escalate
     +----------+----------+
                |
     +----------v-----------+
     |  Trace Store        |  full trajectory, replayable
     +----------+----------+
                |
     +----------v-----------+
     |  Eval + Metrics     |  success, step efficiency, recovery, cost,
     |  + alerting         |  guardrail violations, approval denials
     +----------+----------+
                |
     +----------v----------+
     |  Human Escalation   |  Slack/PagerDuty with summary + evidence links
     +---------------------+
```

## Component Specs

### 1. Task Router and Profiles
Each task type gets an explicit profile:

```yaml
access_review:
  tools: [listEmployees, listGrants, suggestRevocations]
  maxSteps: 6
  maxWallClock: 120s
  irreversible: []            # suggestions only, humans apply changes
cost_analysis:
  tools: [queryBilling, aggregateSpend, compareBudget]
  maxSteps: 4
incident_triage:
  tools: [fetchAlerts, getLogs, getMetrics, runDiagnostics]
  maxSteps: 10
  maxWallClock: 300s
  irreversible: [restartService]   # approval required
```

Profile-based budgets mean a routine task can never inherit an expensive task's
budget. Unknown task types are rejected rather than defaulted.

### 2. Policy Gate
Runs before every tool dispatch:
1. Tool is in the profile allowlist (scoped registry, not a global check).
2. Arguments pass schema + pattern validation.
3. Rate limit per tool and per task (protects fragile systems).
4. If irreversible: an approval token exists, is unexpired, and covers
   `(tool, normalizedArgs)` — approvals are argument-scoped, not tool-scoped.
5. Cumulative side-effect count under `maxWrites`.
6. No tool call may occur while a circuit breaker for that tool is open.

Denials are **observations**, not errors, and are logged as guardrail events so
they show up in metrics rather than disappearing into the trace.

### 3. Tool Executor
- Typed handlers with declared timeouts and retry policy (idempotent tools only).
- Idempotency keys derived from `(taskId, step, tool, normalizedArgs)` so a retry
  cannot double-apply.
- Circuit breaker per tool: after N failures in a window, open the breaker and make
  the agent escalate with context instead of hammering a down service.
- All results sanitized and length-capped before entering memory.

### 4. Memory and Context Management
- Working memory with the pruning policy from Exercise 7.
- **Evidence ledger**: every claim the final answer makes must map to a tool result.
  The answer step is validated against the ledger; unsupported claims are stripped
  or the run escalates.
- Semantic memory: past similar tasks retrieved as few-shot examples (Lab 04 infra).
- Hard cap on tool count in the prompt — 40 tools is a cost and confusion line.

### 5. Human Escalation
- Triggers: budget exhausted, circuit breaker open, approval missing, confidence
  below threshold, or any irreversible action.
- Payload: goal, steps taken, evidence gathered, what remains unknown, the exact
  proposed action awaiting a decision.
- Symmetric path: a human can answer a question mid-run (inject an observation).
- Every escalation is an SLO-tracked incident: median time-to-human-decision is a
  headline metric.

### 6. Observability
- Full trajectory per run, replayable offline against recorded tool results.
- Metrics: task success, step efficiency, tool precision/recall, recovery rate,
  tokens and dollars per task, guardrail denial counts by reason, escalation rate,
  time-to-decision, loop-detector trips, pruning events.
- Distributed tracing across policy, gate, and executor spans.
- Every log line carries `taskId` so cost can be attributed per task type and owner.

### 7. Evaluation Harness
- Scenario suite (200+ cases) with expected tool sequences and expected outcomes.
- Golden traces for regression: any change that alters a golden trajectory is a
  review-required diff.
- Continuous eval on production traces: sample completed runs, score them offline
  with a judge model plus rule checks, and feed the failures back into the suite.
- Prompt/tool-description changes gated on eval delta, like Lab 03's optimizer.

### 8. Safety and Data Handling
- No shell, no generic SQL, no arbitrary HTTP; every tool is a narrow typed operation.
- PII scrub on tool results before they enter memory; raw values held only in the
  scoped tool, never echoed into prompts.
- Read-only by default; write tools require both a profile declaration and approval.
- Full audit log of policy decisions with argument hashes, retained per compliance
  requirements.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Task success (eval suite) | >= 0.90 on read-only tasks, >= 0.75 on write tasks |
| Step efficiency | >= 0.70 |
| Recovery after tool error | >= 0.85 |
| Unauthorized tool call rate | 0 |
| Unapproved irreversible action rate | 0 |
| p95 latency (read-only tasks) | <= 20 s |
| Cost per task | <= $0.15 |
| Escalation decision time (median) | <= 5 min |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Runaway loop | Loop-detector trip counter | Break with a nudge, then escalate |
| Duplicate side effect after retry | Idempotency-key collision log | Key on `(taskId, tool, args)`; verify state before retry |
| Tool outage | Circuit breaker state | Break open, escalate with partial context |
| Argument injection | Schema validation failure | Pattern checks + allowlist + no free-form tools |
| Evidence fabrication | Ledger validation on the answer step | Strip unsupported claims or escalate |
| Prompt bloat from 40 tools | Prompt token metric | Profile-scoped tool sets |
| Cost spike from long histories | Pruning event counter | Enforce token cap, drop oldest summaries |
| Model upgrade regression | Golden trace diff + eval gate | Canary the model, keep previous version pinned |
| Human escalation ignored | Escalation age SLO | Page after N minutes, cap autonomous retries |
| Stale semantic memory examples | Example age metric | TTL on stored trajectories |

## Milestones

- **M1** — tool layer with schemas, idempotency keys, timeouts, circuit breakers.
- **M2** — agent runtime with profiles, budgets, memory, pruning.
- **M3** — policy gate with argument-scoped approvals; guardrail metric wiring.
- **M4** — evidence ledger and answer validation.
- **M5** — 200-scenario eval suite plus golden traces; all green.
- **M6** — escalation path (Slack/PagerDuty) with SLO tracking.
- **M7** — continuous eval on production traces feeding the suite.
- **M8** — runbook, dashboards, and a game-day exercise with a deliberately broken tool.

## Deliverables

1. Agent runtime, tool executors, policy gate, escalation integration.
2. `EvalHarness` with the scenario suite and golden traces.
3. Dashboards: quality, cost, guardrails, escalations.
4. `runbook.md` — triage by symptom (loops, denials, tool outages, slow runs).
5. `THREAT_MODEL.md` — injection vectors, blast radius per tool, mitigations.

## Definition of Done

- [ ] Zero unapproved irreversible actions across 1000 replayed production traces.
- [ ] Zero unauthorized tool calls across the eval suite.
- [ ] Every final answer's claims map to a tool result.
- [ ] Golden trace suite green; a deliberately degraded config fails the gate.
- [ ] Every run is replayable offline.
- [ ] Runbook written by someone who did not build the runtime, and tested in a game day.