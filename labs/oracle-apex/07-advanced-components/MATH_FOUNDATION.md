# Lab 07: APEX Advanced Components — Math Foundation

## 1. IG vs IR — Where the Boundary Sits

Decision is the editing question alone.

| Scenario | Component | Why |
|----------|-----------|-----|
| Monthly sales review with filters | IR | No edits |
| Ad-hoc report the user customises | IR | Column config, no DML |
| Order line entry spreadsheet | **IG** | 12 rows entered per order |
| Bulk price update of 5,000 items | **IG** | Editing |
| Drill-down detail view | IR or master-detail IR | Read-only |
| Exception triage with inline status change | **IG** | Editing |

**Getting this wrong is costly in both directions:**

```
IG used for read-only:  extra configuration, larger payload, no benefit
IR used for editing:    impossible — IR has no editing model
```

## 2. The Save Contract — Payload Size

50 changed cells across 20 rows.

```
JSON payload per changed row (typical):
  Record id, changed column values only
  Rough estimate: ~300-600 bytes per row

20 rows × 500 bytes = ~10 KB
50 rows × 500 bytes = ~25 KB
500 rows × 500 bytes = ~250 KB
```

| Rows changed | Payload | Notes |
|--------------|---------|-------|
| 20 | 10 KB | Typical order |
| 50 | 25 KB | Large order |
| 500 | 250 KB | Still fine |
| 5,000 | 2.5 MB | One enormous DML |

**2.5 MB in a single request is a timeout waiting to happen**, before the DML
cost. Guarding the row count is a correctness control, not a performance one.

## 3. DML Cost at Save

```
One set-based statement applying 50 rows:  ~5 ms
One MERGE per row in a PL/SQL loop (50):   ~90 ms   (18x slower)

5,000 rows:
  Set-based:              ~400 ms
  Row-by-row:             ~9,000 ms (9 s)  plus lock duration
```

APEX's IG save is set-based by design. **The performance risk is not the save — it
is a user accumulating thousands of edits** because nothing told them they were
accumulating them.

## 4. Validation Cost and Feedback Timing

| Rule type | Where it runs | Fires | Feedback delay |
|-----------|--------------|-------|-----------------|
| Cell validation | Browser + DB on check | During editing | Immediate |
| Row validation | Database | On Save | Seconds later |
| DB constraint | Database | On Save | Same as row validation |

### Why cell-level is preferred where possible

```
User makes an error, continues editing 30 more cells, then presses Save.
Cell validation:     error at the moment of entry, context intact
Row validation:      error after all 30 cells, user must find the cause
```

**Time-to-correction:** cell validation resolves in ~3 seconds; row validation
takes ~40 seconds because the user must re-read the message and locate which of 30
cells caused it.

This is why rule placement is a usability decision, not just a technical one.

## 5. Computed Column — Storing vs Recalculating

```
Line total stored:
  quantity = 10, unit_price = 25.00, discount = 10%
  line_total correctly = 225.00

  User changes quantity to 12.
  If line_total is stored and nothing updates it: line_total still 225.00
  Truth: 12 × 25 × 0.9 = 270.00
  Discrepancy: 45.00 on one line
```

### Discrepancy rate over time

```
Lines per month:           50,000
Lines edited after entry:  15%  = 7,500/month
Reconciled nightly by a job (if one exists):  removes the error within a day
Without a reconciliation job: errors persist until someone reports them
```

**A stored computed column requires a reconciliation process that nobody will
remember to build.** Recalculating removes the entire failure mode:

```
Recalculated:  discrepancy rate = 0 by construction
```

## 6. Per-User State Growth

```
State per user per IG:        ~5 KB (columns, widths, order, visibility, sort, filters)
Users:                        1,200
IGs per user:                 7

Total state rows:             1,200 × 7 = 8,400
Total size:                   8,400 × 5 KB = 42 MB
```

### Growth over time without tidying

```
New users per quarter:               200
New IGs per user per quarter:        1

Rows added per quarter:              200 × 1 = 200
Annual:                              800 rows = 4 MB/year
```

