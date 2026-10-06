# Theory — Approximation Algorithms

For NP-hard optimisation problems, exact polynomial solutions are unlikely.
Approximation algorithms accept a provable gap: an α-approximation returns a
solution within a factor α of optimal, in polynomial time. The field is about
proving how small α can be — and sometimes how small it cannot.

## α-approximation

For a minimisation problem, α ≥ 1: ALG ≤ α·OPT. For maximisation, α ≤ 1:
ALG ≥ α·OPT. The smaller α-1 (minimisation) or 1-α (maximisation), the
better. A Polynomial-Time Approximation Scheme (PTAS) gets α = 1+ε for any
fixed ε > 0, with runtime depending on ε. An FPTAS is a PTAS whose runtime is
polynomial in both the input size *and* 1/ε.

## Greedy set cover, Θ(log n)

Set cover: given a universe U of n elements and a collection of sets, choose
the fewest sets covering U. Greedy picks the set covering the most uncovered
elements each step. Standard analysis: charge each element x the price 1/|S_i
\ remaining| of whatever set covers it, where S_i is the greedy pick at that
step. The total charge to OPT's k sets is at most H_n · OPT (H_n is the
harmonic number), because the k optimal sets all cover the remaining
elements, so one of them covers at least a 1/k fraction of what remains —
and greedy does at least as well. Hence ALG ≤ H_n·OPT = Θ(log n)·OPT. This is
tight in a sense: no polynomial algorithm beats (1-o(1))·ln n unless P=NP.

## Vertex cover, 2-approximation

Vertex cover: pick the fewest vertices touching every edge. Take any maximal
matching M (a set of pairwise disjoint edges). Every vertex of M's endpoints
must be in any cover, because each matching edge needs an endpoint, and the
matching edges are disjoint. Output both endpoints of every matching edge.
|ALG| = 2|M| ≤ 2·OPT (since |M| ≤ OPT). The gap is 2 — and closing it is
believed to require super-polynomial time (the Unique Games conjecture pins
the best at 2-ε being hard).

## Metric TSP, 2-approximation

Metric TSP: shortest tour on points obeying the triangle inequality. Compute
an MST, duplicate its edges, find an Eulerian circuit in the doubled tree
(cost 2·MST), and shortcut repeated vertices. By the triangle inequality,
shortcutting never increases cost. So ALG ≤ 2·MST ≤ 2·OPT (the optimal tour
minus any edge is a spanning path, hence a spanning tree, hence ≥ MST). A
tighter 1.5-approximation exists (Christofides: MST + min perfect matching on
odd-degree vertices).

## Greedy for knapsack fails; FPTAS fixes it

0/1 knapsack: maximise value subject to weight capacity. Greedy by
value/weight ratio can be arbitrarily bad — the classic counter-example is
items (weight, value) = (1,1), (W, W), capacity W: greedy takes the small
item worth 1, optimal takes the big item worth W. The fix is dynamic
programming on values, Θ(n·V) — pseudo-polynomial. To get polynomial in the
input *length*, scale the values by δ = ε·max_value/n and round; the DP then
runs in Θ(n²/ε) and guarantees value ≥ (1-ε)·OPT. That is an FPTAS: the
runtime is polynomial in n and 1/ε.

## When does an FPTAS exist?

Whenever there is a DP whose state is a *value* (like knapsack), scaling the
values yields an FPTAS. For strongly NP-hard problems (where the numbers are
bounded in unary), no FPTAS exists unless P=NP. Bin packing and TSP are the
canonical examples where only PTAS/constant-factor approximations exist.

## Hardness as a boundary

Approximation has two sides: for some problems no polynomial α < 1+ε exists
unless P=NP (e.g. 3SAT's α < something, general TSP has no constant-factor
polynomial approximation). This is why the *metric* assumption in TSP matters
— without the triangle inequality, no constant approximation exists at all.

## Pitfalls

- Treating an α-approximation as "almost optimal" — a 2-approximation can be
  a factor 2 off.
- Forgetting the *metric* hypothesis: general TSP has no constant-factor
  polynomial approximation.
- Using integer division to "round" in the knapsack FPTAS: the guarantee is
  in the *scaled* value space.
- Reporting α for a maximisation problem as ≥ 1 — for maximisation, α ≤ 1.
