# CODE_DEEP_DIVE — Supply-chain walkthrough code

All references are to `PROBLEM_WALKTHROUGH.md` in this lab.

## 1. ABC-FSN classifier (Step 1, lines 35–186)

- **Two-pass design**: pass 1 totals usage value; pass 2 walks the
  value-ordered cursor accumulating `l_cum_value`. Cutoffs on the
  *cumulative share* (≤70% → A, ≤90% → B, else C) — not on item counts.
  A zero-total org defaults everything to C (division guard).
- **FSN** on `active_days / 365` (≥75% F, ≥25% S, else N). Movement and
  value are independent axes — read both attributes before judging an SKU.
- **Persistence**: `UPDATE mtl_system_items_b` attributes 1–4
  (ABC/FSN/value/date) + `PIPE ROW` streaming — same pipelined pattern as
  the financials recon package. `classify_all_items` just drains the
  pipeline (processing happens inside).

## 2. Demand stats (Step 2, lines 193–313)

- Monthly buckets (`YYYY-MM`) over trailing 12 months, issues only
  (`transaction_action_id IN (1,2,3)`); sample stddev (`/(n−1)`) and
  **coefficient of variation** `CV = σ/μ` — CV > 1.0 flags items where
  safety-stock logic may be the wrong tool (pitfall: consider MTO).
- `MERGE INTO xx_inv_demand_params` (upsert by item+org) — re-runnable
  monthly without duplicate rows.

## 3. Lead-time stats (Step 3, lines 318–406)

- PO-history `AVG/STDDEV/MAX/COUNT` over 6 months, approved POs only.
  **Zero-history fallback**: setup lead-time sum + assumed 30% stddev —
  new items still get planned instead of crashing the SS formula.
- Same MERGE-upsert shape into `xx_inv_leadtime_params`.

## 4. SS/ROP/min-max (Step 4, lines 415–696)

- `get_z_factor`: stepped lookup (2.05/1.64/1.28 at 98/95/90) — no
  runtime normal-CDF needed.
- `calculate_safety_stock`: full two-variability form with `NO_DATA_FOUND`
  defaults (14 d / 4.2 d); `calculate_reorder_point`: `d·LT + SS`;
  `calculate_min_max`: EOQ with zero-cost guard (falls back to 30-day
  coverage), `Max = ROP + GREATEST(EOQ, coverage·d)`; writes both the item
  master (`min/max_minmax_quantity`, `fixed_order_quantity`) and the
  params table in one `MERGE`.
- `calculate_all_items`: class→(service, coverage) tiering switch —
  the policy table in executable form.

## 5. Recommendations + dashboard (Steps 5–6, lines 701–859)

- Cursor pre-computes on-hand, open-PO (unreceived, `OPEN`/`N`), open-req
  (approved, not cancelled) per item; `DELETE` prior recommendations
  first (regeneration, not accumulation); `CEIL(net/MOQ)*MOQ` rounding;
  priority `CASE` on position vs SS/ROP fractions.
- Dashboard: six-state `CASE` + `DENSE_RANK` triage; `NULLIF(ROP,1)`
  guards division; `onhand/ROP` ratio as the at-a-glance position metric.
