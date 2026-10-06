# Lab 01: APEX Getting Started — Real World Project

## Scenario

A 40-person consulting firm needs a department expense tracking application.
Managers view expenses in an Interactive Report with sorting, filtering, and
searching; finance staff add, edit, and delete records with confirmation; and
everyone sees summaries by category and by month.

There is no existing application and one database schema. One requirement is
non-negotiable from the client's finance team: **a manager must only ever see
their own department's expenses, including in the summary totals** — which is
exactly where prototypes tend to leak.

Second non-negotiable: the list page must load in under 2 seconds with 10,000
expenses, because the client's staff will not wait.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://docs.oracle.com/en/database/oracle/apex/24.2/ — Oracle APEX
  documentation home: regions, page items, processes, authorization schemes,
  dynamic actions, and the application export/import format.
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/ — PL/SQL
  Language Reference: session-independent PL/SQL units, `APEX_UTIL` context
  calls, `DBMS_ASSERT` sanitisation, exception handling, and cursor semantics.

Verify both links resolve to the current release before citing them in a client
document; Oracle re-points these URLs between releases.

## Architecture

```
Expense application (APEX, single schema)
   │
   ├─ Authentication sets session context once:
   │     MY_CTX_DEPARTMENT_ID, MY_CTX_USERNAME, MY_CTX_CLIENT_IP
   │
   ├─ current_department() → NVL(context, -1)      ← FAILS CLOSED
   │
   ├─ Page 1: Expense List
   │     ├─ IR detail            — scoped
   │     ├─ Summary: category    — scoped
   │     ├─ Summary: month       — scoped
   │     └─ Filters: date range (sargable), category, status — all bound
   │
   ├─ Page 2: Expense Form (modal dialog)
   │     ├─ Read query            — scoped
   │     ├─ Save process branching on P2_EXPENSE_ID
   │     ├─ Validation × 3, each naming the bad value
   │     └─ Delete + confirmation + audit snapshot
   │
   ├─ Page 0: Administrator health check
   │     └─ Lists every query touching EXPENSE and flags the unscoped ones
   │
   └─ Source control: app.yaml + ddl.sql + seed.sql
```

## Implementation sketch

```sql
-- Fail closed. NULL context yields no data, not all data.
CREATE OR REPLACE FUNCTION current_department RETURN NUMBER IS
BEGIN
  RETURN NVL(TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID')), -1);
EXCEPTION WHEN OTHERS THEN RETURN -1;
END;
/

-- Every region carries the predicate, including the summaries.
SELECT category, SUM(amount) FROM expense GROUP BY category;   -- ← the leak
-- Duplicate group labels reveal other departments' totals by inference,
-- even though no row was ever displayed.
```

## Requirements

- F1: `expense`, `department`, `app_user` schema with constraints and indexes on
  every filter and sort column.
- F2: Session context set once at authentication.
- F3: Fail-closed `current_department()` used by every region that reads `expense`.
- F4: Interactive Report with sorting, filtering, search, and server-side pagination.
- F5: Summary by category and by month, both scoped.
- F6: Form page with a scoped read query and one save process for both modes.
- F7: Three server-side validations with actionable messages.
- F8: Delete with a confirmation dialog and an audit snapshot.
- F9: Sargable date predicates with supporting indexes.
- F10: Responsive layout verified at 375, 768, and 1440 px.
- F11: Application exported and stored in source control after each increment.
- F12: Page 0 health check flagging any query touching `expense` without the
  scoping predicate.
- NF1: Zero cross-department exposure, verified with two accounts on every region.
- NF2: Delivered within the one-week window.
- NF3: List page under 2 seconds with 10,000 expenses.
- NF4: Security enforced in SQL, never by hiding UI elements.
- NF5: No unauthenticated access to any page.
- NF6: Documented rollback — YAML import restores any prior state.

## Milestones

- Day 1: Schema, indexes, seed data, `current_department()`, context at login.
- Day 2: List page — IR, filters, both summary regions, both scoped.
- Day 3: Form page — read query, save process, both modes verified.
- Day 4: Validations, delete, audit snapshot; health check query.
- Day 5: Responsive fixes, export/import test, performance measurement.
- Day 6: Two-account security test across every region; client walkthrough.
- Day 7: Buffer for findings, documentation, and handover.

## Verification

- Two accounts in different departments; confirm zero overlap in every region,
  including both summaries and both charts.
- Clear the session context and confirm zero rows rather than all rows.
- Attempt a cross-department `UPDATE`; confirm zero rows affected and a clear
  error message rather than a silent no-op.
- Replay the leak deliberately (remove the predicate from one summary), record
  what it disclosed, then restore it — the demonstration is part of the sign-off.
- Validation test per rule; confirm the message names the field and the value.
- Submit the same payload with curl, bypassing the browser, and confirm the
  server still rejects it.
- Delete test; confirm the audit snapshot captures the full prior row.
- Load 10,000 rows; time page 1 and confirm the p95 is under 2 seconds.
- Compare a sargable and a non-sargable month filter and record both plans.
- Run the page 0 health check; confirm zero `UNSCOPED` rows.
- Export, re-import into a clean workspace, and run a smoke test.
- Responsive test at 375, 768, and 1440 px.

## Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| A summary region ships unscoped | Medium | High | Health check query; scoping predicate written first |
| Filter added without an index | Medium | Medium | Index review before each increment |
| Client-side check treated as validation | Medium | Medium | Document the three layers; rely on the `CHECK` |
| YAML export drifts from the workspace | Low | High | Export after every increment, into source control |
| DML left in a region query | Low | High | Processes with a `When` condition; review checklist |
| Silent cross-department update | Low | High | `SQL%ROWCOUNT = 0` raises a named error |

## Rollback

The application is a single export; re-importing the prior YAML restores every
page in about five seconds. The schema is unchanged by the application, so schema
rollback is separate: `ddl.sql` plus `seed.sql` rebuild it from scratch, and
`expense_audit` retains the pre-deletion snapshot of anything already deleted.

Document rollback steps for every change made during the engagement, including
the one that removed the scoping predicate from a summary region — which is
precisely why the demonstration is recorded rather than merely performed.
