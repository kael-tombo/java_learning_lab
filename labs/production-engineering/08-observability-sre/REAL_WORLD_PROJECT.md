# Lab 08: Observability — Logs, Metrics, Traces — Real World Project

## Scenario: "The Twenty Minutes We Could See Coming"

You are an SRE on a subscription billing platform: 14 Spring Boot 3 services, Java 21, Kubernetes, ~250 pods, 40 engineers, 8-person on-call rotation.

**The situation** — Friday 11:47, business hours. `invoice-generator` starts failing. Your entire alerting estate for this service is:

- `service is down` (a load-balancer check)
- `pod restart count > 0`
- a Grafana dashboard nobody has opened in six months

**What happened over 3 hours 10 minutes**:

1. **11:47** — `invoice-generator` starts returning 5xx for ~8% of requests after a Redis failover. Nothing alerts. `invoice-generator` also feeds `payment-capture` asynchronously via a queue; both are invisible on any dashboard.
2. **11:52** — Customer support starts receiving tickets about duplicate invoices. There is no metric correlating support tickets to a service.
3. **12:05** — An engineer notices the error rate *by coincidence*, while investigating an unrelated slow dashboard query.
4. **12:05–12:41** — 36 minutes of investigation using `kubectl logs` on a rotating pod, grepping by timestamp, and one person's `top`. No traces. No per-instance metrics. No request-id correlation, so log lines from the failing pod and the healthy pods cannot be distinguished.
5. **12:41** — Root cause: a `Caffeine` cache with `expireAfterWrite(30m)` and no jitter, all 60 replicas expiring at the same instant after the Redis failover, producing a synchronized 20× cache-miss storm against Redis. Redis CPU hit 95%; the cache-miss path is not instrumented at all, so this was never visible as a metric.
6. **13:20** — Cache TTL jitter applied and deployed. Backlog of 340,000 invoices reconciled.
7. **Postmortem**: three findings. (a) No SLO for `invoice-generator`; nobody agreed what "working" means. (b) The cache-miss path — the most expensive path in the service — had zero instrumentation. (c) There was no correlation id, so diagnosis was archaeology.

**Your job over 4 weeks**: define SLOs for the platform's critical user journeys, instrument the paths that actually cost money, join the three pillars so diagnosis is a click rather than an investigation, and alert on budget burn so a 3-hour incident becomes a 20-minute one.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Define what "working" means (Day 1–3)

### 1.1 Identify critical user journeys

Not services — journeys. A journey crosses services and is what a user experiences:

| Journey | SLI candidates | Owner |
|---|---|---|
| Sign up and first invoice | availability + latency of `POST /subscriptions` → invoice path | Growth eng |
| Pay an invoice | `POST /payments/capture` success within 3 s | Payments eng |
| View a statement | `GET /statements/{id}` p95 < 800 ms | Platform eng |
| Adjust a subscription | availability of plan-change endpoints | Billing eng |

**Deliverable 1 — Journey/SLI map**: each journey mapped to the services and endpoints that must succeed, with a named owner per SLO.

### 1.2 Write the SLO spec

For "Pay an invoice":

```
SLI     = fraction of capture requests that return 2xx within 3 s,
          excluding client-cancelled requests and 4xx validation errors
Window  = 28 days
SLO     = 99.5%   →  budget = 0.5% × 28d = 33.6 h of allowed failure
Latency = 99% of successful captures < 1.5 s
Min valid events = 100 per evaluation window (prevents 3 a.m. single-request paging)
Exclusions documented explicitly, with the reason for each
```

Compute budgets for all four journeys. Note which journeys have budgets small enough that a single incident consumes them.

**Deliverable 2 — SLO specification document** (service-level, not a Slack thread), reviewed and signed by the owning team's lead.

### 1.3 Establish the baseline honestly

Measure the *current* SLI for 14 days before changing anything. Most teams discover they are at 99.2% and never told anyone. Decide explicitly whether to (a) set the SLO at current performance and improve, or (b) set the SLO at the business promise and fund the gap. Record the decision and its cost.

**Deliverable 3 — Baseline SLO report** with the gap-to-promise and a costed remediation plan.

---

## Phase 2 — Instrument the paths that cost money (Day 3–8)

### 2.1 Metric inventory and SLI plumbing

For each journey endpoint:

```java
// Templatized route — never the raw URI.
String route = (String) request.getAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE.name());
observationContext.getLowCardinalityKeyValues().put("http.route", route == null ? "unknown" : route);
```

Histogram buckets chosen to straddle each SLO threshold:

```java
registry.config().meterFilter(MeterFilter.deny().onApply((id, tags) ->
    tags.stream().anyMatch(t -> Set.of("userId","invoiceId","requestId","sql").contains(t.getKey()))));
```

