# Lab 13 — Vision: On-Call Excellence for Consumer Lag

## The Standard
Lag is a leading indicator, never a surprise. Dashboards show lag-by-partition + drain rate; autoscaling reacts to lag; poison pills park in DLQ automatically. On-call decides scale-or-skip in minutes.

## What Great Looks Like
- **Partition-aware design**: partitions ≥ 2× peak concurrency; keys spread evenly; ordering needs explicit.
- **Clients tuned**: poll sizes fit p99 processing; timeouts survive GC; commits acknowledged deliberately.
- **Poison-proof**: bounded retries, DLQ with headers, DLQ-rate alert, replay runbook tested.
- **Scale on lag**: HPA/KEDA on lag metric capped at partition count; cooldowns prevent thrash.
- **E2E SLO**: produce-to-consume p99 tracked; burn alerts page before backlog hits retention.

## Anti-Patterns
- Scaling pods while partitions cap parallelism — idle consumers, same lag.
- Infinite retry on deserialization errors; lag grows forever, no DLQ.
- Auto-commit + non-idempotent writes = duplicates and loss on every rebalance.
- Alerting on CPU while lag silently exceeds retention.

## Habits
1. Lag heatmap reviewed in standup during peaks.
2. Monthly replay drill from DLQ in staging.
3. Load test at 2× produce before promo season.
4. Post-mortems ask "hot key or slow code?" with partition evidence.

## Interview Signal
Strong: per-partition `--describe` reasoning, poll-interval math, DLQ + idempotence. Weak: "we added more consumers and it helped (sometimes)."
