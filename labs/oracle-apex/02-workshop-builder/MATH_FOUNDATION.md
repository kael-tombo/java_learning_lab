# Lab 02: Workshop Builder — Master-Detail Pages with Dynamic Actions

## 1. Queries Per Render — The Multiplier Nobody Budgets For

A master-detail page is two report queries plus one pagination count per level:

```
Master IR query                 1
Master COUNT(*) for pagination  1
Detail IR query (on refresh)    1
Detail COUNT(*)                1
Class/LOD/LOV queries           1-3
```

```
Single-page AJAX refresh, 12 rows visible:
  Master:   15 ms + COUNT 8 ms
  Detail:  25 ms + COUNT 12 ms
  LOVs:     6 ms
  SQL:      66 ms
  Framework + AJAX round trip: ~380 ms
  Total:    ~446 ms
```

**Each master row click re-runs the detail query.** That is the master-detail cost
model — the detail query is not once per page, it is once per interaction.

## 2. Row-Count-Driven Rendering Cost

```
Rows rendered per detail refresh:
  Master rows on page:            25
  Detail rows for a typical master: 8
  Rows actually drawn:            200

Detail rows for a wide master (order with 900 lines):  900
Rows drawn for that one click:   900
```

| Master rows | Typical detail | Wide master |
|-------------|----------------|-------------|
| 25 | 200 (5 ms render) | 22,500 (410 ms render) |
| 100 | 800 (18 ms) | 90,000 (1,600 ms) |

```
Rendering cost ≈ 0.018 ms per row (measured on a 25-column IR)

Rows are the driver. Columns are nearly free until ~40.
```

**The wide master is the failure case.** One click on an order with 900 lines
costs more than the entire page load. Two mitigations, both mandatory:

```sql
-- 1. Cap the detail region and tell the user
WHERE order_id = :P1_ORDER_ID
FETCH FIRST 200 ROWS ONLY;

-- 2. Page it — rows examined stay bounded
```

## 3. Session State — the Actual Storage Cost

Session state is a row in the APEX session table, serialised per request:

```
Collections holding master rows:   200 rows
Average row width:                 ~350 bytes
Serialised:                        200 × 350 = 70 KB

Typical page with 4 collections:   280 KB
Session table row limit reality:   1 (APEX serialises into CLOB)

Read cost per request (deserialise): ~3-8 ms per 70 KB collection
```

```
4 collections, read on every page:  280 KB
Deserialise cost:                   ~25 ms per request
At 600 requests/hour/user:          25 ms × 600 = 15 s of CPU/hour/user
```

| Approach | Session state size | Per-request cost |
|----------|--------------------|------------------|
| Bind a single master ID | ~20 bytes | ~0 ms |
| Session state, 1 collection | ~70 KB | ~4 ms |
| Session state, 4 collections | ~280 KB | ~25 ms |
| 200-row JSON blob | ~90 KB | ~7 ms + parse |

**Storing one ID beats storing 200 rows.** Pass `:P1_ORDER_ID` through session
state; let the detail query re-read from the database. The session state holding
the master ID is ~20 bytes and costs nothing.

## 4. Pagination Cost Curves — Why Offset Is a Trap

```
Rows to satisfy OFFSET n with FETCH FIRST 25:

  n=0      -> read      25 rows
  n=25     -> read      50 rows
  n=9,975  -> read 10,000 rows  (and sort them first)
  n=99,975 -> read 100,000 rows (and sort them first)
```

```
Read rows = offset + page_size

Cost model on the orders table (5M rows, no index on order_date):
  sort 100,000 rows ≈ 900 ms
  sort 10,000 rows  ≈ 95 ms
  sort 25 rows       ≈ 6 ms  (index top-N, if indexed)
```

**Cost grows linearly with page depth.** Two defences:

```sql
-- Keyset pagination: bounded reads at any depth
WHERE (order_date, order_id) < (:last_date, :last_id)
ORDER BY order_date DESC, order_id DESC
FETCH FIRST 25 ROWS ONLY;
```

