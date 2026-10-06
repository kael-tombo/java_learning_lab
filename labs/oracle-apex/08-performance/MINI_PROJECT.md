# Lab 08: APEX Performance — Mini Project

## Goal
Take a deliberately slow 12-second page to under 3 seconds p95 with every change
measured individually — in 90 minutes.

## Requirements

- R1: An APEX Debug breakdown attributing time to named components.
- R2: A sargable rewrite of the dominant region's predicate with plan evidence.
- R3: Literal SQL replaced with binds, with a statement-count comparison.
- R4: Region caching applied with a measured hit rate and a stated trigger.
- R5: Session state audited with the largest item removed.
- R6: A cursor loop converted to `FORALL`, both timed.
- R7: Theme minification and gzip enabled, with transfer time measured.
- R8: p95 and p99 reported from the activity log.

## Steps

1. Build a page with 8 regions over a 2,000,000-row table; measure the baseline.
2. Capture the Debug breakdown and rank components by time.
3. Rewrite the dominant region's predicate as a range; confirm the plan changed.
4. Find literal SQL in a process; replace it with a bind; compare `v$sql`.
5. Apply a region cache to a slow region; simulate requests and measure hit rate.
6. Dump session state; identify and remove the largest item.
7. Find a row-by-row loop; convert to `FORALL`; time both.
8. Enable theme minification and gzip; measure the response size.
9. Report p50, p95, and p99 from the activity log.
10. Check `v$system_event` and state whether any remaining wait is the application's.

## Acceptance criteria

- Every component in the breakdown is named with its time and percentage.
- The sargable rewrite is confirmed by EXPLAIN PLAN, not assumed.
- Bind replacement reduces distinct statements to one.
- Cache hit rate is measured, not assumed, and a trigger is documented.
- The `FORALL` version is measurably faster with correctness verified.
- Theme assets shrink materially after minification and gzip.
- The final result is reported as p95 against the stated target.

## Stretch

- Demonstrate that page cache on this personalised page would be a data leak.
- Show that pagination does not change rows examined for a non-selective filter.