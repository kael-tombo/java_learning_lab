# StampedLock — Performance

## Cost model per operation

- `tryOptimisticRead`: one volatile read (~L1/L3 latency on uncontended
  state, no CAS, no fence on issue). Cheapest acquire in `java.util`.
- `validate`: one load fence plus one volatile re-read. Cheap, but not
  zero — don't validate in a tight loop per field; validate once per
  snapshot.
- `readLock`/`writeLock`: CAS plus possible park/unpark. Same order as any
  queued lock; reader-reader CAS storms are the cost optimism avoids.
- `unlock(stamp)` generic: branch on stamp bits, marginally slower than
  `unlockRead`/`unlockWrite`. Use typed unlocks on hot paths.
- `asReadLock`/`asWriteLock` views: adapter overhead (stamp stash/lookup)
  per lock/unlock. Prefer raw stamps where nanoseconds matter.

## When optimism wins (CODE_DEEP_DIVE snippet 2)

No writers: zero fallbacks observed — every read pays only sample + fence.
Rare writers: occasional fallback, still far below pessimistic cost. Rule of
thumb: optimism wins while `P(fail) * C_fallback < C_readlock - C_opt`, i.e.
while writer rate times window length stays small (see MATH_FOUNDATION).

## When optimism loses

- **Hot writers**: most attempts fail validation, so reads pay optimistic
  attempt + full pessimistic fallback — strictly worse than read-locking
  directly. Switch to plain `readLock()` past the measured crossover.
- **Long sections**: wide sample-to-validate windows catch more writers;
  keep optimistic bodies to a handful of field copies.
- **False sharing**: the guarded fields and hot writer targets should not
  share cache lines with unrelated atomics; pad or isolate writer targets.

## Measurement harness guidance

Benchmark with JMH, not wall-clock loops: `Blackhole` the read results
(else the JIT eliminates the read), vary reader count (1/2/8/32) and writer
share (0/1/5/20%), and report p99 alongside mean — optimism's win is mostly
a tail-latency win (no parking on the read path). Always include a
`ReentrantReadWriteLock` baseline on the same workload.

## Tuning checklist

1. Keep optimistic bodies minimal: copy locals, validate, then compute.
2. Validate once per snapshot, not per field.
3. Use typed unlocks; reserve generic `unlock` for converted stamps.
4. Reuse the conversion path for inspect-then-mutate instead of
   release-reacquire cycles.
5. Reconsider the lock entirely (striping, immutability, copy-on-write)
   before micro-tuning stamp calls — lock choice dominates call shape.

## NUMA and multi-socket note

Optimistic readers issue no writes to the state line, so the line stays
Shared across sockets instead of bouncing in Modified state. The benefit is
largest exactly where cross-socket CAS is most expensive — measure on the
deployment topology, not just a laptop.
