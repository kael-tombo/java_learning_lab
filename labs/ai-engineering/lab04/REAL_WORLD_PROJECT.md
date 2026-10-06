# Lab 04: AI Agent Frameworks — Real-World Project

## Project: Production Agent Platform for Internal Operations

Design and build the agent tier a company runs for real operational work: capability-
scoped tools, budgeted execution, human approval, full observability, offline
evaluation, incident response, and an adoption path for agent use cases.

## Context

Internal agents touch infrastructure, money, and customers. The bar is not "it works in
a demo" — it is that every action is attributable, every irreversible action is
approved, every run is replayable, and a stuck agent is detected rather than discovered
on an invoice.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., submitted
  28 Oct 2022; v3 8 Mar 2023) — https://arxiv.org/abs/2210.03629 — takeaway for this
  lab: interleaving thought, action, and observation improves both interpretability and
  task success, which is why every step here emits a structured span and why the
  trajectory suite is the primary regression gate.
- "Constitutional AI: Harmlessness from AI Feedback" (Bai et al., submitted 1 Dec 2022;
  rev. 21 Dec 2024) — https://arxiv.org/abs/2212.08073 — takeaway for this lab: policy
  can be an explicit written set of principles checked at decision time, which is how
  the `PolicyGate` in this platform enforces refusal and escalation rules without
  retraining the model and keeps the policy auditable as a versioned asset.

## System Architecture

```
   operator / scheduled job / webhook
        |
   +----v----------------------------------------------------------------+
   |  TASK ROUTER                       agent profile per task type:       |
   |                                     tool set, budgets, approvals      |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  AGENT RUNTIME                                                       |
   |  +----------------+   +----------------+   +--------------------+     |
   |  | policy (LLM)   |-->| PolicyGate     |-->| ToolExecutor        |     |
   |  | + history      |   | allowlist      |   | typed handlers      |     |
   |  +----------------+   | arg schema     |   | idempotency keys    |     |
   |                         | pattern        |   | timeouts            |     |
   |                         | approval       |   | circuit breakers    |     |
   |                         | side-effect cap|   | retries (bounded)   |     |
   |                         | rate limit     |   +---------+----------+     |
   |                         +------+---------+             |               |
   +--------------------------------+-------------------------+               |
                                    |                                        |
   +--------------------------------v---------+   +-------------------+       |
   |  MEMORY + PRUNING                      |   |  EVIDENCE LEDGER  |       |
   |  working | episodic | semantic         |   |  every claim maps |       |
   +----------------+-----------------------+   |  to a tool result |       |
                    |                            +---------+---------+       |
   +----------------v--------------------------------────────---+            |
   |  ANSWER VERIFICATION                                          |            |
   |  claims supported? citations valid? confidence?               |            |
   +----------------------------+----------------------------------+------------+
                                |
   +----------------------------v---------+     +------------------+
   |  ESCALATION                          |     |  TRACE STORE     |
   |  budget | breaker | approval |        |     |  full trajectory |
   |  confidence | policy                |     |  replayable      |
   +----------------------------+---------+     +--------+---------+
                                |                        |
   +----------------------------v------------------------v+
   |  OBSERVABILITY & EVALUATION                              |
   |  success | step efficiency | recovery | cost | p95      |
   |  guardrail denials | approval waits | loop trips          |
   |  offline eval suite + golden trajectories                |
   +-----------------------------------------------------------+
```

## Component Specs

### 1. Task Router and Agent Profiles
Every task type gets an explicit profile:

```yaml
access_review:
  tools: [listEmployees, listGrants, suggestRevocations]
  maxSteps: 6
  maxWallClock: 120s
  maxCostUsd: 0.10
  irreversible: []
cost_analysis:
  tools: [queryBilling, aggregateSpend, compareBudget]
  maxSteps: 4
incident_triage:
  tools: [fetchAlerts, getLogs, getMetrics, runDiagnostics]
  maxSteps: 10
  maxWallClock: 300s
  irreversible: [restartService]      # approval required
```

Profiles mean a routine task can never inherit an expensive task's budget. Unknown task
types are rejected rather than defaulted.

### 2. Policy Gate (before every dispatch)
1. Tool in the profile-scoped allowlist.
2. Arguments pass schema, type, and pattern validation.
3. Rate limit per tool and per task.
4. Irreversible tools require a valid, unexpired, **argument-scoped** approval token.
5. Cumulative side-effect count under the cap.
6. No dispatch while the tool's circuit breaker is open.
7. Policy principles checked (versioned constitution) for the action class.

Denials are **observations** plus guardrail metrics, so attempts to bypass the gate are
visible rather than silently dropped.

### 3. Tool Executor
- Typed handlers with declared timeouts and bounded retries (idempotent tools only).
- **Idempotency keys** derived from `(taskId, tool, normalizedArgs)` so a retry cannot
  double-apply a write.
- Circuit breakers per tool: after N failures, open and make the agent escalate with
  context instead of hammering a down service.
- Result sanitization and length caps before entering memory.
- Secrets never returned by tools; secret values are referenced, not embedded.

### 4. Memory and Evidence
- Working memory with the pruning policy (keep recent verbatim, summarize older).
- **Evidence ledger**: every claim in the final answer must map to a tool result.
  Violations are stripped and logged; a claim-free answer escalates.
