# Lab 01: APEX Getting Started — Real World Project

## Scenario
A consulting firm needs a department expense tracking application delivered within
a week. Managers must see all expenses in an Interactive Report with sorting,
filtering, and searching; add, edit, and delete records; and view summaries by
category and month. The firm has no existing application and a single database
schema. One requirement is non-negotiable from the client's finance team: a
manager must only ever see their own department's expenses, including in the
summary totals — which is where most prototypes leak data.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
Department expense application (APEX)
   │
   ├─ Page 1: Expense List
   │     ├─ Interactive Report — expenses (scoped to department)
   │     ├─ Filters: date range, category, status
   │     └─ Summary region — totals by category and month (scoped)
   │
   ├─ Page 2: Expense Form
   │     ├─ Items: date, category, amount, description, status
   │     ├─ Processes: create, update, delete (with confirmation)
   │     └─ Validations: amount > 0, date ≤ today, category required
   │
   └─ Row security: department filter applied in EVERY region query
         └─ Session context: DEPARTMENT_ID set at authentication

Two managers, two departments, zero overlap visible.
```

## Implementation sketch
```sql
-- Row security must be in the query, not just the page
SELECT e.expense_id, e.expense_date, e.category, e.amount, e.description, e.status
  FROM expense e
 WHERE e.department_id = SYS_CONTEXT('MY_CTX', 'DEPARTMENT_ID')   -- never "all"
 ORDER BY e.expense_date DESC;
-- The summary region uses the SAME predicate, or it becomes the leak.
```

## Requirements
- F1: Expense schema with departments, users, and expenses.
- F2: Interactive Report with sorting, filtering, search, and pagination.
- F3: Form page supporting create, update, and delete with confirmation.
- F4: Session-state navigation between list and form.
- F5: Validation on amount, date, category, and required fields.
- F6: Department-scoped row security on every region including summaries.
- F7: Summary by category and month, department-scoped.
- F8: Responsive layout for desktop and tablet.
- F9: Application export and re-import to a second workspace.
- F10: Delete confirmation and an audit trail for deletions.
- NF1: Zero cross-department data exposure, verified with two accounts.
- NF2: Application delivered within the one-week window.
- NF3: List page loads under 2 seconds with 10,000 expenses.
- NF4: Security baseline — summary regions scoped identically to detail regions.
- NF5: No unauthenticated access to any page.
- NF6: Documented rollback — export provides a versioned restore point.

## Milestones
- Week 1: Schema, list page, filters, and search.
- Week 1: Form page with create, update, delete, and validation.
- Week 2: Row security applied to all regions including summaries.
- Week 2: Summary region, responsive layout, and export/import test.
- Week 2: Client walkthrough and handover.

## Verification
- Two accounts from different departments; verify zero overlap in any region.
- Validation test for each rule with a clear message.
- Delete confirmation test; verify the audit entry is written.
- Tablet-width test on a real device or responsive preview.
- Export and re-import to a clean workspace.

## Rollback
Every page is exportable; the schema is unchanged by the application; row
security is a predicate that can be added without touching the UI. Document
rollback steps for every change.