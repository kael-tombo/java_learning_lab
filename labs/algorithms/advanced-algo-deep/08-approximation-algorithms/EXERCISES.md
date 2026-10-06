# Exercises — Approximation Algorithms

Attempt each before reading the hint.

## Ex 1
Give the approximation ratio of greedy set cover and what ALG is bounded by.

<details><summary>Hint</summary>

ALG ≤ H_n·OPT = Θ(log n)·OPT.

</details>

## Ex 2
Why does the maximal-matching vertex cover give a 2-approximation?

<details><summary>Hint</summary>

Every matching edge needs a distinct vertex in the cover, so |M| ≤ OPT; output 2|M|.

</details>

## Ex 3
Sketch the metric TSP 2-approximation.

<details><summary>Hint</summary>

MST → double edges → Euler tour → shortcut; ALG ≤ 2·MST ≤ 2·OPT.

</details>

## Ex 4
Give the knapsack counter-example to value/weight greedy.

<details><summary>Hint</summary>

(w,v)=(1,1),(W,W), capacity W: greedy takes the first, loses a factor W.

</details>

## Ex 5
What is the runtime of the knapsack FPTAS?

<details><summary>Hint</summary>

Θ(n²/ε) after value scaling.

</details>

## Ex 6
Why does metric TSP shortcutting never increase cost?

<details><summary>Hint</summary>

The triangle inequality lets you skip repeated vertices without increasing the path.

</details>

## Ex 7
What is the difference between a PTAS and an FPTAS?

<details><summary>Hint</summary>

PTAS: runtime polynomial in input but possibly exponential in 1/ε; FPTAS: polynomial in both.

</details>
