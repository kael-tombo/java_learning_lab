# Lab 08: APEX Performance — Theory

## The Scenario

A customer's APEX application dashboard takes 12 seconds. It has 8 Interactive
Reports, 3 charts, and 10 dynamic actions. The DBA has already added indexes on
the obvious columns with no improvement, so they concluded "APEX is slow". Someone
suggested enabling pagination, which has now been tried twice with no effect.

## Principle 1: Attribution before action — always

```
APEX Debug timing breakdown for this page:

  Page Processing        8.2 s
    SQL queries          7.1 s
      IR #1 (orders)       3.2 s   ← 27% of total, the single largest item
      IR #2 (customers)    1.8 s
      Charts (3 combined)  2.1 s
      IR #3-8              ~0 s
    PL/SQL processing      0.9 s
    Processes (10 DAs)     0.2 s
  Rendering               3.0 s   ← 10 dynamic actions, no cache
  Session state           0.6 s
  Total                  12.0 s
```

**One run localises the problem.** Two findings immediately:

1. **One region is 3.2 seconds.** Optimising the other seven IRs — which together
   take under a second — changes nothing.
2. **Pagination was already on.** The DBA's "APEX is slow" conclusion came from
   attributing time to the framework rather than to a region.

## Principle 2: Pagination is not a filter — the second time this matters

```
Developer believes:   SELECT ... (returns 25 rows, so it must be fast)
Actually happens:      full scan of 5M rows, filtered, sorted, then 25 returned
```

If the filter is not selective, the database scans nearly the whole table before
producing the first page. **Enabling pagination cannot change that** — which is
why it was tried twice with no effect.

**Pagination controls returned bytes, not rows examined.** The fix is a predicate
the index can serve.

## Principle 3: Sargability — the single highest-return change

```
NOT sargable:  WHERE TRUNC(order_date) = :p_date
               WHERE TO_CHAR(order_date,'YYYY') = :p_year
               WHERE UPPER(customer_name) = :p_name     (unless a function index)

Sargable:      WHERE order_date >= :p_from AND order_date < :p_to + 1
               WHERE UPPER(customer_name) = :p_name     (with a function index)
```

```
Cost on a 5M-row table, 1 month matching:
  TRUNC(order_date) = :p_date       → 5,000,000 rows examined
  order_date >= :d AND < :d+1       →   208,000 rows examined

Reduction: 24x, for a one-line change.
```

**Always check the plan after a predicate change.** A predicate that looks
sargable can still defeat an index if the column is the second operand of a
non-equality join.

## Principle 4: Bind variables and the library cache latch

```sql
-- In a page process, string-built SQL with a literal:
WHERE status = '&P1_STATUS_'
```

Each distinct literal value is a **different statement** requiring a hard parse
and, more importantly, **library cache latch acquisition** — a resource shared by
every session on the instance.

```
Literal SQL, 200 users, 250 working days:
  Distinct statements per status value × users × days
  Hard parses: ~50,000/year
  Each contends on library cache latches with unrelated workloads
```

**This is the mechanism behind "APEX got slow and we don't know why".** It is not
linear — latch contention degrades exponentially, so a moderate APEX problem can
impair an entire database.

## Principle 5: Four cache layers, each for a different problem

| Layer | Scope | Use for |
|-------|-------|---------|
| **Region cache** | One region query | Slow-changing region data |
| **Page cache** | Whole rendered page | Identical pages: no per-user data |
| **Session state cache** | Value across pages in a session | Small stable lookups |
| **Function result cache** | PL/SQL result across sessions | Expensive aggregates |

### Choosing

```
The dashboard's 3.2-second region:
  What does it return?  Order list for the last 30 days
  How stale can it be?  A minute is acceptable for an executive view
  → Region cache, 60 s TTL, ~98% hit rate

The dashboard as a whole:
  Does it contain per-user data?  Yes — user filters
  → PAGE CACHE IS WRONG HERE. It would serve one user's HTML to another.
```

**Page cache on a personalised page is a data disclosure bug**, not a
performance decision.

## Principle 6: Session state is a per-request cost

APEX session state is read and written on every request.

```
Unnecessary content:
  A 40 KB blob of lookup data cached in session state
  Serialised and deserialised on every page

Cost: 40 KB × 2 (write + read) × 0.6 s/page ÷ 0.6 MB/ms...
      empirically, a large session state blob adds 0.5-1.5 s per page
```

Two questions for every session state item:

```
1. Does it need to survive across pages?
2. Could it be re-derived cheaply from the database?

If no to (1) or yes to (2), move it.
```

## Principle 7: PL/SQL in APEX has its own hot spots

```plsql
-- Common APEX PL/SQL anti-patterns:

FOR r IN (SELECT ...) LOOP        -- row-by-row on a collection
  SELECT single_col INTO x
    FROM big_table WHERE ...;      -- query per iteration
END LOOP;
```

