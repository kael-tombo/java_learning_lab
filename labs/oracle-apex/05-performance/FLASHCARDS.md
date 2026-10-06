# Lab 05: APEX Performance — Flashcards

## Attribution

---
**Q**: Why capture a Debug breakdown first?
**A**: A 30-second page has one largest contributor. Optimising the wrong component wastes the whole effort.

---
**Q**: Split in this lab?
**A**: SQL 22,340 ms (74%) · Rendering 4,020 ms (13%) · Session state 1,760 ms (6%) · PL/SQL 1,160 ms.

---
**Q**: Top two contributors?
**A**: Order Summary 9,240 ms + Revenue by Region 6,410 ms = 52% of total.

---
**Q**: Optimisation order?
**A**: Descending attribution. Never by what seems unlikely.

---
**Q**: Why not optimise rendering first?
**A**: It addresses 13% of the problem. The obvious fix is rarely the big one.

---

## Collections

---
**Q**: What problem does a collection solve?
**A**: 16 regions issuing redundant queries over the same rows.

---
**Q**: Query reduction?
**A**: 16 → 1. SQL time 22,340 ms → ~2,400 ms.

---
**Q**: When is a collection wrong?
**A**: When each region genuinely needs different data. It is per-request.

---
**Q**: What does it not remove?
**A**: The aggregation work itself — 6 charts still each aggregate the collection.

---
**Q**: `c001..cNN`?
**A**: Positional by the population SELECT list. Adding a column shifts every later index and corrupts every region. Treat it as a contract.

---

## Caching

---
**Q**: Cache what?
**A**: Slow-changing data: reference lists, historical aggregates. Not live regions.

---
**Q**: Invalidation trigger?
**A**: The stated answer to "when does this become wrong". A TTL, or an explicit `APEX_REGION_CACHE.clear_cache`.

---
**Q**: Hit rate at 6,250 requests/hour, 30 s TTL?
**A**: 51/52 = **98.1%**. A 6,000 ms query becomes effectively 114 ms.

---
**Q**: Hit rate at 12 requests/hour?
**A**: ~0%. Caching is pure overhead at low traffic.

---
**Q**: Region cache vs page cache?
**A**: Region. Never cache a page containing per-user data.

---
**Q**: Function result cache invalidation?
**A**: `DBMS_RESULT_CACHE.invalidate` after a bulk load, rather than waiting for TTL.

---
**Q**: Never put large values in session state cache?
**A**: It is serialised per request, so a big value becomes a per-request cost.

---

## Set-Based Operations

---
**Q**: Row-by-row cost per row?
**A**: ~1.8 ms (1.5 ms round trip + 0.3 ms PL/SQL).

---
**Q**: Set-based per row?
**A**: ~0.015 ms, plus ~5 ms fixed per statement.

---
**Q**: Ratio at 100,000 rows?
**A**: ~30 minutes vs ~1,500 seconds = **~120×**. The ratio converges to 120×, it does not improve further.

---
**Q**: Bulk import pattern?
**A**: Validate in bulk (set UPDATE), apply with MERGE, report rejects with a GROUP BY. Three statements, any volume.

---
**Q**: Batched DELETE?
**A**: 50,000 rows per statement with a short sleep. Peak undo 40 GB → 200 MB (200×).

---

## Export

---
**Q**: Default IR export at 100,000 rows?
**A**: ~90–140 s. Fails the 30 s target.

---
**Q**: Set-based custom export?
**A**: ~8–15 s. Meets it.

---
**Q**: Bound the export how?
**A**: `ROWNUM <= 100000` plus an explicit error above the limit.

---
**Q**: Why refuse rather than truncate?
**A**: A truncated export produces a spreadsheet that reconciles to nothing and takes an hour to diagnose.

---

## Filters and Statistics

---
**Q**: Cascading filters — performance benefit?
**A**: 480 reachable combinations, only ~96 valid. The other 384 scan the full filtered range to prove emptiness: ~15 min/day wasted CPU.

---
**Q**: Statistics staleness effect?
**A**: A 40% cardinality misestimate can flip a join method — nested loops instead of hash join, ~75× slower, with no code change.

---
**Q**: First check for an unexplained slowdown?
**A**: `last_analyzed` and `num_rows` in `user_tables`.

---

## Measurement

---
**Q**: Why measure each change alone?
**A**: Bundled changes cannot be defended in review, and a change causing staleness cannot be isolated.

---
**Q**: Average vs p95 here?
**A**: 4,200 ms average against 30,000 ms p95. The average says acceptable; p95 says unusable.

---
**Q**: Why always look at p99?
**A**: p99 is where genuinely broken cases live. ~30 users/day hit the timeout range.

---
**Q**: Source for p95 measurement?
**A**: `APEX_USER_ACTIVITY_LOG` with `PERCENTILE_CONT`, not a manual run.

---

## Progress and Health

---
**Q**: `APEX_APPLICATION.PROCESS`?
**A**: Progress reporting so a long run does not look hung. Chunk the work so progress advances.

---
**Q**: Batch work scheduling?
**A**: Move exports and refreshes out of the 9–10 AM peak. 600 s removed = 2% of peak load — second-order versus the 31% from per-request optimisation.

---

## Quick Reference

| Task | API |
|------|-----|
| Collection truncate | `APEX_COLLECTION.TRUNCATE` |
| Collection add | `APEX_COLLECTION.ADD_ELEMENT` |
| Collection read | `SELECT c.c001.. FROM APEX_COLLECTION` |
| Region cache clear | `APEX_REGION_CACHE.clear_cache` |
| Result cache invalidate | `DBMS_RESULT_CACHE.invalidate` |
| Progress | `APEX_APPLICATION.PROCESS` |
| Compress payload | `APEX_APPLICATION.GZIP` |
| Activity log | `APEX_USER_ACTIVITY_LOG` |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Before p95 | 30,000 ms |
| After p95 | 2,950 ms (10.2×) |
| SQL share of original time | 74% |
| Query count before/after | 16 → 1 |
| Cache hit rate at peak | 98.1% |
| Row-by-row vs set-based, 100K | ~120× |
| 100K export | 120 s → 12 s |
| 100K import | 50 hours → 25 min |
| Peak-hour DB CPU reduction | 31% |
| Undo, batched delete | 40 GB → 200 MB |

---

## Anti-Patterns

1. Optimising rendering when SQL is 74%.
2. Caching with no stated trigger.
3. Caching a personalised page.
4. Caching a low-traffic application.
5. Row-by-row processing at volume.
6. Unbounded or silently truncating export.
7. Cascading filters missing.
8. Stale statistics.
9. Bundled changes.
10. Reporting the average against a p95 target.

---

## Study Tips
1. Reproduce the attribution table from memory.
2. Compute a cache hit rate for any request rate and TTL.
3. Explain why the set-based ratio converges rather than grows.
4. State the one number you would report for a p95 requirement.