**Deliverable 4 — Metric inventory** listing every metric per service with its label set, cardinality estimate, and SLI role (`numerator`, `denominator`, `diagnostic`). Delete metrics nobody queries; that is a real deliverable, not a joke.

### 2.2 Trace coverage

Deploy the OTel Java agent fleet-wide. Fix context propagation across every async boundary found:

| Boundary | Failure without explicit handling |
|---|---|
| `CompletableFuture.supplyAsync` | orphan child span, never ended |
| `@Async` / `TaskExecutor` | same, plus MDC lost |
| Kafka `send().thenAccept(...)` | producer span unended |
| Spring `@Scheduled` | no parent by design — fine, but mark `trigger=scheduler` |
| WebClient `exchangeToMono` | reactor context loss unless the context-propagating executor is used |

**Deliverable 5 — Trace coverage map**: per service, the percentage of HTTP/KDBC/JDBC spans instrumented, and the list of async boundaries fixed, with a verification that orphan spans dropped to zero.

### 2.3 Structured logs with correlation

Deploy JSON logs fleet-wide with `trace_id`, `span_id`, `request_id` propagated from the gateway. Audit MDC lifecycle across thread pools and `finally` blocks.

**Deliverable 6 — Log correlation audit** with before/after: how many log lines could be joined to a specific request before (0%) and after (100% on the sampled paths).

### 2.4 Instrument the expensive path

The cache-miss path, the retry path, the DB round-trip path, and the queue-produce path all get explicit spans and metrics — because those are the paths that turn a small fault into an incident.

**Deliverable 7 — "Costly path" instrumentation** for cache miss, retry, DB connect, and queue publish, with the metrics a responder would need.

---

## Phase 3 — Join the pillars and build the dashboards (Week 2)

### 3.1 Exemplars end to end

Enable exemplars on all latency histograms. Verify the metric → exemplar → trace → log path works on `invoice-generator` in under two minutes.

**Deliverable 8 — Exemplar verification**, screenshotted, with the wall-clock time recorded.

### 3.2 SLO dashboards

Per journey: SLI value vs SLO line → error budget remaining % → burn rate (fast and slow) → volume → latency percentiles → error rate by status → saturation (thread pool, DB pool, cache miss rate, queue depth) → JVM.

