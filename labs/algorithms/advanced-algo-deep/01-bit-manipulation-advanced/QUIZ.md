# Quiz — Bit Manipulation Advanced

15 questions. Each key gives the reason.

---

## Q1
State the two's-complement definition of -x and what it implies about x and -x below the lowest set bit.

<details><summary>Answer</summary>

-x = ~x + 1. x and -x agree on the lowest set bit and are complements elsewhere, so x & -x isolates that bit.

</details>

## Q2
Why does x & (x-1) clear only the lowest set bit?

<details><summary>Answer</summary>

x-1 flips the lowest 1 to 0 and turns the trailing zeros into ones; ANDing with x keeps the upper bits identical and zeros out that one position.

</details>

## Q3
What is the running time of while(x!=0){x &= x-1; k++}?

<details><summary>Answer</summary>

Θ(popcount(x)) — one iteration per set bit, at most the word width.

</details>

## Q4
Why is XOR used to find the odd-one-out instead of sorting?

<details><summary>Answer</summary>

XOR is associative/commutative and a^a=0, so pairs cancel — Θ(n) time, Θ(1) space, no compares.

</details>

## Q5
What breaks if you use a signed >> to scan a bitboard?

<details><summary>Answer</summary>

The sign bit replicates, injecting 1s from the top; use >>> for a logical shift.

</details>

## Q6
What does 1 << n evaluate to for n = 32 in Java?

<details><summary>Answer</summary>

n is masked to 5 bits, so it becomes 1 << 0 = 1 — a classic silent wrap.

</details>

## Q7
Give the expression for the lowest set bit of M and explain it in one line.

<details><summary>Answer</summary>

M & -M; since -M = ~M+1 the carry propagates through ~M's trailing ones, leaving only the lowest set bit of M.

</details>

## Q8
Why can the running time of Kernighan popcount beat the fixed 32-bit SWAR count for sparse words?

<details><summary>Answer</summary>

Kernighan costs one step per set bit, so a word with k ≪ 32 set bits finishes in k steps while SWAR always runs 5 folds.

</details>

## Q9
What is the result of ~0 in two's complement?

<details><summary>Answer</summary>

-1 (all ones), because ~0 = -0 - 1 = -1.

</details>

## Q10
A mask M has bit pattern …10110. After M &= M-1 what changes?

<details><summary>Answer</summary>

The lowest set bit (position 1) clears: M becomes …10100.

</details>

## Q11
Why does while(n>0) n &= n-1 terminate but miss negative inputs?

<details><summary>Answer</summary>

It stops as soon as the value is non-positive; for n<0 the pattern walks all set bits but n is already negative so the loop body may never run the intended count — use != 0 carefully.

</details>

## Q12
In the SWAR popcount, what does the line x -= (x >>> 1) & 0x55555555 compute?

<details><summary>Answer</summary>

It turns each 2-bit field into the count of its two bits (0,1, or 2) — a pairwise horizontal add.

</details>

## Q13
Give the bit rule for toggling, setting, and testing bit k.

<details><summary>Answer</summary>

Toggle: M ^= 1<<k; set: M |= 1<<k; test: (M>>>k)&1.

</details>

## Q14
Why must INF-style masks in bit-DP use long when a 32-bit quantity can hit Integer.MIN_VALUE?

<details><summary>Answer</summary>

Integer.MIN_VALUE has the sign bit set; arithmetic on it silently wraps, corrupting masked comparisons — widen to long before shifting.

</details>

## Q15
What is the difference in behaviour between >> and >>> on a negative long?

<details><summary>Answer</summary>

>> preserves the sign (arithmetic), >>> shifts in zeros (logical) — only >>> yields the high bit as a plain count.

</details>
