# Problem Walkthrough: Page Designer

## Problem 1: Region and Item Layout — Oracle
### APEX Interview Scenario
"A client at Oracle wants a dashboard page with three charts, a search bar, and a dynamic action that refreshes them. How do you lay this out in Page Designer?"

### The Problem
Design a responsive dashboard page in APEX: one Interactive Report (top), two pie charts (middle row), one bar chart (bottom). All charts must filter by a date range page item.

### Solution Walkthrough
1. **Create Page** — Page type: "Blank Page" with "Page Designer" layout
2. **Add Date Range Items** — Two date pickers (P1_START_DATE, P1_END_DATE) in a Static Content region
3. **Add Interactive Report Region** — SQL with bind variables:
   ```sql
   SELECT * FROM orders WHERE order_date BETWEEN :P1_START_DATE AND :P1_END_DATE
   ```
4. **Add Chart Regions** — Pie: `SUM(amount) BY category`; Bar: `COUNT(*) BY month`
5. **Set Chart Series Source** — Use SQL with bind variables referencing P1_START_DATE and P1_END_DATE
6. **Create Dynamic Action** — Event: "Change" on date pickers
   - True Action: "Refresh" targeting all three chart regions
7. **Responsive Layout** — Set chart region "Grid" columns to 6 (50% width) for pie charts

### Code
```sql
-- Pie chart series query
SELECT category AS label, SUM(amount) AS value
FROM orders
WHERE order_date BETWEEN :P1_START_DATE AND :P1_END_DATE
GROUP BY category
ORDER BY value DESC;

-- Bar chart series query
SELECT TO_CHAR(order_date, 'YYYY-MM') AS label, COUNT(*) AS value
FROM orders
WHERE order_date BETWEEN :P1_START_DATE AND :P1_END_DATE
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY label;
```

### Company Evaluation
- **Oracle**: Mastery of Page Designer layout, component properties panel
- **Deloitte**: Rapid prototyping, clean client-facing dashboard
- **Accenture**: Reusable region templates, consistent styling across apps

---

## Problem 2: Dynamic Actions & JavaScript — Deloitte
### APEX Interview Scenario
"Deloitte's client needs a form where selecting a country auto-fills state/province dropdown. Implement without page submit."

### Problem
Create a cascading dropdown: Country → State → City. No page submission on change.

### Solution Walkthrough
1. **Create Page Items** — P2_COUNTRY (Select List), P2_STATE (Select List), P2_CITY (Select List)
2. **Set Source for P2_COUNTRY** — Static values or lookup table
3. **Dynamic Action on P2_COUNTRY** — Event: "Change"
   - True Action: "Execute PL/SQL Code"
   - Code: Return JSON list of states for selected country
   - Items to Return: `P2_STATE` as JSON array
4. **JavaScript** — In the Dynamic Action Success handler:
   ```javascript
   apex.item('P2_STATE').setValue(JSON.parse(data).map(s => ({return: s.state_id, display: s.state_name})));
   apex.item('P2_CITY').setValue([]);
   ```
5. **Repeat** — Similar DA on P2_STATE for P2_CITY

### Code
```sql
-- PL/SQL in DA (return JSON)
DECLARE
    l_json CLOB;
BEGIN
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'state_id'   KEY state_id,
            'state_name' KEY state_name
        )
    ) INTO l_json
    FROM states
    WHERE country_id = :P2_COUNTRY;

    :P2_STATE := l_json;
END;
/
```

### Company Evaluation
- **Deloitte**: Client-facing interactivity without page reloads, UX best practices
- **Accenture**: JavaScript modularization, DA framework knowledge
- **Oracle**: Deep DA event mapping, true/false action chains

---

## Problem 3: Validation & Processing — Accenture
### APEX Interview Scenario
"Accenture is building an employee timesheet. Add complex validation: no overlapping entries, max 16 hours per day."

### Problem
Validate timesheet entries on form submission. Multiple overlapping logic and daily hour caps.

### Solution Walkthrough
1. **Validation Type** — "PL/SQL Function Body (Returning Boolean)"
2. **Validation Point** — "On Submit" before processing
3. **PL/SQL Validation Code**:
   - Query existing entries for the same employee + date
   - Check new time range against existing entries (overlap logic)
   - Sum total hours for that date (existing + new)
4. **Error Message** — Return descriptive error (e.g., "Overlap with entry #123")
5. **Processing** — On successful validation, insert/update `TIMESHEET_ENTRIES`
6. **Add Dynamic Validation** — Also validate using AJAX on item change for inline feedback

### Code
```sql
DECLARE
    l_overlap_count NUMBER;
    l_total_hours   NUMBER;
BEGIN
    -- Check overlaps
    SELECT COUNT(*)
    INTO l_overlap_count
    FROM timesheet_entries
    WHERE employee_id = :P3_EMPLOYEE_ID
      AND entry_date  = :P3_ENTRY_DATE
      AND entry_id   != NVL(:P3_ENTRY_ID, -1)
      AND (start_time < :P3_END_TIME AND end_time > :P3_START_TIME);

    IF l_overlap_count > 0 THEN
        RETURN FALSE;
    END IF;

    -- Check 16-hour limit
    SELECT NVL(SUM( hours ), 0)
    INTO l_total_hours
    FROM timesheet_entries
    WHERE employee_id = :P3_EMPLOYEE_ID
      AND entry_date  = :P3_ENTRY_DATE
      AND entry_id   != NVL(:P3_ENTRY_ID, -1);

    IF l_total_hours + (:P3_END_TIME - :P3_START_TIME) * 24 > 16 THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
/
```

### Company Evaluation
- **Accenture**: Robust validation for enterprise workloads, error message clarity
- **Deloitte**: Real-time validation UX, client demos of validation rules
- **Oracle**: Validation execution order, computation vs. validation distinction

---

## Problem 4: Page Designer Performance Tuning — Oracle
### APEX Interview Scenario
"At Oracle, a page with 20+ regions loads slowly in Page Designer. Optimize the rendering."

### Problem
Page Designer becomes sluggish when editing apps with complex pages (30+ regions, 200+ items).

### Solution Walkthrough
1. **Use Page Groups** — Organization folders in Page Designer tree
2. **Disable Live Preview** — Uncheck "Preview" for performance
3. **Reduce Region Queries** — Use static regions where possible
4. **Set Region "Source" to "Never"** — For layout-only regions
5. **Use Template Options** — Minimize custom HTML regions
6. **Clear Cache** — Flush APEX page cache:
   ```sql
   -- <!-- UNVERIFIED: APEX_UTIL.CLEAR_PAGE_CACHE needs doc/DB confirmation — package, procedure name, and signature not verified against the APEX docs. -->
   BEGIN APEX_UTIL.CLEAR_PAGE_CACHE(p_page_id => 10); END; /
   ```
7. **Upgrade APEX** — Latest APEX version has tree virtualization

### Code
```sql
-- Identify heavy regions in page
SELECT region_id, region_name, source_type, source
FROM APEX_APPLICATION_PAGE_REGIONS
WHERE application_id = 100 AND page_id = 10
ORDER BY region_id;
```

### Company Evaluation
- **Oracle**: Internal Page Designer architecture, tree rendering optimization
- **Accenture**: Performance baselines, monitoring before/after changes
- **Deloitte**: Practical end-user performance tips for clients
