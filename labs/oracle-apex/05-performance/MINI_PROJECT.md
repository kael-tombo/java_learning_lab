# Lab 05: APEX Performance — Mini Project

## Goal
Take a 30-second dashboard to under 3 seconds p95 using attribution, collections,
caching, and bulk operations — in 90 minutes.

## Requirements
- R1: An APEX Debug breakdown attributing time to named components.
- R2: One collection populated once and read by every region.
- R3: Region caching on at least two regions with a stated invalidation trigger.
- R4: Measured cache hit rate justifying the caching decision.
- R5: One row-by-row block rewritten as a single set-based statement.
- R6: A bounded export refusing requests over a stated row limit.
- R7: A bulk CSV import with a reject log, using set-based statements only.
- R8: p95 and p99 measurement from the activity log.

## Steps
1. Build a dashboard with 10 regions over a 500,000-row table; measure the baseline.
2. Capture the Debug breakdown; identify the top two contributors.
3. Populate a collection and rewire every region to read from it.
4. Re-measure; record the improvement from the collection alone.
5. Cache the two slowest regions for 30 seconds.
6. Simulate 50 requests and measure the actual hit rate.
7. Write the invalidation trigger and test it.
8. Rewrite a row-by-row update loop as a MERGE; time both at 50,000 rows.
9. Build the bounded export and confirm it refuses over the limit.
10. Build the bulk CSV import with a reject log.
11. Report p95 and p99 from the activity log.

## Acceptance criteria
- Every improvement is measured independently, with before and after recorded.
- All regions read from one collection; no region queries the base table.
- The measured hit rate justifies the cache; a low hit rate is reported as such.
- Every cached region has a documented invalidation trigger.
- The 50,000-row update is set-based and demonstrably faster.
- The export refuses over its limit rather than truncating.
- The import produces a reject log with reasons.
- Final p95 is under 3 seconds.

## Stretch
- Show that caching does not help when request rate is low.
- Convert the export to GZIP and compare transfer time.