**The fix is `BULK COLLECT` plus a set-based DML**, which is covered in Lab 05.
The APEX-specific point: PL/SQL processes and Dynamic Action JavaScript run
server-side, so their cost lands on the same request budget as the regions.

```
PL/SQL processing: 0.9 s of the 12 s = 7.5%
Worth fixing, but only after the 3.2 s region.
```

**Order matters.** Micro-optimising 0.9 s of PL/SQL while a region takes 3.2 s
spends effort on 7.5% of the problem.

## Principle 8: Rendering is a real cost on action-heavy pages

```
10 dynamic actions, no page caching
  Each DA: event binding, condition evaluation, potential AJAX round trip

Rendering: 3.0 s of the 12 s = 25%
```

Three legitimate reductions:

1. **Cache the rendered page** — only if no per-user data.
2. **Reduce DA count** — consolidate actions targeting the same element.
3. **Move logic server-side** — a DA that calls a process for a simple value is a
   round trip for nothing.

**Conditional DAs with complex conditions are evaluated on every page load even
when they do nothing.** Simplifying conditions helps.

## Principle 9: Theme assets are a network cost

```
Universal Theme CSS + APEX JavaScript: roughly 1.5-2.5 MB uncompressed
On a 5 Mbps connection:                 1.5 MB / 625 KB/s ≈ 2.4 s
```

This is time spent **before the first region renders** — invisible in the server
timings and completely real to the user.

Reductions, in order:

1. **Enable CSS and JavaScript minification** — typically 40-60% reduction.
2. **Enable gzip compression** — typically another 60-70% on top.
3. **Remove unused page-level JavaScript** — libraries loaded per page that the
   page does not use.

```
1.8 MB uncompressed
  → 0.8 MB after minification
  → 0.25 MB after gzip
  → 0.4 s on a 5 Mbps connection, from 2.9 s
```

**This is a 2.5-second saving that no server-side work can touch.**

## Principle 10: Use the right tools

| Tool | Answers |
|------|---------|
| APEX Debug | Where did this one request spend its time? |
| Activity log | Which pages are slow across many users, and at what percentile? |
| Application Performance Analyzer | Which SQL, PL/SQL, and regions dominate across the app? |
| Database AWR | What is the database doing, and is it waiting or CPU-bound? |

**Each answers a different question and none substitutes for the others.**

The common mistake is using only one. A DBA with AWR says "the database is fine,
I/O is normal" while the application spends 7 seconds in SQL — both are true and
together they mean the SQL is slow, not that the database is.

## Principle 11: Some problems are not the application's to fix

```
Database waits on I/O for 12 seconds:
  Application SQL is not the problem. Storage is.

Library cache latch contention from another system:
  Application SQL is not the problem.

Missing index on a table queried by 50 applications:
  Adding it helps, but the shared fix belongs in the database.

CPU saturated across the instance from all tenants:
  Scaling requires infrastructure, not code.
```

**Knowing where the application's responsibility ends is part of performance
work.** Escalating a storage problem as "APEX is slow" wastes weeks.

## Principle 12: Optimise for the metric you will be measured on

```
Requirement: dashboard under 3 seconds p95
  Optimising the average gets you a number you cannot report
  Optimising p99 gets you a number nobody experiences

Also: a page that is 11.9 s for 1% of users and 1.2 s for the rest
  passes on average
  fails on p95
  and 1% of users still cannot work
```

**Measure and report the same statistic the requirement specifies.**

## Diagnostic Order

1. APEX Debug — attribute this one request.
2. The activity log — attribute across users, at p95.
3. APA — identify dominant SQL, PL/SQL, and regions across the app.
4. Fix the single largest contributor first.
5. Check sargability before adding an index.
6. Check for literals causing hard parses.
7. Choose the cache layer for the problem; never page-cache personalised content.
8. Audit session state size.
9. Enable theme minification and gzip.
10. If waits dominate, escalate to storage — that is not the application's fix.

## Anti-Patterns

- Optimising without a Debug breakdown.
- Adding indexes without checking sargability.
- Concluding "APEX is slow" from database metrics.
- Retrying pagination as a performance fix.
- Page-caching a page with per-user data.
- Micro-optimising PL/SQL while a region takes 3 seconds.
- Ignoring theme assets and network transfer time.
- Optimising the average against a p95 requirement.
- Rewriting an application problem that is a storage problem.

## Summary

The 12 seconds broke down as 3.2 s in one region, 3.0 s rendering, 2.1 s in
charts, and under a second in the other seven reports combined — so the two changes
that mattered were making that one region's predicate sargable and enabling theme
minification plus gzip. Pagination had already been tried and could never have
worked, because it does not change rows examined. Everything else was
attributable to less than 10% each.