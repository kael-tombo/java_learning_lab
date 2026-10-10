# Common Mistakes: Bloom Filter

## 1. Deleting by clearing bits

Unsets bits shared with other elements → false negatives, the one error
the structure forbids. Use a counting variant (4-bit counters, saturating
at 15) if removal is required.

## 2. Using raw hashCode as h1/h2

`String.hashCode` (31-multiplier) has weak low bits — probes correlate,
measured FPR overshoots theory. Always run a 64-bit finalizer first, then
split halves.

## 3. Even h2

`g_i = h1 + i·h2` with even h2 cycles through a fraction of the array —
half the bits unreachable, local saturation. Force `h2 | 1`.

## 4. Int overflow in position math

`h1 + i*h2` overflows `int` for large i/h2; negative mods crash or bias.
Compute in `long` with unsigned halves, mod m last.

## 5. More k = better

Past optimum, extra hashes saturate the array and FPR *rises* (7: 1.0% →
10: 1.3% canonical). Derive k from m/n; verify empirically.

## 6. Union of mismatched filters

OR-ing filters with different (m, k, hash) yields confident garbage.
Check parameter equality first (Guava enforces this in `putAll`).

## 7. Treating "possibly present" as "present"

Gating a destructive/irreversible action on an unconfirmed hit (delete,
block, bill) turns 1% FPR into 1% wrongful actions. Hits need exact
confirmation; only misses are actionable alone.
