# Lab 04: Supply Chain (Cycle Counting) — Real World Project

## Scenario
A chemical manufacturer holds 50,000 SKUs across 3 warehouses. The only physical
count is an annual plant shutdown, which revealed a $2M discrepancy between
system and actual quantities. Analysis shows 80% of that discrepancy comes from
20% of SKUs — high-value, fast-moving raw materials. The warehouse has no
mobile scanning capability, so counts are manual and error-prone. The VP of
Supply Chain wants cycle counting that prevents recurrence without hiring.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/sc/24b/ocins/ (Supply Chain)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Inventory)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
Transaction history ─► ABC classification (+ movement overlay)
                              │
                              ▼
              Count frequency derivation (materiality math)
                              │
                              ▼
              Count schedule: subinventory × counter × time
                              │
                              ▼
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
   Handheld scan                        Manual count fallback
   (barcode → item)                     (paper sheet → entry)
          └───────────────────┬───────────────────┘
                              ▼
                    Variance computation
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        Tolerance check              Root cause coding
        (% + value cap)              (MANDATORY)
                 │                         │
                 └────────────┬────────────┘
                              ▼
              Approval routing ─► Process fix ─► Accuracy trend
```

## Implementation sketch
```sql
-- Bounded loss: this is the business case, not cost savings
-- Expected annual loss WITHOUT cycle counting
SELECT ROUND(0.02 * SUM(mt.primary_quantity * mta.actual_cost_per_unit), 0)
         AS annual_exposure_without_programme
  FROM mtl_transaction_history mt
  JOIN mtl_transaction_account mta ON mta.transaction_id = mt.transaction_id
 WHERE mt.transaction_date >= ADD_MONTHS(TRUNC(SYSDATE), -12);

-- Cause Pareto: tells you where counting stops and fixing starts
SELECT root_cause_code, COUNT(*) discrepancies, SUM(variance_value) total_value,
       ROUND(100 * SUM(variance_value)
             / SUM(SUM(variance_value)) OVER (), 1) cum_pct_value
  FROM xx_count_discrepancy
 WHERE coded_at >= ADD_MONTHS(TRUNC(SYSDATE), -3)
 GROUP BY root_cause_code ORDER BY total_value DESC;
```

## Requirements
- F1: ABC classification over 50,000 SKUs with movement as a second dimension.
- F2: Count frequency derived from materiality arithmetic, per value band.
- F3: Count schedule across 3 warehouses with rotation of location, counter,
      and time of day.
- F4: Tolerance configuration with percentage *and* absolute value caps.
- F5: Handheld barcode scanner deployment via `INV_MATERIAL_STATUS_API`,
      with a manual fallback path.
- F6: Mandatory root-cause coding enforced at the database level.
- F7: Cause Pareto analysis identifying the dominant loss mechanism.
- F8: Approval workflow routing escalations by value and ABC class.
- F9: Accuracy dashboard trended monthly by ABC class against targets.
- F10: Programme health check flagging stale counts and uncoded discrepancies.
- NF1: Discrepancy reduced below 20% of the $2M baseline.
- NF2: A-item inventory accuracy at or above 98%.
- NF3: Annual shutdown count window eliminated or substantially reduced.
- NF4: Scanner investment justified on accuracy first, labour second.
- NF5: Security baseline — shrinkage causes routed to security, not counted away.
- NF6: RPO/RTO with a documented restore drill and inventory reconciliation.

## Milestones
- Week 1: Baseline — discrepancy history, ABC, movement analysis.
- Week 2: Classification, frequency derivation, and schedule agreed.
- Week 3: Scanner deployment and capture path integration.
- Week 4: Tolerance and approval workflow configured.
- Week 5: Root-cause coding live; cause Pareto reviewed with operations.
- Week 6: Accuracy dashboard and programme health check operational.

## Verification
- Backtest: apply the schedule retrospectively and measure loss exposure.
- Fault injection: unknown barcode, duplicate scan, missing count.
- Accuracy trend must improve; if it does not, the cause coding is not working.
- Restore drill with full inventory reconciliation after recovery.

## Rollback
Schedules and tolerances are configuration; root-cause codes are additive;
scanner deployment is parallel to the manual path until cutover. Document
rollback steps for every change.