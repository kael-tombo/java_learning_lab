# Lab 06: Customization (OAF) — Math Foundation

## 1. Performance Budget for the Approval Page

Approvers are paid professionals waiting on a decision. Target:

```
Target page response: < 3 seconds p95
Target approval action: < 2 seconds
```

### Component budget

| Component | Budget | Notes |
|-----------|--------|-------|
| VO queries (4 layers) | 800 ms | Bind variables, indexed |
| Image thumbnail | 200 ms | ~30 KB, cached |
| Page rendering | 700 ms | Regions, items |
| Framework overhead | 600 ms | OA stack, security context |
| Network + client | 700 ms | WAN to 3 regions |
| **Total** | **3,000 ms** | p95 |

**Design against the budget, not against hope.** If four VO queries alone will
exceed 800 ms, the design is wrong regardless of how clean the code looks.

## 2. Layering Saves Queries

Flat design (no layering):

```
SupplierVO:    1 query
HeaderVO:      1 query + 1 supplier query  ← re-fetched
LineVO:        1 query + 1 header query + 1 supplier query  ← re-fetched
```

For an invoice with 20 lines:

```
Flat:      1 + 20×2 = 41 queries
Layered:   4 queries (executed once, inherited by children)
Reduction: 10.25×
```

At 20 ms per query against the database (including round-trip):

```
Flat:      41 × 20 ms = 820 ms
Layered:    4 × 20 ms =  80 ms
Saving:                     740 ms of the 3,000 ms budget (25%)
```

A quarter of the page budget saved by structure rather than tuning. **Layering is
a performance technique, not only a design preference.**

## 3. Hard Parse Cost — Why Bind Variables Are Mandatory

Oracle distinguishes:

```
Soft parse:  statement text identical, shareable cursor reused
Hard parse:  new statement → full parse, new child cursor
```

A literal in the VO SQL generates a **different statement text per invoice**:

```sql
-- invoice 1: SELECT ... WHERE invoice_id = 12345
-- invoice 2: SELECT ... WHERE invoice_id = 12346
```

These are not the same statement. Each needs its own hard parse.

### Shared pool impact

```
Per request with literals: 1 new hard parse
Approvers per day:         200
Working days:              250
Annual hard parses:        200 × 250 = 50,000
```

Each hard parse also consumes **library cache latch** — shared by every session
on the instance. At sufficient volume it degrades unrelated workloads.

### CPU cost per parse

| Operation | CPU (approx) |
|-----------|--------------|
| Hard parse | 0.3 – 1.5 ms |
| Soft parse | 0.01 – 0.05 ms |

```
Literal: 200 req/day × 250 days × 1.0 ms = 50 seconds CPU/year
Bind:    200 req/day × 250 days × 0.03 ms = 1.5 seconds CPU/year
Savings: ~48 seconds CPU/year from bind variables alone
```

Modest in absolute CPU. **The real risk is library cache latch contention**,
which is exponential, not linear — a handful of high-traffic VOs with literals
can throttle the whole instance.

## 4. Image Size — The Dominating Cost

Scanned invoice at typical resolutions:

| Scan setting | Dimensions | Grayscale size | Colour size |
|--------------|-----------|----------------|-------------|
| 150 DPI | 1240×1754 | ~2 MB | ~6 MB |
| 300 DPI | 2480×3508 | ~8 MB | ~26 MB |
| 600 DPI | 4960×7016 | ~30 MB | ~120 MB |

**300 DPI grayscale = 8 MB.** This dominates everything else in the page.

### Concurrent memory load

```
20 approvers viewing simultaneously × 8 MB = 160 MB
Rendered in the app tier JVM heap
```

Default OAF JVM heap is often 512 MB–1 GB. A few concurrent full-image renders
cause heap pressure or `OutOfMemoryError`.

### Thumbnail strategy

```
Thumbnail (200 px wide):     ~30 KB
Full image:                   ~8 MB
Ratio:                        267×
```

For an approval list showing 25 invoices:

```
Thumbnails: 25 × 30 KB = 750 KB      ← acceptable
Full images: 25 × 8 MB = 200 MB     ← not acceptable
```

**Design implication**: list views get thumbnails; full resolution loads only
when an approver opens one invoice. That single decision removes 99.6% of the
image payload.

## 5. Render Time Math

```
Time = Size / Throughput

Thumbnail:  30 KB  /  5 MB/s  = 6 ms
Full:       8 MB   /  5 MB/s  = 1,600 ms
```

