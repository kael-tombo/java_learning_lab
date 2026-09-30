# THEORY: Observability & SRE Engineering for Java Architectures
## Lab 08 | Production Engineering Academy

---

## 1. The Three Pillars vs Modern Unified Observability

Traditional monitoring treated metrics, logs, and traces as disconnected silos. Modern SRE treats them as a single correlated graph rooted in distributed execution:

$$\text{Telemetry Signal} \equiv (\text{Metrics}, \text{Structured Logs}, \text{Distributed Traces}, \text{Continuous Profiles})$$

1. **Metrics (Aggregation over Time)**:
   - Counters, Gauges, Histograms/Summaries.
   - Lowest storage cost ($O(\text{time})$), ideal for rapid alerting (detecting *that* an anomaly is occurring).
2. **Structured Logs (Contextual Events)**:
   - High-fidelity textual/JSON logs with structured attributes (userId, orderId, tenantId).
   - High storage cost ($O(\text{events})$); provides forensic details of failure.
3. **Distributed Traces (Causal Execution DAG)**:
   - Tracks a single transaction across network and process boundaries using W3C Trace Context (`traceparent` header: `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`).
   - Identifies *where* the bottleneck or failure occurred in a multi-hop call graph.
4. **Correlation Anchor**:
   - By injecting `trace_id` and `span_id` as Mapped Diagnostic Context (MDC) into every log line and metric exemplar, an SRE can click a spike on a Prometheus graph, jump directly to the slowest 0.1% trace in Jaeger/Tempo, and see the exact log statements and stack traces.

---

## 2. Service Level Objectives (SLOs), SLIs, and Error Budget Math

### Definitions
- **SLI (Service Level Indicator)**: A quantifiable metric measured over time:
  $$\text{SLI} = \frac{\text{Good Events}}{\text{Total Valid Events}} \times 100\%$$
- **SLO (Service Level Objective)**: Target reliability agreed with business stakeholders (e.g. 99.9% of requests succeed with latency $< 200\text{ms}$ over a rolling 30-day window).
- **Error Budget**: The acceptable margin of failure:
  $$\text{Error Budget} = 100\% - \text{SLO}$$
  For a 99.9% SLO on 10,000,000 requests/month:
  $$\text{Allowed Errors} = 10,000,000 \times 0.001 = 10,000\text{ requests}$$

### Burn Rate Alerting (Google SRE Standard)
Alerting on raw thresholds (e.g. "error rate > 1%") creates false alarms. Alerting on **Error Budget Burn Rate** ensures pages only fire when an outage threatens the monthly SLO:

| Burn Rate | % Budget Consumed | Time to 100% Budget Depleted | Alert Severity |
|:---:|:---:|:---:|:---:|
| **14.4x** | 2% in 1 hour | 2 days | **Page (P1)** |
| **6x** | 5% in 6 hours | 5 days | **Page (P2)** |
| **1x** | 100% in 30 days | 30 days | **Ticket / No Page** |

---

## 3. High-Cardinality Dimensional Explosion

A metric dimension (tag/label) with infinite unique values (e.g. `userId`, `creditCardNumber`, `orderUuid`, `fullURLPathWithId`) causes metric time series to explode exponentially:
$$\text{Total Series} = \prod (\text{Unique values per label})$$
If a label has 1,000,000 unique values, Prometheus memory usage balloons to gigabytes and crashes.
Rule: **Never put high-cardinality values in metric tags; keep them in tracing spans or structured log attributes.**
