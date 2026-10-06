# Lab 05: APEX Performance — VISION

## Where this lab takes you
From a 30-second executive dashboard to under 3 seconds p95 — by attributing
first, then sharing queries, caching what changes slowly, and going set-based.

## The Arc
1. **Attribute** — one Debug run locates the 52% you can actually fix.
2. **Share** — one collection feeding 16 regions.
3. **Cache** — slow-changing regions, with a stated invalidation trigger.
4. **Measure hit rate** — caching only pays at sufficient request volume.
5. **Go set-based** — the 120× difference at volume.
6. **Bound the export** — refuse rather than truncate silently.
7. **Cascade filters** — prevent invalid combinations before they scan.
8. **Report p95** — the mean hides the tail users actually experience.

## Milestones (checkable)
- [ ] M1: Capture the Debug breakdown and name the top two contributors.
- [ ] M2: Populate one collection and rewire all 16 regions to it.
- [ ] M3: Cache two regions and measure the hit rate before trusting it.
- [ ] M4: Write an invalidation trigger for every cache you add.
- [ ] M5: Rewrite one row-by-row block as a single set-based statement.
- [ ] M6: Build a bounded export that refuses over 100K rows.
- [ ] M7: Add cascading filters and confirm invalid combinations are unreachable.
- [ ] M8: Report p95 and p99 from the activity log, not the average.

## Anti-Goals
- Optimising rendering when SQL is 74% of the problem.
- Caching without a stated invalidation trigger.
- Caching a low-traffic application and gaining nothing.
- Caching a page containing per-user data.
- Row-by-row processing at volume.
- Unbounded or silently truncating export.
- Bundling changes so none is attributable.
- Reporting the average when the target is p95.

## The one-sentence thesis
Thirty seconds is a symptom — attribute it, share the redundant queries, cache
what changes slowly with a named trigger, and go set-based where volume makes the
difference 120×.