# MATH_FOUNDATION — DP Basics (Fib / Stairs)
> Recurrences, Master theorem, amortized analysis for introductory DP.

## 1. Recurrences (tailored)
- Naive: `T(n)=T(n-1)+T(n-2)+Θ(1)` → `Θ(φⁿ)`, `φ=(1+√5)/2` (Fib tree size).
- Memo/tab: `n+1` states × `Θ(1)` → `Θ(n)` time; space `Θ(n)` → `Θ(1)` (order-2).
- Countdown `T(n-1)+1` → `Θ(n)` (contrast helper).
- Merge `2T(n/2)+n` → `Θ(n log n)` (contrast; recognition drill).
- Matrix/fast-doubling: `T(n)=T(n/2)+Θ(1)` mults → `Θ(log n)` (with big-int cost caveat).

## 2. Master Theorem
- Fib naive NOT Master (two different sizes, minus form) — tree/substitution instead.
- Fast-doubling/halving forms ARE Master: `T(n/2)+O(1)` → case 2 → `Θ(log n)`.
- Merge/binary contrasts for classification fluency.
- Case table + regularity (brief, same as D&C).
- Trap: calling memo `O(n)` "by Master" — correct tool is state counting.

## 3. Tree + Induction Proofs
- Naive lower: leaves `≥ F(n)` → exponential; upper via `≤2ⁿ`.
- Memo correctness induction: bases + deps-final → `n` final.
- Closed Binet (float) vs integer DP (exact) — error analysis note.

## 4. Amortized Analysis
- Memo aggregate: each state transitions once → `Θ(n)` total (charge per state).
- Potential `Φ` = uncomputed states; fill drops `Φ` by 1 at `O(1)`.
- Table doubling (if growing `dp`): `O(1)` amortized append (same proof as vector).
- Recursion overhead: `n` frames × `O(1)` = `Θ(n)` time/space; iterative removes space.

## 5. Overflow / Mod Math
- Growth `φⁿ/√5`; bits `Θ(n)`; big-int mult cost `M(n)` → naive DP bit-cost `ΣM(k)`.
- Mod `1e9+7` keeps `O(1)` word ops; apply per addition (distributive law).

## 6. Worked Numbers
- `F(50)≈12.5B` naive calls vs 51 memo states.
- Two-var tab: 2 words vs table `n+1` words.
- `n=10⁶` tab mod: 10⁶ adds (~ms); naive impossible.

## 7. Exercises
- [ ] Prove `T=Ω(φⁿ)` by induction.
- [ ] State-count → `Θ(n)` formalization.
- [ ] Master-classify halving vs minus forms.
- [ ] Bit-cost sum with big-int (stretch).
