# PRODUCTION SCENARIOS: Observability & SRE in Practice
## Lab 08 | Production Engineering Academy

---

## Scenario 1: The High-Cardinality Prometheus Cluster Collapse

### Context
A global logistics platform processing package tracking. An engineer added a Micrometer timer to record latency per package lookup:
```java
// FATAL CODE: High-cardinality tag
Timer.builder("package.lookup.duration")
     .tag("tracking_number", request.getTrackingNumber()) // 10 million distinct values!
     .register(registry)
     .record(duration);
```

### The Incident
- Over the weekend, 4 million distinct packages were looked up.
- Micrometer generated 4 million distinct time series in memory inside every Java pod.
- The JVM heap filled with `io.micrometer.core.instrument.ImmutableTag` objects, triggering garbage collection thrashing and doubling memory usage.
- When the centralized Prometheus server scraped the `/actuator/prometheus` endpoint, the scrape payload was **1.8 GB of raw text** per pod!
- Prometheus crashed with `out of memory` (OOMKill), disabling all alerting, dashboards, and automated scaling across the entire company for 6 hours.

### The Remediation
1. Removed `tracking_number` from metric tags immediately.
2. Put `tracking_number` into the OpenTelemetry Trace Span attributes instead, where high-cardinality strings are indexed per trace without creating infinite time-series streams.
3. Added Prometheus relabeling drop rules to filter runaway series before ingestion.

---

## Scenario 2: The Phantom Trace & ThreadLocal MDC Vanishing Act

### Context
A banking app upgraded to Java 21 Virtual Threads and asynchronous reactive pipelines. During an audit, engineers discovered that 75% of log messages in Datadog/Elasticsearch were completely missing `trace_id` and `user_id`.

### Root Cause
- The logging framework relied on standard `org.slf4j.MDC`, which uses platform `ThreadLocal`.
- When requests switched threads (e.g. from an HTTP servlet thread to a `CompletableFuture` worker or reactive subscriber), the `ThreadLocal` map was not propagated!
- The logs generated inside the async completion stage had empty trace context, making distributed debugging across microservices impossible.

### The Architectural Fix
Implemented OpenTelemetry Context propagation and Spring Framework 6 / Micrometer `ContextSnapshot` bridges that propagate MDC across thread transitions automatically.
