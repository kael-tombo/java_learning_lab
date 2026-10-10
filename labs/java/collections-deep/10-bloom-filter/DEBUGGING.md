# Debugging: Bloom Filter

## Measured FPR far above theory

First suspect: hash quality. Swap in a known finalizer (SplitMix64) and
re-measure at fixed (n, m, k) — non-uniform probes break the formula
before they break the code. Second: verify h2 odd and `long` mod; print
position histograms (all m slots should see ~equal hits; clumping =
step/overflow bug). Third: confirm load ≤ design n (saturation inflates
p silently).

## False negatives (should be impossible)

No sizing or hash bug causes these — only bit-clearing (illicit delete),
union with AND instead of OR (drops bits), or reading a different filter
instance than was written (serialization/parameter mismatch). Audit every
path that writes 1→0; adds and ORs only ever write 0→1.

## Union answers look random

Dump (m, k, hash-seed) on both sides. Any mismatch = invalid merge; the
OR result is meaningless. Also confirm word-length equality — trailing
words beyond min(m₁, m₂) silently dropped is a classic truncation bug.

## Saturation without growth in n

Inserted count matches n but half+ the bits set? k too high (each add
sets too many bits) or duplicate-heavy input colliding onto few positions
(hash finalizer missing). Compare actual set-bit fraction vs predicted
1 − e^(−kn/m) (≈1/2 at optimum) — divergence localizes the cause.

## Intermittent misses across restarts

Hash seed or finalizer changed between builds (different library version,
new funnel) → positions move → old bits unreachable. Pin the hash
strategy and version it alongside serialized filters.
