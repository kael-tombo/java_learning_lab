# Quiz: APEX Page Designer — Layout, Dynamic Actions, Validation

Grounded in `02-page-designer/PROBLEM_WALKTHROUGH.md` (4 interview scenarios).

## Questions

1. How do you lay out 1 IR (top) + 2 pies (middle) + 1 bar (bottom) responsively?
2. What SQL shape feeds an APEX pie/bar chart series?
3. How do date-range page items filter all regions without submit?
4. How do you implement Country → State → City cascading selects with no page submit?
5. What does the PL/SQL in the cascading-LOV Dynamic Action return, and how is it consumed?
6. Which validation type + point enforces "no overlapping timesheet entries, max 16h/day"?
7. Sketch the overlap predicate for timesheet validation.
8. How is the 16-hour daily cap computed in SQL?
9. Page Designer is sluggish on a 30-region page — name three mitigations.
10. How do you find the heaviest regions of page 10 in app 100 via SQL?

## Answers

1. Blank page; Static Content region with `P1_START_DATE/P1_END_DATE` date pickers on top; IR region below; two chart regions with Grid column span 6 (50% each); bar chart full width; one Change Dynamic Action refreshing all charts.
2. Two columns: `label` + `value`, e.g. `SELECT category AS label, SUM(amount) AS value ... GROUP BY category`.
3. Reference `:P1_START_DATE/:P1_END_DATE` bind variables in every region SQL + Dynamic Action (Change → Refresh).
4. Three Select Lists; Dynamic Action on parent Change → Execute PL/SQL returning child rows → Success JS sets child value; repeat for next level; clear grandchild.
5. `JSON_ARRAYAGG(JSON_OBJECT(...))` into a page item; Success handler parses JSON and calls `apex.item('P2_STATE').setValue(...)`.
6. **PL/SQL Function Body (Returning Boolean)**, validation point **On Submit – Before Processing**, plus AJAX inline check for UX.
7. `entry_id != NVL(:P3_ENTRY_ID,-1) AND (start_time < :P3_END_TIME AND end_time > :P3_START_TIME)` for same employee+date.
8. `NVL(SUM(hours),0) + (:P3_END_TIME - :P3_START_TIME)*24 > 16` → reject.
9. Use Page Groups/folders; disable live preview; set layout-only regions Source to Never; minimise custom HTML; clear page cache (`APEX_UTIL.CLEAR_PAGE_CACHE`); upgrade APEX for tree virtualization.
10. `SELECT region_id, region_name, source_type, source FROM APEX_APPLICATION_PAGE_REGIONS WHERE application_id=100 AND page_id=10 ORDER BY region_id;`
