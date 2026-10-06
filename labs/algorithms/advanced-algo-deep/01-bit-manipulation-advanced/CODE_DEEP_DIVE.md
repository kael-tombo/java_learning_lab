# Code Deep Dive — Bit Manipulation Advanced

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
public final class Bits {
    private Bits() {}

    /** Kernighan's popcount: one iteration per set bit. */
    public static int popcountKernighan(long x) {
        int k = 0;
        while (x != 0) { x &= (x - 1); k++; }
        return k;
    }

    /** Fixed 5-fold SWAR popcount; mirrors Integer.bitCount logic. */
    public static int popcountSwar(int x) {
        x -= (x >>> 1) & 0x55555555;
        x = (x & 0x33333333) + ((x >>> 2) & 0x33333333);
        x = (x + (x >>> 4)) & 0x0F0F0F0F;
        x += x >>> 8;
        x += x >>> 16;
        return x & 0x3F;
    }

    /** Lowest set bit as a single-bit mask: 0b10110000 -> 0b00010000. */
    public static long lowbit(long m) { return m & -m; }

    public static boolean isPowerOfTwo(long n) { return n > 0 && (n & (n - 1)) == 0; }

    /** Find the odd-one-out when every other value appears exactly twice. */
    public static long oddOneOut(long[] a) {
        long acc = 0;
        for (long v : a) acc ^= v;
        return acc;
    }

    /** Both odd-one-out values when all others appear twice. */
    public static long[] twoOddOnesOut(long[] a) {
        long all = 0;
        for (long v : a) all ^= v;          // a ^ b
        long split = all & -all;            // a bit where a and b differ
        long g1 = 0;
        for (long v : a) if ((v & split) != 0) g1 ^= v;
        return new long[] { g1, all ^ g1 };
    }

    /** Enumerate all submasks of M, standard bit-DP loop. */
    public static void forEachSubmask(int m) {
        for (int s = m; ; s = (s - 1) & m) {
            // use s ...
            if (s == 0) break;
        }
    }
}
```

## Pitfalls

- Signed >> on a negative mask injects 1s from the top — use >>> when scanning a bitboard.
- Shift distance is masked in Java (int: low 5 bits), so 1 << 32 is 1 << 0 — always widen to long near 32.
- 0 & -1 == 0 breaks the naive "x & (x-1) == 0" power-of-two test; guard with n > 0.
- XOR cancellation silently gives wrong answers for groups of 3 (3v mod 2 = v).
- while (n > 0) n &= n-1 terminates early for negative n; use n != 0 when negatives are in scope.
- int mask = 1 << k flips the sign bit for k = 31; accumulate into long for 32+ positions.

## Why the bounds hold

- **x & (x-1) update loop**: Θ(k) time, k = popcount(x) — ≤ 32 (int) / 64 (long) iterations.
- **Brian Kernighan popcount**: Θ(k) time, k = set bits — ≤ word-width iterations.
- **SWAR popcount**: Θ(1) time, word = 32 or 64 bits — 5 field folds, branch-free.
- **XOR cancel duplicated odd-one-out**: Θ(n) time, Θ(1) extra space — only for pairwise (2k) duplicates.
- **M & -M isolate lowest set bit**: Θ(1) time, Θ(1) — single-bit mask.
- **Bit test/set/clear/toggle**: Θ(1) time, Θ(1) — one mask operation each.

## Takeaway

# Theory — Bit Manipulation Advanced
