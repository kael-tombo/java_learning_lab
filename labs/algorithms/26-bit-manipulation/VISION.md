# Vision: Bit Manipulation

## Direction

This lab covers integer bit tricks: masks and shifts for field access,
popcount for density, and XOR cancellation for lone-element problems. The
practical skill is reaching for the one-line identity first and stating its
guard conditions (sign, zero, width) before using it.

## What to learn

- Mask and shift: isolate, set, clear, and test individual bits.
- Kernighan popcount: O(set bits) counting and when tables beat it.
- XOR identities: x^x=0, x^0=x; pair cancellation and range XOR.
- Power-of-two test: x & (x-1) == 0 with the positivity guard.
- Width care: int versus long shifts, sign extension on right shift.

## Non-coverage

- This lab does not cover floating-point bit layouts.
- It does not cover SIMD, bitset libraries, or compression codecs.
- It does not cover cryptography or hash-function design.
- It does not cover arbitrary-precision arithmetic internals.
- All examples fit in 32-bit ints with stated guards.

## How to use this lab

Reproduce the three MOCK_INTERVIEW programs from memory, then extend Q3 with
a bit-reversal routine and verify it against string reversal on 16 values.
Finish with MINI_PROJECT's flag-register exercise.

## Pitfalls

- Dropping the positivity guard on the power-of-two test.
- Shifting ints by 32 or more and meeting modular shift behavior.
- Using XOR cancellation where counts, not parity, decide.

## Done when

- You can write popcount, lone-element, and power-of-two from memory.
- You can state the guard each trick needs without prompting.
- You can explain why XOR order never matters for cancellation.
- You can predict shift results for negative ints correctly.
