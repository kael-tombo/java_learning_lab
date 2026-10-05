# REAL_WORLD_PROJECT — Tries (Prefix Trees) (`08-tries`)
> Ship a production-flavored use-case of tries with metrics. ~6–10 hours.

## Problem statement
Build a small but honest service/CLI around `Trie` for: autocomplete, spell-check, IP routing, dictionaries.
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
client -> Service (Trie + policy) -> snapshot file
              |-> metrics log (CSV: op, nanos, size, aux)
              |-> oracle checker (sampled, off-path)
```
Keep it single-module; no frameworks required (`com.sun.net.httpserver` or plain CLI is fine).

## Milestones
1. Slice 1 (2h): domain model + `Trie` wired, CLI works on tiny fixture.
2. Slice 2 (2–3h): persistence + config + edge handling (empty/dup/null/adversarial).
3. Slice 3 (2–3h): metrics + benchmark script + chart.
4. Hardening (1–2h): oracle test, chaos script, 1-page ops note (deploy, monitor, rollback).

## Deliverables
- `src/` implementation + `README` run instructions (java version, commands).
- `metrics.csv` + chart + 1-page report (targets vs actuals, bottleneck, next scaling step).
- Postmortem: one real bug found via oracle/chaos, invariant violated, fix.

## Load & chaos scripts (concrete)
```bash
# load: 100k mixed ops, 80% read / 15% write / 5% delete, seeded for replay
java -cp out Load --n 100000 --seed 42 --mix 80/15/5 --csv metrics.csv
# chaos: empty pops, duplicate floods, sorted/adversarial order, snapshot-kill-reload
java -cp out Chaos --scenario empty,duplicates,adversarial,crash-reload
```
Acceptance: 0 oracle mismatches, p99 within target, reload preserves all readable state.

## Operations note (write this before calling it done)
1. Deploy: single jar + properties file; log rotation for metrics.csv; JVM flags recorded.
2. Monitor: alert on p99 breach, resize-storm (resizes/min), FPR drift (bloom), height growth (trees).
3. Rollback: previous snapshot file versioned (`snap-YYYYMMDD-HHmm`); reload is idempotent.
4. Capacity: state the dataset size where this design stops working and what replaces it
   (e.g., hash → sharded/Redis; tree → B-tree/DB index; heap → partitioned scheduler;
   trie → FST/Dawg; bloom → scaled stacked filters; queue → durable broker).

## Cost & scaling sketch
- Estimate bytes/elem from your measurement; extrapolate to 10× and 100× data.
- Name the first bottleneck (GC pauses, resize stalls, probe chains, tree height, bit density)
  and the cheapest fix that moves it 10× (batching, pre-sizing, better hash, balance, larger m, ring→broker).
- One paragraph: build-vs-buy — when you would replace `Trie` with managed infra and why.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle Java docs — `Trie` counterpart guarantees: https://docs.oracle.com/javase/8/docs/api/java/util/Map.html
- Reference survey / encyclopedia entry for tries: https://en.wikipedia.org/wiki/Trie
Verify version-specific behavior against your JDK (run `java -version`) before citing numbers.

## Evaluation
- Works end-to-end from cold start (3 pts) · Metrics honest + reproducible (3) · Edge/chaos handled (2) · Report + postmortem depth (2). Ship ≥7/10.

## Appendix A — test matrix (all must pass)
| # | Case | Oracle / check |
|---|---|---|
| T1 | empty get/pop/peek | throws documented exception, state unchanged |
| T2 | single-element round trip | size 0→1→0, invariant holds at each step |
| T3 | duplicate + null policy | matches documented policy, no silent corruption |
| T4 | resize/rebalance boundary | all elements reachable after threshold crossing |
| T5 | 10k random ops vs oracle | 0 mismatches on size/contains/iteration |
| T6 | snapshot-kill-reload | reloaded state equals pre-kill readable state |
| T7 | adversarial order | degrades gracefully, recovers with documented fix |
| T8 | iterator under mutation | fail-fast fires, no silent wrong iteration |

## Appendix B — example 1-page report skeleton
```
Dataset: 100k keys, mix 80/15/5 | JDK 17, laptop, 5-run median, warmed up
Throughput: 42k ops/s | p50 8µs p99 310µs | bytes/elem 48 | resizes 4 | aux (max-chain 3 / height 18 / FPR 0.8%)
Target check: throughput PASS, p99 PASS, memory noted, oracle 0 mismatches, chaos 4/4 graceful.
Bottleneck: resize pauses at 2^N boundaries dominate p99 → pre-size to 2× expected n.
Next step: shard by hash prefix when n > 10M or move index to LSM/B-tree.
```
