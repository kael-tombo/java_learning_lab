# Flashcards: APEX Page Designer

1. Q: Responsive 2-column chart row setting? | A: Region Grid columns = 6 (50% width each).
2. Q: Chart series SQL contract? | A: `label, value` two-column query.
3. Q: Filter-all-regions pattern? | A: Bind vars `:P1_START_DATE/:P1_END_DATE` in each SQL + Change DA → Refresh.
4. Q: Cascading LOV without submit uses? | A: Dynamic Action Change → Execute PL/SQL → JS `apex.item().setValue()`.
5. Q: PL/SQL returns child rows as? | A: `JSON_ARRAYAGG(JSON_OBJECT(...))`.
6. Q: Complex form rule validation type? | A: PL/SQL Function Returning Boolean, On Submit Before Processing.
7. Q: Overlap test in one predicate? | A: `start_time < :new_end AND end_time > :new_start` (same emp/date, exclude self).
8. Q: Hours from DATE subtraction? | A: Multiply by 24: `(:end - :start)*24`.
9. Q: Sluggish Page Designer fix (layout)? | A: Page Groups, disable preview, Source=Never for static regions.
10. Q: Clear cached page 10? | A: `APEX_UTIL.CLEAR_PAGE_CACHE(p_page_id=>10)`.
11. Q: Dictionary view for page regions? | A: `APEX_APPLICATION_PAGE_REGIONS`.
12. Q: True/False DA chain use? | A: Branch logic on PL/SQL success vs failure.
13. Q: Why clear grandchild on parent change? | A: Stale city values no longer belong to new state.
14. Q: AJAX inline validation purpose? | A: Instant feedback before submit; server rule remains source of truth.
15. Q: Bar trend label expression? | A: `TO_CHAR(order_date,'YYYY-MM')`.
