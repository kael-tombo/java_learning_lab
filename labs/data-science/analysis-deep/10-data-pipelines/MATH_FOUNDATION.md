# Math Foundation - Data Pipelines

## 1. Idempotence as a fixed point

Sink state S with merge m: idempotent means m(m(S, b), b) = m(S, b) for
any batch b. Keyed upserts satisfy this (same key overwrites with the
same value); appends do not (replay duplicates rows). The property is
provable per sink in one line - prove it before claiming replay safety.

## 2. Duplicate bound under at-least-once

With per-record duplication probability d over n records, expected
duplicates are n*d and P(at least one duplicate) = 1 - (1-d)^n. Even
tiny d guarantees duplicates at scale - the quantitative reason sinks
must be idempotent rather than hoping transport behaves.

## 3. Windowed aggregation math

Tumbling window mean over width w: each event belongs to exactly one
window, O(n) total. The PipeSchema demo prints window avgs 3.000,
5.333, 4.333 for width 3 - each a plain mean over its slice. Sliding
windows cost O(n*w) naive, O(n) with running sums; keep the running
form when w grows.

## 4. Null-rate and drift checks

nullRate = nulls/rows (0.333 in the demo: 2 of 6). Drift = |mean -
reference| (0.375 vs ref 9.0). Thresholds are policy (e.g. nullRate >
0.05 pages), but the estimators are exact counts - no sampling mystery
at lab scale; document sampling if production checks sample.

## 5. Compatibility as set relations

Reader requires fields R, writer provides W. Compatible if R is a subset
of W with matching types - the keySet().containsAll check plus the type
equality in PipeSchema. Any type change or removed field violates the
subset relation: mechanical, reviewable, no judgment calls.

## 6. Backfill diff arithmetic

Row-count delta, key-overlap fraction, and value-mismatch rate between
staging replay and production quantify a backfill before promotion.
Promote only when all three sit inside pre-declared tolerances - the
numbers are small, the discipline is the point.
