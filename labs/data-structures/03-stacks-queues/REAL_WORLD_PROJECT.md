# REAL_WORLD_PROJECT — Stacks & Queues

Production use-case: **bounded job queue with overflow policy for a worker pool**. Secondary: bracket/expression evaluator CLI.

## 1. Problem statement
Serve enqueue/dequeue with backpressure at scale with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 op latency, throughput (ops/s), max queue depth, correctness bar (FIFO order proof).

## 2. Architecture
- Ingest: producers submitting jobs to the bounded queue.
- Core: ArrayDeque/ring queue behind a narrow interface.
- Serve: dequeue API + depth metrics + health.
- Persist: overflow spill file where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 op latency | define SLO | JMH / load test |
| p99 op latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact FIFO vs oracle | property tests |
| Availability | drain time on shutdown | chaos/restart drill |

## 5. Risks & mitigations
- Overflow loss -> drop-newest/oldest policy + spill.
- Consumer stall -> depth alerts + autoscale hook.
- Memory blowup -> bounded caps + backpressure.
- Concurrency bugs -> SPSC/MPSC discipline + stress tests.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/javase/8/docs/api/java/util/ArrayDeque.html
- https://en.wikipedia.org/wiki/Queue_(abstract_data_type)
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