**Deliverable 9 — SLO dashboards** with a documented reading order (the on-call's first 60 seconds).

### 3.3 Cost guardrails

```promql
# Series count per metric — the cardinality canary
topk(10, count by (__name__) ({__name__=~".+"}))
```

Budget metrics/traces/log volume per service, and alert when a team exceeds theirs.

**Deliverable 10 — Observability cost budget** per service, with actual monthly spend and the sampling policy that keeps it bounded.

---

## Phase 4 — Replace the alerts (Week 2–3)

### 4.1 Multi-window multi-burn-rate alerting

Implement the page/ticket tiers for each journey SLO. Add `runbook_url`, `dashboard_url`, `owner`, and `severity` to every rule.

### 4.2 Delete the noise

Inventory every existing alert in the estate. For each: is it symptom or cause? Did it page in the last 90 days? Did anyone act? Delete or downgrade the dead ones.

**Deliverable 11 — Alert audit**: total alerts before/after, pages per on-call shift before/after, and the list of deleted rules with justification.

### 4.3 Runbooks

One runbook per paging alert, each with: what it means, first three commands, decision tree, rollback path, escalation, and a link to the dashboard.

**Deliverable 12 — Runbook pack** covering the top 15 paging alerts, reviewed by the on-call rotation.

---

## Phase 5 — Prove it (Week 3)

Replay the Redis-failover incident in staging, using your own instrumentation to detect and resolve it:

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Baseline business-hours load | SLI ≥ SLO, no burn alerts |
| S2 | Redis failover (as in the incident) | burn alert pages within 5 min of SLI breach |
| S3 | Synchronized cache expiry (no TTL jitter) | cache-miss rate visible as a metric; alert fires |
| S4 | `payment-capture` 8 s latency | saturation SLI leads latency SLI by ≥ 3 min |
| S5 | Pod restart loop on 3 of 60 replicas | per-instance divergence visible in ≤ 1 min |
| S6 | Queue backlog (producer 3× faster) | queue-depth SLI visible and alerting |
| S7 | Partial dependency failure (5% of calls) | exemplar path from dashboard to log line in ≤ 2 min |

**Deliverable 13 — Detection and diagnosis test report**, with measured MTTD and MTTR per scenario versus the original incident's numbers.

---

## Phase 6 — Operate it (Week 3–4)

- **SLO review cadence**: monthly per service, quarterly per journey. Standing agenda: budget burn, SLI trend, alert quality, is the SLI still the right measure.
- **Error-budget policy**: written rule connecting remaining budget to release risk (ship freely >50%, canary-only 25–50%, freeze <25%), signed off by engineering leadership.
- **Game day**: run S2 and S3 with the on-call in business hours; measure the responder's actual time to first correct hypothesis.
- **Service template**: every new service inherits OTel agent, templatized routes, JSON logs, the alert templates, and an SLO stub it must fill in.
- **Enforcement**: CI fails a PR that adds a metric with an unbounded label, or a new endpoint with no SLI.

**Deliverable 14 — Operational package**: review cadence, budget policy, game-day report, template, CI enforcement.

---

## Phase 7 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| MTTD for a 8%-error incident | 18 min (by coincidence) | < 3 min (burn alert) |
| MTTR for the Redis-failover class | 3 h 10 min | < 30 min |
| Log lines joinable to a request | 0% | 100% on instrumented paths |
| Orphan spans (async leaks) | unknown, est. thousands/day | 0 |
| Metrics per service with a bounded label set | ~40% | 100% |
| Alerts paging per shift | ~6 (many unactioned) | ≤ 1.5 actionable |
| Services with a reviewed SLO | 0 / 14 | 14 / 14 |
| Error budget consumed per quarter | unknown | tracked, with a release policy attached |
| Observability monthly cost | $31K (unbounded, no owner) | $19K, budgeted per service |

Institutionalize: add "SLI/SLO + alert + runbook" to the production readiness review; make SLO spec a prerequisite for a new external-facing endpoint; add burn rate to the engineering quarterly review; publish an internal "cost of observability per journey" page.

**Deliverable 15 — Business case + institutionalization**, presented to leadership with the numbers above.

---

## Deliverables checklist

- [ ] Phase 1 journey/SLI map, SLO spec with budgets, honest baseline.
- [ ] Phase 2 metric inventory, trace coverage map, log correlation audit, costly-path instrumentation.
- [ ] Phase 3 exemplar verification, SLO dashboards, cost budget.
- [ ] Phase 4 multi-window burn alerts, alert audit, runbook pack.
- [ ] Phase 5 seven-scenario detection/diagnosis test report.
- [ ] Phase 6 review cadence, budget policy, game day, template + CI enforcement.
- [ ] Phase 7 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| SLI design | "99.9% uptime" | User-journey SLIs with explicit good/valid/exclusions, floors, and computed budgets |
| Instrumentation | "Added Micrometer" | Templatized routes, bounded labels, costly paths covered, orphan spans eliminated |
| Correlation | "Logs have timestamps" | 100% joinable via `trace_id`/`request_id`, MDC lifecycle correct across pools |
| Alerting | "Lowered the threshold" | Multi-window burn rates with page/ticket tiers and a measured flapping reduction |
| Dashboards | 40 panels | Reading order, budget remaining, saturation SLI that leads latency |
| Proof | Staging happy path | Replays the actual incident shape and measures MTTD/MTTR versus the original |
| Operations | "We look at graphs" | Review cadence, budget-as-release-policy, game day, template + CI enforcement |
| Economics | Technical only | Bounded observability spend per service with an owner |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Google SRE Workbook — "Implementing SLOs" and "Alerting on SLOs"** — https://sre.google/workbook/implementing-slos/ and https://sre.google/workbook/alerting-on-slos/ — the authoritative source for the SLI/SLO/error-budget framing, the multi-window multi-burn-rate alerting recipe (burn rates chosen so a threshold consumes a fixed fraction of the budget over the window), and the guidance that a burn alert needs a confirmation window to avoid flapping. Also the origin of the "release policy tied to remaining budget" pattern.
2. **OpenTelemetry — Java instrumentation docs and sampling** — https://opentelemetry.io/docs/languages/java/ and https://opentelemetry.io/docs/concepts/sampling/ — the canonical source for W3C context propagation (`traceparent`/`tracestate`), the Java agent/SDK/autoconfigure options, and the head-based vs tail-based sampling distinction with its sampling-bias warning. Verify the exact artifact names and `Sampler` API surface for your OTel version before writing config from memory.

Additional anchors worth verifying: Micrometer `Observation` API surface and property names for Spring Boot 3.x (they have shifted between minor versions), Prometheus histogram bucket/exemplar configuration for your version, and the specific burn-rate thresholds recommended by whichever alerting tool you adopt — they are not all identical to the SRE workbook's numbers.

---

## Reflection questions

1. The 18-minute delay before detection was luck. What is the single cheapest change that would have cut it to under 3, and why is it not always the one you pick?
2. Nobody instrumented the cache-miss path because it "wasn't the request path." What rule would make expensive internals a first-class instrumentation requirement?
3. Your baseline SLO is 99.2% and the business promises 99.9%. Who decides, and what does that decision cost?
4. How many pages per shift is right? What number did you set, and what evidence supports it?
5. Tail-based sampling costs more storage than head-based. How would you defend that to a finance stakeholder, numerically?
