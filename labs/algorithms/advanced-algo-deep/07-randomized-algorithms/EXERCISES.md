# Exercises — Randomized Algorithms

Attempt each before reading the hint.

## Ex 1
Give the formula for the expected number of comparisons in randomised quicksort.

<details><summary>Hint</summary>

E = Σ_{i<j} 2/(j-i+1) = Θ(n log n).

</details>

## Ex 2
Why does quickselect recurse on only one side?

<details><summary>Hint</summary>

Only that side can contain the k-th smallest element.

</details>

## Ex 3
Name a Monte Carlo and a Las Vegas algorithm.

<details><summary>Hint</summary>

Miller–Rabin (MC); randomised quicksort (LV).

</details>

## Ex 4
Reservoir sampling: what is the probability of keeping the i-th element for i > k?

<details><summary>Hint</summary>

k/i, evicting a uniform reservoir item.

</details>

## Ex 5
How do k Miller–Rabin rounds multiply their error caps?

<details><summary>Hint</summary>

Independent rounds multiply: error ≤ 4⁻ᵏ.

</details>

## Ex 6
Why does a random pivot defeat an adversary who hands you sorted input?

<details><summary>Hint</summary>

The pivot choice is independent of the input, so the bad Θ(n²) pivot sequence has probability 2^{-Θ(n)}.

</details>

## Ex 7
Expected time of randomised hash-table lookup under load factor α?

<details><summary>Hint</summary>

Θ(1+α) expected chain length.

</details>
