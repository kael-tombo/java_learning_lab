# Lab 03: Supply Chain (Min-Max & Reorder Point) — Mini Project

## Goal
Build a demand-driven replenishment model for 100 SKUs across 3 warehouses in
90 minutes, and produce the net requirements report.

## Requirements
- R1: Tables for items, demand history, on-hand, on-order, and supplier
      lead-time parameters.
- R2: An ABC classification query based on annual dollar usage.
- R3: An FSN classification query based on movement frequency.
- R4: Demand statistics — mean, standard deviation, and lead-time demand.
- R5: Safety stock at a chosen service level, with the formula documented.
- R6: Reorder point and min/max parameters per item and warehouse.
- R7: A netting query producing net requirements (on-hand, on-order,
      reservations subtracted from demand).
- R8: A health dashboard with fill rate, inventory value, and turns.

## Steps
1. Create the schema and load 12 months of demand history for 100 SKUs.
2. Load on-hand, on-order, and reservation data.
3. Run ABC classification; confirm roughly 20% of SKUs carry ~80% of value.
4. Run FSN classification and review the slow-mover population.
5. Compute mean and standard deviation of demand per item.
6. Calculate lead-time demand and safety stock at 95% service.
7. Derive reorder point and min/max; sanity-check an A item by hand.
8. Run netting and produce the recommended purchase quantities.
9. Build the dashboard and check fill rate against the 98% target.

## Acceptance criteria
- ABC/FSN classifications are reproducible from a single query each.
- Safety stock uses a stated service level and a stated lead time.
- Reorder point for one A item is verified by manual calculation.
- Net requirements never recommend ordering when on-hand plus on-order covers
  demand, and the report explains why for at least one line.

## Stretch
- Model a late supplier and show the effect on the recommended order.
- Add seasonality (monthly factors) and quantify the improvement.