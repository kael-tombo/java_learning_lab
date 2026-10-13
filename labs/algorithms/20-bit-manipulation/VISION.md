# Vision: Bit Manipulation
> Masks, shifts, and XOR reasoning: exact control over individual bits.

## Where this leads
- Flag packing, permission sets, parity checks, and compact state encodings.
- Low-level idioms (lowbit, clear-lowest, power-of-two tests) used with proof.
- Reading hex dumps and masks without reaching for a calculator.
## What mastering it unlocks
- Isolate, clear, and test individual bits with shifts and masks.
- Use n & (n-1) to clear the lowest set bit and count bits in O(popcount).
- Test powers of two in one expression and prove why it works.
- Find the single unpaired element with XOR and argue the cancellation.
- Avoid sign-extension and shift-distance pitfalls in Java specifically.
## What it does not cover
- SIMD and vector-intrinsic programming.
- Constant-time cryptographic coding discipline.
- Arbitrary-precision bit algorithms beyond single words.
## Core questions you will answer
- Why does x & -x isolate the lowest set bit in two's complement?
- Why does n & (n-1) drop exactly the lowest set bit?
- Why does XOR find the loner among pairs, and what breaks with triples?
- What does >>> do that >> does not, and when does it matter?
## How to judge progress
- Evaluate mask expressions by hand on hex inputs.
- Prove each one-line idiom from two's complement, not from memory.
- Spot sign-extension bugs in Java shifts on sight.
## Common misuse
- Shifting int by 32+ bits and expecting zero (Java masks the distance).
- Using >> on negative masks where >>> was required.
## After this lab
- 19-number-theory for modular arithmetic on the same integers.
- 15-cryptographic-algorithms for what XOR can and cannot protect.
One-line self-test: Prove the n & (n-1) lowest-bit fact in one line of binary reasoning.
