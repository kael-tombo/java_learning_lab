# Distributed Monitoring - Interview Preparation

> Key interview questions about monitoring and observability in distributed systems.

---

## Core Interview Questions

### Q1: What are the three pillars of observability?
**Answer**: Logs (structured events with timestamps), Metrics (numeric aggregations over time), Traces (request lifecycle across services). Modern observability combines all three. Logs answer "what happened", metrics answer "how many/how fast", traces answer "where in the call path".

### Q2: How do you design a distributed tracing system?
**Answer**: Trace context propagation (trace_id, span_id) via headers (W3C Trace Context, Zipkin B3). Each service creates child span, propagates context. Collector aggregates spans, builds trace tree. Storage: Cassandra (Jaeger), Elasticsearch, or custom columnar store. Sampling: head-based or tail-based.

### Q3: What are RED metrics and why are they important?
**Answer**: Rate (requests per second), Errors (failed requests), Duration (latency distribution). RED focuses on user-facing service health. Each service should expose RED metrics for its dependencies. Derived from Google's SRE "Four Golden Signals": latency, traffic, errors, saturation.

### Q4: How does Google's Monarch monitoring system work?
**Answer**: Monarch: Google's global monitoring system. Time-series database with global data model. Hierarchical aggregation: zone -> cluster -> service. Query language for complex aggregations. Automatic anomaly detection. Multi-tenant with strong isolation. Uses Bigtable for storage.

### Q5: How do we monitor for the "unknown unknowns"?
**Answer**: Service-level objectives (SLOs) with error budgets. Burn rate alerts (how fast error budget consumed). Apdex scores (user satisfaction). Dark launch monitoring. Structured logging with correlation IDs. Canary analysis. Real user monitoring (RUM).

## Company-Specific Focus

| Company | Monitoring Focus |
|---------|-----------------|
| Google | "Monarch, SRE practices, Four Golden Signals" |
| Netflix | "Atlas monitoring system" |
| Amazon | "CloudWatch architecture" |
| Meta | "Scuba real-time analytics" |
| Datadog/NewRelic | "Modern APM design" |

## LeetCode Connections

| Problem | # | Monitoring Concept |
|---------|---|-------------------|
| Design Hit Counter | 362 | Request rate counting |
| Top K Frequent | 347 | Top-k error finding |
| Moving Average from Data Stream | 346 | Sliding window metrics |
| Logger Rate Limiter | 359 | Rate-based alerting |
| Time Based KV Store | 981 | Time-series data queries |

## System Design Connections

- **Design a Metrics Collection System**: Agent -> aggregator -> time-series DB
- **Design a Distributed Tracing System**: Context propagation + sampling
- **Design an Alerting System**: Rule evaluation + deduplication + notification
- **Design a Dashboard System**: Query language + visualization

## Key SRE Concepts

- **Service Level Indicator (SLI)**: Measured metric (latency p99 < 200ms)
- **Service Level Objective (SLO)**: Target (99.9% availability)
- **Service Level Agreement (SLA)**: Contractual obligation (99.95%)
- **Error Budget**: 1 - SLO. How much failure allowed before consequences
- **Burn Rate**: How fast error budget consumed (1hr window, 6hr, 1d, 3d)

> **Key Insight**: Monitoring questions are about systems design for observability. Always discuss the three pillars: logs, metrics, traces. Know RED and USE (Utilization, Saturation, Errors) monitoring methods.