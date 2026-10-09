# How It Works: Combinatorics Core Mechanics

## 1. Why C(n,k) = C(n−1,k−1) + C(n−1,k)

Take element xₙ from {x₁,…,xₙ}. Any k-subset either contains xₙ or doesn't:

- Contains xₙ → choose the remaining k−1 from {x₁,…,xₙ₋₁}: C(n−1,k−1) ways.
- Doesn't → choose all k from {x₁,…,xₙ₋₁}: C(n−1,k) ways.

The two cases are disjoint and cover everything, so the counts add. This is Pascal's rule, and it is also the DP recurrence for computing binomials — the table and the proof are the same object.

## 2. The Multiplicative Formula (and Why Division Is Exact)

C(n,k) = n(n−1)…(n−k+1) / k! — count ordered k-tuples (P(n,k)) then divide by the k! orderings of each subset (a k!-to-1 map because all elements are distinct). In code, `result = result * (n - k + i) / i` at step i divides by i after multiplying by (n−k+i); binomial coefficients are integers, so the product of the first i terms is divisible by i! at every prefix — no floating point, no rounding.

## 3. Inclusion–Exclusion Mechanics

For properties P₁…Pₙ, count elements with none:

N(none) = Σ_{S ⊆ [n]} (−1)^|S| · N(elements with *all* properties in S).

Each element with exactly r properties is counted Σ_{j=0..r} C(r, j)(−1)ʲ = (1−1)ʳ = 0 times if r ≥ 1, and exactly once when r = 0 — by the binomial theorem. So the alternating sum *cancels* every element you don't want and keeps exactly the ones with none. That cancellation identity is the whole proof; you can watch it with r = 2: 1 − 2 + 1 = 0.

## 4. Derangements by Recurrence

!n = (n−1)(!(n−1) + !(n−2)): element 1 goes to any of the other n−1 positions; say it takes position k. Either k's element goes to position 1 (then the remaining n−2 derange: !(n−2)) or it doesn't (then the remaining n−1 elements avoid their spots: !(n−1)). Seeds: !0 = 1, !1 = 0. Values: 1, 0, 1, 2, 9, 44, 265 — and !n = round(n!/e), which is why the probability of no fixed point tends to 1/e ≈ 0.3679.

## 5. Catalan Recurrence From First Returns

Any Dyck path of semilength n returns to height 0 for the first time after 2j steps (some j in 1..n); between those it closes a Dyck path of semilength j−1, and after it, one of semilength n−j. Hence Cₙ = Σ_{j=1..n} C_{j−1}·C_{n−j}, seeds C₀ = 1. Values: 1, 1, 2, 5, 14, 42, 132. The closed form Cₙ = C(2n,n)/(n+1) follows by solving the same recurrence with the kernel method — or by noting among the C(2n,n) monotone paths from (0,0) to (n,n), those touching the diagonal = (n+1)/(2n+1)·C(2n,n)... the reflection principle gives the count of *bad* paths = C(2n, n−1), and C(2n,n) − C(2n,n−1) = Cₙ.

## 6. The Reflection Principle (Counting Bounded Paths)

Number of paths from (0,0) to (a,b) that never touch y = x+1: total C(a+b, a) minus reflected count. Reflect the first touch across the line: the reflected paths land at (b−1, a+1), giving C(a+b, b−1) bad paths. This one geometric swap converts a "staying below a line" constraint — hard to count directly — into a subtraction of two binomials.
