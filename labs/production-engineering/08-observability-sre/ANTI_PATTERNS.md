# ANTI-PATTERNS: Observability, Metrics & Distributed Tracing
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: High-Cardinality Dimensional Explosion in Prometheus Metrics

### The Mistake
```java
// Injecting dynamic IDs directly into Prometheus tags:
meterRegistry.counter("payment.failed",
    "customer_id", customer.getId(),           // Millions of unique IDs!
    "transaction_id", tx.getUuid().toString(),  // Completely unique per request!
    "error_message", exception.getMessage()     // Unbounded strings!
).increment();
```

### Why It Fails (The Billion-Series Crash)
Every unique combination of metric label key-values creates an independent **time-series entry in Prometheus memory**:
$$\text{Active Time Series} = \prod (\text{Cardinality of each label})$$
- 1,000,000 customers $\times$ 5,000,000 transactions = **$5{,}000{,}000{,}000{,}000$ active time series**!
- Prometheus head chunks consume 2 KB per active time series. Memory consumption spikes from 8 GB to hundreds of gigabytes within minutes.
- **The Monitoring Collapse**: Prometheus triggers a Linux OOM-killer kernel crash.
- During a critical payment outage, the entire monitoring system is blind precisely when on-call responders need it most!

### The Correct Production Fix
Strictly enforce the **Cardinality Invariant**:
- **Metrics (Prometheus)**: Low cardinality ONLY ($< 100$ distinct values): `status="500"`, `payment_method="credit_card"`, `gateway="stripe"`.
- **Traces (OpenTelemetry)** & **Logs (MDC)**: High cardinality belongs in trace span attributes or structured JSON log context:
```java
// Correct: Keep high-cardinality in OpenTelemetry Span or MDC:
Span.current().setAttribute("customer.id", customer.getId());
Span.current().setAttribute("transaction.id", tx.getUuid().toString());
```

---

## Anti-Pattern 2: Breaking Distributed Trace Context Across Asynchronous Threads

### The Mistake
Submitting tasks to asynchronous executors without propagating OpenTelemetry context:
```java
@GetMapping("/orders/{id}")
public CompletableFuture<Order> getOrder(@PathVariable String id) {
    // Current thread has active TraceID = 4bf92f...
    return CompletableFuture.supplyAsync(() -> {
        // BUG: Executed by ForkJoinPool worker thread!
        // ThreadLocal context is EMPTY!
        // HTTP calls made from this block have NO traceparent header!
        return paymentClient.chargeOrder(id);
    });
}
```

### Why It Fails
- The distributed trace DAG is broken into disconnected orphans.
- When an engineer inspects the trace in Jaeger or Tempo, the trace ends abruptly at `getOrder()`.
- The downstream database queries and payment calls appear as separate, unlinked "root" traces, making cross-service root-cause attribution impossible.

### The Correct Production Fix
Use **OpenTelemetry Context Wrappers** or configure Spring's `ThreadPoolTaskExecutor` with a `ContextPropagator`:
```java
// Wrap the asynchronous task with current OTel Context:
return CompletableFuture.supplyAsync(
    Context.current().wrapSupplier(() -> paymentClient.chargeOrder(id)),
    tracedExecutorService
);
```

---

## Anti-Pattern 3: Static Threshold Alerting (The Alert Fatigue & Paging Nightmare)

### The Mistake
Configuring alerts on raw, static numbers:
```yaml
# Paging rule:
alert: HighErrorRate
expr: rate(http_requests_total{status="500"}[5m]) > 5
for: 1m
```

### Why It Fails
1. **The Flap at 3:00 AM**: At 3:00 AM, total traffic drops to 10 requests/min. A single client error fires 6 errors in 5 minutes, triggering an urgent PagerDuty page to wake up the on-call engineer for an insignificant blip!
2. **The Black Friday Blindspot**: At peak traffic (50,000 req/sec), 5 errors/sec represents an error rate of $0.01\%$ (healthy baseline). The alert fires continuously, conditioning engineers to ignore pages.
3. **The Slow Budget Bleed**: If error rate is 4 errors/sec for 3 weeks, the alert never fires, yet 100% of the quarterly error budget is silently burned!

