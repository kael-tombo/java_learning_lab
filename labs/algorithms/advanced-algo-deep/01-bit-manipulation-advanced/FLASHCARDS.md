# Flashcards — Bit Manipulation Advanced

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | x & (x-1) | clears the lowest set bit of x |
| 2 | -x in two's complement | ~x + 1 |
| 3 | Lowest set bit of M | M & -M |
| 4 | Brian Kernighan popcount iteration cost | Θ(popcount(x)) |
| 5 | XOR key property | a ^ a = 0, a ^ 0 = a, associative + commutative |
| 6 | Odd-one-out via XOR works for | duplicates in pairs (2k); fails for triples |
| 7 | Set bit k | M |= 1 << k |
| 8 | Clear bit k | M &= ~(1 << k) |
| 9 | Toggle bit k | M ^= 1 << k |
| 10 | Test bit k | (M >>> k) & 1 |
| 11 | Signed shift in Java | >> replicates sign bit |
| 12 | Unsigned shift in Java | >>> shifts in zeros |
| 13 | 1 << 32 in Java int | wraps to 1 << 0 (shift distance masked to 5 bits) |
| 14 | Safe mask for bit k | 1L << k (widen before shifting) |
| 15 | SWAR popcount step count | 5 field folds, branch-free |
| 16 | Integer.MIN_VALUE binary | 1000…0 (sign bit only) |
| 17 | ~0 evaluates to | -1 (all ones) |
| 18 | x & -x for x = 0b10110000 | 0b00010000 |
| 19 | Why n & (n-1) == 0 tests power of two | powers of two have exactly one set bit |
| 20 | n=0 in power-of-two test | not a power of two (0 & -1 == 0) — must guard n>0 |
| 21 | Carry propagation in -M = ~M+1 | flips trailing ones of ~M, stops at first 0 |
| 22 | Kernighan vs SWAR on sparse word | Kernighan wins (k steps vs fixed 5 folds) |
| 23 | Two odd-one-out values | split on lowest bit of x^y: group by (a & d) |
| 24 | while(x != 0) x &= x-1 | iterates once per set bit; works for negatives too |
| 25 | x >> 1 on negative int | arithmetic shift, sign replicates |
| 26 | Masked shift distance in Java | int: low 5 bits; long: low 6 bits |
| 27 | Popcount of Integer.MIN_VALUE | 1 (only the sign bit set) |
| 28 | x & (x-1) on 0 | 0 & -1 = 0, loop terminates immediately |
| 29 | Third SWAR line x=(x+(x>>>4)) & 0x0F0F0F0F | sums 4-bit fields into the low nibble of each byte |
| 30 | Parity trick acc ^= x[i] | bit flip on each occurrence; final acc = XOR of all |
| 31 | Masked update of a bit set | M is a bitset; set/clear/toggle/test encode membership |
| 32 | Overflow guard for INF masks | use long and cap positions below 63 |
| 33 | Lowest set bit mask single-bit | M & -M has exactly the bits of the lowest set bit and nothing else |
| 34 | Negative x in Kernighan loop | walks the two's-complement pattern — still terminates, but count reflects the bit pattern |
| 35 | Java POPCNT | Integer.bitCount compiles to POPCNT on modern x86-64 |
| 36 | Bit scan forward (find lowest set) | Integer.numberOfTrailingZeros |
| 37 | Exactly one bit set test | x != 0 && (x & (x-1)) == 0 |
| 38 | Clear k lowest bits | x &= ~((1 << k) - 1) |
| 39 | Keep k lowest bits | x &= (1 << k) - 1 |
| 40 | Swap two ints without temp | a^=b; b^=a; a^=b — a^b^a = b |
| 41 | Charset with no duplicates small alphabet | bitmask over 26 bits: one bit per letter |
| 42 | Subset enumeration of a mask | for (int s = M; ; s = (s-1) & M) — visits all submasks |
| 43 | Highest set bit position | 31 - Integer.numberOfLeadingZeros(x) |
| 44 | Round up to next power of two | bit smear: x |= x>>1; ... then x+1 |
| 45 | x & -x used in Fenwick tree | lowbit indexes the parent update jump |
| 46 | Gray code g = n ^ (n>>1) | flips one bit between consecutive codes |
| 47 | XOR fold detects single edit | same content except one byte → XOR reveals the changed byte |
| 48 | Masked byte extraction | (x >> (8*k)) & 0xFF |
| 49 | Zigzag encode (MapStruct-style) | (n << 1) ^ (n >> 31) maps negatives to odds |
| 50 | Absolute value via bits | (x ^ (x >> 31)) - (x >> 31) |
| 51 | Bytes of an int, high to low | shift by 24, 16, 8, 0 and mask 0xFF |
| 52 | Two-bit state pack in one int | field k uses bits [2k, 2k+1]; extract with (x >> 2k) & 0b11 |
| 53 | x | (x+1) effect | sets the lowest 0-bit of x to 1 |
| 54 | ~x = -x-1 | flip-all is the additive inverse shifted by one |
| 55 | Byte order (endianness) matters for | bit-serialised formats, not arithmetic |
| 56 | XOR of a range XOR(0..n) | periodic in n mod 4: n, 1, n+1, 0 |
