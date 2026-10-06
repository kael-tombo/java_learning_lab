# Lab 07: Reporting (BI Publisher) — Real World Project

## Scenario
A manufacturing client's CFO wants an AP Aging report showing aging buckets by
supplier category (Raw Materials, MRO, Services, Utilities) with drill-down from
category to supplier to invoice detail. The standard Oracle AP Aging report
supports neither categorisation nor drill-down. The AP population spans 14
currencies totalling $500M, 3.7% of which sits with suppliers that have never
been categorised, and the treasury team maintains exchange rates with gaps. The
report must be delivered as an EBS concurrent program and burst to category
managers monthly.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Financials)
- https://docs.oracle.com/en/cloud/saas/financials/25d/faipp/
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Concurrent program: XX_AP_AGING_RPT (BIPUBLISHER)
   │  params: pAsOfDate, pCategory, pBurst
   ▼
BI Publisher data model (3 levels)
   │
   ├─ View: xx_ap_aging_base
   │     ap_payment_schedules (DUE DATE basis)
   │       + gl_daily_rates   (spot as-at-date, type C, NULL on missing)
   │       + xx_supplier_category (LEFT JOIN → COALESCE 'UNMAPPED')
   │
   ├─ Level 1  category   → SUM in SQL
   ├─ Level 2  supplier   → passes [vendor_id]
   └─ Level 3  invoice    → detail
   │
   ▼
RTF layout (severity colour scale, hyperlinked drill-down)
   │
   ├──► PDF  ──► Bursting ──► CFO (total) + category managers (per category)
   │
   └──► Partition test: Σbuckets == Σtotal   (automated)
        Missing-rate exception report ──► Treasury
```

## Implementation sketch
```sql
-- Aging basis and currency: three correctness properties
SELECT ps.due_date,                                    -- NOT invoice date
       r.conversion_rate,
       CASE WHEN i.invoice_currency_code = 'USD' THEN ps.amount
            WHEN r.conversion_rate IS NULL      THEN NULL  -- NEVER 1.0
            ELSE ps.amount * r.conversion_rate END AS amount_base_usd
  FROM ap_payment_schedules ps
  LEFT JOIN gl_daily_rates r
         ON r.set_of_books_id = i.set_of_books_id
        AND r.currency_code   = i.invoice_currency_code
        AND r.rate_type       = 'C'
        AND r.rate_date       = (SELECT MAX(r2.rate_date) FROM gl_daily_rates r2
                                   WHERE r2.set_of_books_id = r.set_of_books_id
                                     AND r2.currency_code   = r.currency_code
                                     AND r2.rate_type       = 'C'
                                     AND r2.rate_date <= :p_as_of_date);

-- The check that must pass every time
SELECT SUM(bucket_sum) - SUM(overall_total) AS difference,
       CASE WHEN SUM(bucket_sum) - SUM(overall_total) = 0
            THEN 'RECONCILES' ELSE 'BOUNDARY DEFECT' END AS status
  FROM (...);
```

## Requirements
- F1: Aging on due date basis, stated in the report header.
- F2: Five mutually exclusive, exhaustive buckets verified by partition test.
- F3: As-at-date parameter producing reproducible output.
- F4: Multi-currency conversion using spot closing rate as at the aging date.
- F5: Missing-rate exception report routed to treasury.
- F6: Supplier category mapping with a visible `UNMAPPED` bucket.
- F7: Three-level drill-down passing stable identifiers.
- F8: Severity colour scale in the RTF layout.
- F9: Configuration-driven bursting with a category filter guard.
- F10: Concurrent program registration with parameters.
- NF1: Report reconciles to the AP subledger balance exactly.
- NF2: Zero rows affected by overlapping bucket boundaries.
- NF3: Runtime under 5 seconds at production volume.
- NF4: Security baseline — bursting recipients restricted to configured roles.
- NF5: Exchange rate gaps surfaced, never silently defaulted.
- NF6: Documented rollback for every report and configuration change.

## Milestones
- Week 1: Semantics confirmed with finance; as-at date and rate basis agreed.
- Week 2: Aging base view built and index-supported.
- Week 3: Three-level data model and partition test implemented.
- Week 4: RTF layout with drill-down links and colour scale.
- Week 5: Category mapping backfill; unmapped bucket reviewed.
- Week 6: Bursting configured; deployed and validated with finance.

## Verification
- Reconcile report total against the AP subledger balance.
- Fault injection: delete an exchange rate; confirm it appears in exceptions.
- Delete a category mapping; confirm `UNMAPPED` appears rather than a shortfall.
- Re-run with the same as-at date twice; confirm identical output.
- Test at production volume (250,000 open invoices).

## Rollback
The report is additive — existing AP Aging reports remain until cutover. The
aging base view can be dropped; program registration is reversible by
responsibility. Document rollback steps for every change.