# AWS Observability - Mini Project

## Project: Trace-Enabled Instrumentation with a Dimensionality Budget

### Objective
Instrument a three-service call chain with CloudWatch EMF metrics and X-Ray tracing, enforce a
dimensionality budget, and build a dashboard whose every panel answers a decision question.

### Requirements
1. `ObservabilitySimulator` — metric ingestion, dimension limits, and cost modelling
2. `RedMetrics` — request rate, error rate, and duration per route and status
3. `XRaySimulator` — segments, subsegments, and cross-service trace propagation
4. `DimensionalityBudget` — per-namespace series cap with alerting
5. Log correlation: every log line carries the trace ID and a request ID

### Steps

**Step 1: Emit structured metrics, not ad-hoc ones**
```java
void recordRequest(String route, int status, long durationMicros, String tier) {
    dimensions.put("Service", serviceName)
              .put("Route", route)            // template, never the raw path
              .put("Tier", tier);              // "standard" | "premium" -- low cardinality
    putMetricData(metric("Requests", 1, Unit.COUNT, dimensions));
    putMetricData(metric("Latency", durationMicros / 1_000_000.0, Unit.SECONDS, dimensions));
    putMetricData(metric("Errors", status >= 500 ? 1 : 0, Unit.COUNT, dimensions));
}
```
Three dimensions, bounded. Everything else — user ID, request ID, full URL — belongs in logs
and traces, never in metric dimensions.

**Step 2: The dimensionality budget, enforced**
```java
final class DimensionalityBudget {
    private final int maxSeriesPerMetric;
    private final Map<String, Set<Set<String>>> seenCombos = new ConcurrentHashMap<>();

    boolean admit(String metricName, String... dimensionValues) {
        var combos = seenCombos.computeIfAbsent(metricName, k -> ConcurrentHashMap.newKeySet());
        var combo = Set.of(dimensionValues);
        if (combos.contains(combo)) return true;
        if (combos.size() >= maxSeriesPerMetric) {
            cardinalityBreaches.add(metricName + " " + combo);   // drop, never fail the request
            return false;
        }
        combos.add(combo);
        return true;
    }
}
```
Test it by emitting 500 distinct dimension values: the budget must trip, drop the excess, and
**leave the business request unaffected**. Failing the request because of instrumentation is
a self-inflicted outage.

**Step 3: Log lines that join to traces**
```
2026-10-05T11:02:14.331Z INFO  [trace=1-5f2a8b-9c1d4e2f7a3b5c8d span=b2c3d4e5 request=req-9f2a]
  completed order.create orderId=A-10021 durationMs=84 tier=standard
```
Every line carries `trace` and `request`. That single convention makes the difference between
"the logs mention it" and "here is the request". Test it by generating a request and
asserting exactly one `trace=` value appears across all log lines for it.

**Step 4: Trace propagation across services**
```java
// outbound: inject into the request header
var header = "X-Amzn-Trace-Id=Root=" + rootId + ";Parent=" + segmentId + ";Sampled=1";

// inbound: read it and continue the trace
var traceHeader = request.getHeader("X-Amzn-Trace-Id");
```
Add the subsegment for the database call, then the one for the cache call:
```java
var db = xray.beginSubsegment("dynamodb.GetItem");
try { return repository.get(id); } finally { db.end(); }
```
A `finally` block matters: an unclosed subsegment means a trace that never completes, and a
trace that never completes is not queryable. Test that every segment closes by asserting the
trace has no dangling segments after 1000 requests.

**Step 5: A dashboard where every panel earns its place**
| Panel | Question it answers | Decision it informs |
|---|---|---|
| Requests/sec by service | is traffic where I expect? | scale, or investigate a caller |
| Error rate by route | which route is broken? | roll back, page the owning team |
| Latency p50/p99/p99.9 | is the tail the problem? | optimise or accept |
| Throttle count | am I hitting a limit? | request a quota increase |
| Dependency latency | is the slowness mine or theirs? | decide where to look |
| Saturation (CPU/conn pool) | am I near capacity? | scale before it becomes an incident |

If a panel does not map to a decision, delete it. Every panel costs query execution units.

**Step 6: Model the cost**
```text
monthly cost ≈ custom metrics written × $0.30 per 1000
             + log ingestion (GB) × rate
             + dashboard queries × rate
             + alarms × monitors
```
Run the simulator with and without the dimensionality budget. The budget is not a nicety; it
is the difference between a five-figure and a four-figure observability bill.

### Deliverables
1. `ObservabilitySimulator` with ingestion, dimensionality limits, and cost model
2. RED metric emission per service with trace-correlated logs
3. `XRaySimulator` with three-service propagation and a dangling-segment test
4. Dashboard spec mapping every panel to a decision, plus the cost comparison

### Extension (CHALLENGE)
Add exemplar linking from metric data points to trace IDs, then demonstrate how a spike in
`Errors` becomes a jump straight to the specific failed request.

### Estimated Time
3-4 hours