# Lab 08: Observability — Logs, Metrics, Traces — Mini Project

## Project: `ObserveLab` — Instrument a Java Service End to End and Alert on Budget Burn

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Micrometer, OpenTelemetry Java agent + Collector, Prometheus, Grafana, Loki (or ELK), Tempo/Jaeger, Testcontainers

Build a small service that is genuinely observable: every request produces a metric, a trace, and correlatable logs; an SLO is defined and computed from those signals; and alerts fire on error-budget burn rather than on arbitrary thresholds.

---

## Part 1 — The service

Two Spring Boot 3 services so you have a real cross-service trace:

```
[loadgen] → [orders-api:8080] ──HTTP──→ [pricing-stub:8081]
                  │
                  └──JDBC──→ [postgres:5432]
```

`orders-api` exposes:
- `GET /orders/{id}` — the SLO'd path (templated route, not raw).
- `GET /search?q=...` — deliberately dynamic, to demonstrate the cardinality bomb you will fix in Part 5.
- `GET /report` — slow (200 ms–3 s) so you have a latency tail and slow traces.
- `GET /actuator/health`, `/actuator/prometheus`.

---

## Part 2 — Instrumentation (the three pillars)

### 2.1 Metrics

```java
@Configuration
class ObservabilityConfig {

    /** Templatize the URI. Without this you get one series per order id. */
    @Bean
    WebServerFactoryCustomizer<ConfigurableWebServerFactory> observations() {
        return factory -> factory.addObservationRegistryCustomizers(registry -> registry
            .config().observationConvention(
                new ServerRequestObservationConvention() {
                    @Override public String getName() { return "http.server.request"; }
                    @Override public String getContextualName(ServerRequestObservationContext ctx) {
                        return "http.server.request " + ctx.getResponse().getStatusCode();
                    }
                    @Override public KeyValues getKeyValues(ServerRequestObservationContext ctx) {
                        String route = ctx.getCarrier().getAttribute(
                            HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE.name());
                        return KeyValues.of(
                            "http.route", route == null ? "unknown" : route,   // template, not /orders/91234
                            "http.request.method", ctx.getRequest().getMethod(),
                            "http.response.status_code", String.valueOf(ctx.getResponse().getStatusCode()),
                            "error.type", errorType(ctx));
                    }
                }));
    }
}
```

Custom business metric + a deliberately useful histogram:

```java
@Component
class PaymentMetrics {
    private final MeterRegistry registry;

    public PaymentMetrics(MeterRegistry registry) {
        this.registry = registry;
        // Bucket boundaries straddle the 200 ms SLO.
        registry.config().meterFilter(MeterFilter.maximumAllowableTags(
            "orderId", 128, MeterFilter.deny()));
    }

    Timer settlement = Timer.builder("settlement.duration")
        .publishPercentiles(0.5, 0.95, 0.99, 0.999)
        .publishPercentileHistogram()
        .serviceLevelObjectives(50, 100, 200, 400, 800, 1600)
        .register(registry);

    public void record(Duration d, boolean failed) {
        settlement.record(d, Tag.of("outcome", failed ? "error" : "ok"));
    }
}
```

### 2.2 Tracing

Use the OTel Java agent (`-javaagent:opentelemetry-javaagent.jar`) for HTTP/JDBC auto-instrumentation, and configure the service:

```yaml
management:
  tracing:
    sampling:
      probability: 1.0        # set to 0.1 after switching to tail-based
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
```

Then prove context survives async work — the classic leak:

```java
@Service
class OrderService {
    private final AsyncSpan currentSpan;

    public CompletableFuture<Pricing> price(Order o) {
        // WRONG: the child span is never ended, or ends after the parent.
        return CompletableFuture.supplyAsync(() -> pricing.fetch(o), executor)
                .whenComplete((v, t) -> currentSpan.get().end());   // end explicitly
    }
}
```

Or, better, use the Micrometer context-propagating executor so scope and span propagate and end automatically:

```java
@Bean
Executor contextAwareExecutor() {
    return ContextExecutorService.wrap(Executors.newFixedThreadPool(32),
                                      ContextRegistry.getInstance());
}
```

### 2.3 Logs

```xml
<!-- logback-spring.xml -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
  <encoder class="net.logstash.logback.encoder.LogstashEncoder">
    <includeMdcKeyName>trace_id</includeMdcKeyName>
    <includeMdcKeyName>span_id</includeMdcKeyName>
    <includeMdcKeyName>request_id</includeMdcKeyName>
    <customFields>{"service":"orders-api","env":"lab"}</customFields>
  </encoder>
</appender>
```

