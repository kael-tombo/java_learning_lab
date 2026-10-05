# VISION — Data Observability: Knowing Without Being Told
> Where this lab takes you: from dashboards nobody checks to automatic
  detection of freshness, volume, and distribution failures across pipelines.

## The Arc
1. **Signals** — the three pillars: freshness, volume, distribution.
2. **Instrument** — what to emit from a pipeline and at what cost.
3. **Detect** — thresholds, statistical anomaly detection, seasonality.
4. **Explain** — grouping by dimensions, drill-down, lineage-aware alerting.
5. **Respond** — routing, suppression, runbooks, and measuring detection quality.

## Milestones (checkable)
- [ ] M1: emit the 3 pillars from a real pipeline and cost the instrumentation.
- [ ] M2: build an anomaly detector that respects seasonality and does not fire on holidays.
- [ ] M3: group a "volume is down" signal by dimension and find the responsible subset.
- [ ] M4: write a lineage-aware alert that names the likely upstream cause.
- [ ] M5: measure detection quality: MTTD, MTTR, false-positive rate, precision.

## Anti-Goals
- Alerts with no owner, no runbook, and no action.
- Threshold alerts on raw volume during a seasonal peak.
- Monitoring the pipeline's health when the question is the data's health.

## Interview Lens
- "How do you know the data is wrong before a user tells you?"
- "Your alert fired 40 times last week. What did you change?"
- "How do you know your monitoring is working at all?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with the 3 pillars.
- Wk3 add anomaly detection and grouping. Wk4 REAL_WORLD_PROJECT with an incident story.

## Done = You Can
- Detect data failures automatically and prove the detection works.
