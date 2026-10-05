# REAL_WORLD_PROJECT — Trees (Binary Trees) (`04-trees`)
> Ship a production-flavored use-case of trees with metrics. ~6–10 hours.

## Problem statement
Build a small but honest service/CLI around `BinaryTree` for: DOM, file systems, expression trees, decision trees.
Examples: autocomplete API (trie), priority scheduler (heap), ordered index with range scan (BST/balanced tree),
deduplicating ingest cache (hash), graph route planner (graphs), disk-pre-check layer (bloom), ring buffer pipeline (queue/stack).

## Functional requirements
1. CLI or HTTP endpoint: `put/get/delete` (or domain equivalent: `schedule/pop`, `insert/suggest`, `add/mightContain`).
2. Persistence or snapshot: load/save to file (JSON/CSV/serialized); reload preserves correctness.
3. Config: capacity / threshold / k,m / comparator / seed exposed via flags or properties file.
4. Observability: log operation latencies (avg/p50/p99), hit/miss or FPR estimate, resize/rotation counts, memory.
5. Correctness: oracle cross-check on a sample workload (vs `HashMap`/`TreeMap`/`PriorityQueue` as appropriate).

## Non-functional targets (measure and report)
| Metric | Target (toy-prod) | How to measure |
|---|---|---|
| Throughput | ≥10k ops/s single-thread on 100k dataset | benchmark harness, warmup, 5 runs median |
| p99 latency | <1 ms point op on laptop | HDR-ish histogram or sorted samples |
| Memory | report bytes/elem (Runtime/JOL) | before/after load snapshot |
| Correctness | 0 mismatches vs oracle on 10k random ops | oracle test log |
| Resilience | graceful empty/full/degraded (incl. bloom FPR) behavior | chaos script: empty, dup flood, adversarial order |

## Architecture sketch
```
client -> Service (BinaryTree + policy) -> snapshot file
              |-> metrics log (CSV: op, nanos, size, aux)
              |-> oracle checker (sampled, off-path)
```
Keep it single-module; no frameworks required (`com.sun.net.httpserver` or plain CLI is fine).

## Milestones
1. Slice 1 (2h): domain model + `BinaryTree` wired, CLI works on tiny fixture.
2. Slice 2 (2–3h): persistence + config + edge handling (empty/dup/null/adversarial).
3. Slice 3 (2–3h): metrics + benchmark script + chart.
4. Hardening (1–2h): oracle test, chaos script, 1-page ops note (deploy, monitor, rollback).

## Deliverables
- `src/` implementation + `README` run instructions (java version, commands).
- `metrics.csv` + chart + 1-page report (targets vs actuals, bottleneck, next scaling step).
- Postmortem: one real bug found via oracle/chaos, invariant violated, fix.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle Java docs — `BinaryTree` counterpart guarantees: https://docs.oracle.com/javase/8/docs/api/javax/swing/tree/TreeNode.html
- Reference survey / encyclopedia entry for trees: https://en.wikipedia.org/wiki/Binary_tree
Verify version-specific behavior against your JDK (run `java -version`) before citing numbers.

## Evaluation
- Works end-to-end from cold start (3 pts) · Metrics honest + reproducible (3) · Edge/chaos handled (2) · Report + postmortem depth (2). Ship ≥7/10.
