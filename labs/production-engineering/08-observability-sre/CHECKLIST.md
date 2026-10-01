# CHECKLIST: Observability, OpenTelemetry & SRE Production Readiness
## Lab 08 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Distributed Tracing & W3C Context Propagation Standards

- [ ] **W3C Trace Context Standard**:
  - [ ] All inter-service network calls (HTTP, gRPC) propagate the W3C `traceparent` and `tracestate` headers.
  - [ ] Kafka producers and consumers inject and extract `traceparent` from Kafka `RecordHeaders`.
- [ ] **Asynchronous Context Preservation**:
  - [ ] All `ExecutorService`, `ThreadPoolTaskExecutor`, and `@Async` beans wrapped with OpenTelemetry `ContextPropagator` or `TaskDecorator` to prevent thread-local context loss.
  - [ ] Virtual Thread execution paths structured via `StructuredTaskScope` or OTel wrappers to guarantee child spans inherit parent `TraceID`.
- [ ] **Metric Exemplars**:
  - [ ] Prometheus Histograms configured with Exemplars enabled in OpenMetrics format.
  - [ ] Grafana dashboards configured to display clickable exemplar dots linking directly to Tempo/Jaeger traces.

---

## 2. Metric Cardinality & Time-Series Hygiene

- [ ] **Strict Cardinality Invariants**:
  - [ ] Zero high-cardinality dynamic identifiers (`user_id`, `order_id`, `email`, `ip_address`, `session_token`, raw error strings) present in Micrometer / Prometheus tags.
  - [ ] Maximum allowable cardinality for any single metric tag is strictly $\le 100$ unique values.
  - [ ] High-cardinality metadata placed exclusively in OpenTelemetry trace span attributes or structured JSON log context (MDC).
- [ ] **Automated CI/CD Static Linting**:
  - [ ] Static analysis rules (ArchUnit / SpotBugs) enforce metric cardinality invariants in CI, failing any PR introducing dynamic variables into metric tags.

---

## 3. Google SRE Multi-Window Multi-Burn-Rate Alerting

- [ ] **Elimination of Static Threshold Alerts**:
  - [ ] Static error count alerts (`error_rate > 5`) completely eliminated for Tier-0 services.
  - [ ] P1 critical pages tied strictly to **14.4x Error Budget Burn Rate** evaluated simultaneously across a 1-hour long window and a 5-minute short window.
  - [ ] P2 urgent pages tied to **6.0x Error Budget Burn Rate** across a 6-hour long window and a 30-minute short window.
- [ ] **Alert Actionability & Runbook Links**:
  - [ ] Every firing alert notification includes a direct link to an actionable, tested runbook.
  - [ ] Alerts include direct dashboard links pre-filtered by the failing service and environment.

---

## 4. OpenTelemetry Collector & Sampling Architecture

- [ ] **Tail-Based Sampling Configuration**:
  - [ ] Collector configured to buffer traces in memory and retain:
    - $100\%$ of spans with `status.code == ERROR` or HTTP status $\ge 500$.
    - $100\%$ of slow traces exceeding P95 latency ($> 300\text{ms}$).
    - $1\% - 5\%$ of healthy baseline transactions for statistical distributions.
- [ ] **Collector High Availability & Buffering**:
  - [ ] OpenTelemetry Collector deployed as a local daemonset or high-availability deployment with HPA.
  - [ ] Exporter sending queues configured with backpressure limits to prevent memory exhaustion during downstream storage degradation.

---

## 5. Structured JSON Logging & PII Masking Hygiene

- [ ] **Structured JSON Formatting**:
  - [ ] Application logs emitted in structured JSON format via Logstash Logback encoder.
  - [ ] Every log line automatically enriched with `trace_id` and `span_id` extracted from MDC.
- [ ] **PII & PCI Redaction**:
  - [ ] Logback configured with regex masking filters to sanitize credit card numbers (PAN), CVVs, passwords, and authorization tokens before writing to disk.

---

## 6. Continuous Profiling Readiness

- [ ] **Low-Overhead Profiling (async-profiler / Pyroscope)**:
  - [ ] Continuous profiling agent deployed across production pods with sampling frequency tuned to **19 Hz**.
  - [ ] Total profiling CPU overhead verified to be strictly $< 1.0\%$.
  - [ ] Profiles tagged with `service_name`, `version`, and `git_commit` to enable automated flame graph diffing between releases.
