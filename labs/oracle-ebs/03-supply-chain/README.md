# 03 — Supply Chain (Min-Max Planning & Reorder Point)

## Overview

Demand-driven replenishment for 100,000 SKUs × 12 warehouses ($500M):
ABC-FSN classification → demand statistics → lead-time parameters →
safety stock + reorder point + min/max → net-requirements recommendations
→ health dashboard. Goal: −20% inventory ($100M), 98% A-item fill rate.

## Learning Objectives

- [ ] Classify SKUs by ABC (cumulative usage value) + FSN (movement velocity)
- [ ] Derive SS = Z·√(LT·σd² + d²·σLT²), ROP = d·LT + SS, Min/Max + EOQ
- [ ] Generate net-requirements recommendations with MOQ rounding + priority tiers
- [ ] Read the health dashboard (STOCKOUT → HEALTHY) and set class-tiered service levels

## Topics Covered

### 1. ABC-FSN classification (`xx_inv_classification_pkg`)
Cumulative-value ABC (70/90 cutoffs) + active-days FSN (75%/25%);
stored on item attributes; quarterly recalculation. Walkthrough Step 1.

### 2. Demand + lead-time statistics (`xx_demand_calc_pkg`, `xx_leadtime_calc_pkg`)
Monthly demand mean/stddev/CV over 12 months; PO-history lead-time
mean/stddev with setup-time fallback (±30% assumed variability).
Walkthrough Steps 2–3.

### 3. SS/ROP/min-max/EOQ (`xx_reorder_calc_pkg`)
z-factor table; full-variability SS; ROP; EOQ = √(2DS/H); Min=ROP,
Max=Min+max(EOQ, coverage·d); class-tiered service/coverage
(A:98%/15d, B:95%/30d, C:90%/45d). Walkthrough Step 4.

### 4. Recommendations + dashboard (`xx_generate_replenishment`, health view)
Net = Max − (on-hand + open PO + open req); MOQ ceiling; CRITICAL→LOW
priority; six-state health + `DENSE_RANK` triage order. Walkthrough
Steps 5–6, `WORKED_SQL_EXAMPLE.sql`.

## Prerequisites

- EBS INV/PO schemas (`MTL_*`, `PO_*`, `CST_ITEM_COSTS`); PL/SQL packages, MERGE
- Statistics: mean, sample stddev, normal z-values, EOQ model

## Further Reading

- Oracle Inventory Planning Guide (min-max vs ROP vs MRP)
- `../02-financials/` for the  same package/MERGE/period-close discipline in finance
