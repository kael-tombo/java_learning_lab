# Why Number Theory Matters

## It Is the Foundation of Every Secure Connection

TLS handshakes, code signing, SSH, and encrypted messaging rest on number theory: RSA (factoring), Diffie–Hellman (discrete log), and elliptic-curve systems (group structure over a curve). Choosing a key size, an exponent e = 65537, and 40 Miller–Rabin rounds are all number-theoretic parameter choices — made wrong, the scheme is broken regardless of how well the protocol is engineered. A developer who cannot read those parameters cannot review a crypto implementation.

## Hashing, Checksums, and IDs Use Modular Arithmetic

- Java's `HashMap` spreads `hashCode()` with `h ^ (h >>> 16)` and indexes `(n−1) & hash` — bucket selection is arithmetic mod a power of two.
- Rolling hashes (Rabin–Karp) compute Σ cᵢ·bⁱ mod m, enabling substring search in O(n) expected time.
- Luhn, CRC, and IBAN checks are divisibility tests (mod 10, mod polynomial) — trivially forgeable by design, which is why they detect typos, not tampering.
- Snowflake-style IDs pack timestamps into integers and must reason about wraparound — a modular-arithmetic boundary condition.

## Scheduling, Hashing, and Cache Design Are Congruence Problems

Power-of-two table sizes, circular buffers, and ring indexes are all ℤ/2ᵏℤ; double hashing in open addressing uses a second step coprime to the table size *precisely* so the probe sequence covers every slot (gcd(step, size) = 1 — invertibility again). A developer who knows why table sizes are prime (or a power of two with a coprime step) designs probes that don't alias.

## It Trains the "Check Your Preconditions" Reflex

Every theorem in this lab has a hypothesis you can violate: Fermat needs p prime and gcd(a, p) = 1; CRT needs pairwise-coprime moduli; Euler needs gcd(a, n) = 1; Dijkstra-style reasoning needs nonnegativity (lab 04). The 561 Carmichael example and the 2⁻¹ mod 7 confusion are reminders that the *shape* of a correct-looking computation is not its correctness. Those preconditions map 1:1 onto function contracts in code.

## Computing Sides With It: Easy Forward, Hard Backward

Primality: trial division O(√n) vs factoring's best sub-exponential algorithm — the asymmetry that makes key generation workable and attacks infeasible. This "easy direction / hard inverse" pattern appears throughout systems (hashing vs collision search, trapdoor permutations, commitment schemes), and number theory is the cleanest place to internalize it.

## Algebra and Crypto Share the Same Machinery

GCD/extended Euclid is the workhorse behind polynomial GCDs (compiler algebra, error-correcting codes), inverse elements in finite fields (AES S-box inversion in GF(2⁸)), and CRT-based big-int arithmetic (`BigInteger.modPow` internals). BCH/Reed–Solomon codes — protecting CDs, QR codes, and storage — are polynomials over finite fields, i.e., the same theory applied mod a polynomial instead of mod an integer.

## It Connects to Everything Earlier in the Course

- Set theory (lab 02): Z/nZ is a *set* with two operations; units form a subset closed under multiplication.
- Combinatorics (lab 03): φ(n) is a counting function; inclusion–exclusion derives Π(1 − 1/p).
- Graph theory (lab 04): the state graph of repeated multiplication mod n; cycle structure = order of an element.
- Generating functions (lab 05): divisor sums and partition identities are coefficient identities.

The curriculum is not five topics — number theory is where their tools get applied to integers, which is where correctness is checkable by hand and where the stakes (cryptography) are highest.
