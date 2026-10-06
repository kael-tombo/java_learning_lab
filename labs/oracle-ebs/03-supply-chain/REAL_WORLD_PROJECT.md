# Lab 03: Supply Chain (Min-Max & Reorder Point) — Real World Project

## Scenario
A chemical manufacturer holds $500M of inventory across 100,000 SKUs and 12
warehouses. The only physical count is an annual plant shutdown, which reveals
$2M of shrinkage, 80% of it concentrated in 20% of SKUs. A-item fill rate sits
at 91% against a 98% target. You must build a replenishment discipline that
cuts inventory by $100M without losing a single point of fill rate.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/sc/24b/ocins/ (Supply Chain docs)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Inventory)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Demand history ─► ABC / FSN classification
        │
        ▼
Demand statistics ─► Safety stock (service level)
        │                     │
        ├──────► Reorder point / Min-Max
        │                     │
On-hand ─┤                     │
On-order ┼──► MRP netting ──► Net requirements ─► Buyer review
Reservations ┘                                          │
        │                                                ▼
        └──────────► Inventory health dashboard (fill rate, value, turns)
```

## Implementation sketch
```sql
-- Safety stock and reorder point at a 95% service level
WITH d AS (
  SELECT item_id,
         AVG(qty) avg_daily,
         STDDEV(qty) sd_daily
    FROM demand_history
   WHERE request_date >= SYSDATE - 365
   GROUP BY item_id)
SELECT i.item_id, p.lead_time_days,
       ROUND(Z_SERVICE * d.sd_daily * SQRT(p.lead_time_days)) safety_stock,
       ROUND(d.avg_daily * p.lead_time_days
           + Z_SERVICE * d.sd_daily * SQRT(p.lead_time_days)) reorder_point
  FROM d JOIN item i ON i.item_id = d.item_id
  JOIN supplier_lead_time p ON p.item_id = d.item_id;
```

## Requirements
- F1: ABC-FSN classification over 100,000 SKUs with defensible cutoffs.
- F2: Rolling demand statistics that reflect seasonality, not a flat average.
- F3: Safety stock model parameterised by service level per ABC class.
- F4: Reorder point and min/max parameters maintained per item and warehouse.
- F5: MRP netting accounting for on-hand, on-order, and reservations.
- F6: Late-supplier handling so unreliable lead times raise safety stock.
- F7: Replenishment health dashboard: fill rate, inventory value, turns,
      stockout count.
- F8: Cycle-count programme replacing the annual shutdown count for A items.
- F9: Shrinkage root-cause coding feeding back into ABC policy.
- F10: Buyer-facing exception report (only actionable lines surfaced).
- NF1: Inventory value reduced by $100M with A-item fill rate at or above 98%.
- NF2: Annual shutdown count window reduced or eliminated.
- NF3: Recommendation freshness — parameters recomputed on a stated cadence.
- NF4: Security baseline — buyer roles separated from parameter maintenance.
- NF5: Audit trail for every parameter change with approver.
- NF6: RPO/RTO and a documented restore drill for the inventory database.

## Milestones
- Week 1: Baseline — inventory value, fill rate, stockout history, ABC extract.
- Week 2: Classification and demand statistics model built and validated.
- Week 3: Safety stock and ROP parameters set per ABC class.
- Week 4: MRP netting and exception reporting in production.
- Week 5: Cycle-count programme live for A items with shrinkage coding.
- Week 6: Dashboard deployed; target reduction evidenced on a full quarter.

## Verification
- Backtest the policy against 12 months of history and compare fill rate and
  average on-hand against the current min/max baseline.
- Fault injection: late supplier, demand spike, missing on-order data.
- Restore drill verifying parameters and history survive recovery.
- Warehouse sign-off that recommendations are actionable without rework.

## Rollback
Replenishment parameters are versioned by effective date and can be reinstated;
netting changes are report-only until switched to advisory. Document rollback
steps for every parameter change.