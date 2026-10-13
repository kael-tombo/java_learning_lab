# Theory: Hashes and Modular Arithmetic
> Conceptual foundations: what hashes guarantee, how modular powers stay cheap, why key reuse fails.

## Problem statement
- A hash maps arbitrary input to a fixed-size digest; SHA-256 outputs 256 bits.
- Required properties: preimage resistance, second-preimage resistance, collision resistance.
- Modular exponentiation computes x^e mod m for exponents far too large to expand.
- XOR keystream demo shows the mechanism of stream secrecy, not a deployable cipher.

## Hash properties
- Deterministic: same input always gives the same digest; verification recomputes and compares.
- Preimage resistance: given a digest, finding any input that yields it is infeasible.
- Collision resistance: finding two distinct inputs with one digest is infeasible.
- Birthday bound: collisions need about 2^(n/2) trials for n-bit digests - definitional, not measured here.
- One flipped input bit changes about half the output bits (avalanche), which is why tampering shows.

## Square-and-multiply
- Invariant: result times base^exp always equals x^e_original mod m.
- Even exp: square the base, halve exp. Odd exp: shift one factor into result, decrement.
- Every multiply reduces mod m immediately, so values never exceed (m-1)^2.
- Cost O(log e) multiplications; memory O(1). Example: 4^13 mod 497 = 445.

## XOR keystream mechanism
- Ciphertext byte = plaintext byte XOR key byte; decryption applies the same XOR again.
- Correct by involution: (p XOR k) XOR k = p for every byte independently.
- Reuse failure: C1 XOR C2 = P1 XOR P2, the key cancels and plaintext relations leak.
- Lesson: the mechanism is sound, the key management decides secrecy; demos use fixed keys only.

## Correctness arguments
- Hash verification is equality of deterministic recomputation - no probability involved.
- Square-and-multiply follows from the loop invariant by induction on exp steps.
- XOR roundtrip is bitwise involution applied per position.
- None of these argue real-world security; they argue the mechanism is implemented right.

## Complexity derivation
- Hashing streams input once: time O(n) in message bytes, O(1) digest state.
- Modular power: one loop iteration per exponent bit, O(1) work each: O(log e).
- XOR demo: one pass over n bytes: O(n) time, O(n) output.
- Verification costs exactly one extra hash of the same input.

## Variants
- MAC (keyed hash): same machinery plus a secret key gives authenticity - concept only here.
- Digital signatures: private-key operation verifiable with a public key - concept only here.
- Password storage: salt plus slow hash is a separate specialty, named but not built here.

## Pitfalls
- Treating any demo in this lab as deployable cryptography.
- Comparing digests with early-exit equality where timing matters.
- Skipping per-step modular reduction and overflowing silently.
- Reading a Fermat pass as primality proof (see the randomized lab's Carmichael note).

## Interview signal
- State the three hash properties and what breaks when each fails.
- Derive square-and-multiply cost from the exponent-bit loop.
- Show the key-cancellation equation for XOR reuse from memory.
