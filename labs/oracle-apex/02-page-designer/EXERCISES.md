# Exercises: APEX Page Designer

## 1. Dashboard Layout
On a blank page, add `P1_START_DATE/P1_END_DATE` date pickers in a Static Content region, one IR (`WHERE order_date BETWEEN :P1_START_DATE AND :P1_END_DATE`), two pie charts and one bar chart (pie regions Grid span 6).
*Check:* Changing a date refreshes all three charts via one Dynamic Action.

## 2. Chart Series Queries
Write the pie (`SUM(amount) BY category`) and bar (`COUNT(*) BY YYYY-MM`) series queries with bind variables. Run in SQL Workshop with literal dates first, then bind.
*See `WORKED_EXAMPLE.sql` §1.*

## 3. Cascading LOVs
Build `P2_COUNTRY/P2_STATE/P2_CITY` selects. Implement the Change DA on country executing the `JSON_ARRAYAGG` PL/SQL from the walkthrough; add JS Success handler setting `P2_STATE` and clearing `P2_CITY`. Repeat for state→city.

## 4. Timesheet Validation
Implement the overlap + 16h validation function from the walkthrough on a `TIMESHEET_ENTRIES` form. Test: (a) overlapping row rejected, (b) 3×6h rows on one day rejected, (c) edit of same row allowed.
*Starter:* `WORKED_EXAMPLE.sql` §2.

## 5. Performance Audit (challenge)
On a heavy page, group regions into Page Groups, set static regions to Source Never, disable preview, then run the `APEX_APPLICATION_PAGE_REGIONS` inventory query and note the heaviest sources. Clear cache and re-time Designer load.
