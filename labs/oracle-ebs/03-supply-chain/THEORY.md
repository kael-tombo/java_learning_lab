# THEORY — Min-Max Planning & Reorder Point

## 1. Why ABC-FSN, not one dimension

Value (ABC) tells you *what hurts when it stocks out*; velocity (FSN)
tells you *what moves*. An A-N item (expensive, dead) needs disposal
review, not safety stock; a C-F item (cheap, fast) needs never to stock
out because the holding cost is trivial. The walkthrough's two-pass
classifier (total value first, then cumulative 70/90 cutoffs; active-days
75%/25%) encodes exactly this matrix, and storing it on item attributes
makes every downstream program class-aware for free.

## 2. The three formulas (and what each term defends against)

- **Safety stock**: `SS = Z·√(LT·σd² + d²·σLT²)`. First term: demand
  wobble over lead time. Second term: lead-time wobble scaled by demand.
  Most teams compute only the first — and the walkthrough's pitfall #1
  says 80% of stockouts come from the second (lead-time variability).
- **Reorder point**: `ROP = d·LT + SS`. Expected demand during lead time,
  plus the buffer. Order when position hits ROP — not when the shelf is
  empty.
- **Min/Max**: `Min = ROP`, `Max = Min + max(EOQ, coverage·d)` where
  `EOQ = √(2DS/H)`. Min is the trigger; Max bounds the order-up-to level
  so batching never explodes (max ≤ ~2× min per the pitfalls).

## 3. Service levels are exponential in cost

A:98% (z=2.05), B:95% (z=1.64), C:90% (z=1.28). Because SS scales with Z,
uniform 98% costs ~40% more inventory than tiered levels at equal
availability. The `calculate_all_items` loop hard-codes this tiering
(plus 15/30/45 coverage days) — policy as code, not tribal knowledge.

## 4. Net requirements + priority = the daily runbook

`Net = Max − (on-hand + open PO + open req)`; recommend only when
position < Min; round up to MOQ; tier CRITICAL (below SS) → LOW. The
health view then compresses everything into six states with a
`DENSE_RANK` triage order, so the planner's morning starts at rank 0
(STOCKOUT), not at 100,000 rows.
