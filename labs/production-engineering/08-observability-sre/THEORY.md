# THEORY: Observability, OpenTelemetry & SRE Reliability Engineering
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Unified Observability Graph: Metrics, Traces, Logs & Exemplars

Traditional monitoring siloed telemetry into disconnected databases: Prometheus for metrics, Elasticsearch for logs, Jaeger for traces. Modern SRE treats telemetry as a **single, unified, correlated graph** anchored by distributed trace context.

```
                           ┌──────────────────────────────────────────────┐
                           │            W3C Trace Context                 │
                           │   (trace_id, span_id, trace_flags)           │
                           └──────────────────────┬───────────────────────┘
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     Prometheus Metrics +        │      │    OpenTelemetry Tracing DAG    │      │    Structured JSON Logging      │
│          EXEMPLARS              │      │      (Causal Span Tree)         │      │      (MDC Context Injection)    │
├─────────────────────────────────┤      ├─────────────────────────────────┤      ├─────────────────────────────────┤
│ • Aggregated over time          │      │ • Inter-service network hops    │      │ • Exact error forensics         │
│ • Detects "THAT" an outage is   │ ────►│ • Identifies "WHERE" the delay  │ ────►│ • Identifies "WHY" code broke   │
│   occurring in < 30 seconds     │      │   occurred in the DAG           │      │   (Stack trace, query payload)  │
│ • Exemplar links metric point   │      │ • Propagates via HTTP headers,  │      │ • Filtered by trace_id          │
│   directly to 99th-p trace!     │      │   Kafka headers, gRPC metadata  │      │   for 100% correlation          │
└─────────────────────────────────┘      └─────────────────────────────────┘      └─────────────────────────────────┘
```

### 1.1 The W3C Trace Context Standard
Distributed transactions traverse multiple processes, containers, and asynchronous thread boundaries via the **W3C `traceparent` header**:

$$\texttt{traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01}$$

- **`00`**: Version (current standard).
- **`4bf92f3577b34da6a3ce929d0e0e4736`**: `TraceID` (16 bytes / 32 hex chars) — universally identifies the end-to-end user request.
- **`00f067aa0ba902b7`**: `ParentID` / `SpanID` (8 bytes / 16 hex chars) — identifies the immediate upstream caller.
- **`01`**: `TraceFlags` (`01` = recorded/sampled; `00` = unsampled).

### 1.2 Metric Exemplars: Bridging the Metric-to-Trace Divide
In Prometheus and OpenMetrics, an **Exemplar** attaches a concrete `TraceID` to a specific bucket observation in a histogram:
```text
http_server_requests_seconds_bucket{le="0.5"} 14208 # {trace_id="4bf92f3577b34da6a3ce929d0e0e4736"} 0.482 1727768400.120
```
When an on-call engineer sees a P99 latency spike on a Grafana dashboard, they click the exemplar dot directly on the metric graph, which instantly opens the exact trace span in Tempo/Jaeger without searching or guessing!

---

## 2. Service Level Objectives (SLOs), SLIs & Error Budget Mathematics

Reliability is not 100%. Aiming for 100% availability is economically irrational and stalls product innovation. Google SRE codifies reliability around **Service Level Indicators (SLIs)**, **Service Level Objectives (SLOs)**, and **Error Budgets**.

### 2.1 Mathematical Formulations
$$\text{SLI (Service Level Indicator)} = \frac{\sum \text{Good Events}}{\sum \text{Total Valid Events}} \times 100\%$$

$$\text{Error Budget} = 100\% - \text{SLO}$$

For an e-commerce platform processing $20{,}000{,}000$ checkout requests over a rolling 30-day window with an agreed **99.9% SLO**:
$$\text{Allowed Errors (30-day budget)} = 20{,}000{,}000 \times (1.0 - 0.999) = 20{,}000\text{ allowed failed requests}$$

