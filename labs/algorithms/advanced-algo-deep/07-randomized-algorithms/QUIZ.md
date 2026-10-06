# Quiz — Randomized Algorithms

15 questions. Each key gives the reason.

---

## Q1
Expected comparisons of randomised quicksort?

<details><summary>Answer</summary>

Θ(n log n).

</details>

## Q2
Why are the worst cases of quicksort no longer adversary-controllable?

<details><summary>Answer</summary>

The pivots are random, so the Θ(n²) path has probability 2^{-Θ(n)} regardless of input.

</details>

## Q3
Difference between Monte Carlo and Las Vegas?

<details><summary>Answer</summary>

LV: always correct, expected time. MC: bounded time, correct with high probability.

</details>

## Q4
Expected time of randomised selection?

<details><summary>Answer</summary>

Θ(n).

</details>

## Q5
Error of k-round Miller–Rabin?

<details><summary>Answer</summary>

≤ 4⁻ᵏ (Monte Carlo).

</details>

## Q6
Reservoir sampling inclusion probability for the i-th item, i > k?

<details><summary>Answer</summary>

k/i.

</details>

## Q7
Why is reservoir sampling one pass?

<details><summary>Answer</summary>

It only needs the i-th item once and a k-sized reservoir.

</details>

## Q8
Expected lookup time in a randomised hash table?

<details><summary>Answer</summary>

Θ(1) when the load factor is Θ(1).

</details>

## Q9
What does Freivalds' algorithm check?

<details><summary>Answer</summary>

Whether A·B = C for n×n matrices, in Θ(n²) instead of Θ(n³) — Monte Carlo.

</details>

## Q10
How to boost a Monte Carlo algorithm?

<details><summary>Answer</summary>

Repeat independently: k rounds multiply the success probabilities.

</details>

## Q11
Why do LV algorithms still have a bad worst case?

<details><summary>Answer</summary>

The worst case still exists; it just becomes improbable rather than eliminated.

</details>

## Q12
What makes randomised selection Las Vegas?

<details><summary>Answer</summary>

It always returns the correct k-th smallest; only the number of steps varies.

</details>

## Q13
What does a random hash function prevent?

<details><summary>Answer</summary>

The adversary from constructing a worst-case key set for the particular hash.

</details>

## Q14
Quickselect recurrence in expectation?

<details><summary>Answer</summary>

E[T(n)] ≤ E[T(3n/4)] + Θ(n) = Θ(n).

</details>

## Q15
Why is E[T] for quicksort not Θ(n²)?

<details><summary>Answer</summary>

The Θ(n²) pivot path has probability 2^{-Θ(n)}; the dominant paths are balanced.

</details>
