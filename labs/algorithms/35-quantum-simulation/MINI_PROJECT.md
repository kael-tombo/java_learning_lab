# MINI_PROJECT — Classical Simulation of Quantum Circuits
> Build a tiny state-vector simulator (H, X, CNOT, measurement sampling) with an honest memory estimator. Classical hardware only.

## Inputs
- Circuit file: one gate per line, e.g. `H 0`, `X 1`, `CNOT 0 1`, qubit count on the first line (max 12 for full runs).
- Fixed checks: H|0> amplitudes, Bell-pair probabilities, memory table for n = 10/20/30/40.

## Build steps
1. Store the state as a 2^n complex-double vector; implement H, X by direct amplitude updates and CNOT by index swaps.
2. Verify H|0> gives amplitudes 0.7071/0.7071 with probabilities 0.5/0.5 and unit norm.
3. Verify H+CNOT on |00> gives probabilities 0.5/0/0/0.5 (Bell pair).
4. Implement measurement sampling with a seeded RNG (single-shot and 1000-shot histogram modes).
5. Add `--estimate-only`: print amplitudes and bytes (= 2^n x 16) for any n without allocating; refuse full simulation above the configured qubit cap with the byte figure in the error.

## Acceptance criteria
1. H|0> output matches amp 0.7071/0.7071 and norm 1.0000.
2. Bell circuit output matches probs 0.5000,0.0000,0.0000,0.5000.
3. Memory table reproduces bytes 16384 / 16777216 / 17179869184 / 17592186044416 for n = 10/20/30/40.
4. `--estimate-only` for n = 50 prints the byte figure and allocates nothing (verified by heap log or refusal message).
5. 1000-shot Bell histogram shows only 00 and 11 outcomes (seeded run).
6. README states in one paragraph that this is classical simulation cost, with no claims about quantum hardware.

## Analysis prompts
1. Why does the byte figure double per qubit, independent of gate count?
2. Which gates in your set only permute amplitudes, and which create superposition?
3. At what n does your machine hit its cap, and what exactly runs out?

## Non-goals
- Noise models, tensor-network or stabilizer methods, and any real-device execution or performance claim.

## Worked reference (verified outputs)
- H|0> prints amp0=0.7071 amp1=0.7071 with p0=0.5000 p1=0.5000 and unit norm.
- Bell circuit prints probs 0.5000,0.0000,0.0000,0.5000; memory rows print 16384 / 16777216 / 17179869184 / 17592186044416 bytes.

## Stretch
- Add the Z gate and a GHZ-3 check (probabilities 0.5 on 000 and 111, zero elsewhere).
- Implement a stabilizer-mode fast path for H/S/CNOT-only circuits and note where it stops applying.
