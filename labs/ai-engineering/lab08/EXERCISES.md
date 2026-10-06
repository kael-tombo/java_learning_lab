# Lab 08: AI Observability — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Trace Structure (E)

Build `Trace` with the full span list; JSONL writer; hashed payloads. Verify a
round-trip.

---

## Exercise 2: Cost Meter with Attribution (E)

Per-request and per-line costs; attribute to tenant, feature, route, model version,
cache status. Verify a hand computation.

---

## Exercise 3: Invoice Reconciliation (M)

Compare metered cost to a synthetic invoice; report the discrepancy. Verify within 2%.

---

## Exercise 4: Cost per Outcome (M)

`cost/request / success_rate` per feature; compare against raw cost to show the
ranking differs.

---

## Exercise 5: Percentile Estimation (M)

Reservoir sampling for TTFT/TPOT; compare to exact on a known distribution.

---

## Exercise 6: Metric Cardinality Guard (M)

Implement a label validator: reject unbounded label values. Verify a request-id label
is caught.

---

## Exercise 7: Stratified Sampling (M)

Random plus error plus escalation plus disagreement strata; verify the random sample is
unbiased and the mix is reported separately.

---

## Exercise 8: PSI Drift Detector (M)

Quantile bins, rolling comparator, thresholds. Verify a shifted window triggers.

---

## Exercise 9: Manifest Diff for Triage (M)

Diff two release manifests and produce a ranked first hypothesis per alert type.

---

## Exercise 10: Retry Amplification Detector (H)

From traces, compute attempts/request; detect a storm; verify early warning before
aggregate cost breaches budget.

---

## Exercise 11: Cache Hit Rate Collapse Detector (M)

Alert on a sharp drop in prefix or semantic hit rate; verify a simulated layout change
trips it.

---

## Exercise 12: Guardrail Stage Attribution (H)

For each blocked request, record the first layer that caught it; produce the
attribution histogram and identify the weakest layer.

---

## Exercise 13: Alert Router (M)

Given an anomaly, produce the first question, the owner, and the runbook link. Verify
every alert type has all three.

---

## Exercise 14: Retention Job (M)

Implement trace/log retention with per-class policies; verify expired records are
removed and the job reports counts.

---

## Exercise 15: PII Scrub at Write (M)

Scrub before persisting; verify zero residual patterns after a re-scan.

---

## Exercise 16: Latency/Error Anomaly Detection (H)

Seasonal baseline plus residual scoring; detect a synthetic p95 shift and an error-rate
shift.

---

## Exercise 17: Dashboard Aggregation (H)

Build per-intent, per-route, per-model dashboards from traces; verify totals reconcile.

---

## Exercise 18: Business Metric Join (H)

Join task completion and cost per intent; verify the correlation is computable and
reported with the data volume.

## Stretch A: Distributed Tracing (H)

Propagate trace ids across stage boundaries and service calls; verify a full chain
reconstructs.

---

## Stretch B: Exemplar Traces (H)

Automatically surface the traces most informative about a quality drop (worst, fastest
failure, most common guardrail stage).

---

## Stretch C: Anomaly Correlation (H)

Detect which upstream change correlates with a downstream metric shift.

---

## Stretch D: Observability Cost Model (H)

Model the cost of traces, metrics, and evals; optimize the sampling plan to fit budget
while preserving CI width.

---

## Stretch E: Multi-Tenant Noise Isolation (H)

Detect anomalies per tenant with a hierarchical baseline so one noisy tenant does not
mask a real regression elsewhere.

---

## Stretch F: Offline/Online Quality Gap (M)

Compare sampled offline scores against online proxies; quantify the gap and its
direction.