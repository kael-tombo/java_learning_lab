# ARCHITECTURE DECISIONS: Enterprise Observability & OpenTelemetry
## Lab 08 | Production Engineering Academy

---

## ADR-01: Enterprise Telemetry Architecture (OpenTelemetry Standard)

### Status: ACCEPTED

### Context
Engineering teams historically utilized a fragmented mix of proprietary APM agents (Datadog, Dynatrace, New Relic) alongside Micrometer and custom log formatters, locking the company into expensive vendor contracts and causing trace breaks across polyglot microservices.

### Decision
1. **Standardize on OpenTelemetry (OTel)**:
   - All Java microservices must use OpenTelemetry Java API / Instrumentation.
   - W3C Trace Context (`traceparent`) is the mandatory wire format for all HTTP, gRPC, and Kafka headers.
2. **OpenTelemetry Collector DaemonSet / Sidecar Architecture**:
   - Applications emit telemetry over gRPC (OTLP format) to a local OpenTelemetry Collector running on localhost/DaemonSet.
   - The Collector handles batching, compression, retry, PII data scrubbing, and fan-out to backend storage (Prometheus for metrics, Tempo/Jaeger for traces, OpenSearch for logs).
3. **Structured JSON Logging**:
   - All standard output logs must be formatted as structured JSON with mandatory fields: `timestamp`, `level`, `service`, `trace_id`, `span_id`, `message`.

### Consequences
- Completely eliminates proprietary APM agent vendor lock-in.
- Centralizes sampling decisions and PII masking inside the OTel collector.
