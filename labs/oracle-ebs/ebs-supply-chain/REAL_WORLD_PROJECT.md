# EBS Supply Chain — Real World Project

## Scenario
An industrial distributor runs EBS R12.2 with 38,000 SKUs across 9 warehouses
and 1,400 order lines a day. On-time delivery is 84%, order accuracy complaints
run at 6%, and the pricing engine produces customer disputes worth roughly
$180K a year because nobody can reconstruct which rule set a quote came from.
Seasonal peaks are unplannable and drop-ship requests are handled by hand. You
own the supply chain performance programme.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/sc/24b/ocins/ (Supply Chain docs)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Order Management)
- https://docs.oracle.com/database/121/OMPRD/ (Order Management concepts)

## Architecture
```
Requisition ─► PO ─► Receipt ─► Three-way match ─► AP
                                │
Inventory ◄── ATP (on-hand − reserved − supply) ◄── Planning
     │                                                     │
     ▼                                                     ▼
Order ─► Pricing hierarchy ─► Credit check ─► Fulfilment ─► Ship
     │                                        │
     ├─► Drop ship (no inventory touch)       └─► Configure to order (BOM)
     └─► Reservation / back-to-back supply
                                   │
                                   ▼
                 Price dispute trace + order accuracy dashboard
```

## Implementation sketch
```sql
-- ATP: on-hand less reserved, supply, and work-in-process
SELECT msi.segment1 item,
       SUM(msi.quantity_on_hand)                              on_hand,
       SUM(msi.reservation_quantity)                          reserved,
       SUM(msi.supply_quantity)                               supply,
       SUM(msi.quantity_on_hand - msi.reservation_quantity
                           - msi.supply_quantity)              available
  FROM mtl_system_items_qty msi
 WHERE msi.organization_id = 101
 GROUP BY msi.segment1
HAVING SUM(msi.quantity_on_hand - msi.reservation_quantity
           - msi.supply_quantity) < 0;

-- Pricing provenance: which hierarchy published this price
SELECT pfh.operator, pfh.list_price_type_code, pfh.adjustment_percentage
  FROM oe_price_list_headers_c plh
  JOIN oe_pricing_formulas_hd pfh ON pfh.list_header_id = plh.list_header_id
 WHERE plh.list_header_id = 1001;
```

## Requirements
- F1: ATP and available-to-promise correctness, with supply netting.
- F2: Three-way match configuration tuning to reduce price variance holds.
- F3: Pricing hierarchy redesign with full provenance for every quoted price.
- F4: Pricing dispute workflow reducing disputes to near zero.
- F5: Seasonal capacity plan across all 9 warehouses.
- F6: Drop-ship and back-to-back flow with automated supply ordering.
- F7: Configure-to-order capability for the top 200 assembled products.
- F8: Freight and tax calculation accuracy with a reconciliation to invoicing.
- F9: Order accuracy dashboard: line fill rate, backorders, OTIF, complaints.
- F10: Warehouse execution improvements tied to measured pick/pack times.
- NF1: On-time in-full delivery at or above 96%.
- NF2: Order line accuracy at or above 99%.
- NF3: Pricing disputes reduced by at least 90%.
- NF4: Peak season absorbed without overtime beyond the agreed budget.
- NF5: Security baseline — pricing maintenance separated from order entry.
- NF6: RPO/RTO with a documented restore drill and inventory reconciliation
     after recovery.

## Milestones
- Week 1: Baseline — OTIF, fill rate, complaints, dispute causes, ATP accuracy.
- Week 2: ATP and availability corrections applied; supply netting fixed.
- Week 3: Pricing hierarchy redesigned with provenance captured.
- Week 4: Three-way match tuning and drop-ship flow automation.
- Week 5: Configure-to-order for the top 200 products.
- Week 6: Dashboards and warehouse execution improvements deployed.

## Verification
- ATP backtest against actual order history for the top 1,000 items.
- Dispute trace: reconstruct 20 historical quotes exactly.
- Fault injection: stockout mid-order, supplier late, price rule conflict.
- Restore drill with a full inventory reconciliation afterwards.

## Rollback
Pricing hierarchy changes are versioned by effective date; ATP corrections are
data fixes with reversal scripts; fulfilment path changes are configuration.
Document rollback steps for every change.