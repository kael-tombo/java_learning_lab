# Quiz — String Algorithms Advanced

15 questions. Each key gives the reason.

---

## Q1
What is the KMP failure function π[i]?

<details><summary>Answer</summary>

Length of the longest proper prefix of p[0..i] that is also a suffix of p[0..i].

</details>

## Q2
Why is KMP Θ(n) and not Θ(n·m)?

<details><summary>Answer</summary>

The matched length j increases ≤ n times and each π-application decreases j, so decreases ≤ increases; total work Θ(n).

</details>

## Q3
On mismatch in KMP, what happens to the text pointer?

<details><summary>Answer</summary>

Nothing — it never moves back; only j falls back via π.

</details>

## Q4
What does Rabin–Karp hash, and what is the false-positive source?

<details><summary>Answer</summary>

The pattern and each length-m window of the text; collisions on the hash.

</details>

## Q5
Why is Z-array construction Θ(n)?

<details><summary>Answer</summary>

The window right edge r only moves right, and each comparison either advances r or stops it.

</details>

## Q6
How to use Z for pattern matching?

<details><summary>Answer</summary>

Compute Z on p + sentinel + t; any entry ≥ m is an occurrence.

</details>

## Q7
What invariant makes Manacher linear?

<details><summary>Answer</summary>

The rightmost palindrome edge never moves left; each centre inherits its mirror radius, clamped.

</details>

## Q8
Max states in a suffix automaton of length n?

<details><summary>Answer</summary>

2n - 1.

</details>

## Q9
What extra confirm does Rabin–Karp need on a hash hit?

<details><summary>Answer</summary>

A character-by-character comparison of the window with p.

</details>

## Q10
Why does KMP never reset the text pointer?

<details><summary>Answer</summary>

The matched prefix already constrains the alignment; resetting would discard information and break the bound.

</details>

## Q11
What does a suffix automaton accept?

<details><summary>Answer</summary>

Exactly the suffixes of its string; every path spells a substring.

</details>

## Q12
Why use a sentinel like "#" between p and t in Z matching?

<details><summary>Answer</summary>

Prevents a Z entry from spanning the boundary and over-counting the match length.

</details>

## Q13
Give a case where naive matching does n·m work.

<details><summary>Answer</summary>

t = aaaa…a, p = aaab.

</details>

## Q14
What is the expected Rabin–Karp cost with a q-modulus hash?

<details><summary>Answer</summary>

Θ(n + m) expected; collisions add a small false-positive term.

</details>

## Q15
Why does π[j-1] give the next candidate j after a mismatch?

<details><summary>Answer</summary>

It is the longest prefix of p that could still match ending at the same text position.

</details>
