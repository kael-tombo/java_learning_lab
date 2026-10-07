# Lab 08: APEX Performance — Real World Project

## Scenario
A customer's APEX dashboard takes 12+ seconds to load and frequently times out.
It contains 8 Interactive Reports pulling from tables with 5M+ rows, 3 charts
with complex aggregations, and 10 dynamic actions. The customer's database
administrator has already added indexes on the obvious columns and seen no
improvement, so they concluded "APEX is slow". The team has been asked to fix it
and has one week. Someone suggested enabling pagination on the reports, which a
developer has already done twice with no effect.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (performance)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- (link removed)

## Architecture
```
Before: 12.4 s
   └─ APEX Debug attribution:
        Page Processing   8.2 s
          SQL queries     7.1 s
            IR #1 orders      3.2 s   ← unbound predicate, full scan
            IR #2 customers  1.8 s   ← aggregation over 5M rows
            IR #3-8          0.9 s
            Charts           2.1 s   ← two charts hit the same data
        Session state     0.6 s   ← oversized blob
        Rendering         3.6 s   ← 10 dynamic actions, no cache

After: 2.8 s
   └─ Shared query + binds + covering index + cache + lazy regions
        SQL queries     1.9 s   (0.4 s after collection sharing)
        Rendering       0.6 s   (cached, 2 regions lazy)
        Session state   0.1 s
```

## Implementation sketch
```sql
-- BEFORE: literal from a page item built at runtime → hard parse, full scan
SELECT o.order_id, o.order_date, o.total
  FROM orders o
 WHERE o.status = '&P1_STATUS_'          -- literal: not sargable, no bind cache

-- AFTER: bind variable + covering index
SELECT o.order_id, o.order_date, o.total
  FROM orders o
 WHERE o.status = :P1_STATUS
   AND o.order_date >= :P1_FROM;         -- range predicate

CREATE INDEX ix_orders_status_date ON orders (status, order_date, total);
```

```text
Pagination does NOT make the query cheap.
APEX fetches the first page — the database still scans until it has 25 rows
that match. On a low-selectivity filter that is still millions of rows.
```

## Requirements
- F1: APEX Debug timing breakdown captured before any change.
- F2: Component-level attribution with the largest contributor named.
- F3: Fix the dominant contributor first and measure it alone.
- F4: Replace literal predicates with bind variables.
- F5: Covering indexes matched to the actual queries.
- F6: Shared queries across regions via collections.
- F7: Caching for stable regions with documented invalidation.
- F8: Session state audit and reduction.
- F9: Lazy-loaded or conditional regions where not all are always needed.
- F10: Load test at 1.5× concurrent user count.
- NF1: Dashboard under 3 seconds p95.
- NF2: Filter change under 1 second.
- NF3: CSV export of 100,000 rows under 30 seconds.
- NF4: No database load regression during peak hours.
- NF5: Security baseline — pagination and caching must not bypass row scoping.
- NF6: Documented rollback for every index and configuration change.

## Milestones
- Week 1: Day 1–2 Debug capture and attribution; day 3 dominant fix.
- Week 1: Day 4–5 binds, indexes, and collection sharing.
- Week 2: Caching, session state, lazy regions.
- Week 2: Load test and final measurement.

## Verification
- Before/after Debug breakdown on identical data volume.
- EXPLAIN PLAN per fixed query, confirming index usage.
- Load test at 1.5× users; database CPU compared before and after.
- Fault injection: filter combination returning few rows on a large table.
- Security test: cached and paged results still respect row scoping.

## Rollback
Each index is independently removable; region caching is per-region
configuration; the original queries are retained in version control until
sign-off. Document rollback steps for every change.