- Episodic memory: past trajectories as few-shot examples, with a TTL.
- Semantic memory: durable facts (Lab 04 retrieval infrastructure), tenant-scoped.

### 5. Human Approval
- Triggered by: budget exhaustion, breaker open, missing approval, confidence below
  threshold, or an irreversible action.
- Payload: goal, steps taken, evidence gathered, unknowns remaining, the exact proposed
  action.
- Approvals are argument-scoped with expiry; approving one call does not approve the
  next.
- Bidirectional: a human can inject an observation mid-run.
- SLO: median time-to-human-decision is a headline metric.

### 6. Observability
- Full trajectory per run, replayable offline against recorded tool results.
- Metrics: task success, step efficiency, tool precision/recall, recovery rate,
  cost per task, guardrail denials by reason, approval wait time, loop-detector trips,
  pruning events, escalation rate.
- Distributed tracing across policy, gate, and executor spans.
- Every log line carries `taskId`, `tenant`, and `owner` for cost attribution.

### 7. Evaluation
- Scenario suite (200+) with expected tool sequences and outcomes.
- **Golden trajectories**: any change altering a golden trajectory is a review-required
  diff.
- **Continuous eval**: sample completed production runs, score offline (rules plus a
  judge model), and feed failures into the suite.
- Prompt and tool-description changes gated on eval delta, like a code change.
- Canary per agent-profile change with automated rollback.

### 8. Safety and Data Handling
- No shell, no generic SQL, no arbitrary HTTP; every tool is a narrow typed operation.
- PII scrub on tool results before they enter memory; raw values never echoed into
  prompts.
- Read-only by default; write tools need a profile declaration and approval.
- Immutable audit log of policy decisions with argument hashes and external retention.
- Injection awareness: retrieved documents and tool outputs are labelled data.

### 9. Incident Response
- Runbooks per alert (stuck agent, breaker storm, approval backlog, cost spike,
  quality drop) with the first question and the containment action.
- Containment: kill switch per agent profile, per-tool disable, pin the prompt
  version, safe mode.
- Drills quarterly; time-to-detect and time-to-contain measured.
- Post-incident: fix plus a new scenario in the suite before closure.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Task success (read-only profiles) | >= 0.90 |
| Task success (write profiles) | >= 0.80 |
| Step efficiency | >= 0.70 |
| Recovery after tool error | >= 0.85 |
| Unauthorized tool call rate | 0 |
| Unapproved irreversible action rate | 0 |
| Loop-detector trip rate | < 2% of runs |
| Approval wait (median) | <= 5 min |
| Cost per task | <= $0.15 |
| p95 latency (read-only) | <= 20 s |
| Escalation rate | < 10% of runs |
| Golden-trajectory diffs | 100% reviewed |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Runaway loop | Loop-detector trip counter | Break with a nudge, then escalate |
| Duplicate side effect | Idempotency collision log | Key on `(taskId, tool, args)` |
| Tool outage | Breaker state | Open breaker; escalate with context |
| Argument injection | Validation failure | Patterns + allowlist + no generic tools |
| Evidence fabrication | Ledger validation | Strip claims or escalate |
| Prompt bloat from tool schemas | Prompt token metric | Profile-scoped tool sets |
| Cost spike from long histories | Pruning counter | Enforce cap; drop oldest summaries |
| Approval backlog | Wait-time SLO | Page; cap autonomous retries |
| Model upgrade regression | Golden diff + eval gate | Canary; pin previous version |
| Silent behaviour change | Continuous eval on traces | Failures enter the suite |
| Secret leaked into a prompt | PII scan | Redact before memory |
| Human escalation ignored | Escalation age SLO | Page after N minutes |
| Cross-tenant tool access | Scoped registry test | Deny by default |

## Milestones

- **M1** — task router and agent profiles.
- **M2** — policy gate with argument-scoped approvals and guardrail metrics.
- **M3** — tool executor with idempotency, timeouts, circuit breakers.
- **M4** — memory with pruning; evidence ledger.
- **M5** — escalation integration with SLO tracking.
- **M6** — scenario suite plus golden trajectories.
- **M7** — continuous eval on production traces.
- **M8** — observability dashboards and cost attribution.
- **M9** — runbooks and first drill (measure both times).
- **M10** — game day: simulate an exfiltration attempt end to end.

## Deliverables

1. Agent runtime, policy gate, tool executors, escalation integration.
2. Scenario suite with golden trajectories.
3. Dashboards for quality, cost, guardrails, approvals, escalations.
4. `runbook.md` — triage by symptom.
5. `THREAT_MODEL.md` — injection, exfiltration, and blast radius per tool.
6. `REPORT.md` — posture: what is automated, what is gated, what remains manual.

## Definition of Done

- [ ] Zero unapproved irreversible actions across 1,000 replayed production traces.
- [ ] Zero unauthorized tool calls across the eval suite and isolation tests.
- [ ] Every final answer's claims map to a tool result.
- [ ] Golden-trajectory suite green; a degraded config fails the gate.
- [ ] Every run replayable offline.
- [ ] Time-to-detect and time-to-contain measured in a drill and documented.
- [ ] Runbook written by someone who did not build the runtime, and tested.