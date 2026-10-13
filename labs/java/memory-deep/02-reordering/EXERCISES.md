# Exercises: Reordering

All exercises use JDK 9+, no dependencies, x86-64 for rates (verdicts
portable). Keep the volatile-flag rendezvous unless told to remove it.

## 1. Establish the baseline

Run `DekkerAnomaly` (20000 iters) three times. Record each `bad` count
and confirm `reordering observed: true` every run. Expect a large
fraction (tens of percent; up to ~79% measured) — the exact number does
not matter, the margin over the 1% bar does. Write down your three
counts: they are your machine's signature for later comparison.

## 2. Hide it without fixing it (free-running)

Remove the `go`/`done` handshake so both racers loop freely, keeping
plain `x`/`y` and the store;load bodies. Run 20000 iterations. The
`(0,0)` count collapses (often near zero) with *zero* change to the
verdict — the program is identically racy. Deliverable: one paragraph
on why collision rate is a property of the harness and the race is a
property of the program.

## 3. Hide it differently (barrier phasing)

Restore plain racers but synchronize iterations with a `CyclicBarrier`
(align starts). Run and compare with exercise 1's counts: fewer
anomalies, same verdict. Explain why aligning starts spreads the
critical windows (the barrier trip itself is synchronization with
variable latency) while the volatile spin holds them tight.

## 4. Prove the buffer (drain test)

Insert `LockSupport.parkNanos(1)` between each store and load
(`DelayDrains`, snippet 3). Run three times; confirm `0/20000` and
`drain delay eliminates the anomaly: true`. Then write the elimination
argument in two sentences: same bytecode emitted, only timing changed,
so neither compiler hoisting nor OoO issue can be the mechanism here.

## 5. Fix it twice, compare the mechanisms

Run `VolatileFix` (both fields volatile) and `MonitorFix` (pair under
one lock): confirm `0/20000` for both, three runs each. Then answer:
which fix works by *ordering* (fences on both sides) and which by
*exclusion* (no overlap at all)? Which would you ship for a two-flag
protocol, and why is the drain of exercise 4 never an acceptable
third option?

## 6. Release/acquire Dekker (chains are not total orders)

Convert the racers to `VarHandle.setRelease`/`getAcquire` (lab 03
snippet 5's `RaDekker` shape) and run 20000 iterations. Confirm
anomalies persist at high rates (measured 61-90% — race intact).
Contrast with snippet 4's `ReleaseAcquire` (50000-intact
message-passing chain): same access modes, opposite verdicts. Write
the three-sentence explanation: pairwise chains compose for
message-passing; Dekker needs a total order; only StoreLoad fences on
both sides (full volatile) or exclusion supply it.

## Done when

You can predict, before running, whether a variant prints nonzero or
zero — for free-running, barrier-phased, drained, volatile, locked,
and release/acquire shapes — and derive each prediction from the
store-buffer mechanism plus the TSO pair table.
