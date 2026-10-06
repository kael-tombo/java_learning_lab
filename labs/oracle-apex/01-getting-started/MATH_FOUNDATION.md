# Lab 01: APEX Getting Started — Math Foundation

## 1. Region Query Cost — the Fundamental APEX Fact

A page with N regions issues N queries on every render.

```
Regions on the expense list page:   5
  IR detail                           1 query
  Summary by category                 1 query
  Summary by month                    1 query
  Department LOV                      1 query
  Row-count for IR pagination         1 COUNT(*) query

Queries per page render: 5
Cost per query (10,000 rows, indexed):  15 ms
Rendered SQL time:                       75 ms
Framework overhead:                      ~400 ms
Total page load:                        ~475 ms
```

**The framework overhead exceeds the SQL time.** This is normal for APEX and
changes optimisation priorities: on a fast query set, PL/SQL micro-optimisation
buys nothing.

## 2. Pagination Is Not a Filter

The most common APEX misunderstanding.

```sql
-- What the developer thinks happens
SELECT * FROM expense ORDER BY expense_date;   -- "only 25 rows displayed"

-- What actually happens
SELECT * FROM expense
 WHERE department_id = 1
 ORDER BY expense_date DESC
 FETCH FIRST 25 ROWS ONLY;
```

The database must still find and sort rows until it has 25 matches.

### Sort cost with no index

```
Rows to sort for the first page: the whole table
Table size:                        1,000,000 rows

Index on (department_id, expense_date DESC):
  Top-N sort via index             ->  25 rows read
No index:
  Full scan + sort                 ->  1,000,000 rows read
```

```
Ratio: ~40,000x more rows read without the index
```

And the `COUNT(*)` for pagination is unavoidable regardless of display:

```sql
SELECT COUNT(*) FROM expense WHERE department_id = 1;   -- always full range
```

So pagination reduces **returned bytes**, never **rows examined**.

## 3. Filter Selectivity — the Cost Driver

```sql
-- Query: WHERE department_id = :d AND status = :s ORDER BY expense_date DESC
```

| Filter | Rows matched | Cost |
|--------|-------------|------|
| dept = 3 only | 83,000 | Baseline |
| dept = 3 AND status='APPROVED' | 66,000 | 1.3x |
| dept = 3 AND date last 7 days | 1,600 | 52x faster |
| dept = 3 AND date today | 230 | 360x faster |

```
Selectivity ratio = total rows / rows matched
```

**A date range is the highest-value filter in almost every APEX application**
because it is both selective and index-friendly. This is why the date items must
be in the query rather than applied after it.

## 4. The Sargable Predicate Rule

```sql
-- NON-SARGABLE: function on the indexed column disables the index
WHERE TRUNC(expense_date) = :p_date
WHERE TO_CHAR(expense_date,'YYYY-MM') = :p_month
WHERE UPPER(description) = UPPER(:p_desc)

-- SARGABLE: column compared directly to a value
WHERE expense_date >= :p_from AND expense_date < :p_to + 1
WHERE expense_date >= ADD_MONTHS(:p_month, 1)
```

### Cost comparison

| Form | Index used? | Rows read (1M table, 1 month match) |
|------|-------------|-------------------------------------|
| `TRUNC(expense_date) = :d` | No | 1,000,000 |
| `expense_date >= :d AND < :d+1` | Yes | 24,000 |

```
24,000 / 1,000,000 = 2.4% of the rows -> 41x faster
```

This one change is usually the highest-return optimisation in a slow APEX
report, and it costs nothing.

## 5. Row Security Coverage Math

The requirement: a manager sees only their department, **including summaries**.

```
Total expenses:            12,000
Department A expenses:       1,000
Department B expenses:       1,000

Regions on the list page:   5
Regions correctly scoped:   4
Unscoped summary region:    1
```

**Compliance score: 4/5 = 80%. One region exposes the rest.**

### Disclosure through grouping

```
Unscoped summary grouped by category:
  Travel     50,000
  Supplies   10,000
  Travel     50,000     <-- duplicate label: a second department is visible
  Supplies   10,000
```

Two identical group labels with identical totals reveal the existence and value
of another department's spending. **The inference is the disclosure**, even
though no row was visible.

