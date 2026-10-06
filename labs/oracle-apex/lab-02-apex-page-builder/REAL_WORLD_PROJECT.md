# Lab 02: APEX Page Builder — Real World Project

## Scenario
A client wants a sales dashboard delivered in APEX. It needs one Interactive
Report at the top, two pie charts in the middle row, and a bar chart at the
bottom, all driven by a date range the user selects, plus a drill-through to a
detail page when a bar is clicked. The team already has the queries written but
the page takes 11 seconds because every region runs its own unfiltered query.
The developer building it is new to Page Designer and has been adding regions
without understanding when their SQL actually executes.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (Page Designer)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)

## Architecture
```
Sales Dashboard page (12-column grid)

Row 1:  [ Interactive Report — sales by region ....................... ]
Row 2:  [ Pie: by category ] [ Pie: by channel ] [ Static Content: filters ]
Row 3:  [ Bar: revenue by month .................................... ]

Every region query binds the SAME items:
  :P1_START_DATE, :P1_END_DATE, :P1_REGION, :P1_CATEGORY

Dynamic Action: Change on either date item → Refresh (all 4 regions), AJAX
Bar click → Branch to detail page passing region + month
```

## Implementation sketch
```sql
-- Before: 4 independent unfiltered queries = 4 full scans per page render
-- After: every query is bounded by the same two bind variables
SELECT TO_CHAR(order_date,'YYYY-MM') month, SUM(net_amount) revenue
  FROM sales_order
 WHERE order_date >= :P1_START_DATE            -- sargable range
   AND order_date <  :P1_END_DATE + 1
   AND (:P1_REGION IS NULL   OR region_id   = :P1_REGION)
   AND (:P1_CATEGORY IS NULL OR category_id = :P1_CATEGORY)
 GROUP BY TO_CHAR(order_date,'YYYY-MM')
 ORDER BY 1;
```

```sql
-- Execution model: rendering runs top-to-bottom on page load.
-- A Dynamic Action on "Change" replaces the page submit with a targeted AJAX
-- refresh of only the regions that depend on the changed item.
```

## Requirements
- F1: 12-column grid layout with three logical rows.
- F2: Interactive Report region with sorting and filtering.
- F3: Three chart regions with correct types for their data.
- F4: Shared date-range and category filters bound into every query.
- F5: Dynamic Action refreshing all dependent regions without page submit.
- F6: Bar-click drill-through to a detail page with context passed.
- F7: Page process with a correct condition.
- F8: Conditional branch for the drill-through.
- F9: Responsive layout for desktop, tablet, and mobile.
- F10: Region-level display conditions where a region may legitimately be empty.
- NF1: Page loads under 3 seconds p95 with default filters.
- NF2: Filter change refreshes in under 1 second.
- NF3: All regions consistent — every one honours the same filter set.
- NF4: Security baseline — no region exposes data the user may not see.
- NF5: Empty states handled without a blank or broken region.
- NF6: Documented rollback — export provides a versioned restore point.

## Milestones
- Week 1: Layout grid, regions, and shared filter items.
- Week 2: Queries bound and verified for filter consistency.
- Week 3: Dynamic Actions and drill-through navigation.
- Week 4: Responsive tuning and empty-state handling.
- Week 4: Performance verification and client walkthrough.

## Verification
- Change each filter and confirm every region updates together.
- Confirm no full page submission on filter change (APEX Debug).
- Fault injection: a filter combination returning no rows.
- Responsive test at 375 px, 768 px, and 1440 px widths.
- Performance comparison before and after binding the filters.

## Rollback
Every change is inside an exportable application; Dynamic Actions and processes
are removable individually. Document rollback steps for every change.