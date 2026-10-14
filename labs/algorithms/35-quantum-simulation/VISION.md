# VISION — Classical Simulation of Quantum Circuits
> Direction: from mystique to bookkeeping — a simulator is a 2^n-vector machine, and the wall is memory, not cleverness.

## Where this sits
- Classical state-vector simulation stores 2^n complex amplitudes and applies unitaries by direct update: exact, general, and memory-walled near a few dozen qubits.
- Around it: stabilizer simulation (Clifford circuits in polynomial time), tensor networks (good for shallow/local circuits), and hardware execution, which this track does not cover.
- The durable lesson is cost accounting: bytes per amplitude times 2^n, before any gate runs.

## 4-week direction
- Week 1: hand-apply H to |0> and H+CNOT to |00>; reproduce both lab outputs on paper.
- Week 2: finish MINI_PROJECT; memorize the byte table for n = 10/20/30/40.
- Week 3: add one gate (e.g. Z or CZ) and one 3-qubit check (GHZ probabilities 0.5/0.../0.5).
- Week 4: REAL_WORLD_PROJECT review; whiteboard the doubling argument in 5 minutes.

## Done criteria
- Explain unitarity as norm preservation with the Q1 numbers.
- Explain entanglement operationally: Bell outcomes correlate, single-qubit factors do not exist for it.
- Quote the memory figure for any n up to 60 from the doubling rule.

## Non-coverage
- This lab makes no claims about quantum hardware speed, advantage, roadmaps, or vendors.
- No noise modeling, error correction, or variational algorithms beyond naming them as separate tracks.
- Grover and QFT appear only as named circuits students may simulate at small n; no query-complexity proofs here.

## Pitfalls
- Presenting simulator timings as statements about quantum devices; they are statements about classical memory.
- Forgetting the 16-bytes-per-amplitude constant when estimating (complex = 2 doubles).
- Sampling without a recorded seed and calling the histogram a result.

## Adjacent labs
- Pair with 32-exact-exponential for exponential-cost budgeting discipline and 33-matrix-algorithms for the unitary-as-matrix mechanics.
- Revisit before simulating anything above 25 qubits; the estimator gate comes first.

## Weekly drills
- Recompute the byte figure for n = 25 and n = 35 from the doubling rule.
- Re-derive Bell probabilities from H then CNOT on paper in under 5 minutes.
- Recite the classical-simulation-only scope sentence before demoing any result.

## Anti-roadmap
- Do not let simulator numbers appear in any sentence about quantum devices.
- Do not allocate before estimating; the estimator runs first by policy, not habit.
