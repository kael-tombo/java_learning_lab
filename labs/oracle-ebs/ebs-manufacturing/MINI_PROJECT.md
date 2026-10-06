# EBS Manufacturing — Mini Project

## Goal
Take one product from BOM definition through planning, execution, and
traceability in 90 minutes.

## Requirements
- R1: A 3-level BOM and a 4-operation routing with setup and run times.
- R2: Work centres with calendar, capacity, and resource limits.
- R3: MPS/MRP run producing a planned order with a stated justification.
- R4: A released WIP job with material issues and completions recorded.
- R5: One repetitive job run with backflush and yield accounted.
- R6: Lot genealogy traced from raw material lot to finished good lot.
- R7: An ECO/ECN effect with an effective date and revision impact.
- R8: A quality inspection whose result is visible in the genealogy view.

## Steps
1. Define items, BOM levels, and the routing; validate with a costing run.
2. Create work centres and assign the routing operations to them.
3. Load demand and run MPS, then MRP; record the planned order quantity.
4. Release the planned order and record the resulting WIP job.
5. Issue components and complete the job; confirm the on-hand balances moved.
6. Run a repetitive job with backflush enabled and check the yield figure.
7. Receive raw material with lot tracking; produce and complete the finished lot.
8. Query the genealogy and prove the link from raw lot to finished lot.
9. Effect an ECO and show which prior and future orders use which revision.

## Acceptance criteria
- The routing drives a realistic completion time from the work-centre calendar.
- Backflush produces a yield figure you can explain.
- The genealogy query returns the full chain from raw lot to finished lot.
- The ECO shows a clear before/after revision effect on open orders.

## Stretch
- Load one work centre beyond capacity and show the schedule slippage.
- Add a quality failure and trace the impacted lots forward.