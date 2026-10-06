# Lab 08: APEX Performance — Real World Project

## Scenario
A customer's APEX application dashboard takes 12 seconds and frequently times out.
It contains 8 Interactive Reports, 3 charts, and 10 dynamic actions. The database
administrator has already added indexes on the obvious columns and seen no
improvement, so they concluded "APEX is slow". Someone enabled pagination on the
reports; it was tried twice with no effect. The team has been asked to fix it and
has one week. The customer also reports that the application "feels slow before
anything appears", which no server-side measurement has been able to explain.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (performance)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/rnprf/

## Architecture
```
Dashboard (5M-row orders table, 3,400 users, 3,500 views/week)

  Attribution (APEX Debug + activity log + APA)
    Region: Orders            3,214 ms   27%   ← non-sargable TRUNC()
    Rendering                  3,008 ms   25%   ← 10 unconsolidated DAs
    3 charts                   2,120 ms   18%   ← same data, recomputed each time
    Region: Customers          1,802 ms   15%   ← literal-built SQL, hard parses
    PL/SQL                       912 ms    8%   ← row-by-row cursor loop
    Session state                604 ms    5%   ← 40 KB lookup blob
    Regions 5-8                   20 ms   <1%

  AFTER
  ┌───────────────────────────────────────────────────────────┐
  │ Sargable range predicate + covering index       3,214→190│
  │ Static SQL with binds (1 statement, not 8)     1,802→180│
  │ Region cache 60 s, ~85% hit rate               2,120→340│
  │ FORALL instead of cursor loop                     912→120│
  │ 10 DAs consolidated to 3                        3,008→1,410│
  │ Session state lookup blob removed                 604→ 90│
  │ Theme minify + gzip (transfer, not server)      2,900→400│
  └───────────────────────────────────────────────────────────┘
  14,580 ms → 2,750 ms   (5.3x)
```

## Implementation sketch
```sql
-- BEFORE: function on the indexed column — full scan of 5M rows
WHERE TRUNC(o.order_date) = TO_DATE(:P1_ORDER_DATE,'YYYY-MM-DD')
ORDER BY o.net_amount DESC     -- top-N sort also requires the full set

-- AFTER: sargable range, and an index that satisfies the sort
WHERE o.order_date >= TO_DATE(:P1_ORDER_DATE,'YYYY-MM-DD')
  AND o.order_date <  TO_DATE(:P1_ORDER_DATE,'YYYY-MM-DD') + 1
ORDER BY o.net_amount DESC;
CREATE INDEX ix_orders_date ON orders (order_date, net_amount);
-- 5,000,000 rows examined → 208,000, and no sort step
```

```text
Pagination was tried twice because it cannot work:
  pagination limits RETURNED rows, not rows EXAMINED.
  With a non-sargable predicate, the database still scans the whole table.
```

## Requirements

- F1: APEX Debug attribution with component-level timings.
- F2: Activity log percentiles (p50, p95, p99) per page.
- F3: Application Performance Analyzer run across the whole application.
- F4: Sargable predicates on every region query, verified by plan.
- F5: Indexes added only where a plan confirms they are needed.
- F6: Bind variables replacing all literal-built SQL.
- F7: Library cache latch contention checked and reduced.
- F8: Region cache on slow-changing regions with documented triggers.
- F9: Page cache explicitly assessed and rejected where personalised.
- F10: Session state audited; unnecessary items removed.
- F11: PL/SQL row loops converted to `FORALL` or MERGE.
- F12: Dynamic Actions consolidated; complex conditions precomputed.
- F13: Theme CSS and JavaScript minification plus gzip enabled.
- F14: Statistics refreshed and plans re-verified.
- F15: System wait analysis confirming which remaining waits are not the
      application's to fix.
- NF1: Dashboard under 3 seconds p95.
- NF2: Filter change under 1 second.
- NF3: CSV export of 100,000 rows under 30 seconds.
- NF4: Library cache latch sleep percentage below 1%.
- NF5: Theme asset transfer under 500 ms.
- NF6: Security baseline — caching must not bypass row scoping.
- NF7: Documented rollback for every index and configuration change.

## Milestones
- Week 1 Day 1–2: Debug, activity log, APA; attribution and ranking.
- Week 1 Day 3: Sargable rewrite and index for the dominant region.
- Week 1 Day 4: Bind variables; latch contention re-checked.
- Week 1 Day 5: Region cache with trigger documentation.
- Week 2 Day 1–2: Session state audit; PL/SQL conversion.
- Week 2 Day 3: Dynamic Action consolidation; theme minification and gzip.
- Week 2 Day 4–5: Load test; p95 verification; wait analysis.

## Verification

- Before/after Debug breakdown and activity log percentiles on identical volume.
- EXPLAIN PLAN for every rewritten query, confirming index usage.
- `v$sql` statement count before and after bind replacement.
- `v$latch` library cache sleep percentage before and after.
- Response size and transfer time before and after theme changes.
- Fault injection: empty filter result; 100,000-row export.
- Security test: cached results still respect row scoping.
- `v$system_event` review confirming remaining waits are infrastructure.

## Rollback

Each index is independently removable; query rewrites are version-controlled and
revertible; cache settings are per-region configuration; theme minification is a
single checkbox. Document rollback steps for every change.