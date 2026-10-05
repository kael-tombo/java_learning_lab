# VISION — Vector Database Capstone

> Build an approximate nearest-neighbour index that you can explain at the level
  of the graph, the metric, and the recall/latency trade.

## Why this capstone

Vector search is where a plausible implementation quietly loses accuracy. The
hard parts are the graph structure, the metric (cosine vs IP vs L2 — not
interchangeable for unnormalized vectors), the filtering interaction, and the
recall measurement. Build it and all four become concrete.

## The Arc

1. **Similarity** — L2, inner product, cosine, and when each is correct.
2. **Flat search** — exact, the baseline you must beat, and its cost.
3. **Graph index** — HNSW: layers, `efConstruction`, `efSearch`, and recall.
4. **Filters** — pre-filter vs post-filter, and the filtered-recall problem.
5. **Operate** — build times, memory, updates, deletions, and measurement.

## Milestones (checkable)
- [ ] M1: implement exact search and record its latency as the baseline.
- [ ] M2: implement HNSW and measure recall@k against the baseline across `efSearch`.
- [ ] M3: demonstrate the filtered-recall cliff and implement two mitigations.
- [ ] M4: handle updates and deletes, including the tombstone approach.
- [ ] M5: build a recall harness with a ground-truth set, and report the curve.

## Anti-Goals
- Reporting recall from a self-built index without ground truth.
- Assuming cosine and inner product are the same.
- Filtering after the graph search and calling it equivalent.

## Interview Lens
- "Your recall dropped from 0.98 to 0.91. What changed?"
- "How do you know your index is better than brute force?"
- "How do you delete a million vectors?"

## 30-Day Plan
- Wk1 metrics + exact search. Wk2 HNSW build, measure the recall/latency curve.
- Wk3 filters + deletes. Wk4 the recall harness and a written accuracy report.

## Done = You Can
- State your recall, your latency, and the parameter that trades one for the
  other, and justify all three.
