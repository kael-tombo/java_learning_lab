# Lab 05: APEX Performance — Real World Project

## Scenario
A large enterprise APEX application with 10,000+ concurrent users is degrading.
The Executive Dashboard — the most critical page — takes 30+ seconds and
frequently times out. It contains 10 interactive reports over tables with 5M+ rows,
6 chart regions with complex aggregations, 3 classic year-over-year reports,
cascading filters, and CSV export on every report. Targets: under 3 seconds p95,
under 1 second for filter changes, 100K-row export under 30 seconds, and minimal
database impact during the 9–10 AM and 2–3 PM peaks. The client wants the query
execution time reduced by 80% without a hardware refresh.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (performance)
- (link removed)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)

## Architecture
```
Executive Dashboard (10,000+ users, 50,000 views/day)

  Attribution (APEX Debug):
    SQL 22,340 ms (74%) · Rendering 4,020 ms · Session state 1,760 ms

  AFTER
  ┌─────────────────────────────────────────────────────────────┐
  │ Before Header: collection 'DASHBOARD_ORDERS'              │
  │   ONE set-based query over the shared filters               │
  │   → 1 query instead of 16                                  │
  └─────────────────────────────────────────────────────────────┘
        │              read by (no table access)
        ├─► Order Summary IR      ├─► Revenue by Region chart
        ├─► Top Products IR       ├─► Category chart
        ├─► Year-over-Year IR     ├─► Channel chart
        └─► (6 more regions)

  Cache: 2 slow regions, 30 s TTL, ~98% hit rate
         invalidation trigger: explicit clear_cache on reference change

  Session state: oversized blob → minimal identifiers

  Export: bounded set-based, refuses >100,000 rows
  Import: 3 set-based statements + reject log

  Measured: 30,000 ms p95 → 2,950 ms p95 (10.2x)
```

## Implementation sketch
```sql
-- One query populates the collection; every region reads it.
APEX_COLLECTION.TRUNCATE('DASHBOARD_ORDERS');
FOR r IN (
  SELECT so.order_id, so.order_date, so.region_id, sr.region_name,
         so.category_id, sc.category_name, so.product_id, sp.product_name,
         so.quantity, so.unit_price,
         ROUND(so.quantity * so.unit_price, 2) net_amount
    FROM sales_order so
    JOIN sales_region   sr ON sr.region_id   = so.region_id
    JOIN sales_category sc ON sc.category_id = so.category_id
    JOIN sales_product  sp ON sp.product_id  = so.product_id
   WHERE so.order_date >= :P1_FROM_DATE
     AND so.order_date <  :P1_TO_DATE + 1
) LOOP
  APEX_COLLECTION.ADD_ELEMENT('DASHBOARD_ORDERS', r.order_id, r);
END LOOP;
```

```sql
-- Row-by-row vs set-based at 100,000 rows: 30 minutes vs 1,500 seconds
MERGE INTO sales_product t
USING price_update_staging s
   ON (t.sku = s.sku)
 WHEN MATCHED THEN UPDATE SET t.unit_price = s.new_price;
COMMIT;
```

## Requirements
- F1: APEX Debug attribution with component-level timings.
- F2: Shared collection feeding every region on the dashboard.
- F3: Region caching on slow-changing regions with measured hit rate.
- F4: Explicit invalidation triggers with a named owner per cache.
- F5: Session state reduced to what is genuinely needed across pages.
- F6: All row-by-row processing rewritten as set-based operations.
- F7: Bounded export refusing over 100,000 rows with a clear message.
- F8: Bulk CSV import with validation and a reject log.
- F9: Cascading filters preventing invalid combinations.
- F10: Index set matched to the actual queries, plus statistics refresh.
- F11: Batched cleanup to avoid undo and lock pressure.
- F12: Progress reporting for long-running operations.
- NF1: Dashboard under 3 seconds p95.
- NF2: Filter change under 1 second.
- NF3: 100,000-row export under 30 seconds.
- NF4: Query execution time reduced by at least 80%.
- NF5: Peak-hour (9–10 AM, 2–3 PM) database impact reduced.
- NF6: Every optimisation measured individually and attributable.
- NF7: Security baseline — collection and cache must not bypass row scoping.
- NF8: Documented rollback for every index and configuration change.

## Milestones
- Week 1: Day 1–2 attribution; day 3 collection implementation and measurement.
- Week 1: Day 4–5 caching with hit-rate measurement and invalidation triggers.
- Week 2: Set-based rewrites, bounded export, bulk import.
- Week 2: Index and statistics work; cascading filters.
- Week 3: Load test at 10,000 users; p95 verification; monitoring.

## Verification
- Before/after Debug breakdown on identical data volume.
- Cache hit rate measured over a simulated 50-request window.
- 100,000-row export and import timed end to end.
- Load test at peak concurrency; database CPU compared before and after.
- Fault injection: filter combination returning nothing; export over the limit.
- Security test: cached and collection-backed results still respect row scoping.
- Statistics refresh verified; `last_analyzed` confirmed current.

## Rollback
Each index is independently removable; collection population is per-page and
can be reverted to direct queries; cache settings are per-region configuration;
set-based rewrites are code changes version-controlled separately. Document
rollback steps for every change.