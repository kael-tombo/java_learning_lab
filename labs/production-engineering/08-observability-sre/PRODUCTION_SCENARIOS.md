# PRODUCTION SCENARIOS: Observability & SRE Reliability War Stories
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The $1,200,000 Prometheus Cardinality Blackout

### 1. Incident Context & Architecture
- **Event**: Cyber Monday Flash Sale.
- **Service**: `order-checkout-gateway` (Spring Boot, Prometheus, Grafana).
- **Incident Severity**: P0 / SEV-0 ($60,000/minute revenue stream).

### 2. The Disaster During Traffic Surge
At 18:00 UTC, traffic surged to 40,000 requests/sec:
- Suddenly, **all Grafana dashboards went completely blank**!
- Alertmanager stopped firing alerts; Prometheus UI became completely unresponsive.
- Simultaneously, checkout failure rates spiked, but engineers had **zero visibility** into what was happening!
- Total blackout duration: **42 minutes**, costing an estimated **$1,200,000 in unmonitored checkout drop-offs**.

### 3. Forensic Autopsy: The Rogue Tag
Inspection of Prometheus logs after emergency node restart:
```text
level=error msg="fatal error: out of memory allocating 8589934592 bytes"
```
A junior engineer had added a Micrometer counter 3 days prior:
```java
// THE FATAL COMMIT:
meterRegistry.counter("checkout.events", 
    "status", "failed",
    "cart_id", cart.getId().toString())  // 12 million unique UUIDs!
    .increment();
```
Under peak sale load:
- Over 12,000,000 unique `cart_id` values were pushed to Prometheus within 15 minutes.
- The TSDB inverted index memory exploded from 12 GiB to **over 128 GiB**, triggering the Linux OOM-killer.
- Prometheus entered a crash loop, blinding the entire engineering organization during the most critical revenue hour of the year!

### 4. Production Remediation
1. **Emergency Prometheus Relabeling**:
   Added a `metricRelabelings` rule dropping the `cart_id` label at the scrape gate:
   ```yaml
   metricRelabelings:
     - action: labeldrop
       regex: "cart_id"
   ```
2. **ArchUnit Static CI Gate**:
   Implemented static code analysis rules in CI that fail any PR attempting to add dynamic string variables as Micrometer tag keys or values.
3. Prometheus stabilized at 14 GiB RAM; dashboards restored.

---

## Scenario 2: The Broken Trace Context Async Blindspot

### 1. Incident Context
- **Service**: `loan-origination-pipeline` (Asynchronous microservice architecture).
- **The Mystery**: P99 latency breached SLA limits (climbing from 250ms to 4,800ms).
- **The Investigation Failure**:
  Engineers opened Jaeger to inspect the slow traces:
  - The root span for `POST /api/v1/loan/apply` showed total duration of **only 12ms**!
  - Where were the remaining 4,788 milliseconds being spent?
  - The trace simply stopped!

### 2. Forensic Discovery: Un-Instrumented `CompletableFuture`
Code audit of the controller revealed:
```java
@PostMapping("/apply")
public ResponseEntity<Void> apply(@RequestBody LoanApplication app) {
    // Current thread has active TraceID: 00-4bf92f...
    CompletableFuture.runAsync(() -> {
        // EXECUTED BY FORKJOINPOOL!
        // OpenTelemetry ThreadLocal was NOT transferred!
        creditBureauClient.score(app);     // Took 4,500ms! (Unlinked orphan trace!)
        documentGenerator.create(app);     // Took 300ms! (Unlinked orphan trace!)
    });
    return ResponseEntity.accepted().build(); // Returned in 12ms!
}
```
Because `CompletableFuture.runAsync()` executes on a worker thread from `ForkJoinPool.commonPool()`, the calling thread's `ThreadLocal` was not propagated:
- The downstream credit bureau calls ran as isolated, un-parented traces.
- Engineers could not correlate the slow credit score query with the incoming user request!

### 3. Production Remediation
Implemented the `TraceContextTaskDecorator` to automatically propagate OTel context and MDC across all thread pool submissions:
```java
CompletableFuture.runAsync(
    Context.current().wrap(() -> {
        creditBureauClient.score(app);
        documentGenerator.create(app);
    }),
    managedTaskExecutor
);
```
Traces immediately unified into a complete, end-to-end DAG, revealing the credit bureau API timeout as the true bottleneck.

---

## Scenario 3: The Exemplar-Driven 45-Second Incident Mitigation

### 1. Incident Context
- **Service**: `high-frequency-payment-orchestrator` (40 replicas, 50,000 req/sec).
- **The Anomaly**: At 11:22 UTC, P99 latency suddenly spiked from 14ms to 1,200ms.

### 2. The Traditional Triage Nightmare vs. Exemplar Workflow
- **Traditional Workflow (30–45 Minutes)**:
  Filter logs for "error", guess which pod is struggling, search Jaeger for recent slow traces, try to cross-reference timestamps.
- **The Exemplar Workflow (45 Seconds)**:
  1. **T+00:10**: SRE opens the Grafana Latency Percentiles dashboard.
  2. **T+00:15**: SRE hovers over the sharp 1,200ms spike and clicks on an **Exemplar dot** attached directly to the P99 bucket curve.
  3. **T+00:20**: Grafana opens a split-screen Tempo trace view for `TraceID=7a8b9c...`.
  4. **T+00:30**: The trace DAG clearly shows:
     - Total duration: 1,210ms.
     - Span: `HikariPool-1.getConnection()` took **1,180ms** waiting for an available database connection!
  5. **T+00:45**: SRE identifies the exact issue: database connection pool starvation caused by a stuck table lock in a background reporting query.
  6. The SRE kills the reporting query, and latency drops back to 14ms. Total time from alert to mitigation: **under 2 minutes**!

---

## Scenario 4: The 100% Trace Sampling Storage Cost Shock

### 1. Incident Context & FinOps Escalation
- **Service**: `global-iot-telemetry-gateway`.
- **Workload**: 80,000 incoming telemetry events/sec.
- **The Bill Shock**: The monthly AWS / Datadog invoice arrived with an unexpected **$42,000 charge for Tracing Ingestion and Storage**!
- Tracing costs were **3× higher than the actual compute and database infrastructure combined**!

### 2. Root Cause: Head-Based 100% Sampling
The microservice fleet was configured with:
```yaml
OTEL_TRACES_SAMPLER: "always_on"  # 100% of all traces recorded!
```
At 80,000 req/sec across 6 hops = **480,000 spans/sec** written to storage 24/7. $99.9\%$ of these spans were identical, successful 2ms health checks and routine sensor updates that nobody ever looked at.

### 3. Production Remediation via Tail-Based Sampling
Deployed an in-cluster OpenTelemetry Collector configured with **Tail-Based Sampling**:
- Keep **100%** of errors and HTTP 5xx responses.
- Keep **100%** of slow traces ($> 200\text{ms}$).
- Keep **1%** of healthy baseline transactions.
*Financial Outcome*:
- Ingested trace volume dropped from 480,000 spans/sec to **7,200 spans/sec** ($98.5\%$ reduction).
- Monthly tracing cost plummeted from **$42,000 to $1,800** (saving **$482,400 annually**) with zero loss of forensic data for failures.
