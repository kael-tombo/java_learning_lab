# Lab 03: Supply Chain (Min-Max & Reorder Point) — Vision

## Where this lab takes you
From annual shutdown inventory counts to demand-driven replenishment across
100,000 SKUs and 12 warehouses, cutting $100M of working capital.

## The Arc
1. **Classify** — ABC by annual dollar usage, FSN by movement frequency.
2. **Observe** — demand statistics that reflect real consumption, not guesswork.
3. **Protect** — safety stock from lead-time variability.
4. **Trigger** — reorder point and min/max as complementary policies.
5. **Net** — MRP netting against on-hand, on-order, and reservations.
6. **Recommend** — net requirements the buyer can act on.
7. **Measure** — a health dashboard that shows fill rate and inventory value.

## Milestones (checkable)
- [ ] M1: Run an ABC-FSN classification over 100,000 SKUs and defend the cutoffs.
- [ ] M2: Compute lead-time demand and its variability from demand history.
- [ ] M3: Calculate safety stock at a stated service level.
- [ ] M4: Derive reorder point and min/max for an A item and a C item.
- [ ] M5: Run MRP netting and explain each planned order quantity.
- [ ] M6: Show why on-order quantities reduce but never reverse the ROP.
- [ ] M7: Produce a replenishment health dashboard with fill rate and turns.
- [ ] M8: Justify a 20% inventory reduction on the numbers.

## Anti-Goals
- Setting min/max once at implementation and never revisiting it.
- Using a single lead time for all items regardless of variability.
- Counting on-order stock at face value when the supplier is late.
- Optimising inventory value at the expense of A-item fill rate.

## The one-sentence thesis
Reorder point is a probability statement, not a number someone typed — change
the service level and the policy should change with it.