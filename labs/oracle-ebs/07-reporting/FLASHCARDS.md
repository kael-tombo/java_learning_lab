# Lab 07: Reporting (BI Publisher) — Flashcards

## Aging Semantics

---
**Q**: Aging basis for a payables report?
**A**: Payment **due date**. Invoice-date aging counts not-yet-due invoices as overdue.

---
**Q**: Bucket definition?
**A**: Current (≤0) · 0-30 (1..30) · 31-60 (31..60) · 61-90 (61..90) · 90+ (>90).

---
**Q**: `BETWEEN 0 AND 30` + `BETWEEN 30 AND 60`?
**A**: Day 30 double-counted. Due dates cluster on payment terms, so this is material.

---
**Q**: How do you prove buckets are right?
**A**: Partition test — Σbuckets == Σtotal. Zero difference required, in an automated test.

---
**Q**: Aging date as a parameter?
**A**: Yes. Period-end aging must be reproducible; `SYSDATE` makes a signed-off report move on re-run.

---
**Q**: Which table for due date?
**A**: `AP_PAYMENT_SCHEDULES`.

---

## Currency

---
**Q**: Rate type and date resolution?
**A**: `rate_type = 'C'`, resolved as `MAX(rate_date) <= :as_of_date`.

---
**Q**: Missing rate?
**A**: Return NULL and report it. **Never** `NVL(rate, 1)`.

---
**Q**: Magnitude of the 1.0 default bug?
**A**: ¥12M reported as $12M instead of $85K — $11.9M overstatement, silently.

---
**Q**: Reproducible conversion requires?
**A**: Consistent rate type and date resolution. Same as-at date → identical output always.

---

## Mapping and Drill-Down

---
**Q**: Unmapped supplier categories?
**A**: `LEFT JOIN` + `COALESCE(...,'UNMAPPED')`. `INNER JOIN` understates by 3.7% with no error.

---
**Q**: Why does `INNER JOIN` matter so much?
**A**: $18.4M missing means the report never reconciles to the ledger and nobody can explain the difference.

---
**Q**: Pass what between drill levels?
**A**: Stable IDs (`vendor_id`), never names. A rename silently breaks links.

---
**Q**: Three levels?
**A**: Category (SUM in SQL) → Supplier (returns `vendor_id`) → Invoice detail.

---

## Performance

---
**Q**: Aggregate where?
**A**: In SQL. Shipping 250,000 rows to sum 4 in RTF is a 4,000× waste.

---
**Q**: Cost of template aggregation?
**A**: 33 min CPU/month aggregated vs 5.6 hours unaggregated.

---
**Q**: `TRUNC(due_date) <= :d`?
**A**: Disables the index — 4M rows/4.5 s vs 250K rows/0.3 s. Use `due_date < :d + 1`.

---
**Q**: Filter where?
**A**: In SQL. Post-filtering in the layout processes every row and discards most.

---

## Layout and Delivery

---
**Q**: Conditional formatting purpose?
**A**: Encode severity as a colour ramp so the conclusion lands in the first glance.
Cuts "what needs attention?" from ~15 s to ~2 s.

---
**Q**: Report header must state?
**A**: As-at date, aging basis (due date), rate basis (spot, type C), currency.

---
**Q**: Bursting recipients from where?
**A**: A configuration table (`XX_CATEGORY_MANAGER`), never a hardcoded list.

---
**Q**: Bursting guard?
**A**: Refuse when category is NULL — otherwise all 200 managers get 40,000 rows.

---
**Q**: Registration type?
**A**: `BIPUBLISHER` executable with parameters for as-of date, category, burst.

---

## Quick Reference

| Task | Object |
|------|--------|
| Due date | `AP_PAYMENT_SCHEDULES.due_date` |
| Invoice header | `AP_INVOICES_ALL` |
| Vendor site | `AP_VENDOR_SITES_ALL` |
| Exchange rates | `GL_DAILY_RATES` (`rate_type='C'`) |
| Supplier name | `PO_VENDORS_ALL` |
| Category mapping | `XX_SUPPLIER_CATEGORY` (custom) |
| Recipients | `XX_CATEGORY_MANAGER` (custom) |
| Request history | `FND_CONCURRENT_REQUESTS` |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| AP population | $500M, 14 currencies |
| Unmapped suppliers | 130 (7%), $18.4M (3.7%) |
| Detail rows vs aggregated | 250,000 → 4 |
| Row reduction from SQL aggregation | ~4,000× |
| Template CPU, unaggregated | 5.6 hrs/month |
| `TRUNC()` vs range predicate | 4.5 s vs 0.3 s |
| Scanning time saved by colour | ~2.2 hrs/month |

---

## Report Health Checks

1. **Partition test**: Σbuckets == Σtotal → must be zero difference.
2. **Reconciliation**: report total == AP subledger open balance.
3. **Missing rates**: exception query returns zero rows.
4. **Unmapped**: `UNMAPPED` bucket reviewed each period.
5. **Runtime**: under 5 s; a rising trend means the view needs refreshing.

---

## Anti-Patterns

1. Invoice-date aging on a payables report.
2. `0-30` and `30-60` boundary overlap.
3. `SYSDATE` hardcoded.
4. `NVL(rate, 1)`.
5. `INNER JOIN` to the category mapping.
6. `TRUNC(column)` in a filter.
7. Aggregating in the template.
8. Names in drill-down links.
9. Bursting with no category guard.

---

## Study Tips
1. Compute the same three invoices on both aging bases out loud.
2. Explain why the partition test must be automated.
3. State the 1.0 conversion failure and its magnitude.
4. Give the SQL fix for a `TRUNC()` filter.