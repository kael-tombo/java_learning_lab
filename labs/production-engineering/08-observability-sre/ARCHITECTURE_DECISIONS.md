# ARCHITECTURE DECISIONS: Enterprise Observability & SRE Reliability Standards
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: OpenTelemetry (OTel) as Enterprise Telemetry Standard

### Status: ACCEPTED

### Context
Telemetry across 400 microservices was fragmented across proprietary vendor SDKs (Datadog agent, New Relic agent, Zipkin). Trace propagation broke across service boundaries due to incompatible HTTP header formats (`x-b3-traceid` vs `x-datadog-trace-id`), preventing end-to-end distributed tracing.

### Decision
1. **Mandatory W3C Trace Context**:
   - All inter-service communication (HTTP, gRPC, Kafka) must propagate distributed context using the W3C standard `traceparent` and `tracestate` headers.
2. **Standardization on OpenTelemetry**:
   - All Java microservices must instrument telemetry via the OpenTelemetry Java API / Micrometer Observation API.
   - Applications must never bind directly to proprietary vendor telemetry APIs.
3. **In-Cluster OpenTelemetry Collector**:
   - Telemetry signals (Metrics, Traces, Logs) are exported via OTLP/gRPC to a local in-cluster OpenTelemetry Collector daemonset before forwarding to backend storage (Prometheus, Tempo, Loki).

### Consequences
- End-to-end distributed trace propagation guaranteed across all microservices.
- Eliminates vendor lock-in; backend observability storage can be swapped without modifying application code.

---

## ADR-02: Google SRE Multi-Window Multi-Burn-Rate Alerting Standard

### Status: ACCEPTED

### Context
On-call engineers suffered from chronic alert fatigue: over 1,400 PagerDuty pages were fired monthly, of which $> 85\%$ were actionable false alarms or transient metric spikes. Meanwhile, slow-burning degradation went unnoticed until customers escalated on social media.

### Decision
1. **Elimination of Static Metric Threshold Alerts**:
   - Paging alerts on raw error counts (`error_rate > 5`) or arbitrary CPU percentages are strictly decommissioned.
2. **Multi-Window Multi-Burn-Rate Standard**:
   - Critical (P1) paging alerts must evaluate **Error Budget Burn Rates** against the 30-day service SLO.
   - P1 pages require **both** a Short Window (5 minutes) and a Long Window (1 hour) burning at $\ge 14.4\times$ the allowable rate to trigger an alert.
3. **Non-Paging Ticket Allocation**:
   - Slow-burning degradations ($1.0\times$ burn rate over 3 days) must generate automated Jira work-queue tickets instead of waking on-call engineers.

### Consequences
- PagerDuty notification volume dropped by $88\%$ across the engineering organization.
- Eliminates alert fatigue; $100\%$ of fired pages represent actionable, real threats to service SLOs.

---

## ADR-03: Metric Cardinality Governance Policy (Zero Dynamic Identifiers)

### Status: ACCEPTED

### Context
Prometheus clusters frequently crashed with Out-Of-Memory errors during production outages. In multiple post-mortems, engineers were found adding `user_id`, `order_uuid`, or raw SQL queries into Micrometer meter tags, causing active time-series indexes to explode into billions of entries.

### Decision
1. **Strict Cardinality Invariant**:
   - No metric tag or label may contain unbound or high-cardinality identifiers (`user_id`, `order_id`, `email`, `ip_address`, `session_token`, `exception.getMessage()`).
   - The maximum allowable cardinality for any single metric tag is **100 unique values**.
2. **Automated CI/CD Cardinality Linter**:
   - Static analysis linters (ArchUnit / SpotBugs) in CI inspect all `MeterRegistry` and `@Timed` annotations. Any code introducing dynamic string variables as tag keys or values fails the build.
3. **High-Cardinality Telemetry Placement**:
   - High-cardinality metadata must reside exclusively in OpenTelemetry trace span attributes or structured JSON logging (MDC).

### Consequences
- Prometheus memory footprint stabilized with zero OOM crashes.
- Preserves metric scrape reliability during large-scale production surges.

---

## ADR-04: Tail-Based Trace Sampling Architecture (OTel Collector)

### Status: ACCEPTED

### Context
Sustained traffic of 60,000 requests/sec generated over 450,000 trace spans per second under 100% head-sampling. Network egress to cloud tracing backends cost $\$28,000/\text{month}$, and tracing serialization introduced a $12\%$ CPU tax on application pods.

### Decision
1. **Head-Sampling at Application Level**:
   - Application pods configure a low probabilistic head-sampling rate ($5\%$) for normal traffic.
2. **Tail-Based Sampling at OpenTelemetry Collector**:
   - The OpenTelemetry Collector cluster buffers traces in memory until an entire distributed transaction completes.
   - **Sampling Rules**:
     - Keep **$100\%$** of traces where any span returns an error (`status.code == ERROR` or HTTP status $\ge 500$).
     - Keep **$100\%$** of traces where total transaction duration exceeds P95 latency ($> 300\text{ms}$).
     - Keep **$5\%$** of healthy, low-latency baseline transactions for background statistical percentiles.

### Consequences
- Telemetry network egress and storage costs slashed by **$92\%$** ($\$25,700/\text{month}$ savings).
- Guarantees $100\%$ capture of forensic traces for every single error or latency outlier.

---

## ADR-05: Continuous CPU & Memory Profiling Integration (async-profiler / Pyroscope)

### Status: ACCEPTED

### Context
Diagnosing intermittent CPU spikes and transient memory allocation regressions required manually attaching profilers to live production pods during active outages, which was risky, time-consuming, and introduced safepoint bias.

### Decision
1. **Continuous Low-Overhead Profiling**:
   - Deploy continuous profiling agents (Pyroscope / Grafana Phlare using async-profiler under the hood) across production pods.
   - Configured with a low sampling frequency (19 Hz) to ensure total CPU overhead is strictly $< 1.0\%$.
2. **FlameGraph Correlation**:
   - Profiles are continuously tagged with `service_name`, `version`, and active `trace_id`.
   - On-call engineers can inspect historical CPU and memory allocation flame graphs for any 15-minute window in the past 14 days without modifying running pods.

### Consequences
- Eliminates safepoint-biased diagnostic blindspots.
- Enables instant comparison of CPU flame graphs before and after production releases.
