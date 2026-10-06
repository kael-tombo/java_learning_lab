# Lab 02: APEX Page Designer — Real World Project

## Scenario
A client wants a sales dashboard delivered in APEX: an Interactive Report at the
top, two pie charts in the middle row, a bar chart at the bottom, all driven by a
date range the user selects, plus drill-through to a detail page when a bar is
clicked. The queries are already written, but the page takes 11 seconds because
every region runs its own unfiltered query over a 5M-row table. The developer
building it is new to Page Designer and has been adding regions without knowing
when their SQL actually executes — including a page process that appears to do
nothing.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (Page Designer)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)

## Architecture
```
Sales Dashboard (12-column grid)

Row 1: [ Dashboard Filters — Static Content ......................... ]
Row 2: [ Sales IR .................................................. ]
Row 3: [ Pie: Category (6) ] [ Pie: Channel (6) ] [ No-data region  ]
Row 4: [ Bar: Revenue by Month .................................. ]

Every region query binds: :P1_FROM_DATE, :P1_TO_DATE, :P1_REGION, :P1_CATEGORY
Computation sets the 30-day default BEFORE any region queries
Dynamic Action refreshes dependent regions via AJAX with a non-null condition
Row-level scoping predicate present in all four region queries
Drill-through: bar click → session state (region_id, month_key) → branch
```

## Implementation sketch
```sql
-- Before: 4 regions × full scan of 5M rows = 11 seconds
-- After: every region bounded by the same sargable range predicate
SELECT so.region_id, TO_CHAR(so.order_date,'YYYY-MM') month_key,
       TO_CHAR(so.order_date,'Mon YYYY') label, ROUND(SUM(so.net_amount),2) value
  FROM sales_order so
 WHERE so.order_date >= :P1_FROM_DATE              -- sargable range
   AND so.order_date <  :P1_TO_DATE + 1
   AND so.region_id = current_user_region()        -- row security too
   AND (:P1_CATEGORY IS NULL OR so.category_id = :P1_CATEGORY)
 GROUP BY so.region_id, TO_CHAR(so.order_date,'YYYY-MM'), TO_CHAR(so.order_date,'Mon YYYY');
```

```text
Phases:  Computation (Before Header) → regions query → render
        Page processes only on SUBMIT — which is why the developer's process
        appeared to do nothing when they pressed Refresh.
```

## Requirements
- F1: 12-column grid layout with four rows and region spans.
- F2: Interactive Report with sorting, filtering, and search.
- F3: Three chart regions with types suited to their data.
- F4: Shared date, region, and category filters bound into every query.
- F5: Computation setting a 30-day default before rendering.
- F6: Dynamic Action refreshing dependent regions via AJAX, with condition.
- F7: Bar-click drill-through to a detail page passing IDs and keys.
- F8: Cascading category LOV driven by the region item.
- F9: Inverted-range validation with an actionable message.
- F10: Empty-state display conditions with a "no data" region.
- F11: Row-level scoping predicate in all four region queries.
- NF1: Page load under 3 seconds p95.
- NF2: Filter change under 1 second with no full page re-render.
- NF3: All regions consistent — every one honours the same filter set.
- NF4: Security baseline — no region exposes data outside the user's scope.
- NF5: Empty periods handled explicitly rather than rendering empty charts.
- NF6: Documented rollback — export restores any prior page configuration.

## Milestones
- Week 1: Layout grid, regions, and shared filter items.
- Week 1: Queries bound and verified for filter consistency.
- Week 2: Computation defaults, Dynamic Actions, and validations.
- Week 2: Drill-through, cascading LOVs, and empty states.
- Week 3: Responsive tuning, row-security audit, performance verification.

## Verification
- Change each filter and confirm every region updates together.
- APEX Debug: confirm no full page submission on filter change.
- Timing comparison before and after on identical data volume.
- Fault injection: inverted range, empty period, single-day period.
- Drill-through test with a renamed region label; confirm it still works.
- Responsive test at 375, 768, and 1440 px.
- Row-security test with a user scoped to one region.

## Rollback
Every change is inside an exportable application; Dynamic Actions, computations,
and validations are individually removable. Document rollback steps for every
change.