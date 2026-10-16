# Fraud Detection System - Performance

## Request budget
- Inline path must fit amount checks, velocity counters, rules, and model scoring.
- Precompute slow aggregates asynchronously; serve them from a fast store.
- Timeouts fall back to a safe default plus an alert, never an unbounded wait.

## Review capacity
- Threshold sets queue inflow; size reviewer staffing from the expected flag rate.
- Order the queue by score and value so limited reviews hit the riskiest cases.
- Track time-to-decision; stale reviews lose their blocking value.

## Training cost
- Retrain on mature windows only; provisional labels waste compute and mislead.
- Refresh features on a slower cadence than thresholds and rules.
- Version everything so a bad refresh rolls back cleanly.

## What to watch
- Decision latency p99, rule hit rates, score mix, queue depth, label maturity.

## Inline path tuning
- Order rules by hit rate so common patterns short-circuit earliest.
- Keep velocity counters in memory with fixed windows; evict cold keys.
- Batch feature lookups per request where the store supports it.

## Async pipeline pacing
- Precompute aggregates on a cadence faster than their staleness tolerance.
- Backpressure slow producers instead of serving partial aggregates silently.
- Mark staleness on every served value so defaults trigger correctly.

## Queue throughput
- Parallelize independent reviews; reserve senior reviewers for the top band.
- Time-box per-case review so one hard case cannot stall the lane.
- Shed low-risk passes first when depth alarms fire, never high-risk blocks.

## Retraining economy
- Train on mature windows sized to pattern stability, not calendar habit.
- Freeze features during threshold experiments to isolate the lever.
- Roll back by version pointer when a refresh degrades band precision.

## Latency verification
- Measure decision p99 at the request edge, not inside the scorer.
- Include rule time, feature time, and model time in the per-request split.
- Alert on p99 movement per decision class: block, review, and pass differ.