**A full-resolution image alone consumes over half the entire 3,000 ms budget.**
On a 2 Mbps WAN link:

```
8 MB / 250 KB/s = 32 seconds
```

The page is unusable. No amount of server-side tuning fixes a 32-second
transfer — the constraint is the client's bandwidth, and the only answer is to
send less data.

## 6. Approval Throughput and Concurrency

```
Approvals per day:        800
Average per approver:     800 / 200 = 4 invoices/day
Time per approval:        90 seconds (read, decide, act)
Concurrent approvers:     200 × (90s / 3600s) = 5 average concurrent
Peak (2× average):        10 concurrent
```

Peak concurrent of 10, all viewing images:

```
10 × 8 MB (full) = 80 MB  in-flight
10 × 30 KB (thumbnails) = 300 KB in-flight
```

**Peak concurrency is low enough that thumbnails plus caching handle it
comfortably.** Full images would still work at 10 concurrent but leave no margin
for a month-end spike.

## 7. Structured Reason Codes — Analysis Value

Free-text rejection reasons produce:

```
Rejected:  150 invoices
Extractable themes: 0
Action:  none possible
```

Structured codes produce:

| Reason | Count | % | Action |
|--------|-------|---|--------|
| `PRICE_VAR` | 94 | 63% | Renegotiate contracts; tighten PO pricing |
| `DUPLICATE` | 31 | 21% | Add duplicate-detection heuristic |
| `QTY_VAR` | 18 | 12% | Fix receipt process |
| `INVALID` | 7 | 4% | Training |

**63% concentration identifies the highest-value process improvement.** That is
the entire return on structured coding — it converts rejections from a data-entry
artifact into a diagnostic.

## 8. Audit Log Volume

```
800 approvals/day × 250 days = 200,000 rows/year
Plus VIEW events: 200 approvers × 15 views/day × 250 = 750,000
Total: ~950,000 rows/year
```

At ~200 bytes/row: **190 MB/year**. Manageable, but:

```
If VIEW events are logged:  4× the volume
```

**Decision**: log APPROVE/REJECT/RETURN (the auditable decisions) but consider
whether VIEW events meet a stated retention requirement. Logging everything
"because it might be needed" produces log tables nobody queries.

```
Retention: 7 years → 200,000 decision rows × 7 = 1.4M rows, ~280 MB. Fine.
```

## 9. Function Security Risk

Suppose the page is granted to a read-only responsibility without per-function
security:

```
Users granted page access:  200
Of those, should be able to approve:  40
Should NOT (read-only):                 160

Without per-function checks:
  Accounts able to approve:  200  (not 40)
  Over-privileged:           160

Expected control failure rate: 160/200 = 80%
```

With function security and the controller check:

```
Accounts able to approve:  40
Over-privileged:            0
```

**80% over-provisioning is not a near-miss; it is a failed control.** Per-function
security with an authorization check in the controller is the control that makes
the page deployable to a mixed audience.

## 10. Concurrency Conflict Rate

Two approvers on the same invoice:

```
Invoices per day:               800
Approvers per invoice:         ~1.4 (escalation chains)
P(two approvers active simultaneously) ≈ 0.02
Conflicts per day:              800 × 0.02 = 16
Conflicts per year:             16 × 250 = 4,000
```

**4,000 annual conflicts is not a rare edge case — it is a routine event.**

Without a re-check, each conflict produces one approval that overwrites the
other. At a healthcare client, a silently overwritten approval on a rejected
claim is a compliance issue, not a bug.

```
With the re-check: 4,000 conflicts → 4,000 clean "already actioned" messages
Without it:        4,000 conflicts → ~4,000 silent overwrites
```

## 11. Development vs Maintenance Cost

| Approach | Build | Upgrade (per patch) | Total over 5 years |
|----------|-------|--------------------|--------------------|
| Extension | 40 hrs | 1 hr × 4 patches = 4 hrs | 44 hrs |
| Customisation | 30 hrs | 15 hrs × 4 patches = 60 hrs | 90 hrs |

```
Extension advantage:  46 hours over 5 years  (~1.5 extra build weeks)
```

The customisation is **faster to build and slower to own**. This inversion is the
reason extension-first discipline exists — the build saving is real but it is the
smallest term in the total.

```
Rule: extension adds ~10 build hours and removes ~56 maintenance hours.
      Even a 50% probability estimate makes extension correct.
```