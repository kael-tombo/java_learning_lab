# EXERCISES — Supply Chain

## 1. Classify a toy universe (beginner)
10 items with given annual values + active days. Hand-compute ABC (70/90
cumulative) and FSN (75%/25%). Then run `classify_all_items` on matching
test rows and compare. *Reflection: which item changes class if the A
cutoff moves 70→80, and what does that cost?*

## 2. CV triage (beginner)
Compute CV for three demand histories (steady, seasonal, lumpy). Above
what CV does the walkthrough suggest abandoning safety-stock planning?
Justify from the SS formula's normality assumption.

## 3. SS sensitivity (intermediate)
Fix d=100/d, σd=20, LT=10 d. Vary σLT ∈ {0, 2, 5} at 95% service. Tabulate
SS. Confirm the lead-time term dominates past σLT≈3 — the quantified form
of pitfall #1.

## 4. MOQ inflation audit (intermediate)
Take 5 C-items with computed EOQ vs supplier MOQ (MOQ = 3× EOQ). Run
`xx_generate_replenishment` and measure order inflation vs net
requirements. Draft the MOQ-renegotiation memo for the worst offender
(walkthrough pitfall #5).

## 5. Peak-season override (advanced)
Implement seasonal coverage multipliers (2× coverage days for flagged
seasonal SKUs in peak months) inside `calculate_all_items`, plus a
`seasonal_flag` on the params table. Re-run for a December peak org and
verify Max levels move while Min/ROP stay put. Defend the choice in a
one-page note.
