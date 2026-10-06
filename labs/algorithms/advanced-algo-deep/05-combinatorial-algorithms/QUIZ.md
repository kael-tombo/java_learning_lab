# Quiz — Combinatorial Algorithms

15 questions. Each key gives the reason.

---

## Q1
State Pascal's rule and its proof idea.

<details><summary>Answer</summary>

C(n,k)=C(n-1,k-1)+C(n-1,k); a k-subset either contains a fixed element or not.

</details>

## Q2
Why prefer Pascal over n!/(k!(n-k)!) in integer code?

<details><summary>Answer</summary>

Pascal only adds, so no division ordering issues and no intermediate overflow from factorials.

</details>

## Q3
Give three objects counted by the Catalan numbers.

<details><summary>Answer</summary>

Valid parenthesis strings, binary trees with n internal nodes, non-crossing matchings.

</details>

## Q4
State the Catalan recurrence and its interpretation.

<details><summary>Answer</summary>

C_{n+1}=Σ_{i=0}^{n} C_i C_{n-i}; split at the matching close of the first paren.

</details>

## Q5
Why is C(n,k) computed in Θ(n·k)?

<details><summary>Answer</summary>

The Pascal table has (n+1)(k+1) cells, each O(1).

</details>

## Q6
What is the inclusion–exclusion count of derangements?

<details><summary>Answer</summary>

D_n = n! Σ_{k=0}^{n} (-1)^k/k!; tends to n!/e.

</details>

## Q7
State the Stirling number S(n,k) recurrence.

<details><summary>Answer</summary>

S(n,k) = k·S(n-1,k) + S(n-1,k-1).

</details>

## Q8
How are onto maps counted by S(n,k)?

<details><summary>Answer</summary>

Onto maps = k!·S(n,k), since blocks are labelled.

</details>

## Q9
Why is meet-in-the-middle a time-space trade?

<details><summary>Answer</summary>

It cuts time from Θ(2^n) to Θ(2^{n/2}) but stores Θ(2^{n/2}) partial results.

</details>

## Q10
Total submask enumerations over all k-bit masks?

<details><summary>Answer</summary>

Θ(3^k).

</details>

## Q11
What does C(n,k) count?

<details><summary>Answer</summary>

k-element subsets of an n-element set.

</details>

## Q12
How to avoid factorial overflow for C(n,k)?

<details><summary>Answer</summary>

Use Pascal's recurrence or multiply-divide with gcd reduction.

</details>

## Q13
What is c(n,k) (Stirling first kind)?

<details><summary>Answer</summary>

Permutations of n elements with exactly k cycles.

</details>

## Q14
Why is inclusion–exclusion exponential in the number of properties?

<details><summary>Answer</summary>

It sums over all 2^k subsets of properties.

</details>

## Q15
What is the border... no — what is the closed form of C_n?

<details><summary>Answer</summary>

C_n = (1/(n+1))·C(2n,n).

</details>
