# VISION — Streams

## Vision Statement
**Describe what, not how** — streams turn nested loops into declarative pipelines that are parallelizable, testable, and self-documenting.

---
## Mental Models
### 1. Pipeline: Source → Ops → Terminal
Intermediate ops lazy; nothing runs until terminal (`collect`, `reduce`). Order matters.
### 2. Laziness + Short-Circuit
`filter.map.limit` fuses; `findFirst/anyMatch` stop early. Infinite `generate/iterate` need `limit`.
### 3. Collectors as Reducers
`groupingBy`, `partitioningBy`, `toMap` (merge fn!) — downstream composition replaces hand-rolled loops.
### 4. Parallelism Cost
`parallelStream` helps CPU-bound bulk ops; hurts on small/I/O-bound/ordered/stateful lambdas. Measure.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Simple loop? | Keep loop; stream when pipeline clarifies |
| Side effects in lambda? | No — pure functions only |
| toMap dupes? | Supply merge function |
| Parallel? | Only large, CPU-bound, stateless; benchmark |

---
## Career Trajectory
- **L1:** filter/map/collect, Optional basics.
- **L2:** grouping/partitioning, flatMap, reduce.
- **L3:** custom collectors, parallel tuning, spliterators.
- **L4:** data-pipeline architecture, reactive bridging.

---
## 4-Week Path
```
W1: filter/map/sorted/collect, method refs.
W2: flatMap, reduce, groupingBy/partitioningBy.
W3: Optional bridging, primitives (IntStream), debugging.
W4: Sales-analytics pipeline kata + parallel benchmark.
```
## Success Metrics
- [ ] Replace 30-line loop with readable 8-line pipeline
- [ ] Handle empty/duplicate keys without exceptions
- [ ] Justify sequential vs parallel with numbers
