# Lab 04: Supply Chain (Cycle Counting) — Mini Project

## Goal
Design a complete cycle counting programme for a 500-SKU, 2-warehouse operation
in 90 minutes, with schedules, tolerances, and root-cause coding.

## Requirements
- R1: ABC classification query with cumulative value percentage.
- R2: Movement analysis identifying items ABC alone would under-protect.
- R3: A derived count interval for the highest-value item, with arithmetic shown.
- R4: A count schedule with rotating subinventory, counter, and time.
- R5: Tolerance configuration with percentage and value cap per class.
- R6: A variance view computing variance %, value, and approval path.
- R7: A mandatory root-cause code table that cannot be closed without one.
- R8: An accuracy-by-class trend query and a cause Pareto query.

## Steps
1. Load 12 months of transaction and cost data for 500 SKUs.
2. Run the ABC query; confirm the 80/20 concentration.
3. Overlay transaction counts; identify high-movement, mid-value items.
4. Derive the count interval for the top A item from materiality.
5. Build the rotation schedule across 2 warehouses and 4 weeks.
6. Define tolerances: A/B/C with both percentage and value caps.
7. Create count records with deliberate variances; compute approval paths.
8. Attempt to close a discrepancy with no cause code; capture the error.
9. Run the accuracy trend and the cause Pareto.

## Acceptance criteria
- ABC cumulative percentage matches the expected ~80/20 shape.
- At least two items are identified that pure ABC would under-protect.
- The derived interval shows its arithmetic, not just the answer.
- Approval escalates on value cap even when percentage is within tolerance.
- A discrepancy cannot be closed without a root cause code.

## Stretch
- Compute the expected annual loss without the programme and with it.
- Build a cause Pareto and state which cause counting alone cannot fix.