# Distributed Monitoring - Mini Project

## Project: Trace-Safe Metrics, Cardinality Budget, and Burn-Rate Alerts

### Objective
Instrument a three-service call chain, implement RED metrics and span propagation, enforce a
cardinality budget, and build multi-window burn-rate alerting against an SLO.

### Requirements
1. `MetricRegistry` — counters, gauges, histograms with label cardinality limits
2. `TracingSpan` — context propagation across service boundaries
3. `AlertEvaluator` — multi-window, multi-burn-rate SLO evaluation
4. `CardinalityGuard` that rejects label combinations exceeding budget
5. Tests proving trace continuity and alert firing behaviour

### Steps

**Step 1: RED metrics for every service boundary**
```java
record RedSnapshot(long requests, long errors, double sumLatencySeconds, long inflight) {}
// Request rate, Error rate, Duration -- per route, not per URL path
metrics.counter("http_requests_total", "route", "/orders/{id}", "status", "200").inc();
```
Label by **route template**, never by raw path — `/orders/12345` as a label is unbounded
cardinality and will take down the metrics backend on day one.

**Step 2: Cardinality is a budget**
```java
final class CardinalityGuard {
    private final int maxSeriesPerMetric;
    private final Map<String, AtomicInteger> seriesCount = new ConcurrentHashMap<>();

    void check(String metricName, String... labels) {
        var key = metricName + String.join(",", labels);
        if (seriesCount.computeIfAbsent(key, k -> new AtomicInteger()).incrementAndGet() > maxSeriesPerMetric)
            throw new CardinalityBudgetExceeded(key);      // fail the emission, not the request
    }
}
```
Test it by emitting 10,000 distinct label values and asserting the guard trips at the limit
rather than letting the backend fall over. The right behaviour is dropping the new series,
never failing the business request.

**Step 3: Histograms, and choosing buckets deliberately**
```java
Histogram latency = registry.histogram("http_request_duration_seconds",
    List.of(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0));
// p99 accuracy depends on bucket width, not on bucket count
```
Compute the accuracy loss for a given bucket boundary and show why p99 of 250ms in a
[200, 500] bucket is only known to ±250ms. Buckets are a business decision about which
latency ranges matter.

**Step 4: Trace context propagation**
```java
// Inject on the client side
Span client = tracer.span("GET /orders/{id}")
    .propagateInto(Map.of("traceparent", W3C.format(client.context())));

// Extract on the server side -- the whole chain depends on this
Span server = tracer.extractInbound(request.headers()).span("handle GET /orders/{id}");

server.useChildSpan("db.query", () -> repository.findById(id));
server.tag("db.system", "postgresql");
```
Test: fire a request through all three services and assert one trace ID with four spans in
the right parent/child relationships. Then drop propagation on one service and watch the
trace break into fragments — that is the bug this test prevents.

**Step 5: Symptom-based alerting with burn rate**
```
SLO: 99.9% of requests succeed over 30 days
Budget: 0.1% of requests may fail

Fast burn:  14.4x over 1h  AND 5m   -> page   (burns 2% of a 30-day budget in 1 hour)
Slow burn:   6x   over 6h  AND 30m  -> page   (burns 5% in 6 hours)
Both burn windows must be true. This cuts alert volume dramatically versus a single threshold.
```
```java
record BurnRate(String window, Duration period, double threshold, boolean page) {}
record BurnAlert(String slo, BurnRate fast, BurnRate slow) {}

boolean shouldPage(double errorRatio1h, double errorRatio5m,
                   double errorRatio6h, double errorRatio30m, SLO slo) {
    double budget = 1 - slo.target();
    boolean fast = errorRatio1h / budget >= 14.4 && errorRatio5m / budget >= 14.4;
    boolean slow = errorRatio6h  / budget >= 6.0  && errorRatio30m / budget >= 6.0;
    return fast || slow;                 // AND within each rate, OR between the two rates
}
```
The `AND` inside a rate and the `OR` between rates is the detail that makes this work.
Test all four combinations of true/false and assert exactly two page.

**Step 6: Every alert names an action**
```java
record Alert(String name, String symptom, String firstAction, String runbookUrl) {}
```
Reject any alert definition without a non-empty `firstAction`. A count of rejected
definitions is itself a useful metric about the team.

### Deliverables
1. `MetricRegistry`, `CardinalityGuard`, histogram bucket rationale
2. `TracingSpan` with W3C propagation and a three-service trace-continuity test
3. `AlertEvaluator` with the multi-window burn-rate table and four combination tests
4. A RED dashboard spec where each panel names the decision it informs

### Extension (CHALLENGE)
Add sampling (head-based with a consistent probability) and show the error budget impact:
sampled traces lose visibility into rare errors unless sampling is biased toward them.

### Estimated Time
4 hours