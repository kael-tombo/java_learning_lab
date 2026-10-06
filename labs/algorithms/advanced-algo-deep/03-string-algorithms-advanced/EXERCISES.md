# Exercises — String Algorithms Advanced

Attempt each before reading the hint.

## Ex 1
Build the π table for pattern "ababaca".

<details><summary>Hint</summary>

π = [0,0,1,2,3,0,1].

</details>

## Ex 2
Give a text and pattern where naive matching is Θ(n·m).

<details><summary>Hint</summary>

t = "aaaa…a", p = "aaab" — n·m comparisons.

</details>

## Ex 3
Compute Z for "aabcaabxaaz".

<details><summary>Hint</summary>

Z = [0,1,0,0,3,1,0,0,2,1,0,0] (windowed reuse gives this).

</details>

## Ex 4
Write the rolling-hash update and state what it reuses.

<details><summary>Hint</summary>

H = (H - t[i]·B^(m-1))·B + t[i+m]; reuses m-1 of m multiplications.

</details>

## Ex 5
Why can Rabin–Karp report a match that is not real?

<details><summary>Hint</summary>

Only the hash compared — confirm with a character comparison.

</details>

## Ex 6
What does Manacher return for "babad"?

<details><summary>Hint</summary>

3 — "bab" (or "aba").

</details>

## Ex 7
How many states can a suffix automaton of a length-n string have?

<details><summary>Hint</summary>

At most 2n-1.

</details>
