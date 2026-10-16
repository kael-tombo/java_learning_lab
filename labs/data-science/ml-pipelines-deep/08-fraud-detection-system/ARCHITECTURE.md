# Fraud Detection System - Architecture

## Components
- Feature service: serves cheap inline features inside the request budget.
- Rules engine: evaluates deterministic patterns first for instant decisions.
- Model scorer: scores non-ruled traffic and returns calibrated scores.
- Review queue: holds uncertain cases ordered by score and value.
- Label joiner: merges late dispute outcomes by transaction key.

## Data flow
- Request -> features -> rules -> model -> decision (block, review, pass), all logged.
- Async path precomputes slow aggregates into the feature store.
- Labels flow back into training data and rule tuning on a refresh cadence.

## Latency split
- Request path carries only cheap features and the warmed model.
- Slow lookups stay async; missing values use documented defaults, not blocking waits.
- Timeouts produce a safe default decision plus an alert, never an unbounded wait.

## Storage
- Decisions log with score, rule hits, feature snapshot, and model version.
- Mature label tables power official metrics; fresh tables are provisional.
- Rule and threshold changes are versioned like code.

## Feature freshness
- Inline features read from low-latency stores refreshed on short cadences.
- Async aggregates land on their own schedule with staleness markers.
- Stale markers route decisions to safe defaults instead of silent old values.

## Queue mechanics
- Ordering key combines score rank with value at risk for reviewer priority.
- Aging rules escalate cases whose blocking value decays with time.
- Depth alarms fire before overflow so thresholds tighten deliberately.

## Rule lifecycle
- Rules deploy versioned with hit-rate dashboards from the first hour.
- Decaying hit rates trigger review; dead rules retire on schedule.
- Emergency rules ship narrowly scoped and expire unless renewed.

## Audit trail
- Every decision stores score, rule hits, snapshot, version, and timestamp.
- Reviewer labels join the same record with reviewer id and decision time.
- Regulators and postmortems read the identical trail, not reconstructions.
