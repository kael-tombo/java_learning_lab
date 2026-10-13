# Math Foundation: Two's Complement Proofs and Popcount
> Bitwise identities proved from arithmetic: lowbit, clearing, XOR group laws.

## Definitions
- ~x flips all bits; -x = ~x + 1 by two's complement definition.
- x & -x: intersection of x with its negation (the lowbit claim).
- Popcount: number of 1-bits; word size w = 32 (int) or 64 (long).
- Shifts: << zero-fills; >> sign-extends; >>> zero-extends; distances masked.

## Counting argument
- Each idiom: O(1) word ops, O(1) space - verification by inspection.
- Clearing-loop popcount: one iteration per set bit = exactly popcount iterations.
- Shift-loop popcount: w iterations always; builtin: O(1)-class reference.
- Flag packing: 31 independent booleans per int (position 31 excluded by sign).

## Recurrence
- None needed: straight-line identities proved by bit-position case analysis.
- Clearing progress: popcount strictly decreases each n &= n-1 step.
- Loop termination: popcount reaches 0 after exactly popcount steps.
- XOR accumulation: order-free by commutativity/associativity of XOR.

## Derivation of the bound
- x & -x: -x = ~x+1 flips trailing ones to 1... proof: trailing zeros of x stay aligned. (4 lines)
- n & (n-1): subtracting borrows through trailing ones, clearing the lowest 1. (3 lines)
- Power-of-two: single-bit numbers are exactly the positive n with n&(n-1) == 0. (2 lines)
- XOR loner: pairs cancel to 0, identity leaves the loner: a^a^b = b. (2 lines)

## Worked mini-proofs
- Proof 1: lowbit isolation from ~x+1 bit pattern. (4 lines)
- Proof 2: clearing drops exactly the lowest set bit (borrow analysis). (3 lines)
- Proof 3: loner correctness from XOR group laws. (2 lines)

## Exercises with answers
- 1. 12 & -12. Answer: 4.
- 2. Iterations of clearing-loop on 0b1011000. Answer: 3.
- 3. Loner of [4,1,2,1,2]. Answer: 4.

## Pitfalls
- Power-of-two test without n > 0 (0 passes the mask check).
- >> vs >>> confusion on negative values.
- Shift distances >= width silently masking.

## Checklist
- Prove lowbit and clearing from two's complement without notes.
- State all three shift rules with an example each.
