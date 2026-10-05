# MINI PROJECT — Streams: Sales Analytics Pipeline

## Goal (2 weeks, ~8–10h)
Turn a messy `orders.csv` into revenue insights with pure-function stream pipelines + a sequential-vs-parallel verdict.

## Requirements
### Functional
1. Load `Order(id,region,product,qty,unitPrice,date)`; pipelines: revenue by region/product, top-5 products, monthly trend, avg order by region.
2. Collectors: `groupingBy` + downstream (`summingDouble/mapping`), `partitioningBy(highValue)`, `toMap` with merge fn (dupe IDs summed, not crash).
3. `flatMap` line items; `Optional` for nullable discount; `IntStream`/`DoubleSummaryStatistics` for qty/price summaries.
4. Parallel report: same pipeline sequential vs parallel on 200k rows; document winner + why (stateless? ordering? size?).
### Non-functional
- No side effects in lambdas; no `collect` mutation outside; handle empty file (empty maps, not exceptions).
- 16+ tests: grouping totals, dupe-merge, empty input, short-circuit (`findFirst`) behavior.
- README: pipeline diagrams (source→ops→terminal) + parallel decision.

## Phases
### Week 1 — Pipelines (4–5h)
- Model + 4 queries + collector tests.
- Deliverable: console report on 10k sample.
### Week 2 — Scale + Verdict (4–5h)
- 200k generator, parallel timing (5 runs avg), empty/dupe hardening.
- Deliverable: benchmark table + verdict memo.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Collector use | Downstream comp, merge fn | Correct basics | Manual loops |
| flatMap/Optional | Clean, tested | Present | orElse-abuse |
| Purity/empty-safe | Pure + empty-proof | Mostly | Side-effect lambda |
| Benchmark | 5-run avg + reasoning | Timed once | Missing |
| Tests | 16+ | 10+ | Happy only |

Pass ≥ 70. Stretch: custom `Collector` (top-N); `takeWhile/dropWhile` cohort query.
