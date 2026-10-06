# Lab 08: AI Observability — Real-World Project

## Project: Production Observability and FinOps Platform

Design and build the telemetry system for an AI product: end-to-end tracing,
cardinality-safe metrics, cost attribution with invoice reconciliation, online quality
monitoring, drift detection, alert routing with runbooks, and privacy-compliant
retention.

## Context

In an AI product, the gap between "users say it got worse" and "we know which component
changed" is usually measured in days. This platform closes that gap.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: serving systems are defined
  by throughput, memory, and latency behaviour under load, which is why this platform
  treats queue depth, batch size distribution, preemption rate, and cache hit rate as
  first-class operational signals rather than GPU utilisation alone.
- "Holistic Evaluation of Language Models (HELM)" (Liang et al., submitted 16 Oct 2022;
  v7 Feb 2023) — https://arxiv.org/abs/2211.09110 — takeaway for this lab: reproducible,
  multi-metric reporting with published conditions is the standard for defensible claims,
  which is why every report here carries a scenario set, metric set, manifest hash, and
  confidence interval.

## System Architecture

```
   REQUESTS (chat | rag | agent | batch)
        |
   +----v----------------------------------------------------------------+
   |  INSTRUMENTATION (mandatory at launch)                             |
   |  trace_id propagation | span per stage | manifest hash             |
   |  PII scrub on the serialized line | bounded metric labels        |
   +----+----------------------------------------------------------------+
        |
   +----v-------------------+     +-------------------+   +------------+
   |  TRACES                 |     |  METRICS          |   |  LOGS      |
   |  full request lineage   |     |  cardinality-safe |   |  scrubbed  |
   |  hashed payloads        |     |  percentiles      |   |  retention |
   |  per-class retention    |     |  distributions    |   |  by class  |
   +----+--------------------+     +--------+----------+   +----+-------+
        |                             |                   |
        +--------------+--------------+                   |
                       v                                  |
              +------------------+                         |
              |  COST METER      |<------------------------+
              |  per line, per   |  reconciled monthly against invoices
              |  tenant, feature |  cost per successful outcome
              +--------+---------+
                       |
        +--------------+-------------------------------------+
        |                                              |
  +-----v------+                              +--------v---------+
  | QUALITY    |                              | DRIFT            |
  | 100% cheap |                              | PSI on inputs    |
  | sampled    |                              | alert ->         |
  | judged     |                              | investigate      |
  +-----+------+                              +------------------+
        |
        v
  +------------------+     +------------------+
  | ALERT ROUTER     |     | DASHBOARDS       |
  | owner + first    |     | per intent/route/ |
  | question +       |     | model; exemplars  |
  | runbook          |     +------------------+
  +------------------+
```

## Component Specs

### 1. Instrumentation (Launch Requirement)
- Trace context propagated across stage boundaries and service calls.
- One span per stage: retrieval, prompt, generation, guardrails, tools.
- **Manifest hash** on every trace, plus per-component versions.
- Retrieval scores recorded, not just hits, so near-misses are visible.
- PII scrub on the serialized line, before persistence.
- Instrumentation coverage is a release gate: a new stage without a span fails the
  build.

### 2. Traces
- Full lineage per request; hashed payloads with pointers for on-demand content.
- Per-class retention: successes 7 days, errors 90 days, audit 7 years.
- Tenant-deletable on request, enforced by a job with a metric.
- Sampled 100% for errors, 1-5% for successes.

### 3. Metrics (Cardinality-Safe)
- Allowed label set only: intent, route, model version, prompt version, cache status,
  outcome class, tenant tier.
- Registration-time validation rejecting request ids, user ids, raw queries, trace ids.
- Percentiles with published sketch type and reservoir size; tail percentiles treated
  as approximate.
- Distributions, not just averages: batch size, chunk counts, token counts.
- Series-count budget enforced per metric family.

### 4. Cost Attribution
- Per line: input tokens, output tokens, embedding, rerank, GPU time.
- Dimensions: tenant, team, feature, route, model version, prompt version, cache status,
  agent vs direct.
- **Monthly reconciliation** against provider invoices; discrepancy above 2% alerts with
  a two-way diagnosis (meter over- or under-counting).
- **Cost per successful outcome** as the north-star metric, per feature.
- Budgets with 50/80/100% alerts plus a trajectory forecast.
- Chargeback/showback dashboard teams trust (accuracy is the adoption lever).

### 5. Online Quality Monitoring
- 100% cheap signals: schema validity, refusal, length, PII, citation presence, tool
  errors, finish reason.
- Stratified judging: random (headline) plus errors, escalations, signal disagreement
  (fix queue). Reported separately, never averaged.
