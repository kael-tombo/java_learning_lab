# Math Foundation: Happens-Before as a Partial Order

## hb is a strict partial order (by construction)

Let A be the set of actions. `hb` is the transitive closure of program
order plus synchronization order, minus reflexivity: irreflexive (no
action hb itself), transitive (a hb b and b hb c implies a hb c), and
antisymmetric in the induced ordering. Antisymmetry matters: a cycle
(a hb b hb a) would be contradictory, and the JMM's consistency rules
exclude executions containing one. Intuition: hb is a DAG of "must be
observable in this order" constraints.

## Transitive chains do the work (three-link pattern)

Every demo verdict is one chain. With W = writes, R = release action,
Q = acquire action, D = reads:

```
W --po--> R --so--> Q --po--> D   implies   W --hb--> D
```

- StartEdge: W = 1000 stores, R = Q = start, D = 1000 loads.
- JoinEdge: W = 500 squares, R = Q = join machinery, D = sum loop.
- LatchEdge: W = 3 graph writes, R = countDown, Q = await return.
- LockEdge: 2M links chained (R_i = unlock_i, Q_{i+1} = lock_{i+1}).

If any link is missing, transitivity fails and no constraint reaches D.

## Counting interleavings: why DRF buys understanding

With n threads and k actions each, interleavings grow combinatorially
(roughly (nk)! / (k!)^n before constraints). For 8 threads x 250000
increments that number is astronomically useless. DRF collapses the
analysis: instead of hardware states, enumerate interleavings of atomic
bodies — and for `LockEdge` every interleaving sums to 2000000, so no
enumeration is needed at all. Race-freedom converts a counting problem
into a single invariant (the lock serializes bodies).

## Sequential consistency, stated plainly

An execution is SC iff there exists a total order T over all actions
such that (1) T respects each thread's program order and (2) each read
sees the latest prior write in T. The DRF theorem: race-free executions
always admit such a T. Debugging then means "find the interleaving,"
never "model the store buffers" — the only concurrency mathematics
that fits in a reviewer's head.

## Causality as a well-foundedness constraint

JLS 17.4.8 requires each value to have a causal derivation from writes
in the execution — informally, no value appears "before" its writer in
the justification order. The forbidden `r1 == r2 == 42` outcome (no
write of 42 anywhere) is the canonical violation. The lab probe checks
the contrapositive empirically: 100000 racy samples, all within the
written range, zero exceptions. Values form a closed set under reads;
order within the set is unconstrained.

## Rates vs verdicts (the statistical habit)

Guaranteed demos assert verdicts (equality with 1499500, 41541750,
2000000) over any run count — one run suffices logically, repeats add
confidence in the harness, not the rule. Racy probes assert over rates
(zero invented values in 100000 samples) where the claim is itself
statistical. Never invert the two: a rate (100% green on racy code)
never promotes to a verdict, and a verdict never needs a rate.
