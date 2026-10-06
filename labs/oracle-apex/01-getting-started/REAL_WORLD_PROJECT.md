# Lab 01: APEX Getting Started — Real World Project

## Scenario
A consulting firm needs a department expense tracking application delivered within
a week. Managers must view all expenses in an Interactive Report with sorting,
filtering, and searching; add, edit, and delete records with confirmation; and
view expense summaries by category and month. The firm has no existing
application and a single database schema. One requirement is non-negotiable from
the client's finance team: a manager must only ever see their own department's
expenses, including in the summary totals — which is exactly where prototypes
tend to leak.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Expense application (APEX, single schema)
   │
   ├─ Authentication sets session context:
   │     MY_CTX_DEPARTMENT_ID, MY_CTX_USERNAME, MY_CTX_CLIENT_IP
   │
   ├─ current_department()  →  NVL(context, -1)   ← FAILS CLOSED
   │
   ├─ Page 1: Expense List
   │     ├─ IR detail      — scoped
   │     ├─ Summary: category — scoped
   │     ├─ Summary: month    — scoped
   │     └─ Filters: date range, category  (sargable, bound)
   │
   ├─ Page 2: Expense Form
   │     ├─ Read query — scoped
   │     ├─ Save process branching on P1_EXPENSE_ID
   │     ├─ Validation × 3 with specific messages
   │     └─ Delete + audit snapshot
   │
   └─ Source control: app.yaml + ddl + seed
```

## Implementation sketch
```sql
-- Fail closed: NULL context yields no data, not all data
CREATE OR REPLACE FUNCTION current_department RETURN NUMBER IS
BEGIN
  RETURN NVL(TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID')), -1);
EXCEPTION WHEN OTHERS THEN RETURN -1;
END;
/

-- Every region, including summaries, carries the predicate.
-- The unscoped summary is the classic disclosure:
SELECT category, SUM(amount) FROM expense GROUP BY category;
-- → duplicate group labels reveal other departments' totals by inference.
```

## Requirements
- F1: Expense schema with constraints and indexes on filter columns.
- F2: Session context set once at authentication.
- F3: Fail-closed scoping function used by every region.
- F4: Interactive Report with sorting, filtering, search, and pagination.
- F5: Summary by category and by month, both scoped.
- F6: Form page with a scoped read query and a save process for both modes.
- F7: Three server-side validations with actionable messages.
- F8: Delete with confirmation and an audit snapshot.
- F9: Sargable date predicates with supporting indexes.
- F10: Responsive layout verified at 375, 768, and 1440 px.
- F11: Application exported and stored in source control.
- NF1: Zero cross-department exposure, verified with two accounts on every region.
- NF2: Delivered within the one-week window.
- NF3: List page under 2 seconds with 10,000 expenses.
- NF4: Security baseline — scoping enforced in SQL, not by the UI.
- NF5: No unauthenticated access to any page.
- NF6: Documented rollback — YAML import restores any prior state.

## Milestones
- Week 1 Day 1: Schema, seed data, and row security function.
- Week 1 Day 2: List page with IR, filters, and both summary regions.
- Week 1 Day 3–4: Form page with save, validation, and delete audit.
- Week 1 Day 5: Responsive fixes and export/import test.
- Week 1 Day 6–7: Cross-department security test and client walkthrough.

## Verification
- Two accounts in different departments; confirm zero overlap in every region.
- Clear the session context and confirm zero rows, not all rows.
- Attempt a scoped UPDATE against another department's row; confirm zero rows affected.
- Validation test for each rule; confirm the message names the bad value.
- Delete test; confirm the audit snapshot captures the row.
- Export, re-import to a clean workspace, and run a smoke test.
- Responsive test at 375, 768, and 1440 px.

## Rollback
The application is a single export; re-importing the prior YAML restores every
page. The schema is unchanged by the application, so schema rollback is separate
and documented. Document rollback steps for every change.