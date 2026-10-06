# Lab 01: APEX Getting Started — Theory

## The Scenario

A department expense tracking application, delivered in a week, with one
non-negotiable requirement: a manager sees only their own department's expenses,
**including in the summary totals**. Everything below is arranged around that
single constraint, because it is the constraint that prototypes violate.

## Principle 1: APEX is a page-and-region model over your schema

```
Workspace (shared APEX instance)
   └─ Schema (your data)
        └─ Application
             └─ Pages
                  └─ Regions (Interactive Report, Form, Chart, ...)
                       └─ Items (page items, columns)
```

The application is metadata that describes pages. The data is yours in your
schema. Nothing sits between you and the SQL — which is why APEX debugging is
straightforward, and why APEX cannot protect you from a badly written query.

**Corollaries**
- Row security is your responsibility, not the framework's.
- Every query you write is visible and reviewable.
- A query that works in SQL Workshop works identically in a region.

## Principle 2: Every region is a query, and it runs on every render

```
Page render:
   Run region 1 query   → rows to client
   Run region 2 query   → rows to client
   Run region 3 query   → rows to client
```

A page with 12 regions issues 12 queries on every render, whether or not the
user scrolls to them. This single fact determines:

1. **"Pagination" is not a filter.** APEX asks for 25 rows; the database still
   runs the query over the filtered range. On a low-selectivity filter over
   millions of rows, the query still reads most of the table.
2. **Removing a region removes a query.** It is a real optimisation — but only
   if the removed query was expensive. Framework overhead is roughly 400 ms and
   dominates until about 20 regions.
3. **A `COUNT(*)` for pagination is separate work.** It runs over the whole
   filtered range regardless of page size.

## Principle 3: Sargability decides whether your indexes are used

```sql
-- Non-sargable: a function applied to the INDEXED COLUMN
WHERE TRUNC(expense_date) = :p_date
WHERE TO_CHAR(expense_date,'YYYY-MM') = :p_month

-- Sargable: the column is compared to a value
WHERE expense_date >= :p_from AND expense_date < :p_to + 1
WHERE expense_date >= ADD_MONTHS(:p_month, 1)
```

The distinction is *which side* the function is on. `NVL(:P_DEPT_ID, column)`
is fine — the function is on the bind. `NVL(column, :P_DEPT_ID)` is not.

Measured effect on a one-million-row table with one month matching:

| Form | Index used | Rows read |
|------|-----------|-----------|
| `TRUNC(expense_date) = :d` | No | 1,000,000 |
| `expense_date >= :d AND < :d+1` | Yes | 24,000 |

Roughly 41× fewer rows read, for zero cost and zero user-visible change. This is
usually the highest-return change available in a slow APEX report.

## Principle 4: Session state is how you pass context

| Approach | Where the value lives | User-editable? |
|----------|----------------------|----------------|
| Session state | APEX session table (server) | No |
| URL query string | Browser address bar | Yes |
| Page submission | POST body | Yes, via dev tools |

Session state prevents trivial tampering: there is no browser control to change
it. But it is **not** an authorisation control — it does not prevent an unscoped
`UPDATE`. You need both:

```
Session state  → removes trivial tampering
Scoped UPDATE  → enforces authorisation regardless
```

Use the URL when a link must be shareable or bookmarkable. Use session state when
the value identifies *whose* data the user may see.

## Principle 5: DML belongs in a process with a condition, never in a region query

```
Insert/update on one form page:
  Process: "Save Expense"
  Type:    PL/SQL (or Automatic Row Processing)
  When:    Both (on load and on submit)
  PL/SQL:  IF :P2_EXPENSE_ID IS NULL THEN INSERT ... ELSE UPDATE ... END IF;
```

Why it must be a process and not the report's SQL:

- The report query runs on render. Putting DML in it means the render can write.
- A process with a `When` condition runs only when you intended.
- Automatic Row Processing handles both modes by primary key, with no branching
  to get wrong.

