# QUIZ — Supply Chain

## 1. ABC cutoffs: 70/90 of what — item counts or cumulative value?
<details><summary>Answer</summary>Cumulative annual usage value. ~20% of items typically hold 70% of value — that concentration is the whole point.</details>

## 2. A-N item (expensive, non-moving): safety-stock or disposal review?
<details><summary>Answer</summary>Disposal review. Buffering dead stock burns holding cost with no fill-rate gain; FSN exists to catch exactly this.</details>

## 3. SS formula's two terms defend against what, respectively?
<details><summary>Answer</summary>`LT·σd²`: demand wobble over lead time. `d²·σLT²`: lead-time wobble scaled by demand — the source of ~80% of stockouts.</details>

## 4. ROP in one sentence?
<details><summary>Answer</summary>Expected demand during lead time plus safety stock: order when inventory position hits it, not when the shelf empties.</details>

## 5. Min vs Max roles?
<details><summary>Answer</summary>Min (=ROP) triggers; Max (=Min+order-up-to) bounds batching. Keep Max ≤ ~2× Min or ordering collapses into max-level batches.</details>

## 6. Uniform 98% service vs tiered 98/95/90: cost delta and why?
<details><summary>Answer</summary>~40% more inventory, because SS scales with z (2.05 vs 1.64/1.28) applied to every SKU including C-items that don't need it.</details>

## 7. Why MERGE (upsert) for params tables instead of INSERT?
<details><summary>Answer</summary>Monthly recalculation must be re-runnable — MERGE updates existing rows instead of duplicating them.</details>

## 8. New item, zero PO history: what lead time does the code use?
<details><summary>Answer</summary>Setup-time sum with assumed 30% stddev — planned-but-flagged beats crashing the SS formula.</details>

## 9. Net requirements formula + MOQ handling?
<details><summary>Answer</summary>Net = Max − (on-hand + open PO + open req); recommend only if position < Min; round up via CEIL(net/MOQ)·MOQ.</details>

## 10. Dashboard rank 0 means what, and what do you do first?
<details><summary>Answer</summary>STOCKOUT (on-hand = 0). Expedite/reallocate before anything else — ranks 1–3 (below-SS, below-ROP, healthy) wait their turn.</details>