```
Keyset: reads ~25 rows at ANY depth        -> flat cost curve
Offset: reads offset+25                    -> linear cost curve
```

## 5. Sargability and Selectivity in Detail Queries

The detail query always filters on `order_id`. That is the best case — one
equality predicate on a foreign key index:

```
Orders:            5,000,000
Lines per order:   average 8, worst 900
Lines total:       ~40,000,000

Detail query with index on lines(order_id):
  Rows read: ~8 per typical click        -> sub-millisecond

Detail query with the index dropped:
  Rows read: 40,000,000 full scan       -> ~14 seconds
```

| Detail predicate | Rows read | Ratio vs indexed |
|------------------|-----------|------------------|
| `order_id = :id` | 8 | 1× |
| `order_id = NVL(:id, 0)` | 8 | 1× (still sargable) |
| `TO_CHAR(order_id) = :id` | 40,000,000 | 5,000,000× |
| `order_id IN (SELECT ...)` unindexed | depends | order-dependent |

**`NVL` on the bind is fine; a function on the *column* is fatal.** The distinction
is which side of the predicate the function is applied to.

## 6. Bind Variables and Plan Stability

Dynamic Actions fire on every change, so the detail query runs hundreds of times
per session. Literal substitution is the specific danger:

```sql
-- NEVER — one hard parse per distinct order_id
WHERE order_id = 8412

-- ALWAYS — one hard parse, N soft parses
WHERE order_id = :P1_ORDER_ID
```

```
100 distinct order_ids per session (Dynamic Action fired 100 times):

Literal SQL:  100 hard parses  × ~1.8 ms  = 180 ms
Bind SQL:       1 hard parse   × ~1.8 ms  =   1.8 ms
               100 soft parses × ~0.02 ms =   2.0 ms
                                                    --------
Bind total:                                          3.8 ms

Saving: 176 ms per session, plus shared- and child-cursor memory.
```

```
Shared pool per distinct statement:  ~2-6 KB
Literal variant per distinct value:  2-6 KB, never aged out under load
10,000 distinct order_ids browsed:   10,000 × 4 KB ≈ 40 MB of unreusable cursor
```

```
Bind variables cap shared-pool growth:
  MAX(shared pool) ≈ (number of distinct statements) × cursor size
  With binds:      ≈ 3 statements × 4 KB = 12 KB
```

## 7. Collection vs Re-Query — Deciding by Arithmetic

```
Option A: master rows in a collection, detail filtered in PL/SQL
  Populate collection: 1 query, 200 rows, 15 ms
  Per click: PL/SQL scan of 200 elements: ~0.05 ms
  100 clicks: 15 + 5 = 20 ms total

Option B: session-state ID, detail re-queried from the database
  Per click: 1 indexed query, ~8 rows, 0.4 ms + parse 0.1 ms
  100 clicks: ~50 ms total
```

| Clicks/session | Collection | Re-query | Winner |
|----------------|-----------|----------|--------|
| 10 | 15.5 ms | 5 ms | Re-query |
| 100 | 20 ms | 50 ms | Collection |
| 500 | 40 ms | 250 ms | Collection |

```
Break-even ≈ 40-60 clicks per session.
Below that, the collection is pure overhead.
```

## 8. Dynamic Action Execution Cost

Every Dynamic Action is a server round trip unless it is pure JS:

```
Event: Change on P1_ORDER_ID

  Server-side DA (Execute JavaScript → server call):  ~60-120 ms round trip
  Pure JS DA (set value, show/hide):                 ~0 ms server cost
  Refresh region DA:                                 triggers the 66 ms of §1
```

```
Page with 6 DAs, 3 of them server-side:
  Render:              ~446 ms
  Per interaction: 3 × 90 ms = 270 ms of round trips
  10 interactions: 2,700 ms of waiting

Replace server-side with declarative (Fire on Page Load, DA condition, or JS):
  10 interactions: ~660 ms  (just the refreshes)
```