```
4 MB/year is not a crisis. The crisis is 8,400 rows scanned on every
region-cache invalidation and no way for a user to recover from a bad layout.
```

**The reset action matters more than the tidying job.** A user whose columns are
invisible cannot fix it themselves, and the alternative is a support ticket.

## 7. Saved Filters — The Same Problem, Smaller

```
Saved filters per user per IG:   up to 10 (APEX default cap)
Users × IGs:                     1,200 × 7 × up to 10 = 84,000 filter definitions
Average size:                     ~1 KB
Total:                            ~84 MB
```

Set the cap to 5. It is above what users actually keep and below what creates a
search problem for support.

## 8. Chart Readability — The 52-Point Threshold

| Points | Render time | Reader can distinguish? |
|--------|-------------|------------------------|
| 6 | 40 ms | Yes |
| 12 | 60 ms | Yes |
| 52 | 180 ms | Marginal — weeks in a year |
| 200 | 900 ms | No |
| 400 | 1,800 ms | No, and visibly slow |

### What a 400-point chart actually communicates

```
400 daily points on a monthly view:
  Each point is ~0.09 px wide on a 1,200 px chart
  The chart is a solid block

Correct rendering of the same data as a monthly aggregate: 30 points
```

**Aggregation is a design decision.** A chart that needs aggregation to be legible
should not have been built on daily data.

## 9. Region Count on an Analytics Page

```
8 Interactive Reports + 3 charts + 2 grids = 13 regions
Queries per render: 13

If 4 reports read overlapping data:
  Collection shared: 13 → 10 queries
```

| Regions | SQL time | Total load |
|---------|----------|------------|
| 5 | 300 ms | ~700 ms |
| 13 | 800 ms | ~1,200 ms |
| 25 | 1,500 ms | ~1,900 ms |

**Framework overhead dominates until ~2 regions.** An analytics page with 13
regions is past that, so region count is a real lever here — unlike a typical
business page.

## 10. Master-Detail Interaction Cost

```
Without master-detail (join everything):
  Detail query for a selected order requires a page submit and full re-render
  1 query joining orders + lines + items + UOMs

With master-detail grids:
  Master query: 1 (order summary, aggregated)
  On selection:  1 detail query via AJAX
  No page re-render, no process execution
```

```
Per selection:
  Submit approach:     full page ~900 ms
  AJAX detail:         ~180 ms
  Improvement:         5x
```

The gain is both speed and context: scroll position and the user's other filters
survive.

## 11. Plugin Economics

```
Writing a plugin:                          ~2 days (packaging, testing, install)
Cost versus a shared Dynamic Action:       ~+1.5 days
Cost versus copying framework code:        ~+0.5 days

Use count threshold:                       3 pages or more
```

| Reuse | Recommendation | Total cost |
|-------|---------------|------------|
| 1 page | Shared component or Dynamic Action | 0.5 day |
| 2 pages | Shared component, reconsider | 1 day |
| **3+ pages** | **Plugin** | **2 days** |
| 3 pages, copied framework code | Maintenance: 0.5 day per APEX upgrade, forever | unbounded |

```
3 pages × 2 days plugin = 6 days
3 pages × 1 day copy    = 3 days + 0.5 day per upgrade × N upgrades

Break-even: N ≈ 6 upgrades
```

After six APEX upgrades, the plugin has paid for itself. **The threshold of three
is conservative and correct.**

## 12. Full Before/After: Order Entry

| Metric | Per-line Forms-style approach | Single IG |
|--------|------------------------------|-----------|
| Page loads per order (12 lines) | 12 | 1 |
| Round trips per order | 12+ | 1 |
| Time per order (12 lines) | ~4 min | ~50 s |
| Validation feedback | On submit | Immediate for cell rules |
| Order total visible while entering | No | Yes |
| Discrepancies from computed-column drift | ~15% of edited lines | 0 |
| Errors per 1,000 orders (baseline 15%) | 150 | ~12 |

```
Order entry time: 4 min → 50 s  = 4.8x
Order errors:      15% → 1%      = 15x fewer
```

**The 15× error reduction is the number that matters.** It comes from the editing
model making errors visible while they are still being made.