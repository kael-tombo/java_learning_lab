# Lab 08: APEX Performance — Exercises

## Exercise 1: Attribute the Page
**Time**: 25 minutes | **Difficulty**: Beginner

### Objective
Produce a ranked component breakdown.

### Steps
1. Build a page with 8 regions over a large table.
2. Enable APEX Debug and capture one load.
3. Rank components by time and compute percentages.
4. Identify the two components holding over half the time.

### Verification
- [ ] Breakdown captured with all components named
- [ ] Percentages computed
- [ ] Top two components identified with their share
- [ ] Regions 5-8 shown to be a negligible share

---

## Exercise 2: Sargability and the Plan
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Turn a full scan into an index range scan.

### Steps
1. Write the query with `TRUNC(column) = :d`.
2. Capture EXPLAIN PLAN and timing.
3. Rewrite as `>= :d AND < :d + 1`.
4. Add a supporting index; re-capture plan and timing.

### Verification
- [ ] Plan before shows a full scan
- [ ] Plan after shows an index range scan
- [ ] Rows examined quantified before and after
- [ ] Rule stated: functions on the right, never the left

---

## Exercise 3: Why Pagination Did Not Help
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Prove pagination cannot fix a non-selective filtered query.

### Steps
1. Query with pagination and a low-selectivity filter.
2. Capture rows examined and timing.
3. Query without pagination; compare.
4. Apply a sargable predicate and re-measure.

### Verification
- [ ] Rows examined captured in all three cases
- [ ] Explanation given for why returned rows and examined rows differ
- [ ] Sargable predicate shows the actual improvement
- [ ] Top-N sort with no index identified as a separate cost

---

## Exercise 4: Binds and Latch Contention
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Replace literal-built SQL and measure the latch effect.

### Steps
1. Write a page process building SQL by concatenation.
2. Query `v$sql` for distinct statements and executions.
3. Check `v$latch` for library cache sleep percentage.
4. Replace with static SQL and a bind; re-measure both.

### Verification
- [ ] Distinct statement count reduced to one
- [ ] Latch sleep percentage recorded before and after
- [ ] Explanation given for why the latch effect is non-linear
- [ ] Explanation given for why it affects unrelated sessions

---

## Exercise 5: Choose the Cache Layer
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Match four problems to the right cache layer.

### Steps
1. List four problems: slow order list, personalised dashboard, 40 KB lookup on
   10 pages, expensive monthly aggregate.
2. Choose region, page, session state, or function result cache for each.
3. Identify which proposed cache would be a data disclosure bug.
4. Write the invalidation trigger for each.

### Verification
- [ ] All four matched correctly
- [ ] Page cache correctly rejected for the personalised page
- [ ] Trigger written for each cache
- [ ] Explanation given for why page cache on personalised content is a leak

---

## Exercise 6: Measure the Hit Rate
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Prove caching is worthwhile at this traffic level.

### Steps
1. Set a 60-second TTL on a region cache.
2. Simulate 60 requests per hour; measure hit rate.
3. Simulate 6 requests per hour; measure again.
4. State at what request rate caching stops paying.

### Verification
- [ ] Hit rates measured at both traffic levels
- [ ] Break-even request rate stated
- [ ] Conclusion drawn from measurement rather than assumption

---

## Exercise 7: Session State Audit
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Reduce per-request overhead from session state.

### Steps
1. Dump all session state keys and their sizes.
2. Classify each: required across pages, derivable, or unnecessary.
3. Remove the largest unnecessary item.
4. Measure the before/after per-request overhead.

### Verification
- [ ] Full inventory produced
- [ ] Largest item removed and replaced with a cached region
- [ ] Per-request overhead reduced
- [ ] Decision rule applied: needs to survive? derivable cheaply?

---

## Exercise 8: PL/SQL Bulk Conversion
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Convert row-by-row processing and measure the gain.

### Steps
1. Write a 500-row cursor loop with per-row SQL; time it.
2. Convert to `BULK COLLECT` + `FORALL`; time it.
3. Convert to a single `MERGE`; time it.
4. Verify row counts match across all three.

### Verification
- [ ] All three timed at the same volume
- [ ] Ratios computed (expect ~30× and ~60× versus the loop)
- [ ] Correctness verified

---

## Exercise 9: Theme Asset Optimisation
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Reduce pre-render transfer time.

### Steps
1. Measure the current CSS and JavaScript response size.
2. Enable CSS and JavaScript minification; re-measure.
3. Enable gzip; re-measure and compute transfer time.
4. Compare against a 5 Mbps connection.

### Verification
- [ ] Sizes measured at each stage
- [ ] Transfer time computed
- [ ] Saving compared against the total page time
- [ ] Explanation given for why this does not appear in Debug output

---

## Exercise 10: Percentile Reporting
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Report the statistic the requirement names.

### Steps
1. Generate activity log entries with a realistic spread.
2. Compute average, p50, p95, p99, and max.
3. Demonstrate a case where the average passes and p95 fails.
4. Check `v$system_event` and state which waits are not the application's.

### Verification
- [ ] All percentiles computed
- [ ] Average/p95 divergence demonstrated
- [ ] Final result reported as p95
- [ ] System waits classified: application versus infrastructure

---

## Exercise 11: Statistics and Plan Instability
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Recognise a plan change with no code change.

### Steps
1. Gather statistics on a table; capture the plan.
2. Bulk load rows without refreshing statistics.
3. Re-capture the plan and timing.
4. Refresh statistics; re-measure.

### Verification
- [ ] Plan captured before and after the load
- [ ] Plan change identified
- [ ] `last_analyzed` confirmed stale between steps
- [ ] Timing difference quantified