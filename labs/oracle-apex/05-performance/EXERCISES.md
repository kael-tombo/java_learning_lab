# Lab 05: APEX Performance — Exercises

## Exercise 1: Attribute the 30 Seconds
**Time**: 25 minutes | **Difficulty**: Beginner

### Objective
Produce a component-level timing breakdown.

### Steps
1. Build a page with 10 regions over a large table.
2. Enable APEX Debug and capture the breakdown.
3. Split the total into SQL, PL/SQL, rendering, and session state.
4. Identify the top two contributors by percentage.

### Verification
- [ ] Breakdown captured before any change
- [ ] Percentages computed and summing to 100
- [ ] Top two contributors named with their share
- [ ] Optimisation order derived from the breakdown, not intuition

---

## Exercise 2: Share a Query with a Collection
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Reduce 16 region queries to one.

### Steps
1. Populate a collection from the shared query in a Before Header process.
2. Rewire every region to read from `APEX_COLLECTION`.
3. Confirm no region queries the base table.
4. Measure before and after.

### Verification
- [ ] All regions read from the collection
- [ ] Query count reduced from 16 to 1
- [ ] Improvement measured
- [ ] Column index contract documented (c001..cNN positions)

---

## Exercise 3: Cache and Measure the Hit Rate
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Cache a region and prove the hit rate justifies it.

### Steps
1. Cache the slowest region for 30 seconds.
2. Simulate 50 requests within one TTL window.
3. Measure actual hits and misses.
4. Compute the effective cost with and without the cache.

### Verification
- [ ] Hit rate measured, not assumed
- [ ] Effective cost computed from the measured rate
- [ ] Conclusion stated on whether caching was worth it
- [ ] Low-request-rate case explored and reported

---

## Exercise 4: Invalidation Triggers
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Give every cache a documented invalidation path.

### Steps
1. Cache a region dependent on a reference table.
2. Update the reference table.
3. Confirm the cached data is stale.
4. Call `APEX_REGION_CACHE.clear_cache` and confirm freshness.

### Verification
- [ ] Staleness demonstrated before invalidation
- [ ] Explicit invalidation restores freshness
- [ ] Named owner and trigger documented for each cache
- [ ] Explanation of why an untriggered cache is a latent incident

---

## Exercise 5: Set-Based Rewrite
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Replace row-by-row processing and measure the difference.

### Steps
1. Write a row-by-row update over 50,000 rows; time it.
2. Rewrite it as a single MERGE; time it.
3. Repeat for insert and delete.
4. Record the ratio at each volume.

### Verification
- [ ] Both versions timed at the same volume
- [ ] Ratio recorded and compared against the ~120× expectation
- [ ] Correctness verified (row counts match between versions)

---

## Exercise 6: Bounded Export
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Export at scale without timing out or truncating silently.

### Steps
1. Build a set-based export of 100,000 rows; time it.
2. Add an explicit row limit with a clear error message.
3. Confirm the limit refuses rather than truncating.
4. Add GZIP and compare transfer time.

### Verification
- [ ] 100,000 rows exported under 30 seconds
- [ ] Over-limit request refused with a specific message
- [ ] No silent truncation anywhere in the path
- [ ] GZIP comparison recorded

---

## Exercise 7: Bulk Import with Reject Log
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Import a large CSV with set-based statements only.

### Steps
1. Load 50,000 rows into staging.
2. Validate in bulk with two set-based UPDATEs.
3. Apply valid rows with a single MERGE.
4. Produce a reject report grouped by reason.

### Verification
- [ ] No row-by-row loop anywhere in the path
- [ ] Validation covers all rows
- [ ] Reject report grouped by reason
- [ ] Total import time recorded against a row-by-row baseline

---

## Exercise 8: Cascading Filters
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Prevent invalid filter combinations.

### Steps
1. Count reachable combinations without cascading.
2. Implement cascading LOVs.
3. Recount valid combinations.
4. Compare query cost for a formerly invalid combination.

### Verification
- [ ] Combination counts computed before and after
- [ ] Cascading LOV configured with a parent item
- [ ] Cost of a formerly invalid combination quantified

---

## Exercise 9: Statistics and the Silent Regression
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Recognise planner behaviour change with no code change.

### Steps
1. Gather statistics on a table.
2. Load 2,000,000 rows without refreshing them.
3. Compare the query plan and timing.
4. Refresh statistics and re-measure.

### Verification
- [ ] `last_analyzed` and `num_rows` checked before and after
- [ ] Plan change captured
- [ ] Timing difference quantified
- [ ] Explanation given for why this looks like an unexplained regression

---

## Exercise 10: Report p95, Not the Average
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Measure the distribution the requirement actually specifies.

### Steps
1. Generate activity log entries with a realistic spread.
2. Compute average, p50, p95, p99, and max.
3. Show a case where the average passes and p95 fails.
4. Report the final result as p95.

### Verification
- [ ] All percentiles computed
- [ ] Divergence between average and p95 demonstrated
- [ ] Final result reported as p95 against the stated target