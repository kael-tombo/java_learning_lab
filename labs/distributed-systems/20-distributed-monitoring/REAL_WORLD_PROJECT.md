# Distributed Monitoring - Real World Project

## Project: Replacing Noisy Alerting with an SLO-Based Observability Stack

### Objective
Audit an existing alerting estate, replace cause-based alerts with symptom-based SLO
monitoring, fix cardinality problems that are breaking the metrics backend, and reduce page
volume while improving detection of real user impact.

### Why This Matters
Most teams page far more than they should and miss more than they should, simultaneously.
Cause-based alerts fire on things that are not user impact; user impact goes unpaged because
nobody wrote a threshold for it. This project fixes both halves.

### Architecture Overview
```
  Services ─▶ OTel SDK ─▶ Traces (spans + exemplars)
     │            └──▶ Metrics (RED per route, cardinality-guarded)
     │            └──▶ Logs (structured, trace-correlated)
     ▼
  Collector (scrape + transform + cardinality limit + sampling)
     ├──▶ Metrics store (Prometheus-compatible)
     ├──▶ Trace store (long retention on errors)
     └──▶ SLO engine ── burn-rate evaluation ──▶ Pager ──▶ on-call
```

### Phase 1: Audit the Existing Estate (Week 1)
1. List every alert with: trigger, how often it fires, how often it was actionable, and what
   happened if ignored
2. Compute: page volume per week, and the percentage that were actionable
3. List every metric label in use and estimate series count; find the top offenders
4. Find the user-impact paths with no alerting at all — these are the real gaps

**Expect an actionable rate well under 50%.** That number is the project's justification.

### Phase 2: Fix Cardinality First (Week 2)
Cardinality problems break the pipeline, and they block everything else.
1. Add a hard limit in the collector; drop excess series rather than failing ingestion
2. Find every high-cardinality label: user IDs, request IDs, full URLs, SQL text
3. Route user IDs and request IDs to **traces**, where they belong, not to metrics
4. Move free-text (SQL, error messages) to logs and exemplar links
5. Measure series count before and after; target a reduction of at least 10x

### Step 3: Define SLOs Where They Matter (Week 3)
1. Pick the three journeys that matter most, defined as user-visible flows, not services
2. For each, define an SLI from real traffic: success ratio over a window, with the numerator
   and denominator written down
3. Set targets from current performance plus an improvement commitment — not aspirational
4. Choose windows (28 days is common) and state the error budget as a number
5. Record what happens when the budget is exhausted: freeze releases, and name who decides

### Step 4: Rewrite the Alerts (Week 4)
1. Delete every cause-based alert that has fired twice without user impact — move them to a
   ticket
2. Keep cause-based alerts only where the action is genuinely to *fix a component* (disk
   filling, certificate expiry) and where the symptom alert would come too late
3. Add multi-window burn-rate page alerts per SLO, using the fast/slow table from the lab
4. Add ticket-only (non-paging) alerts at lower burn rates for early warning
5. Every remaining page alert has a runbook link and a `firstAction`

### Phase 5: Operate (Week 5+)
1. Dashboards per journey: SLI, burn rate, error budget remaining, deploy markers overlaid
2. Alert on the observability system itself — dropped spans, dropped series, ingestion lag
3. Weekly review: pages per week, actionable ratio, false positives, mean time to mitigate
4. Runbook: "SLO burn alert" — check deploys first, then dependency health, then capacity
5. Quarterly review against the SLO: is the target still the right number?

### Deliverables
1. Alert audit with page volume and actionable ratio
2. Cardinality fix with series-count before/after and the labels moved to traces
3. Three journey SLIs with error budgets and an exhaustion policy
4. Burn-rate alert set, dashboards, and a self-monitoring runbook

### Success Criteria
- Page volume down at least 50% within 60 days
- Actionable page ratio above 80%, measured weekly
- Every user-impact path has an SLO and a burn-rate page alert
- No metrics ingestion failures from cardinality in the following 60 days

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon CloudWatch metrics and monitoring concepts —
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-metrics-monitoring.html
  Use for: the maintained statement of custom metric dimensions and cardinality limits. Verify
  the current service quota values for metrics per region before designing a cardinality
  budget to sit just under them.
- Kubernetes Documentation, "Logging Architecture" and cluster monitoring —
  https://kubernetes.io/docs/concepts/cluster-administration/monitoring/
  Use for: the maintained guidance on what a cluster-level monitoring pipeline must collect
  and the cost trade-off of verbose collection. Useful for the sizing section of the
  cardinality fix.

### Estimated Time
7-8 weeks part-time