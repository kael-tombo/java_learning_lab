# MATH_FOUNDATION — Two Pointers Technique
> Recurrences / Master theorem / amortized. Lab `17-two-pointers`.

## 1. Why math matters here
- Two Pointers Technique claims O(n) time after sort, O(1) extra space — this file proves it.
- Tools: recurrences, Master/Akra-Bazzi, potential method, probability.

## 2. Recurrence setup
- Divide-and-conquer shape: T(n) = a·T(n/b) + f(n), T(1)=Theta(1).
- DP shape: T(n) = sum of subproblem costs + transition cost.
- Example: for Two Pointers Technique, instantiate a,b,f from loop/recursion structure.
- Unrolling: draw recursion tree, sum per level.

## 3. Master theorem (statement + use)
- Case 1: f(n)=O(n^{log_b a - ε}) → T(n)=Theta(n^{log_b a}).
- Case 2: f(n)=Theta(n^{log_b a} log^k n) → T(n)=Theta(n^{log_b a} log^{k+1} n).
- Case 3: f(n)=Omega(n^{log_b a + ε}) + regularity → T(n)=Theta(f(n)).
- Worked: T(n)=2T(n/2)+O(n) → Case 2 → Theta(n log n).
- Worked: T(n)=T(n-1)+O(1) → Theta(n) by unrolling.
- Gap: floors/ceilings ignored asymptotically; Akra-Bazzi for uneven splits.

## 4. Substitution method template
- Guess O(g(n)); prove by induction with constants c,n0.
- Show upper and lower separately; pick c large / small.
- Example induction for linear recurrences in Two Pointers Technique.

## 5. DP counting argument
- #states × transition cost = total time.
- For left/right move by predicate; monotonicity of feasibility: count states, bound transitions, multiply.
- Space = #states kept simultaneously (rolling optimization).
- Typical: O(n) time after sort, O(1) extra space derived by this product.

## 6. Amortized analysis (3 methods)
- Aggregate: total over sequence ÷ n. Example: dynamic array push.
- Accounting: charge extra on cheap ops; spend on expensive ones.
- Potential: Φ(D0)=0, Φ>=0; amortized a_i = c_i + Φ_i − Φ_{i-1}.
- Apply to Two Pointers Technique: each index pushed/popped ≤ once → O(n) total.

## 7. Probabilistic analysis (for randomized variants)
- Linearity of expectation; indicator variables.
- Expected QuickSort-style: E[T]=O(n log n) via comparison indicators.
- High-probability via Chernoff; amplification by repetition.
- Hash collision probability ≤ 1/M per pair (union bound).

## 8. Lower bounds
- Comparison lower bound Omega(n log n) for sorting-based steps.
- Information-theoretic: log2(#outputs) bits needed.
- Adversary argument for search/matching lower bounds.

## 9. Worked proofs (3)
- Proof A: closed form of linear recurrence by induction (6 lines).
- Proof B: Master Case 2 on balanced split (8 lines).
- Proof C: amortized O(1) for pointer/window moves via potential Φ = window size (8 lines).

## 10. Exercises with solutions
1. Solve T(n)=3T(n/2)+O(n). → Theta(n^{log2 3}). [Solution sketch included]
2. Solve T(n)=T(n/2)+O(1). → Theta(log n).
3. Prove sieve bound O(n log log n) via harmonic-over-primes sum.
4. Show two-pointer scan is O(n) amortized (each pointer moves ≤ n).
5. Amplify Monte Carlo error from 1/3 to <10^-6: repetitions needed? → ~30 (Chernoff/majority).

## 11. Pitfalls
- Dropping floors/mods changes constants, not asymptotics — but breaks code.
- Confusing expected vs worst-case guarantees.
- Forgetting regularity condition in Case 3.

## 12. Checklist
- [ ] Can state Master cases cold. [ ] Can do potential-method sketch. [ ] Can derive O(n) time after sort, O(1) extra space.
