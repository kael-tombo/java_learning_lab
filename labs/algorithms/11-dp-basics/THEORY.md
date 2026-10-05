# THEORY — DP Basics (Fib / Climbing Stairs)
> Mechanics + invariants + complexity proof sketch for introductory DP.

## 1. Problem Statement
- Exemplars: `fib(n)=fib(n-1)+fib(n-2)`, `ways(n)=ways(n-1)+ways(n-2)` with bases.
- Input `n≥0`; output exact count/value (watch overflow → `long`/mod).
- Overlapping subproblems + optimal substructure (trivial here) → DP applies.
- Success: `O(n)` time from exponential naive, `O(1)` space optimized.

## 2. Mechanics: Three Forms
- Naive recursion: direct recurrence, recomputes subtrees — `O(2ⁿ)`.
- Top-down memo: `dfs(n)` with `memo[]` (`-1`=unknown); store before return.
- Bottom-up tab: `dp[0..n]`fill in order; answer `dp[n]`; compress to two vars.
- Order matters: dependencies (`n-1,n-2`) computed before `n` (DAG order).
- Base cases: `fib(0)=0,fib(1)=1`; `ways(0)=1,ways(1)=1` — off-by-one hotspot.

## 3. Invariants
- Memo I: `memo[k]≠-1 ⇒ memo[k]=true answer(k)`; computed entries never change.
- Tab I: after iteration `i`, `dp[j]=answer(j)` ∀ `j≤i`.
- Init: bases correct. Step: recurrence combines already-final deps.
- DAG view: states `0..n`, edges `i→i+1,i+2`; topological order = increasing `i`.
- Termination: `n` bounded steps; recursion depth `n` (stack risk).

## 4. Worked Traces
- `fib(5)`: naive tree 15 nodes; memo computes 5 states once each.
- `ways(4)`: dp `1,1,2,3,5` → 5. Show table row per `i`.
- `n=0/1` bases returned directly — test both.

## 5. Complexity Proof Sketch
- Naive: `T(n)=T(n-1)+T(n-2)+O(1)` → `Ω(2^{n/2})`, `O(2ⁿ)` (fib tree size `~φⁿ`).
- Memo: each of `n+1` states computed once, `O(1)` work each → `O(n)` time, `O(n)` space + recursion.
- Tab: same `O(n)` time, `O(n)` table; two-var `O(1)` (only last two needed).
- Space lower: recurrence order-2 → `Ω(1)`; reconstruction needs full table if path required.
- Induction proof of correctness on `n` using recurrence + bases.

## 6. Correctness Argument
- Induction: bases hold; assume `<n` correct → deps correct → `n` correct.
- Memo/tab equivalence: same recurrence, different evaluation order (DFS vs BFS on DAG).
- Counter-example: wrong base (`ways(0)=0`) shifts all answers by one.

## 7. When NOT to Use
- Closed form exists (Binet/matrix `O(log n)`) and `n` huge → use fast doubling.
- No overlap (each state once anyway) → plain recursion/divide-conquer suffices.
- `n` ≤ ~25 in interview → naive may pass; DP still preferred for clarity.

## 8. Java Notes
- `long` for `fib` (int overflows at n=47); mod `1e9+7` variants need `%` per add.
- Recursive memo depth `n` → iterative for `n>~5000` (stack).
- `Arrays.fill(memo,-1)`; sentinel must not collide with valid answers.

## 9. Common Misconceptions
- "Memo and tab differ asymptotically" — both `O(n)` here; differ in constants/stack.
- "DP always needs 2-D" — dimension = state size; Fib needs 1-D/2 vars.
- "Bases don't matter" — they anchor induction; most bugs live there.

## 10. Checklist
- [ ] All three forms coded + timed.
- [ ] Bases + `n=0` tested.
- [ ] Overflow/mod policy stated.
- [ ] State-DAG order comment present.
