# Lab 01: EBS Architecture — Vision

## Where this lab takes you
From "the app tier is slow" to a diagnosis that names the saturated tier, the
service that caused it, and the specific change that fixes it.

## The Arc
1. **Read the symptom** — month-end slowdown described in business terms.
2. **Split the evidence** — which tier is actually constrained?
3. **Find the mechanism** — a single Concurrent Manager serialising everything.
4. **Find the contention** — `JTF_QUEUE_LOCK` explained, not memorised.
5. **Apply the fix** — tier cloning plus specialised Concurrent Managers.
6. **Prevent recurrence** — JTF clustering and work shifts.
7. **Prove it** — load test and monitored before/after comparison.

## Milestones (checkable)
- [ ] M1: State the two metrics that proved the app tier was the constraint.
- [ ] M2: Explain why 60% database utilisation rules out the database.
- [ ] M3: Diagnose the single-queue Concurrent Manager from the request log.
- [ ] M4: Explain what `JTF_QUEUE_LOCK` contention actually is.
- [ ] M5: Produce a node-cloning plan with per-node service assignment.
- [ ] M6: Create specialised managers with correct target nodes.
- [ ] M7: Configure work shifts to throttle non-critical work at peak.
- [ ] M8: Present before/after load test results with measured deltas.

## Anti-Goals
- Increasing forms processes when the bottleneck is CM queue depth.
- Attributing a month-end slowdown to "more data" without a metric.
- Scaling the application tier without checking queue wait time first.
- Fixing CM contention by raising the process count rather than specialising.

## The one-sentence thesis
App tier CPU at 100% with the database at 60% is a tier diagnosis, not a SQL
problem — the queue in front of the worker is the system under study.