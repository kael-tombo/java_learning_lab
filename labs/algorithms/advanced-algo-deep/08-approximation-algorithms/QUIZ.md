# Quiz — Approximation Algorithms

15 questions. Each key gives the reason.

---

## Q1
Define α-approximation for a minimisation problem.

<details><summary>Answer</summary>

ALG ≤ α·OPT, α ≥ 1.

</details>

## Q2
Define α-approximation for a maximisation problem.

<details><summary>Answer</summary>

ALG ≥ α·OPT, α ≤ 1.

</details>

## Q3
Approximation ratio of greedy set cover?

<details><summary>Answer</summary>

H_n = Θ(log n).

</details>

## Q4
Approximation ratio of matching-based vertex cover?

<details><summary>Answer</summary>

2.

</details>

## Q5
Approximation ratio of MST-doubling TSP?

<details><summary>Answer</summary>

2 (metric case).

</details>

## Q6
What is Christofides' ratio?

<details><summary>Answer</summary>

3/2 for metric TSP.

</details>

## Q7
Why does general TSP have no constant-factor polynomial approximation?

<details><summary>Answer</summary>

Without the triangle inequality, a bad tour can be arbitrarily worse than optimal — no constant factor is achievable in polynomial time unless P=NP.

</details>

## Q8
What is the knapsack FPTAS runtime?

<details><summary>Answer</summary>

Θ(n²/ε).

</details>

## Q9
What does the knapsack greedy fail on?

<details><summary>Answer</summary>

A tiny high-ratio item can block taking a large high-value item.

</details>

## Q10
When does an FPTAS exist?

<details><summary>Answer</summary>

When a value-DP can be scaled — i.e. when the problem is not strongly NP-hard.

</details>

## Q11
Why is exact knapsack DP pseudo-polynomial?

<details><summary>Answer</summary>

Its runtime Θ(n·W) is polynomial in the *value* W, not in the input bit-length log W.

</details>

## Q12
What does the metric hypothesis mean?

<details><summary>Answer</summary>

Edge weights satisfy the triangle inequality.

</details>

## Q13
Set cover tightness?

<details><summary>Answer</summary>

Greedy is Θ(log n)-approximate, and no polynomial algorithm does (1-o(1))·ln n better unless P=NP.

</details>

## Q14
Vertex cover gap?

<details><summary>Answer</summary>

2, via maximal matching; beating 2 is the Unique-Games-hard direction.

</details>

## Q15
What makes a problem "strongly NP-hard"?

<details><summary>Answer</summary>

NP-hard even when the numeric inputs are bounded by a polynomial in the input length (unary).

</details>
