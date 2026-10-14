# VISION — Searching Track
> Direction: from binary-search-by-default to matching the structure to the query mix — hits vs misses, uniform vs skewed.

## Where this sits
- Sorted arrays: binary O(log n) always, exponential for unbounded fronts, interpolation O(log log n) only under uniformity.
- Hash tables: expected O(1) at controlled load factors; misses and resize pauses are the real costs.
- Trees: BST O(h) degrading without balance; balanced trees restore O(log n) with rotation overhead.
- The query mix (hit rate, skew, range vs point) picks the winner, not the data structure alone.

## 4-week direction
- Week 1: write binary search half-open from memory; prove the interval invariant on paper.
- Week 2: finish MINI_PROJECT; measure the interpolation collapse yourself on skewed keys.
- Week 3: push a hash table through 0.5/0.75/0.95 load and record probe growth.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the method-choice decision tree in 10 minutes.

## Done criteria
- State each method's bound plus the assumption it depends on (uniformity, load, balance).
- Split any search benchmark into hit and miss columns by reflex.
- Pick the method for a given (n, hit rate, skew, range need) and defend it with numbers.

## Non-coverage
- This track does not build text search, nearest-neighbor, or learned indexes; point/range lookup on ordered and hashed keys is the scope.
- Concurrency control for live indexes is policy (snapshots here), not implemented locking.
- External-memory (B-tree) search is named with its page-size trigger, not built.

## Pitfalls
- Averaging hits and misses; miss cost dominates adversarial mixes.
- Deploying interpolation on skewed keys because the uniform bound looked good.
- Letting load factor drift; probe counts compound silently.

## Adjacent tracks
- Pair with sorting for index construction and data-structures for hash/BST internals.
- Revisit when a lookup path slows; the hit/miss split is the first diagnostic.

## Weekly drills
- Write half-open binary search from memory and prove termination via the shrinking interval.
- Recompute interpolation's expected probe count assumption chain (uniformity in, O(log log n) out).
- State the load-factor discipline (resize at 0.75, why) with the probe-growth reason.

## Anti-roadmap
- Do not blend hit and miss latencies; report the split or report nothing.
- Do not enable interpolation without the skew monitor watching it.
