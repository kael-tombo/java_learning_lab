# Lab 08: AI Observability — Mini Project

## Project: Observability Pipeline with Cost Attribution and Drift Alerts

Build the observability system a production AI service runs on: traces, metrics,
structured logs, cost attribution with reconciliation, stratified sampling, drift
detection, and an alert router.

## Goal

A telemetry system where any single bad request can be reconstructed, any cost anomaly
is attributable to a line and a cause, and any quality drop is triaged to a component.

## Requirements

### Phase 1: Traces
- [ ] Full span structure with hashed payloads.
- [ ] JSONL writer with scrubbing on the serialized line.
- [ ] Round-trip read verified.
- [ ] Manifest hash and version fields on every trace.

### Phase 2: Metrics
- [ ] `MetricRegistry` with bounded labels and a cardinality guard.
- [ ] Percentiles via reservoir sampling; sketch spec published.
- [ ] Batch size distribution, error classes, cache hit rates, preemption rate.

### Phase 3: Cost
- [ ] Per-line breakdown sorted by share.
- [ ] Attribution by tenant, feature, route, model version, cache status.
- [ ] Synthetic invoice reconciliation within 2%, with a two-way verdict.
- [ ] Cost per successful outcome per feature; show the ranking differs from raw cost.

### Phase 4: Sampling
- [ ] Stratified sampler: random, errors, escalations, signal disagreement.
- [ ] `blended()` throws; verify a dashboard cannot accidentally mix strata.
- [ ] Budget-aware sampling plan (given a budget, choose sizes per stratum).

### Phase 5: Drift
- [ ] PSI with quantile bins and thresholds.
- [ ] Inject drift into intent mix, query length, and language; verify detection.
- [ ] Verify drift triggers investigation, not rollback.

### Phase 6: Detection
- [ ] Retry storm detector (three conditions).
- [ ] Cache collapse detector (sudden drop, not gradual).
- [ ] Latency and error anomaly detection against a seasonal baseline.
- [ ] Guardrail stage attribution with an uncaught count.

### Phase 7: Alerts and Runbooks
- [ ] Alert router for 8 alert types with owner, first question, runbook.
- [ ] Verify an unregistered alert type throws.
- [ ] Runbook quality scoring.

### Phase 8: Privacy and Retention
- [ ] Retention job with per-class TTLs; counts reported.
- [ ] Tenant purge implemented and measured.
- [ ] Zero residual PII after a re-scan of stored traces.

### Phase 9: Dashboard
- [ ] Per-intent, per-route, per-model dashboards reconciling to raw traces.
- [ ] Exemplar trace surfacing (worst, fastest failure, most common guardrail stage).

## Directory Layout

```
lab08/
  src/com/aiengineering/lab08/{trace,metric,cost,sampling,drift,alert,guardrail,privacy,dashboard}/
  out/traces.jsonl
  out/metrics.json
  out/invoice.csv
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — traces round-trip; scrubbing verified.
2. **M2** — metrics with the cardinality guard; percentiles published.
3. **M3** — cost breakdown and reconciliation within 2%.
4. **M4** — stratified sampler; `blended()` throws.
5. **M5** — drift injected into three dimensions and detected.
6. **M6** — retry storm and cache collapse detectors fire.
7. **M7** — guardrail attribution with an uncaught count.
8. **M8** — alert router; unregistered type throws.
9. **M9** — retention job; tenant purge verified.
10. **M10** — dashboards reconcile; exemplars surfaced.
11. **M11** — report written.

## Acceptance Criteria

- [ ] Any single trace reconstructs end to end.
- [ ] Zero inline prompt content; zero residual PII after a re-scan.
- [ ] Forbidden metric labels rejected at registration.
- [ ] Cost reconciles within 2% with a correct two-way verdict.
- [ ] Cost per outcome reorders features relative to raw cost.
- [ ] Strata never averaged (enforced in code).
- [ ] Drift detected in all three injected dimensions.
- [ ] Retry storm detected before the cost budget line.
- [ ] Every alert type has an owner, first question, and runbook.
- [ ] Drift alert does not trigger rollback.
- [ ] Retention per class; tenant purge measured.

## Stretch Goals

- [ ] Distributed tracing across services.
- [ ] Exemplar trace selection optimizing debuggability.
- [ ] Anomaly correlation between an upstream change and a downstream shift.
- [ ] Observability cost model with an optimized sampling plan.
- [ ] Multi-tenant hierarchical baselines.
- [ ] Offline/online quality gap quantification.
- [ ] Seasonal baseline with a robust median/MAD residual.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Metrics backend overload | Unbounded label cardinality |
| Compliance incident | PII in logs; scrubbing after persist |
| Bill 3x with no explanation | Untagged call paths |
| Quality drop undiagnosed | No manifest diff; versions not recorded |
| Alert fatigue | No owners, no runbooks, noisy thresholds |
| Strata averaged in a dashboard | No enforcement in code |
| Drift alert auto-rolled back | Conflated with quality signals |
| Retry storm seen only in the invoice | No attempts/request metric |
| Missing stage span | Instrumentation not a launch requirement |
| Retention never runs | No metric on the retention job |

## Definition of Done

`REPORT.md` contains: the stack diagram, an example trace, the cardinality guard rules,
the percentile sketch specification and its limitations, the cost breakdown with shares,
the reconciliation result, the cost-per-outcome table with the reordering, the sampling
plan and budget, the drift detection results for three dimensions, the retry storm and
cache collapse drills, guardrail attribution with the uncaught count, the alert table,
the retention report, the dashboard reconciliation, and a "which alert would have caught
the last three incidents" retrospective.