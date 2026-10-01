# Flashcards: APEX Getting Started

1. Q: What two pages form the minimal APEX CRUD? | A: Interactive Report (list) + Form (edit), linked by PK.
2. Q: What bind-variable syntax references a page item in SQL? | A: `:P1_ITEM` / `:G_DEPT_ID` — never string concatenation.
3. Q: What does `NVL(:G_DEPT_ID, e.department_id)` implement? | A: Row-level security with admin bypass (NULL = all rows).
4. Q: Which process type implements Form save without manual DML? | A: Automatic Row Processing (DML).
5. Q: Where does duplicate-check validation run? | A: On Submit, Before Processing, as PL/SQL Function Returning Boolean.
6. Q: What Dynamic Action refreshes the IR on date-filter change? | A: Event Change on `P1_DATE_FROM/TO` → Action Refresh region.
7. Q: What format mask pattern shows currency amounts? | A: `FMT_L` / `999G999G990D00`.
8. Q: How are PENDING/APPROVED/REJECTED colour-coded? | A: Badge LOV: yellow / green / red.
9. Q: What computation sets `G_DEPT_ID` after login? | A: `SELECT department_id ... WHERE manager_email = :APP_USER`.
10. Q: What pagination mode keeps a 10k-row IR fast? | A: Server-side pagination, 25 rows.
11. Q: What does the Delete button require? | A: Confirmation dialog ("Are you sure...").
12. Q: What does `mv_expense_summary` pre-aggregate? | A: count/total by department, category, month.
13. Q: Which theme family is used? | A: Vita / Redwood Light.
14. Q: What three dashboard regions exist? | A: Summary stats report + category pie + monthly bar.
15. Q: Pitfall: security by obscurity? | A: Hiding a button is not enough — enforce WHERE-clause filtering in every query.