Correlation filter, with the `finally` that prevents MDC leaks across pooled threads:

```java
@Component
class CorrelationFilter extends OncePerRequestFilter {
    static final String REQ = "request_id";
    private final Tracer tracer;

    @Override protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain c)
            throws ServletException, IOException {
        String rid = Optional.ofNullable(req.getHeader("X-Request-Id")).orElseGet(UUID::randomUUID::toString);
        String tid = Optional.ofNullable(tracer.currentSpan().context().traceIdString()).orElse("");
        try (MDC.MDCCloseable a = MDC.putCloseable(REQ, rid);
             MDC.MDCCloseable b = MDC.putCloseable("trace_id", tid)) {
            res.setHeader("X-Request-Id", rid);
            c.doFilter(req, res);
        }   // closeable removes the MDC entries even if the chain throws
    }
}
```

---

## Part 3 — Define the SLO and compute the budget

```java
@Component
class SliCalculator {

    record Sli(double availability, double latencyWithin200ms, long valid) {}

    /**
     * SLI = good / valid over the window.
     *  - valid excludes requests the policy declares non-eligible (client aborts, health checks).
     *  - A minimum `valid` floor prevents 1-request windows from paging.
     */
    Sli compute(long totalRequests, long serverErrors, long tooSlow,
                long excluded, long minValid) {
        long valid = totalRequests - excluded;
        if (valid < minValid) return new Sli(Double.NaN, Double.NaN, valid);
        long good = valid - serverErrors - tooSlow;
        return new Sli((double) (valid - serverErrors) / valid, (double) good / valid, valid);
    }
}
```

Recording rules that make the SLI cheap to query:

```yaml
groups:
- name: sli
  interval: 30s
  rules:
  - record: sli:http_server_request_rate5m
    expr: sum(rate(http_server_requests_seconds_count{env="lab"}[5m]))
  - record: sli:availability_ratio5m
    expr: |
      1 - sum(rate(http_server_requests_seconds_count{env="lab",status=~"5.."}[5m]))
            / ignoring(status) sum(rate(http_server_requests_seconds_count{env="lab"}[5m]))
  - record: sli:latency_ok_ratio5m
    expr: |
      sum(rate(http_server_requests_seconds_bucket{env="lab",le="0.2"}[5m]))
      / sum(rate(http_server_requests_seconds_count{env="lab"}[5m]))
```

**Deliverable**: `SLO.md` with the SLI definition, exclusions, window, budget (`0.1% × 30d = 43.2 min`), and the PromQL that computes it. Show that `le="0.2"` is exactly the numerator — a bucket boundary you chose deliberately.

---

## Part 4 — Alerting on budget burn

```yaml
groups:
- name: slo-burn
  rules:
  # Fast burn: exhaust the 30-day budget in ~2 days. Page.
  - alert: SLOBurnFast
    expr: |
      (1 - sli:availability_ratio5m) > (14.4 * 0.001)
      and
      (1 - sli:availability_ratio5m:5m) > (14.4 * 0.001)
    for: 2m
    labels: { severity: page, budget_exhaustion_days: "2" }
    annotations:
      summary: "Availability budget burning 14.4x — out of budget in ~2 days"
      runbook_url: "https://runbooks.example.com/slo-burn-fast"
      dashboard_url: "https://grafana.example.com/d/slo?var-service=orders-api"

  # Slow burn: will miss the SLO but no imminent outage. Ticket.
  - alert: SLOBurnSlow
    expr: |
      (1 - sli:availability_ratio5m:1h) > (1 * 0.001)
      and
      (1 - sli:availability_ratio5m:6h) > (1 * 0.001)
    for: 15m
    labels: { severity: ticket }
```

Now demonstrate *why* two windows:

```bash
# Inject a 90-second total outage of orders-api.
kubectl scale deploy orders-api --replicas=0; sleep 90; kubectl scale deploy orders-api --replicas=2
```

| Alert variant | Fires? | Pages? | Why |
|---|---|---|---|
| Naive `error_rate > 0.5%` for 1m | yes | yes | correct here, but also pages on a 60 s blip that self-heals |
| Naive `error_rate > 0.001` (any) | yes | yes | pages on a single failed request at 3 a.m. |
| Burn `> 14.4×` on 1 window only | yes | yes | pages on a 90 s blip — false positive |
| Burn `14.4×` on 1h **AND** 5m | yes | yes | correct: sustained, will exhaust in ~2 days |

