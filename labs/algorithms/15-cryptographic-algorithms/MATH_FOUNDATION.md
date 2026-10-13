# Math Foundation: Birthday Bound, Bit Costs, XOR Algebra
> Collision math, square-and-multiply bit counting, XOR group laws - all conceptual.

## Definitions
- n-bit digest: 2^n possible outputs; k hashed inputs drawn in the analysis.
- Collision: distinct inputs with equal digests; preimage: input matching a given digest.
- Exponent bit-length L = floor(log2 e) + 1 drives square-and-multiply cost.
- XOR: bitwise addition mod 2; involution means applying twice returns the start.

## Counting argument
- Collision pairs among k inputs: C(k, 2) pairs, each colliding with probability 2^-n.
- Expected collisions about k^2 / 2^(n+1); setting to 1 gives k about 2^(n/2).
- Hence the birthday bound: 256-bit digests need on the order of 2^128 trials.
- Preimage stays at 2^n trials: collisions are quadratically easier than preimages.

## Recurrence
- Square-and-multiply loop: one iteration per exponent bit, O(1) modular work each.
- Cost Theta(L) = Theta(log e) multiplications; memory O(1) accumulators.
- Hash streaming: one pass, O(1) state update per byte: Theta(n) for n bytes.
- XOR pass: one gate-delay-class op per byte position: Theta(n).

## Derivation of the bound
- Birthday: union bound over pairs gives the k^2/2^(n+1) estimate above.
- Modpow: L bits force L squarings plus at most L multiplies: Theta(log e).
- Verification hashing costs exactly one more pass: no asymptotic overhead.
- Key-reuse leak: C1 XOR C2 = P1 XOR P2 holds bitwise for every position.

## Worked mini-proofs
- Proof 1: birthday estimate from pair counting and union bound. (5 lines)
- Proof 2: modpow invariant (result x base^exp constant) by induction on bits. (5 lines)
- Proof 3: XOR cancellation (p^k)^(q^k) = p^q from associativity/commutativity. (3 lines)

## Exercises with answers
- 1. Trials for 50 percent collision at n = 64? Answer: about 2^32.
- 2. Multiplies for e = 13 (binary 1101)? Answer: 3 squarings + 2 multiplies = 5.
- 3. (HELLO^k)^(WORLD^k) in bytes? Answer: HELLO XOR WORLD byte-wise.

## Pitfalls
- Confusing preimage (2^n) with collision (2^(n/2)) difficulty.
- Counting only squarings and forgetting the conditional multiplies.
- Treating the birthday estimate as a guarantee rather than an expectation.

## Checklist
- Derive the birthday bound from pair counting cold.
- Derive modpow cost from exponent bit-length.
