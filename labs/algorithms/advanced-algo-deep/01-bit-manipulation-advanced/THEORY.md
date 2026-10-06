# Theory — Bit Manipulation Advanced

A bit is the two-valued primitive every integer is built from. Advanced bit
manipulation is the toolkit for working directly on that representation:
clearing and counting set bits, cancelling duplicated values with XOR, and
doing word-parallel arithmetic on packed fields.

## Two's complement refresher

Negative integers are stored as `~x + 1`. Equivalently, `x` and `-x` share the
same trailing zeros, and differ in the lowest set bit and everything above it:
`x = y011…10…0`, `-x = y…100…0`-style — concretely, `-x` flips every bit of
`x` from the lowest set bit leftwards. All the tricks below fall out of this one
fact.

## x & (x-1): clear the lowest set bit

Let `x` have lowest set bit at position k, i.e. `x = …b 1 0…0` with b = 0 and
the low k bits are 0. Then `x-1 = …b 0 1…1`: the bit at position k becomes 0,
every lower bit becomes 1, and higher bits are unchanged. ANDing:

```
x   = …b 1 0 0 0
x-1 = …b 0 1 1 1
x&(x-1) = …b 0 0 0
```

The lowest set bit is cleared; everything else is untouched. Iterating
`x &= x-1` visits exactly the set bits of x, so a loop that empties x this way
runs in **Θ(popcount(x))** — never more than 32 (int) or 64 (long)
iterations, and typically far fewer. This is Brian Kernighan's insight
(1972), and it is why `while (x != 0) { x &= x-1; count++; }` beats testing
32 bits when the word is sparse.

## XOR cancellation

`a ^ a = 0` and `a ^ 0 = a`, plus XOR is associative and commutative, so a
stream with every element twice except one yields the odd one out: scan-fold
with `acc ^= x[i]`. This is the standard *find the single non-duplicated
element* answer, Θ(n) time and Θ(1) space, and it generalises: duplicated
**groups of size 2k** always cancel. It does **not** work for groups of 3 or 5
(a tertiary variant uses two 64-bit counters, the `ones`/`twos` trick).

## Masked updates and toggles

A bit set is a mask `M`; the standard update rules are:

| Operation | Expression | Effect |
|-----------|-----------|--------|
| Set bit k | `M |= (1 << k)` | forces the bit to 1 |
| Clear bit k | `M &= ~(1 << k)` | forces the bit to 0 |
| Toggle bit k | `M ^= (1 << k)` | flips the bit |
| Test bit k | `(M >> k) & 1` | extracts the bit |
| Lowest set bit | `M & -M` | isolates one bit |

`M & -M` works because `-M = ~M + 1`, and adding 1 propagates a carry through
the trailing zeros of `~M` — i.e. the low k+1 bits flip at exactly the lowest
set bit of M. This single-bit mask is the primitive behind looping over a
non-empty set of *which positions are occupied* without a scan.

## Signed shifts and masks

In Java `>>` is the *signed* (arithmetic) shift: the sign bit replicates.
`>>>` is the *unsigned* (logical) shift: zeros shift in. For a 32-bit
histogram or a bitboard loop, the unsigned shift is usually the intended one.
Two classic traps:

1. `1 << n` with a signed `int`: if `n = 31` the mask is negative, and
   `n ≥ 32` silently wraps (the shift distance is masked to 5 bits). Use
   `1L << n` for shifts near 64 or validate `n`.
2. Masking with `mask << k` where `mask` has its high bit set can overflow
   into the sign bit — prefer `long` for accumulation.

## SWAR and popcount

SWAR (SIMD Within A Register) applies the same operation to several packed
fields of one machine word. Hamming-weight via SWAR folds the mask with the
field-shifted value:

```java
int popcount(int x) {
    x -= (x >>> 1) & 0x55555555;          // pairwise sums in 2-bit fields
    x = (x & 0x33333333) + ((x >>> 2) & 0x33333333);  // 4-bit fields
    x = (x + (x >>> 4)) & 0x0F0F0F0F;     // 8-bit fields
    x += x >>> 8; x += x >>> 16;          // horizontal sum
    return x & 0x3F;
}
```

Each line sums adjacent field counts in place; after the fold, the low 6 bits
hold the total. This is a **fixed 5-step** algorithm with no branches — which
is why `Integer.bitCount` (which compiles to the POPCNT instruction on x86-64
and ARM) is the production choice.

## Complexity and boundaries

All of these are `O(1)` *per word operation* on a fixed-width machine; the
asymptotic content is in how many words you must process. Popcount over an
`n`-element `int[]` is `Θ(n)`; the Kernighan update loop over a sparse set
is `Θ(popcount)` per step. The one place to be careful is that `n & (n-1)` on
a *negative* `n` clears its lowest set bit too — `while (n != 0) n &= n-1`
terminates for negatives as well (it walks the two's-complement bit pattern),
but `while (n > 0)` would not.

## Summary

The bit-level toolkit is small — `& | ^ ~ << >>>` plus the five mask rules —
but every trick is a direct reading of two's complement. Prove the trick once
from the digit definition, and it becomes a building block you can trust
inside larger algorithms (bitboards, subsets, hashing, packed DP states).
