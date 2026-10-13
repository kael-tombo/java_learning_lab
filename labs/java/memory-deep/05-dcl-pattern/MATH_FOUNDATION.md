# Math Foundation: DCL Pattern

## The ordering claim, stated

Let `c` be the constructor's field stores, `w` the volatile publication
write (inside the lock), and `r` any later volatile read at check (1).
Correct DCL establishes:

```
c ->hb w ->hb(sync+volatile) r  ==>  r observes initialized state
```

The first link rides the monitor (construction sequenced before the
write inside the same critical section, plus the lab-04 freeze for the
finals). The second rides the volatile write/read edge (JSR-133) chained
with the monitor exit/entry edges. Either link removed, no conclusion.

## The recheck as a uniqueness argument

Let T1 and T2 both read null at check (1) and serialize on the monitor.
Monitor mutual exclusion orders their critical sections, say T1 then
T2. T1's write hb T1's monitor exit hb T2's monitor entry hb T2's
recheck read. Hence T2's recheck observes non-null and skips
construction: exactly one initialization. Without the recheck, T2's
second entry has no read ordered after T1's write, so it initializes
again — `constructions == 2` follows by construction, not by timing.

## Why the outer check preserves correctness

The outer check reads the volatile and returns early only on non-null.
Any non-null it returns was written by some critical section, hence
ordered after that section's construction. The early return therefore
observes initialized state by the same volatile edge — the fast path
inherits the slow path's proof.

## The single-read refinement

Two volatile reads admit an interleaving the single local forbids:
`r_a == null` (enter lock), publication by another thread, `r_b` reads
the new instance, method returns an object its first check never saw.
With `h` read once, checked object and returned object are identical by
construction — check-then-act skew eliminated syntactically.

## Cost shapes, not thresholds

Per-call cost is structural: DCL pays one acquire (~1 ns framing),
synchronized pays one monitor pair (~20 ns). The crossover call rate is
a hardware-dependent ratio, not a constant — this lab asserts no number
for it. The defensible claim is the shape (fence vs monitor), measured
per platform when the decision matters.
