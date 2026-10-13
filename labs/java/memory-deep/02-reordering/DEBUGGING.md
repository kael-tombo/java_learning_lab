# Debugging: Reordering

## Confirm the anomaly is real before explaining it

Run `DekkerAnomaly` for the full 20000 iterations and check the ladder:
`bad > iters / 100` must print `true` with margin (measured up to ~79%,
i.e., ~79x the bar). A handful of anomalies in 20000 still counts as
real (verdict nonzero) but suggests loose rendezvous — tighten before
drawing mechanism conclusions.

## Checklist when (0,0) never appears (but should)

- Rendezvous intact? Both racers must spin on volatile `go`, signal
  volatile `done1`/`done2`, and the driver must reset `x = y = 0`
  before each `go = true`. A missed reset or a non-volatile flag
  collapses the window.
- Free-running by accident? If the racers loop without the
  go/done handshake, they phase-lock: add the handshake back.
- Barrier-phased? `CyclicBarrier` per iteration aligns starts, not the
  store;load windows — the barrier trip itself spreads execution.
  The volatile-flag spin is tighter; keep it.
- Single core or power-saving? Fewer cores and parked frequencies
  shrink the overlap window. Vary `-XX:ActiveProcessorCount` and let
  frequency settle; compare verdicts, not counts.
- `-Xint` or cold JIT? Interpreted execution drains buffers between
  bytecodes incidentally. Run warmed, TieredCompilation on — the
  production shape.

## Checklist when the fix still shows anomalies

- Volatile on *both* fields? One volatile side still races (the plain
  side's StoreLoad still escapes). Snippet 2 volatiles both `x` and `y`.
- Rendezvous flags disturbed? The `go`/`done` flags must stay volatile
  in every variant — making them plain to "simplify" reopens hoisting
  of the spin itself.
- Release/acquire mistaken for volatile? `setRelease`/`getAcquire`
  Dekker still prints 61-90% anomalies (lab 03 snippet 5): expected,
  not a bug in the harness. Escalate to full volatile or a lock.
- Lock scope shrunk? Each side's store *and* load must sit inside the
  same `synchronized (LOCK)`; locking stores only is still racy.

## Telling layers apart (the elimination protocol)

1. Baseline: snippet 1, record anomaly verdict (nonzero).
2. Drain test: insert `LockSupport.parkNanos(1)` between store and load
   (snippet 3). Anomaly gone with identical bytecode ⇒ store buffer
   (layer 3) on x86. Anomaly persists ⇒ suspect compiler/CPU layers
   (expected on ARM: use volatile and compare).
3. Edge test: volatile both fields (snippet 2) ⇒ must read 0/20000 on
   every platform. If not, the harness (not the hardware) is broken.

## Tools

- jcstress for histograms when iteration counts in hand-rolled drivers
  are questioned; `-XX:+PrintAssembly` (hsdis) to confirm the racer
  bodies still contain plain store;load with no extra fences in
  snippet 1; `taskset`/processor-count flags to vary topology.

## What NOT to do

Do not "fix" with sleeps, do not benchmark anomaly percentages across
machines, and do not assert exact counts in tests — assert the verdict
ladder (nonzero vs zero) exactly as the snippets print it.