The same reasoning applies to deletes: a process with a confirmation dialog, not a
link that deletes on click.

## Principle 6: Validation must be server-side, and the constraint is the backstop

Three layers, and only the last one is authoritative:

```
1. Client-side JS    → fast feedback, trivially bypassed (curl, Postman, dev tools)
2. Page validation   → server-side, good messages, can be omitted by mistake
3. CHECK constraint   → enforced by the database regardless of client or code
```

```
CHECK (amount > 0)
```

At 1,000 submissions/day with roughly 0.5% of requests coming from outside the
browser, a client-only check lets about 5 invalid rows per day through. The
constraint makes that number zero.

Write the message so it names the field **and** the offending value:

```
Amount must be greater than 0. Entered: -50
```

## Principle 7: Row security must cover every region, including summaries, and must fail closed

```sql
-- Fails CLOSED: no context means no rows, never all rows
CREATE OR REPLACE FUNCTION current_department RETURN NUMBER IS
BEGIN
  RETURN NVL(TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID')), -1);
EXCEPTION WHEN OTHERS THEN RETURN -1;
END;
```

Every region touching secured data carries the predicate:

```sql
WHERE department_id = current_department()
```

**The classic failure is scoping the detail and forgetting the summary.**

```
Unscoped summary grouped by category:
   Travel     50,000
   Supplies   10,000
   Travel     50,000    ← duplicate label: another department is visible
   Supplies   10,000
```

No row belonging to another department was displayed, yet duplicate group labels
with identical totals reveal the existence and the value of their spending. The
inference is the disclosure. Scoped:

```
   Travel     50,000
   Supplies   10,000
   Travel      4,000    ← only your own; others invisible
   Supplies    2,000
```

Then take the scoping up a level so a missed predicate cannot leak at all:

| Layer | Coverage | Depends on |
|-------|----------|-----------|
| Predicate in each query | Reviewer discipline | Every query written correctly |
| VPD policy on the table | Database enforcement | Nothing |

Write the predicate first, then add VPD as the thing that makes the missed
predicate impossible.

## Principle 8: Deletion needs confirmation and an audit snapshot

```
Confirmation dialog  → stops accidents
Audit snapshot       → preserves the only remaining evidence
```

A delete destroys the only record. An audit table holding a copy of the row
means the action is reversible and attributable years later. Storage cost is
negligible — about 7,280 deleted rows over a 7-year retention is under 3 MB —
and it is the difference between "we can find out" and "we cannot".

## Principle 9: The export is the rollback path

```
Export a 12-page application:  ~400 KB of YAML
Import time:                   ~5 seconds
Rollback:                      import the previous YAML
```

Compare with reconstructing the application by hand: hours. This is why the
export belongs in source control from day one rather than at delivery. A rollback
plan that is not a file is not a plan.

## Principle 10: Selectivity is the performance driver, and dates are the lever

| Filter | Rows matched | Relative cost |
|--------|-------------|---------------|
| Department only | 83,000 | baseline |
| Department + status | 66,000 | 1.3× |
| Department + last 7 days | 1,600 | 52× |
| Department + today | 230 | 360× |

```
Selectivity ratio = total rows / rows matched
```

A date range is the highest-value filter in almost every APEX application
because it is both selective and index-friendly. The practical consequence: the
date items must be inside the query, not applied afterwards by the framework or
by JavaScript. A filter that is not in the SQL is not a filter, it is a display
preference.

## Putting It Together

The order of the work matters more than the individual techniques:

1. Schema with constraints and indexes on every filter column.
2. The scoping function, written before the first query, failing closed.
3. Session context set once at authentication.
4. Regions, each carrying the predicate, including summaries.
5. Processes for DML, validation for messages, constraint as backstop.
6. Delete with confirmation and audit.
7. Export to source control after every working increment.

Retrofitting row security means re-reading every query, and the one you miss is
the disclosure. That is why it belongs on day one even though it costs three
hours there and two hours of review later.