```
Scoped summary grouped by category:
  Travel     50,000
  Supplies   10,000
  Travel      4,000    <-- only your own; others invisible
  Supplies    2,000
```

## 6. Session State vs URL — Exposure Comparison

```
Approach                     Where the ID lives          User-editable?
Session state                APEX session table          No (server side)
URL query string             Browser address bar         Yes
Page submission              POST body                   Yes (via dev tools)
```

### Attempting to tamper

```
URL:  myapp/page2?P1_EXPENSE_ID=1043
      -> change to 1044 -> loads another department's expense (if unscoped)

Session state:
  -> no browser control exists to change
```

But session state is **not** an authorisation control:

```
Session state is stored per session, keyed by an opaque session ID in the cookie.
It prevents casual URL tampering. It does NOT prevent an unscoped UPDATE.
```

Therefore both are needed:

```
Session state   -> removes trivial tampering
Scoped UPDATE   -> enforces authorisation regardless
```

## 7. Validation Coverage

```
Validation rules defined:      3
Rules implemented server-side: 3
Rules implemented client-side: 1  (JS check on amount)

Requests bypassing the browser: ~0.5% (curl, Postman, a script)
```

At 1,000 submissions/day:

```
Rules bypassed: 1,000 x 0.005 = 5/day
```

A client-side-only check would let 5 invalid rows per day through. The database
`CHECK` constraint is the final backstop:

```sql
CHECK (amount > 0)   -- enforced regardless of client
```

## 8. Delete Frequency and Audit Value

```
Expenses per day:        200
Deletes per day (est.):   4  (2%)
Retention requirement:   7 years

Deletes over 7 years:    4 x 260 x 7 = 7,280 rows
```

Without an audit table, each deletion destroys the only record. With one, the
snapshot column makes the audit self-sufficient even after the row is gone.

```
Audit storage: 7,280 rows x ~400 bytes = 2.9 MB over 7 years
Trivial cost, and it is the only remaining evidence.
```

## 9. Region Count and Page Load

| Regions | SQL time | Total load | Note |
|---------|----------|------------|------|
| 3 | 45 ms | ~450 ms | Lean |
| 6 | 90 ms | ~495 ms | Typical |
| 12 | 180 ms | ~585 ms | Getting heavy |
| 20 | 300 ms | ~705 ms | Investigate |

**Framework overhead (~400 ms) dominates until ~20 regions.** Removing regions
saves less than it appears to, unless the removed query was itself expensive.

```
Removing a 15 ms region from a 585 ms page: saves 15 ms (2.6%)
Removing a 900 ms region from a 1,400 ms page: saves 900 ms (64%)
```

Optimise the expensive region, not the cheap one.

## 10. Load Test Expectation

```
Target: 50 concurrent users, p95 page load under 2 seconds

Users:                50
Think time per page:  ~20 s
Requests/second:      50 / 20 = 2.5 req/s

Per request: ~475 ms of database+framework work
Database concurrency: 2.5 x 0.475 = 1.19 -> ~1.2 active sessions
```

**The application is nowhere near a capacity limit.** At 2.5 requests/second even
an unindexed version would probably pass. This matters for expectations:

```
Load testing a new APEX app usually confirms adequacy rather than finding a limit.
The value is in measuring p95 and in confirming row security under concurrency.
```

## 11. Week One — Effort Distribution

| Task | Hours | Notes |
|------|-------|-------|
| Schema and seed data | 4 | Includes test data generation |
| List page and IR | 6 | The largest single block |
| Filters and search | 3 | |
| Form create/update | 5 | |
| Delete and validation | 3 | |
| Row security | 3 | Cheap on day 5; expensive retrofitted |
| Summary regions | 3 | |
| Responsive fixes | 3 | |
| Export and import test | 2 | |
| Walkthrough | 3 | |
| **Total** | **35** | One week |

**Retrofitting row security** would add roughly 2 hours of query review but also
carries the risk of missing a query — the reason it goes on day 1 in the theory,
even though it is only 3 hours here.

## 12. Export and Restore

```
Export size (12 pages, ~40 regions):  ~400 KB YAML
Import time:                          ~5 seconds
Rollback:                             import the previous YAML

Downtime for a rollback: 5 seconds
```

Compare to reconstructing the application manually: **hours**. This is why the
export belongs in source control from day 1 rather than at delivery.