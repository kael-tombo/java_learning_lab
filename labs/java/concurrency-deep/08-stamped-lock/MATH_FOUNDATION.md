# StampedLock — Math Foundation

## Version equality as consistency proof

Let `V(t)` be the version bits of `state` at time `t`. Writer release
events strictly increment `V` (mod 2^k for a k-bit sequence field). An
optimistic read samples `s = V(t0)`, copies fields during `[t0, t1]`, then
checks `s == V(t1)` after a load fence. If no write release occurred in
`(t0, t1)`, `V` is constant there, so the copied fields experienced no
concurrent completed write — the snapshot is consistent. Any completed
write changes `V`, failing the check. (Overlapping but uncompleted writes
are excluded by the 0-stamp rule: sampling under write hold yields 0.)

## Failure probability model

Assume writers complete as a Poisson process with rate `w` per second and
the optimistic window (sample to validate) lasts `T` seconds. Then:

```
P(fail) = 1 - e^(-wT)  ~=  wT   (for wT << 1)
```

Short sections (small `T`) and rare writes (small `w`) keep `P(fail)` near
zero — the regime optimism is built for. Doubling section length doubles
the failure rate linearly; doubling writer rate does the same. Expected
cost per read is `C_opt + P(fail) * C_fallback`, which beats `C_readlock`
exactly while `P(fail)` stays small. No universal crossover exists; measure
`w` and `T` on the target machine.

## Why the fence matters (ordering, not just timing)

Without the load fence, the CPU could reorder field reads after the version
re-read, so `V(t0) == V(t1)` would no longer bracket the copies — a write
could land between the version check and the (reordered) field read and go
undetected. The fence enforces sample -> copy -> re-check order, which is
what makes the equality argument sound on real hardware (JLS 17.4).

## Sequence wrap and the 1-year bound

With a k-bit sequence advanced once per write cycle at rate `w`, wrap time
is `2^k / w`. The javadoc's "no sooner than one year" is a lower bound on
this quantity for any plausible `w`, meaning a stamp validated promptly
cannot alias a wrapped-around version. Only stamps held unvalidated across
absurd durations risk spurious success — hence validate-then-act quickly.

## Reader-count arithmetic

Reader acquisition adds `RUNIT` to `state`; release subtracts it. The
sole-reader conversion CAS succeeds exactly when the reader field equals
one unit and no write bit is set — an exact integer condition, which is why
contended conversion deterministically returns 0 rather than waiting.

## CAS contention scaling

Pessimistic read acquisition CAS-fails under concurrent readers at a rate
growing with fan-out (all writers target one word). Optimistic sampling
performs zero writes to shared state, so its coherence cost is one read
miss at most — O(1) per reader regardless of fan-out. That is the whole
throughput argument, formalized.
