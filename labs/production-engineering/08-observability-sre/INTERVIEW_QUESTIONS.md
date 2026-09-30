# INTERVIEW QUESTIONS: Observability & SRE in Practice
## Lab 08 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What is metric cardinality explosion, why does it crash time-series databases like Prometheus, and how do you prevent it in Java?
**Answer**:
Every unique combination of metric name and key-value label pairs forms an independent time series stored in memory and indexed as an inverted index. If a developer tags a metric with a high-cardinality value such as `userId` or `orderUuid`, millions of distinct time series are instantiated. This consumes gigabytes of RAM in both the Java process (Micrometer tag cache) and Prometheus TSDB, eventually causing OutOfMemory crashes.
**Prevention**: Keep metric labels strictly bounded to low-cardinality enums (e.g. `http_status`, `method`, `region`). Put unique transaction identifiers exclusively into Tracing Span attributes or structured JSON log payloads.

---

## Staff / Principal Level (8+ Years)

### Q2: Derive the math for Multi-Window Multi-Burn-Rate alerting for an SLO of 99.9% availability over a 30-day period.
**Answer**:
- Over 30 days ($43,200$ minutes), an SLO of 99.9% allows $0.1\%$ error budget ($43.2$ minutes of total downtime).
- A **1x burn rate** consumes 100% of the budget over 30 days.
- A **14.4x burn rate** consumes $2\%$ of the monthly budget in 1 hour:
  $$\text{Burn} = \frac{0.02}{1 / 720} = 14.4$$
- To avoid alerting on short transient spikes while catching sustained outages rapidly, Google SRE mandates a **two-window lookback**:
  - The alert fires only if BOTH the **short window** (e.g. 5 minutes) AND the **long window** (e.g. 1 hour) are burning at $14.4\times$.
  - This guarantees the alert triggers within minutes of a catastrophic failure, but automatically resets the moment the incident is mitigated, preventing phantom pages.