**Every DA with a server-side action is a hidden network hop.** Declare the logic
in the page where it can be declarative, not in a process.

## 9. Da Refresh vs Full Page Load

```
Full page submit:  ~446 ms render + ~120 ms browser nav + ~180 ms DOM rebuild
                  ≈ 750 ms

AJAX refresh:      ~66 ms SQL + ~90 ms round trip + ~25 ms DOM patch
                  ≈ 180 ms

Ratio: 750 / 180 ≈ 4.2×
```

At 100 master-row clicks per user per day and 400 users:

```
Full page:  400 × 100 × 750 ms = 30,000 s of wait/day
AJAX:       400 × 100 × 180 ms =  7,200 s of wait/day
Saving:     22,800 s/day ≈ 6.3 hours of aggregate user waiting
```

## 10. Multi-Level Master-Detail Cost

Three levels deep (customer → order → line):

```
Queries per deepest click:
  Level 1 refresh:  master query + COUNT          =  23 ms
  Level 2 refresh:  middle query + COUNT          =  37 ms
  Level 3 refresh:  detail query + COUNT          =  37 ms
  SQL:                                            =  97 ms

Fire on Page Load on all three:                   =  97 ms on every page render
Fire only on the deepest level:                   =  23 ms until the user drills
```

**`Fire on Page Load` is the single most common multi-level performance defect.**
It converts a lazy query into an eager one on every page render.

## 11. Virtual Columns — Computation Per Row

```
Virtual column: order_total = SUM(line_amount) over lines

Per-row cost when the expression references other columns only:
  ~0.001 ms/row  (in-memory arithmetic)

Per-row cost when the expression runs a SQL function against the database:
  ~1.5 ms/row   (implicit query per row)

25 rows on screen:
  Arithmetic virtual column:   0.025 ms
  SQL virtual column:         37.5 ms
```

```
Never put a database function in a virtual column on a detail region.
Aggregate in the source query, or in a collection built once.
```

## 12. Session Timeout Math for Interactive Drill-Down

```
Session timeout:              120 minutes
Average drill-down session:   35 minutes
Sessions abandoned mid-flow:  15%  (user walks away from a report)
```

```
Users/day:                     1,200
Sessions started:              1,200 × 2.4 = 2,880
Abandoned sessions:            2,880 × 0.15 = 432
Wasted session slots:          432 × 120 min = 51,840 min
Useful work:                   2,448 × 35 min  = 85,680 min

Overhead ratio: 51,840 / (51,840 + 85,680) = 37.7%
```

```
Reduce timeout to 45 minutes:
  Wasted: 432 × 45 = 19,440 min
  Overhead: 19,440 / (19,440 + 85,680) = 18.5%

But 45 min breaks the legitimate 60-min analysis session.
Correct answer: 120 min for the app, 30 min for an "idle" screen,
implemented with an Idle Timeout Dynamic Action that warns at 25 minutes.
```

## 13. Combined Master-Detail Budget

| Item | Cost | Notes |
|------|------|-------|
| Page render (2 regions + LOVs) | 66 ms SQL | ~446 ms total |
| Per-click detail refresh | 97 ms | 4.2× cheaper than navigation |
| Per-interaction DA overhead | 270 ms | 3 server-side actions |
| Session state (ID only) | ~20 bytes | vs 280 KB with collections |
| Deepest click (3 levels) | 97 ms SQL | only if lazy |

```
Interactions per session:      40
Total SQL:                     66 + 40 × 90 = 3,666 ms
Total DA round trips:          40 × 270 = 10,800 ms   ← dominant cost

Fix the DAs first. The SQL is already fine.
```

**Every number here is a diagnostic, not a target.** If a page misses its SLA,
the answer is almost always in the row counts and the DA configuration, not in a
missing index.
