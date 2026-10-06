# Exercises — Combinatorial Algorithms

Attempt each before reading the hint.

## Ex 1
Compute C(8,3) by Pascal and prove the recurrence.

<details><summary>Hint</summary>

C(8,3)=56; the recurrence partitions k-subsets by a distinguished element.

</details>

## Ex 2
Write the Catalan recurrence and compute C_4.

<details><summary>Hint</summary>

C_0=1, C_{n+1}=ΣC_iC_{n-i}; C_1=1,C_2=2,C_3=5,C_4=14.

</details>

## Ex 3
Count onto maps from a 5-set to a 3-set.

<details><summary>Hint</summary>

3!·S(5,3) = 6·25 = 150.

</details>

## Ex 4
Count derangements of 4 elements by inclusion–exclusion.

<details><summary>Hint</summary>

4!·(1 - 1 + 1/2 - 1/6 + 1/24) = 9.

</details>

## Ex 5
Why does meet-in-the-middle change Θ(2^n) to Θ(2^{n/2})?

<details><summary>Hint</summary>

Enumerate each half and combine by sort/binary-search: 2·2^{n/2} + merge.

</details>

## Ex 6
How many submasks does the mask 0b1011 have, and what is the enumeration order?

<details><summary>Hint</summary>

2³ = 8; starts at 0b1011, iterates s=(s-1)&M, ends at 0.

</details>

## Ex 7
State when inclusion–exclusion is practical.

<details><summary>Hint</summary>

When k is small (≤ ~20) and the intersection terms simplify.

</details>