Then inject a 40-second blip and show the two-window rule does *not* page while the naive rule does.

**Deliverable**: `ALERT_EVALUATION.md` with the matrix above, measured with real Prometheus/Alertmanager state.

---

## Part 5 — Cardinality: find and fix a bomb

Enable exemplars and a raw-URI metric temporarily to create the problem:

```java
// DELIBERATELY BAD — remove in the fix
Timer.builder("api.request.raw").tag("uri", request.getRequestURI()).register(registry).start(request);
```

Drive 20,000 requests across 20,000 distinct `/orders/{id}` paths, then count series:

```promql
count(count by (job, instance, uri, method, status) (api_request_raw_seconds_count))
```

Expected result: ~100,000+ series for one metric.

Apply the fix (template the route via `BEST_MATCHING_PATTERN_ATTRIBUTE`, as in Part 2) and re-measure. Also add:

```java
registry.config().meterFilter(MeterFilter.deny().onApply(
    (id, tags) -> tags.stream().anyMatch(t -> t.getKey().equals("orderId"))));
```

**Deliverable**: `CARDINALITY.md` with before/after series counts, the memory estimate, and the rule that prevents recurrence in code review.

---

## Part 6 — Tail-based sampling that keeps your errors

```yaml
# otel-collector config
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
    - name: errors
      type: status_code
      status_code: { status_codes: [ERROR] }
    - name: slow
      type: latency
      latency: { threshold_ms: 500 }
    - name: baseline
      type: probabilistic
      probabilistic: { sampling_percentage: 5 }
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [otempo/jaeger]
```

Run a 20-minute workload with a 1% injected error rate and a heavy tail, then measure:

| Policy | Traces stored | Errors captured | Slow (>500 ms) captured |
|---|---|---|---|
| Head-based 100% | 100% | 100% | 100% |
| Head-based 1% | 1% | ~1% (statistical) | ~1% (biased away from slow) | 
| Tail-based (above) | ~8% | 100% | 100% |

**Deliverable**: `SAMPLING.md` with the measured table and the cost/benefit argument.

---

## Part 7 — Exemplars: metric → trace → log in one hop

```promql
histogram_quantile(0.99, sum by (le) (rate(settlement_duration_seconds_bucket[5m])))
```

In Grafana, enable exemplars on the panel, hover the outlier bucket, click the exemplar dot, land on the exact trace, then jump to the log line by `trace_id`.

**Acceptance**: you can go from "p99 is 800 ms at 10:42" to the SQL statement that caused it in under two minutes, on a system you built.

---

## Part 8 — Alerts and dashboards as reviewed artifacts

Every alert must carry:
```yaml
labels:
  severity: page
  service: orders-api
annotations:
  summary: "..."
  description: "What is happening, what it means, and what to do first."
  runbook_url: "..."
  dashboard_url: "..."
```

Dashboard panels (in order): SLI value with SLO line → error budget remaining % → burn rate (fast/slow) → request volume → p50/p95/p99/p999 → error rate by status → saturation (thread pool, DB pool, queue depth) → JVM (heap, GC pause rate) → dependency latency.

**Deliverance**: `DASHBOARD.md` explaining the reading order, i.e. the on-call's first 60 seconds.

---

## Acceptance Criteria

- [ ] `SLO.md` defines good/valid/exclusions and computes the budget; the `le="0.2"` bucket is a deliberate numerator.
- [ ] Traces propagate across `orders-api` → `pricing-stub` **and** through `CompletableFuture`, with zero orphan spans (verify by counting spans with missing parents).
- [ ] Every JSON log line carries `trace_id` and `request_id`; MDC does not leak across requests (prove with a 100% check over 1,000 requests).
- [ ] Alerts use multi-window burn rates; the evaluation matrix shows the two-window rule suppressing a 40 s blip that the naive rule pages on.
- [ ] `CARDINALITY.md` shows a >100× series reduction with the metric named and the code fix shown.
- [ ] Tail-based sampling retains 100% of errors and slow traces at <10% of volume.
- [ ] Exemplar path completed in under two minutes, screenshotted.
- [ ] Every alert has a runbook URL and every panel has a purpose in the reading order.

---

## Stretch

- Wire Grafana OnCall/Alertmanager routing to a real on-call rotation and measure pages-per-shift.
- Add a second SLI (throughput/queue-depth) for a `Saturation` view and prove it leads the latency SLI by 3–5 minutes.
- Implement a chaos-driven SLO test: inject latency via Toxiproxy and show the burn-rate alert fires *before* the error rate changes.
