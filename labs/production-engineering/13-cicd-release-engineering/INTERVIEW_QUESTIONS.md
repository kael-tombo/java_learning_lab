# INTERVIEW QUESTIONS: Release Engineering & Zero-Downtime Deployments
## Lab 13 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Explain the Expand-Contract pattern for zero-downtime database migrations.
**Answer**:
When modifying database schemas in systems running 24/7 with zero downtime, application code and schema cannot change simultaneously.
1. **Expand**: Add new columns or tables as optional/nullable. Both old and new versions of application code function without error.
2. **Dual-Write**: Deploy application code that writes to both old and new columns, ensuring data consistency while reading from old.
3. **Backfill**: Asynchronously copy historical rows to populate the new column.
4. **Switch Read**: Deploy code reading from the new column.
5. **Contract**: Stop writing to old column, remove deprecated code, and safely drop the old column from the database in a final independent release.

---

## Staff / Principal Level (8+ Years)

### Q2: How do you design an automated Canary Analysis system that avoids false-positive rollbacks while catching subtle performance regressions?
**Answer**:
- **Baseline vs Canary Comparison**: Compare the Canary deployment against an identical "Baseline" deployment (running the old version with equal traffic and pod count) rather than the entire production fleet to eliminate cluster-wide external noise (e.g. cloud latency spikes or third-party partner outages).
- **Statistical Significance**: Use Mann-Whitney U test or Kolmogorov-Smirnov test to verify whether the latency distribution of the Canary is statistically significantly worse than Baseline, rather than relying on crude static threshold comparisons.
- **Warm-Up Exclusion**: Discard telemetry from the first 3 minutes of a newly launched canary pod to prevent JIT compilation and classloading warmup spikes from triggering false-positive aborts.
