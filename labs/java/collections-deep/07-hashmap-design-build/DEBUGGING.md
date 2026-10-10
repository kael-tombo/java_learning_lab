# Debugging: Open-Addressing Map

## Phantom miss (get returns null for a present key)

Dump the table with indices and states. Walk the probe from the key's
index by hand: did the walk stop at a DELETED (bug: treating tombstone as
EMPTY) or at a nulled delete-slot (bug: null-on-remove)? Both show as a
premature stop one slot before the key's actual position.

## Table "full" at 60% size

Print `size`, tombstone count, capacity. If tombstones push
`(size+t)/n` past the cap without triggering resize, the trigger formula
is wrong. Fix: include tombstones; verify resize resets the counter.

## Duplicate keys after put

Same key stored twice = probe sequences diverged between puts — either
`hashCode` is nondeterministic across calls (mutable key fields!) or
`get` and `put` use different index functions. Log `hash & (n-1)` for both
calls; they must match.

## Resize loses entries

After resize, iterate old vs new and diff key sets. Usual cause: copying
slots instead of rehashing, or re-applying spread to an already-spread
hash. Re-insert from key objects through the single `indexFor(hash)`
path.

## Latency cliff at fixed size

Benchmark average miss probes vs α and compare with the theory table
(2.5 @ 0.5, ~6 @ 0.7, ~50 @ 0.9). Overshoot means clustering from a weak
spread — check the `^ (h >>> 16)` step is applied exactly once, on the raw
`hashCode`, before masking.

## Infinite probe loop

A probe that never hits EMPTY cycles forever on a full table. Add a
full-cycle guard (steps == n → resize/throw) — open addressing without one
hangs instead of failing.
