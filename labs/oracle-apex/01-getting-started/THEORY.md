# Lab 01: APEX Getting Started — Theory

## The Scenario

A department expense tracking application, delivered in a week, with one
non-negotiable requirement: a manager must only ever see their own department's
expenses — **including in the summary totals**.

## Principle 1: APEX is a page-and-region model over your schema

```
Workspace (shared APEX instance)
   └─ Schema (your data)
        └─ Application
             └─ Pages
                  └─ Regions (Interactive Report, Form, Chart, ...)
                       └─ Items (page items, columns)
```

Nothing is hidden from you. The application is metadata that describes pages;
the data is yours in your schema. This transparency is why APEX debugging is
straightforward — there is no framework layer between you and the SQL.

**The corollary matters**: because APEX is transparent, it cannot protect you from
a bad query. Row security is your responsibility.

## Principle 2: Every region is a query, and it runs on every render

```
Page render:
   Run region 1 query   → rows to client
   Run region 2 query   → rows to client
   Run region 3 query   → rows to client
   ...
```

This is the single most important performance fact in APEX. A page with 12
regions issues **12 queries on every page render**, whether the user is looking
at all of them or not.

Two consequences:

1. **"Pagination" is not a filter.** APEX requests 25 rows; the database still
   executes the query. On a low-selectivity filter over 5 million rows, the
   query still scans most of the table.
2. **Reducing region count is a real optimisation.** Removing a region removes a
   query.

The alternative — sharing one query across several display regions — is what
collections are for. See Lab 07.

## Principle 3: Session state is the correct way to pass context

When a user clicks a row and you navigate to a form page, you need to pass the
record ID. Three options:

| Approach | Assessment |
|----------|-----------|
| URL query string | Visible, editable, bookmarkable — user can change it |
| Page submission | Heavy, submits the whole page |
| **Session state** | **Correct** — not in the URL, survives navigation |

```sql
-- Read the ID from session state, not from the URL
SELECT expense_id, expense_date, category, amount, description
  FROM expense
 WHERE expense_id = :P1_EXPENSE_ID
   AND department_id = :P1_DEPARTMENT_ID;   -- scoping here, not only in UI
```

**Session state items are not in the URL, so a user cannot tamper with them by
editing a link.** They are also not a security boundary — they live in the
database — but they remove the trivial attack of changing a URL parameter.

## Principle 4: DML happens in processes, not in the region query

A Form region's query is a `SELECT`. Saving is done by a **page process**:

```
Process: "Save"
  When:     "Create" or "Update" (the standard form condition)
  Type:     PL/SQL Page Process
  Source:   the INSERT or UPDATE
```

This means:
- The form region is always read-only in intent.
- The DML is explicit, reviewable, and versionable on export.
- A developer can see exactly what writes to the database.

The **condition** is what makes a form work for create and update. A form
supporting both uses `P_NEW_RECORD` (set by the "New" button) to choose the
branch:

```sql
IF :P_NEW_RECORD = 'Y' THEN
  INSERT INTO expense (...) VALUES (...);
ELSE
  UPDATE expense SET ... WHERE expense_id = :P1_EXPENSE_ID;
END IF;
```

## Principle 5: Validation is server-side and must be actionable

There is no client-side validation to rely on — page items are plain HTML
elements and the request can be constructed by anyone.

```text
Rule: amount > 0
Bad message: "Invalid value"
Good message: "Amount must be greater than zero. Entered: -50"
```

The second tells the user what to fix and what they typed. In an application
with 20 validation rules, message quality is the difference between 2 minutes of
correction and 10.

**Validation belongs on the server because the client is not trusted.** A
JavaScript check is a usability convenience, not a control.

## Principle 6: Row security must be in every query, including summaries

This is the requirement most often half-implemented. The pattern that fails:

```
Detail regions:   WHERE department_id = :P1_DEPARTMENT_ID   ✓ scoped
Summary region:   SELECT category, SUM(amount) FROM expense GROUP BY category
                                                            ✗ NOT scoped
```

The summary reveals the department's full position even though no individual row
is visible — and worse, if the group-by is coarse, a user can **infer** other
departments' totals from the group labels.

```
Department A:  Travel 50,000   Supplies 10,000
Department B:  Travel 50,000   Supplies 10,000
```

With an unscoped summary, a user sees two identical "Travel" rows and knows
immediately that another department exists with that value. **Grouping by a
scoped column is not enough; the filter must be there too.**

The safest pattern is a single context function used by every region:

```sql
-- In every region query, without exception
WHERE department_id = SYS_CONTEXT('MY_CTX', 'DEPARTMENT_ID')
```

And set the context once, at authentication. If the context is ever NULL, the
region returns nothing rather than everything:

```sql
-- Fail closed: no context means no data, not all data
WHERE department_id = NVL(SYS_CONTEXT('MY_CTX','DEPARTMENT_ID'), -1)
```

## Principle 7: Delete deserves a confirmation and an audit row

Delete is irreversible and is the operation users misclick. Two requirements:

1. **Confirmation** — APEX's standard "delete" button pattern with a JS
   confirmation dialog.
2. **Audit** — record who deleted what and when, because after deletion the
   evidence is otherwise gone.

```sql
CREATE TABLE expense_delete_audit (
  expense_id  NUMBER NOT NULL,
  deleted_by  VARCHAR2(64) NOT NULL,
  deleted_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  reason      VARCHAR2(400)
);
```

## Principle 8: Export is your restore path

Every APEX application can be exported as a single YAML/SQL bundle containing
all pages, regions, items, processes, and theme references.

This means:
- Development is version-controllable.
- Deployment between environments is an import.
- **Rollback is an import of the previous export.**

Keep every application under source control. "It was only a few clicks" is not
a change history.

## Principle 9: Responsive is a layout decision

APEX's Universal Theme is responsive by default, but a fixed-width region
breaks it. Two common causes:

```
Custom fixed-width layout regions
Fixed pixel sizes on charts
```

Test at three widths: 375 px (mobile), 768 px (tablet), and 1440 px (desktop).
A layout that only works at the last one is not delivered.

## Principle 10: Prototype to deliverable in a week

The realistic week-one sequence:

| Days | Work |
|------|------|
| 1 | Schema, load test data, list page with IR |
| 2 | Filters and search |
| 3 | Form page with create/update |
| 4 | Delete with confirmation, validation |
| 5 | Row security across all regions |
| 6 | Summary region, responsive fixes |
| 7 | Export, second-environment import, walkthrough |

**Row security on day 5 is later than it should be.** Add the scoping predicate
on day 1 — retrofitting it means re-reading every query, and any query missed
becomes a disclosure. Build it in from the first query.

## Diagnostic Order

1. Which page region owns the slow part? (APEX Debug, not intuition.)
2. Is any query unfiltered where it should be scoped?
3. Is context passing through session state or the URL?
4. Does every DML statement live in a process with a condition?
5. Does every region — including summaries — carry the scoping predicate?
6. Does the context fail closed when NULL?
7. Is the application exported and under source control?

## Anti-Patterns

- Adding row security at the end rather than with the first query.
- Scoping detail regions but not summary regions.
- Passing record IDs in the URL instead of session state.
- Putting INSERT/UPDATE inside a region query.
- Relying on client-side validation.
- Deleting without confirmation or an audit row.
- Assuming pagination makes a query cheap.
- Delivering without testing at 375 px width.

## Summary

The week's work was not the CRUD mechanics — it was three decisions made early
that determined whether the application was safe and supportable: scoping
predicates on every region including summaries from the first query, session
state rather than URL parameters for context, and DML confined to processes with
explicit conditions. The CRUD itself followed from those.