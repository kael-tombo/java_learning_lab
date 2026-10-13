# Math Foundation: Anomaly Rates and Ordering Verdicts

## SC impossibility as case analysis

Claim: no SC execution of Dekker yields r1 == r2 == 0. Proof: SC gives
a total order T over {Wx, Wy, Ry, Rx} respecting program order
(Wx < Ry, Wy < Rx). Whichever of Wx, Wy comes first in T, the other
thread's read comes after *both* writes or after its own write at
minimum — in every linear extension at least one read follows the
opposite write, so at least one read sees 1. All extensions yield
(1,0), (0,1), or (1,1). The (0,0) cell has probability exactly 0 under
SC — observing it refutes SC with a single sample.

## Reading the measured rates honestly

Snippet 1's ~79% (and mid-double-digits across configurations) is an
estimate of P(overlap and buffer-hit | rendezvous) on one x86 machine —
not a universal constant. Treat it with the usual sampling respect:
20000 rounds gives sub-percent standard error on the rate, which is
why the 1% assertion bar (`bad > iters / 100`) holds at ~79x margin.
The rate's job is to distinguish "routine" from "rare"; the verdict's
job (nonzero = race) is the portable claim. Never export the 79% to
another machine — export the nonzero.

## Why rendezvous math matters more than core counts

Model each round as: windows of width w (store-to-load gap, ~ns) with
start-time jitter j (handshake spread). P(collision) scales with w/j.
The volatile spin minimizes j (both racers released by one volatile
write, spinning without syscalls); free-running maximizes j (independent
schedulers); barrier phasing adds trip-latency variance to j. Same w,
same buffers, wildly different rates — the harness moves j, the program
determines w. Rates compare harnesses; verdicts compare programs.

## The drain as a one-parameter experiment

Inserting delay d between store and load replaces w with max(0, w - d)
as seen by the buffer: P(anomaly) falls monotonically in d on x86, and
1 ns already reaches zero. A compiler-hoisting theory predicts P flat
in d (same bytecode); the data refutes it. This is the lab's only
equation-shaped argument, and it is deliberately qualitative: the sign
of the derivative, not its value, convicts the buffer.

## Pairwise chains vs total order (counting argument)

Release/acquire gives two directed edges (Wx -> Ry-observed,
Wy -> Rx-observed) but no constraint between the cross observations.
Two chains on four operations admit linear extensions containing
(0,0) — the measured 61-90% says most extensions realize it under
rendezvous. Full volatile adds StoreLoad fences that jointly forbid the
(0,0) extension on every platform: the fence count (0/0/1 across
plain/release/volatile) is the structural variable, and only the last
value closes the cell. Lab 03 prices exactly this step (~1 ns to ~10 ns
on x86).

## Statistical hygiene for the exercises

- Assert verdicts (`bad > iters/100`, `bad == 0`), never exact counts.
- Run each variant at least 3x; report all three counts, not the best.
- Change one variable per comparison (handshake, delay, mode, scope).
- Keep iteration counts fixed (20000) so rates are comparable within
  one machine; never compare absolutes across machines.
