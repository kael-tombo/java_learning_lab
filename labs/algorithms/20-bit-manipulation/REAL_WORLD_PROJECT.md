# Real-World Project: Flag Register and Popcount Lab
> Permission-flag API plus three popcount methods with counted operations.

## Problem
Feature flags pack into one int; the API sets, clears, toggles, and tests bits safely.
Popcount has three implementations whose operation counts are measured, not guessed.
## Inputs
- Flag names mapped to bit positions 0..30 (sign bit excluded and documented).
- 1000 fixed 32-bit test values covering 0, -1, powers of two, and alternating patterns.
- Counter-instrumented popcount variants: shift-loop, n-and-(n-1), builtin.
## Steps
1. Implement set/clear/toggle/test on an int register with range-checked positions.
2. Verify flag round-trips: set then test is true, clear then test is false, for all 31 positions.
3. Implement shift-loop popcount counting loop iterations.
4. Implement n-and-(n-1) popcount counting iterations (equals popcount).
5. Compare all three against the builtin on all 1000 values.
6. Print total iterations per method and the ratio of shift-loop to lowbit-loop.
## Acceptance criteria
- All flag round-trips pass for positions 0..30.
- All three popcounts agree on all 1000 values.
- Lowbit-loop iterations equal the true popcount on every value.
- Position 31 or negative is rejected with a message.
- Alternating-pattern values show the documented iteration gap between methods.
## Failure modes
- Sign-bit position 31 is refused (documented two's-complement reason).
- Shift distances are masked per Java semantics in tests (no hidden assumptions).
- Negative test values exercise >>> paths explicitly.
## Extensions
- Bitmask subset enumerator over n items with the 2^n count asserted.
- XOR loner-finder extended to the two-loners partition variant.
## How to demo
- Show the iteration table across the three methods on the 1000 values.
- Show the >>> vs >> demo on a negative register value.