```
                30-Day Error Budget (99.9% SLO = 20,000 Failed Requests)
┌──────────────────────────────────────────────────────────┬──────────────┐
│                  19,980,000 Good Requests                │20,000 Budget │
│                         (99.9%)                          │   (0.1%)     │
└──────────────────────────────────────────────────────────┴──────┬───────┘
                                                                  │
                    Rate of Consumption = BURN RATE                ▼
   ┌──────────────────────────────────────────────────────────────────────┐
   │ • 1x Burn: Consumes 100% budget in exactly 30 days (Healthy normal)  │
   │ • 14.4x Burn: Consumes 2% of total budget in 1 hour (PAGE P1!)       │
   │ • 144x Burn: Consumes 100% of total budget in 5 hours (CATASTROPHIC) │
   └──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Google Multi-Window Multi-Burn-Rate Alerting
Traditional static threshold alerting (e.g. `error_rate > 1%`) fails: it pages on tiny, inconsequential spikes and stays silent during slow, catastrophic budget leaks. The Google SRE standard evaluates **two concurrent rolling windows** (short window + long window) across specific burn rates:

| Alert Severity | Burn Rate | % Budget Consumed | Long Window | Short Window | Time to 100% Exhaustion |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Page (P1 - Critical)** | **$14.4\times$** | $2.0\%$ | 1 Hour | 5 Minutes | 2 Days |
| **Page (P2 - Urgent)** | **$6.0\times$** | $5.0\%$ | 6 Hours | 30 Minutes | 5 Days |
| **Ticket (P3 - Workday)** | **$1.0\times$** | $10.0\%$ | 3 Days | 6 Hours | 30 Days |

**Prometheus Alert Rule for 14.4x Burn Rate**:
```promql
# Long window (1h) AND Short window (5m) both burning at 14.4x:
(
  sum(rate(http_requests_total{status=~"5.*"}[1h])) 
  / 
  sum(rate(http_requests_total[1h]))
) > (14.4 * (1 - 0.999))
and
(
  sum(rate(http_requests_total{status=~"5.*"}[5m])) 
  / 
  sum(rate(http_requests_total[5m]))
) > (14.4 * (1 - 0.999))
```

---

## 3. High-Cardinality Dimensional Explosion in Metric Time-Series

### 3.1 The Combinatorial Explosion Formula
In Prometheus, M3DB, or VictoriaMetrics, a metric is defined by its name and unique set of key-value label pairs. Every unique combination generates a **distinct in-memory time-series index**:

$$\text{Total Active Series} = N_{\text{metric}} \times \prod_{i=1}^{k} C(\text{label}_i)$$

Where $C(\text{label}_i)$ is the cardinality (number of distinct values) of label $i$.

### 3.2 The Disaster Scenario
Suppose a junior developer instruments an HTTP request latency histogram with the following labels:
```java
// CATASTROPHIC ANTI-PATTERN:
meterRegistry.timer("http.requests",
    "method", request.getMethod(),              // 4 values (GET, POST, PUT, DELETE)
    "status", String.valueOf(response.getStatus()), // 10 values
    "user_id", user.getId(),                   // 5,000,000 values!
    "order_id", order.getUuid().toString());   // 10,000,000 values!
```

$$\text{Total Series} = 4 \times 10 \times 5{,}000{,}000 \times 10{,}000{,}000 = 2{,}000{,}000{,}000{,}000{,}000 \text{ series!}$$

**The Crash**:
- Each Prometheus time-series consumes $\approx 2\text{ KB}$ of RAM in head chunk memory.
- Prometheus attempts to allocate petabytes of RAM, runs out of memory, enters a crash loop, and the entire monitoring infrastructure collapses during a production outage!

### 3.3 The Cardinality Golden Rule
| Telemetry Signal | Permitted Cardinality | Example Attributes |
|:---|:---:|:---|
| **Metrics (Prometheus)** | **Low ($< 100$ per label)** | `method="POST"`, `status="500"`, `region="us-east-1"`, `client="web"` |
| **Traces (OpenTelemetry)** | **High (Unlimited)** | `user.id="usr_8492"`, `order.uuid="ord_91820"`, `db.statement` |
| **Structured Logs (MDC)** | **High (Unlimited)** | `ip_address`, `cart_total`, `session_token_hash` |

---

## 4. OpenTelemetry Context Propagation Across Threads & Virtual Threads

In asynchronous, non-blocking, or reactive Java pipelines (Netty, CompletableFuture, RxJava, Project Reactor, and Java 21 Virtual Threads), standard `ThreadLocal` context propagation breaks:

```
Thread A (HTTP Server EventLoop):
  TraceContext: TraceID = 4bf92f...
  Issues asynchronous DB query ──► Passes callback to Thread B
                                          │
Thread B (HikariCP Worker Pool):           ▼
  ThreadLocal is EMPTY! ──► TraceContext is LOST!
  Outgoing DB query has NO traceparent header! Tracing DAG is broken!
```

### 4.1 Solutions: OpenTelemetry Context Wrappers
OpenTelemetry provides context encapsulation to bridge execution across thread boundaries:
```java
// Wrap Runnable or Callable with current active OTel context:
Runnable wrappedTask = Context.current().wrap(originalRunnable);
executorService.submit(wrappedTask);
```

### 4.2 Project Loom (Virtual Threads) & Scoped Values (JEP 446)
While Virtual Threads support `ThreadLocal`, allocating millions of virtual threads with large thread-local maps creates memory overhead. Modern OpenJDK 21+ architectures leverage **Scoped Values (`ScopedValue<T>`)**:
- Immutable, bounded to execution scope.
- Inherited automatically by child virtual threads structured via `StructuredTaskScope`.
- Eliminates thread-local memory leaks.

---

## 5. Micrometer 1.10+ Observation API (Spring Boot 3)

Spring Boot 3 replaced legacy Spring Cloud Sleuth with the unified **Micrometer Observation API**:

```java
// A single instrumentation produces BOTH metrics AND distributed tracing spans!
Observation.createNotStarted("order.fulfillment", observationRegistry)
    .lowCardinalityKeyValue("order.type", "digital")     // Becomes Prometheus tag
    .highCardinalityKeyValue("order.id", order.getId())  // Becomes OpenTelemetry trace span attribute
    .observe(() -> executeFulfillment(order));
```

This ensures zero discrepancy between metric counters and distributed trace spans.
