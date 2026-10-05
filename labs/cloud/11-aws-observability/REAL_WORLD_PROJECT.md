# AWS Observability - Real World Project

## Project: Production Observability Platform Across an AWS Estate

### Objective
Build the observability platform for a real estate: metrics standards, structured logging,
distributed tracing, dashboards, and SLO-based alarms — plus the cardinality and cost controls
that keep it affordable.

### Why This Matters
Observability debt compounds. Teams add metrics per service with no naming convention, no
dimensionality budget, and no owner, and within a year the estate costs more to run than the
services it observes and nobody can answer a question with it.

### Architecture Overview
```
  Services ─┬─▶ CloudWatch metrics (standard namespace + EMF for business KPIs)
            ├─▶ CloudWatch Logs (structured JSON, trace-correlated, retention per tier)
            └─▶ OTLP ─▶ AWS X-Ray / ADOT collector ─▶ traces
                                    │
                         Dashboards + SLO burn-rate alarms
                                    │
                        central account, cross-account role
```

### Phase 1: Standards and Inventory (Week 1)
1. Define the metric naming and dimension standard; state the required RED metrics per service
2. Inventory existing metrics: how many namespaces, how many custom metrics, monthly cost
3. Identify the top 20 metrics by cost and decide for each: keep, aggregate, or delete
4. Define the log schema (structured JSON with `trace`, `request`, `service`, `version`)
5. Define trace sampling: 100% for errors, sampled for successes, with a decision on who pays

### Phase 2: Instrumentation Library (Week 2)
1. A shared Java library emitting the standard metrics and log schema
2. CloudWatch EMF for structured metric extraction rather than one API call per datapoint —
   the cost difference is substantial at volume
3. Trace propagation as a library concern so no team implements it differently
4. A `CardinalityGuard` in the library that drops oversized dimensions at the source
5. Version the schema; dashboards must not break when a service ships a new version

### Phase 3: Logs and Retention (Week 3)
1. Structured JSON with mandatory fields; reject unstructured logs in code review
2. Retention by tier: 30 days hot for app logs, 400 days for audit and security logs in S3
3. Log-based metrics for the events that matter, so business behaviour is queryable without
   parsing logs
4. PII handling: redact at the emitter, not in the log pipeline — once it is in a log it has
   been written somewhere you do not control
5. Cross-account central log archive with tightly scoped permissions

### Phase 4: Dashboards and SLO Alarms (Week 4)
1. One dashboard per service (RED + saturation) and one per journey (SLI and burn rate)
2. Deploy markers overlaid on every latency and error chart
3. SLOs defined for the top three journeys; error budgets stated numerically
4. Multi-window burn-rate page alerts, ticket-only alerts at lower rates
5. Every page alert has a runbook with a `firstAction`; reject any that does not
6. Test each alert by triggering the underlying condition deliberately

### Phase 5: Cost and Governance (Week 5+)
1. Cost dashboard per service and per namespace, reviewed monthly
2. Delete unused dashboards and alarms — an alarm nobody acts on is pure cost
3. Tag metrics and logs with team and service for chargeback; make cost visible to owners
4. Quarterly standards review: new services adopt the library, existing ones are checked
5. Document what is deliberately not collected, and why

### Deliverables
1. Metrics, log, and trace standards with adoption status per service
2. Shared instrumentation library with EMF, propagation, and cardinality guard
3. Structured logging with redaction, retention tiers, and cross-account archive
4. Dashboards, SLO alerts with runbooks, and a monthly cost report by owner

### Success Criteria
- Every service emits the standard RED metrics and correlated logs via the shared library
- Metric series count reduced by at least 50% with no loss of query capability
- Observability cost per service visible and charged back to its owning team
- Every page alert has a runbook, and every runbook was exercised at least once

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon CloudWatch metrics and monitoring —
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-metrics-monitoring.html
  Use for: the maintained guidance on custom metric dimensions, quotas, and cost drivers.
  Verify current service quotas and pricing dimensions before setting a cardinality budget.
- Amazon CloudWatch Logs —
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html
  Use for: log group retention classes and the retention options referenced in Phase 3.
  Verify which retention classes are available in your region.

### Estimated Time
7-8 weeks part-time