### The Correct Production Fix
Adopt Google SRE **Multi-Window Multi-Burn-Rate Alerting**:
- Base alerts on the **rate of Error Budget consumption** relative to the SLO.
- Require both a **short window (5m)** and a **long window (1h)** to burn simultaneously before paging. This guarantees zero pages on transient blips while ensuring high-velocity outages page within 2 minutes.

---

## Anti-Pattern 4: Unstructured String Concatenation Logging

### The Mistake
```java
// String concatenation in hot paths:
log.error("Failed to process order for user " + userId + " with amount " + amount + " error: " + e.getMessage());
```

### Why It Fails
1. **Un-parseable Logs**: Log aggregation tools (Elasticsearch, OpenSearch, Loki) must execute slow, expensive regex patterns over arbitrary text to extract fields.
2. **Missing Correlation Context**: The log entry lacks `trace_id`, `span_id`, and `service_name`. When searching logs during an outage, an engineer cannot isolate the log lines belonging to a specific failed HTTP session.
3. **Heap Churn**: String concatenation inside hot loops allocates transient `StringBuilder` objects, increasing Minor GC pressure.

### The Correct Production Fix
Use **Structured JSON Logging with MDC Injection**:
```java
// In logback-spring.xml: Use Logstash / JSON encoder with automatic traceId injection
try (MDC.MDCCloseable c = MDC.putCloseable("user_id", userId)) {
    log.error("Order processing failed: amount={}, reason={}", amount, e.getMessage(), e);
}
```
*Emitted Structured JSON*:
```json
{
  "timestamp": "2026-10-01T08:14:02.102Z",
  "level": "ERROR",
  "message": "Order processing failed: amount=150.00, reason=Insufficient funds",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "service": "checkout-service",
  "user_id": "usr_84920"
}
```

---

## Anti-Pattern 5: 100% Trace Sampling Under High-Throughput (The Observability Tax)

### The Mistake
Configuring `OTEL_TRACES_SAMPLER=always_on` on a microservice fleet processing 50,000 requests/sec.

### Why It Fails
- At 50,000 req/sec with an average trace spanning 8 microservice hops, the system generates **400,000 spans per second**!
- Network bandwidth between application pods and the OpenTelemetry Collector saturates (hundreds of megabytes per second of trace telemetry).
- Jaeger / Tempo storage backends (Cassandra / S3) cost **more than the actual production database**!
- Application CPU overhead increases by $15\% - 25\%$ purely to serialize and export trace spans.

### The Correct Production Fix
Use **Adaptive Tail-Based Sampling** in the OpenTelemetry Collector:
1. Sample **$1\% - 5\%$ of successful requests** for baseline latency analysis.
2. Sample **$100\%$ of requests that return HTTP 5xx or throw uncaught exceptions**.
3. Sample **$100\%$ of requests whose latency exceeds P99 thresholds** ($> 500\text{ms}$).
This preserves 100% of anomalous and forensic traces while slashing network and storage costs by $95\%$.

---

## Anti-Pattern 6: Logging Sensitive Customer PII / PCI Data in Plaintext

### The Mistake
Logging raw request and response payloads containing credit card numbers, passwords, Social Security numbers, or authorization tokens:
```java
log.info("Incoming payment request payload: {}", requestPayload);
```

### Why It Fails
- Breaches international privacy regulations (GDPR, HIPAA, PCI-DSS) with massive regulatory fines.
- Anyone with read access to Kibana, Datadog, or Grafana Loki gains access to unencrypted customer secrets and credentials.

### The Correct Production Fix
1. Configure automatic Logback / Log4j2 masking filters using regex patterns for PAN (Primary Account Number), CVV, and Authorization headers.
2. Use dedicated DTOs with `@ToString(exclude = "cvv")` or custom Jackson serializers that redact sensitive fields.
