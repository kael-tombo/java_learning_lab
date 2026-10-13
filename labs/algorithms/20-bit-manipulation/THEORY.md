# Theory: Bits, Masks, and Two's Complement Idioms
> Exact bit control with proved one-liners and Java shift semantics.

## Problem statement
- Integers are fixed-width two's complement words; every idiom here is arithmetic, not magic.
- Operations: AND, OR, XOR, NOT, left shift, signed and unsigned right shifts.
- Java specifics: int is 32-bit, long 64-bit; shift distances mask to 5 (int) or 6 (long) bits.
- Sign-bit position 31 (int) behaves differently under >> vs >>>.

## Two's complement facts
- -x = ~x + 1; x and -x share exactly the lowest set bit, all lower bits zero.
- x & -x isolates the lowest set bit (e.g., 12 & -12 = 4).
- n & (n-1) clears the lowest set bit: borrowing flips the trailing ones and the bit itself.
- Iterating n &= n - 1 visits each set bit once: popcount in O(number of ones).

## Core idioms with proofs
- Power-of-two test: n > 0 and (n & (n-1)) == 0; powers have a single bit, and only they do.
- Bit test: (x >> i) & 1; set: x | (1 << i); clear: x & ~(1 << i); toggle: x ^ (1 << i).
- XOR loner: pairs cancel (a^a = 0), order irrelevant (xor commutes/associates): remainder is the loner.
- Triples break it: a^a^a = a, so the loner trick needs exactly-paired backgrounds.
- Mask building: (1 << k) - 1 keeps the low k bits; prove by the geometric bit pattern.

## Shifts in Java
- << fills with zeros; >> sign-extends (keeps negativity); >>> zero-extends (logical shift).
- Distance masking: x << 32 == x for int (32 mod 32 = 0), never zero as newcomers expect.
- Negative >> keeps leading ones; the same value under >>> gains leading zeros - test both.
- Casts before shifting: (1 << 31) is negative int; use 1L for bit 31 and above.

## Complexity derivation
- Every idiom is O(1) word operations: constant time, no extra space.
- Popcount by clearing loops in O(popcount); shift-loop in O(word size); builtin is O(1)-class.
- Flag APIs pack 31 booleans per int: 31x denser than a boolean array, with O(1) access.
- Subset enumeration over n bits still costs Theta(2^n) - bits compress, they do not conquer.

## Variants
- builtin popcount (Integer.bitCount) as the reference every hand loop is checked against.
- Bitset sieve: same sieve idea with bit-packed storage.
- Two-loner partition: split by a differing bit, then two independent loner passes.

## Pitfalls
- >> on negative masks where >>> was required (sign extension corrupts the high bits).
- Shift distance >= width silently masking instead of zeroing.
- Forgetting the n > 0 guard so 0 passes the power-of-two test.
- 1 << 31 overflow surprises when building high masks with int literals.

## Interview signal
- Prove x & -x and n & (n-1) from the borrow behavior, not from memory.
- State >> vs >>> vs distance-masking rules with examples.
- Explain why XOR loner needs pairs, with the triple counterexample.
