# Mini Project: Bit Idioms Deck
> Six one-line idioms, each proved and tested on fixed values.

## Background
- Two's complement makes x and -x share exactly the lowest set bit.
- Each idiom gets a proof line plus truth-table-grade tests.
- Java shift semantics (>> vs >>>, distance masking) are tested explicitly.
## Goal
Implement and prove six idioms with a shared test battery.
Demonstrate the two classic Java shift pitfalls with outputs.
## Tasks
1. Implement lowest-set-bit, clear-lowest, power-of-two test, toggles, and masks.
2. Write the one-line proof comment above each idiom.
3. Test all idioms on 0, -1, powers of two, and alternating-bit values.
4. Show >> vs >>> outputs on a negative value side by side.
5. Show shift-by-32 behavior with the masking rule quoted in the README.
6. Find the loner with XOR on a paired array and verify the answer.
## Acceptance criteria
- All idioms pass the full battery including 0 and -1.
- Shift demos print the documented differing outputs.
- Loner test returns the expected value on three fixtures.
- README holds all six proof lines with no hand-waving.
- Alternating-bit values behave as the proofs predict.
## Pitfalls
- int shifts on long values without the L suffix or casts.
- Sign extension through >> where >>> was required.
- Power-of-two test forgetting the n > 0 guard (0 passes otherwise).
- XOR loner applied to tripled elements where it does not apply.
## Stretch
- Popcount three ways with iteration counts compared.
- Subset enumeration over bitmasks with the 2^n assertion.
## Timebox
One afternoon session, roughly 2 hours with proofs.
