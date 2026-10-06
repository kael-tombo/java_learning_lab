# Exercises — Bit Manipulation Advanced

Attempt each before reading the hint.

## Ex 1
Write `clearIsolated(int mask, int k)` returning mask with bit k forced to 0, and justify via the digit definition.

<details><summary>Hint</summary>

`mask & ~(1 << k)` — complement flips only bit k.

</details>

## Ex 2
Implement `isPowerOfTwo(int n)` for longs including 0 and negatives.

<details><summary>Hint</summary>

`n > 0 && (n & (n-1)) == 0`.

</details>

## Ex 3
Count set bits in a long using Kernighan's loop; argue the iteration bound.

<details><summary>Hint</summary>

Each iteration clears exactly one 1-bit, so at most popcount(x) steps.

</details>

## Ex 4
Isolate the lowest set bit of `0b10110000`; give the answer in binary.

<details><summary>Hint</summary>

M & -M = 0b00010000.

</details>

## Ex 5
Show `1 << 31` in a signed int is `Integer.MIN_VALUE`, and write the safe mask for positions 0..31.

<details><summary>Hint</summary>

Use `1L << k` and cast, or test k != 31.

</details>

## Ex 6
Two numbers appear once, all others twice — find both with XOR and one split on the lowest differing bit.

<details><summary>Hint</summary>

xor-fold to get x^y, take lowest set bit d, group by (a & d).

</details>

## Ex 7
Why does XOR cancellation fail when every other element appears 3 times? Give the fix.

<details><summary>Hint</summary>

3 mod 2 = 1 does not cancel; track per-bit count mod 3 with two masks.

</details>
