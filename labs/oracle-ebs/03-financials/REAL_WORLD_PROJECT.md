# Lab 03: Financials — Real World Project

## Scenario
A manufacturing company implementing EBS Financials finds 30% of supplier
invoices landing on Payables Invoice Holds during UAT. The AP manager cannot
explain them to suppliers and is losing goodwill with vendors who wait weeks for
payment. Root causes are a price variance tolerance set to 0% and a receipt
matching rule comparing invoiced delivered quantity against ordered quantity.
Meanwhile SOX requires that every hold be individually justified, so simply
releasing them is not an option. You own the fix.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Payables)
- https://docs.oracle.com/en/cloud/saas/financials/25d/faipp/
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
PO ──► Receipt ──► Invoice ──► Validation (matching + tolerances)
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
                 VALIDATED                 HOLD (AP_HOLDS_ALL)
                     │                           │
                     ▼                           ▼
              Approval workflow          Hold taxonomy + value at risk
                                             │
                    ┌────────────────────────┴──────────┐
                    ▼                                   ▼
           Batch release program            Workflow notification
           (reason coded, audited)           to AP + buyer
```

## Implementation sketch
```sql
-- Hold taxonomy: what is actually holding invoices?
SELECT h.hold_type, hr.hold_reason, COUNT(DISTINCT h.invoice_id) inv_count,
       SUM(i.invoice_amount) held_value
  FROM ap_holds_all h
  JOIN ap_hold_codes hr ON hr.hold_type = h.hold_type
                        AND hr.hold_code = h.hold_code
  JOIN ap_invoices_all i ON i.invoice_id = h.invoice_id
 WHERE h.release_flag = 'N'
 GROUP BY h.hold_type, hr.hold_reason
 ORDER BY held_value DESC;

-- Price variance distribution: choose the tolerance from data, not guesses
SELECT ROUND(((i.invoice_amount - r.receipt_amount)
              / NULLIF(r.receipt_amount,0)) * 100, 2) pct_variance,
       COUNT(*) inv_count
  FROM ap_invoices_all i
  JOIN ap_invoice_distributions_all id ON id.invoice_id = i.invoice_id
  JOIN ap_receipt_lines_all r ON r.receipt_line_id = id.receipt_line_id
 WHERE r.receipt_amount > 0
 GROUP BY ROUND(((i.invoice_amount - r.receipt_amount)
                 / NULLIF(r.receipt_amount,0)) * 100, 2)
 ORDER BY ABS(pct_variance) DESC;
```

## Requirements
- F1: Hold taxonomy by reason, volume, and value at risk.
- F2: Matching-rule correction to received quantity with regression evidence.
- F3: Price and quantity tolerances derived from measured variance distributions.
- F4: Batch hold release program with mandatory reason codes and audit trail.
- F5: Workflow notification routing held invoices to the right AP approver.
- F6: Automated hold-release candidates report for AP Specialist review.
- F7: Hold-rate dashboard with regression alerting.
- F8: Supplier-facing aging report explaining holds to vendors.
- F9: Three-way match control preserved and evidenced after tolerance change.
- F10: UAT regression pack re-run proving no new hold categories appear.
- NF1: Hold rate reduced from 30% to under 8%.
- NF2: Zero holds released without a reason code and approver.
- NF3: SOX control over the three-way match demonstrated intact.
- NF4: Supplier payment cycle time reduced (measure and report).
- NF5: Security baseline — release restricted to authorised AP roles.
- NF6: RPO/RTO with a documented restore drill for the AP database.

## Milestones
- Week 1: Hold taxonomy built; top causes quantified.
- Week 2: Variance distributions analysed; tolerances proposed.
- Week 3: Matching rules and tolerances changed in UAT.
- Week 4: Batch release program and workflow notification implemented.
- Week 5: Regression pack re-run; SOX evidence assembled.
- Week 6: Production rollout with per-week hold rate measurement.

## Verification
- Reproduce the same invoice data before and after; hold rate must drop.
- Attempt to release a hold without a reason code; it must fail.
- Fault injection: extreme variance, missing receipt, duplicate invoice.
- Restore drill verifying holds and audit records survive recovery.

## Rollback
Matching-rule and tolerance changes are configuration with recorded prior
values; the release program is reversible by disabling its schedule; audit
records are append-only. Document rollback steps for every change.