- Judge version in the manifest; judge-human agreement re-measured monthly.
- Business layer joined: task completion, time-to-resolution, deflection, revenue per
  request, escalation rate.

### 6. Drift Detection
- PSI on intent mix, query length, language, retrieval top-score, refusal rate.
- Compare a rolling window against a reference window; quantile bins.
- Drift triggers investigation and eval-suite review, **not** rollback.
- Separate alert for eval-set drift (does the suite still represent traffic?).
- Hierarchical baselines per tenant so one noisy tenant does not mask a regression.

### 7. Detection
- Retry amplification from `attempts/request`; three-condition storm rule.
- Cache hit-rate collapse as a deployment-bug detector.
- Latency and error anomaly detection against a robust seasonal baseline.
- Guardrail stage attribution, with the uncaught count as a tracked metric.

### 8. Alerts and Runbooks
- Every alert: type, owner, first question, runbook link, severity, default action.
- Registration rejects alert types without a runbook.
- Runbook quality scored mechanically; untested containment actions are work items.
- Quarterly drills measuring time-to-detect and time-to-contain.
- Exemplar traces surfaced automatically for quality drops (worst, fastest, most common
  guardrail stage).

### 9. Privacy and Compliance
- PII scrub before persistence, on the serialized line.
- Prompt/completion content stored only on request or for flagged/sampled cases with a
  documented purpose.
- Audit logs (policy decisions, guardrail verdicts, approvals) long-retention,
  tamper-evident, externally stored.
- Data classification per span type driving retention and access.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Trace coverage | 100% of production requests |
| Instrumentation coverage gate | Blocks release on a missing stage span |
| Metric cardinality | Zero forbidden labels; series budget enforced |
| Cost reconciliation | < 2% discrepancy |
| Cost per outcome | Tracked and improving per feature |
| Online sample freshness | < 30 min |
| Judge-human agreement | >= 0.80 |
| Drift alert precision | Investigated alerts that were real > 70% |
| Alert with an owner and runbook | 100% |
| Time to detect (drill) | < 15 min |
| Time to contain (drill) | < 60 min |
| PII in stored telemetry | 0 |
| Observability cost / AI spend | < 5% |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Metrics backend outage | Series explosion | Cardinality guard at registration |
| Compliance incident | PII scan | Scrub on the serialized line |
| Bill spike unexplained | Reconciliation | Two-way diagnosis; mandatory tagging |
| Quality drop undiagnosed | Manifest diff | Version everything; diff-first runbook |
| Alert fatigue | Block precision, unowned alerts | Registration requires runbook + owner |
| Drift alert auto-rolls back | Wrong action | Separate drift and quality signals |
| Retry storm late detection | attempts/request | Leading indicator, not the invoice |
| Cache collapse missed | Hit-rate alert | Deploy-bug detector |
| Retention not enforced | Retention job metric | Job with counts, not a policy doc |
| Observability cost creep | Obs cost / AI spend | Sampling plan; series budget |
| Tenant purge incomplete | Purge audit | Store-level enforcement |
| One tenant masks a regression | Hierarchical baselines | Per-tenant detection |
| Exemplars unavailable | Dashboard links | Automated exemplar selection |

## Milestones

- **M1** — instrumentation standard plus the coverage gate.
- **M2** — tracing store with per-class retention and tenant purge.
- **M3** — metrics backend with the cardinality guard and distributions.
- **M4** — cost meter, attribution, reconciliation, budgets.
- **M5** — online quality monitoring with separated strata.
- **M6** — drift detection and eval-set freshness alerting.
- **M7** — retry, cache, latency, error, and attribution detectors.
- **M8** — alert router with runbooks and drills.
- **M9** — dashboards with exemplar selection.
- **M10** — finance sign-off on the chargeback dashboard.
- **M11** — game day: three incidents, runbooks exercised.

## Deliverables

1. Instrumentation standard and coverage gate.
2. Trace, metric, and log pipelines with retention.
3. Cost attribution with reconciliation and chargeback.
4. Quality and drift monitoring.
5. Alert router, runbooks, and drill reports.
6. `REPORT.md` — quality trend, cost per outcome trend, drift history, incident
   detection performance.
7. `TELEMETRY_STANDARD.md` — what every team must instrument.

## Definition of Done

- [ ] Every production request has a full trace with a manifest hash.
- [ ] A new stage without a span fails the build.
- [ ] Cost reconciles within 2% and finance signs off on the dashboard.
- [ ] Zero PII in stored telemetry, verified by scan.
- [ ] Every alert has an owner, first question, and a runbook exercised in a drill.
- [ ] Quality drops triaged to a component within 1 hour, demonstrated in a drill.
- [ ] Observability cost under 5% of AI spend.
- [ ] Retention enforced with a metric, and tenant deletion verified.