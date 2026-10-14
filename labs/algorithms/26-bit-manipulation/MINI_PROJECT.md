# Mini-Project: Flag Register

## Goal

Model an 8-bit device register with named bits and drive it through a fixed
set-bit, clear-bit, toggle-bit, and test-bit script with printed state.

## Inputs

- Bits: 0 power, 1 ready, 2 error, 3 mode0, 4 mode1; bits 5-7 reserved zero.
- Script: set power, set ready, set mode1, toggle ready, clear power.

## Steps

1. Store the register as a single int masked to 8 bits after every op.
2. Implement set, clear, toggle, and test using masks and shifts only.
3. Run the 5-step script, printing the binary string after each step.
4. Assert the final value equals bit 2 unset, mode1 set, rest as expected.
5. Add popcount of the final register and print it.
6. Attempt to set reserved bit 7; show the mask rejects it with a message.
7. Print the mode field (bits 4-3) decoded as an integer 0-3.

## Acceptance criteria

1. Binary trace shows 5 states, each exactly 8 characters of 0/1.
2. Final register value is 00010000 (decimal 16).
3. Popcount of the final register prints 1.
4. Reserved-bit write rejected with a message, register unchanged.
5. Mode field decodes to 2 for the final state.
6. No boolean array or string parsing used for bit storage.
7. All output uses plain ASCII characters.

## Grading note

- Binary trace of 5 states, each exactly 8 characters, required.
- Final 00010000 with mode field 2 and popcount 1.
- Reserved-bit write must leave the register unchanged.

## Stretch

- Add an interrupt mask register and show combined pending calculation.
- Decode the full register into a one-line status summary.
