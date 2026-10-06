# Math Foundation — Bit Manipulation Advanced

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Two's complement identity

In a two's-complement word of width w, -x ≡ 2ʷ - x (mod 2ʷ). Hence x + (-x) ≡ 0 and ~x = (2ʷ - 1) - x = -x - 1.

This holds for every width w, so x & -x is computed by the same rule for int (w=32) and long (w=64).

## x & (x-1) proof

Write x = A·2^(k+1) + 2^k (lowest set bit at k). Then x-1 = A·2^(k+1) + (2^k - 1). ANDing clears 2^k and keeps A·2^(k+1): x & (x-1) = A·2^(k+1).

The formula is valid exactly when k is the lowest set bit of x; it removes precisely that bit.

## Why XOR cancels pairs

Over GF(2), x ^ x = 0 and XOR is addition. For a multiset where every value appears 2k times, the sum is 2k·v = 0 (mod 2). Only the odd-frequency value survives.

This fails for groups of size 3: 3v mod 2 = v, so it does NOT cancel — a counter-example is {a, a, a} returning a. Fix: track the count mod 3.

## Isolating the lowest set bit

For M = A·2^(k+1) + 2^k, -M ≡ 2^w - M. In bits, -M = ~M + 1 = (2^w - 1 - M) + 1 = 2^w - M. The addition flips the trailing (w-k-1) ones of ~M and sets position k, giving -M = B·2^(k+1) + 2^k. Then M & -M = 2^k.

M & -M has exactly one bit set — the lowest set bit of M.

## SWAR popcount fold invariant

After step 1, each 2-bit field f holds bitcount(f). Step 2 replaces each 4-bit field with the sum of its two 2-bit subfields. Induction: after step t, each 2^(t+1)-bit field holds its own bitcount. After 5 folds the 32-bit word holds the total.

The invariant holds because addition in field f never exceeds the field width until the final horizontal add.

## Power-of-two characterisation

n > 0 is a power of two ⟺ n has exactly one set bit ⟺ n & (n-1) = 0. The last equivalence fails for n = 0 (0 & -1 = 0), so the guard n > 0 is essential.

Counter-example to dropping the guard: n = 0 satisfies (n & (n-1)) == 0 but is not a power of two.
