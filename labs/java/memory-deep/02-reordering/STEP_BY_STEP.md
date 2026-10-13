# Step by Step: Measure, Eliminate, Fix

## Goal

Five runs, five verdicts: nonzero (anomaly), zero (volatile), zero
(drain — diagnostic), intact chain (release/acquire), zero (monitor).
Under an hour on any x86-64; verdicts portable beyond it.

## Step 1: run the anomaly (nonzero)

1. Open `DekkerAnomaly`: two daemon racers, volatile `go`/`done`
   handshake, plain `x`/`y`, main driver over 20000 rounds.
2. Compile and run with warmed JVM (one throwaway run first).
3. Confirm `forbidden (0,0) outcomes = bad/20000` with large `bad` and
   `reordering observed on real hardware: true`.
4. Record your count: this machine's signature. Do not compare it with
   anyone else's — compare only later verdicts on this machine.

## Step 2: volatile fix (zero by ordering)

1. Open `VolatileFix`: identical except `static volatile int x, y`.
2. Run three times; confirm `0/20000` and `volatile ordering holds:
   true` every time.
3. Note what did *not* change: threads, handshake, iteration count.
   The delta is two keywords — ordering semantics, nothing else.

## Step 3: drain test (zero by timing — diagnostic only)

1. Open `DelayDrains`: snippet 1 plus `parkNanos(1)` between each
   store and load.
2. Run; confirm `0/20000` and `drain delay eliminates: true`.
3. Write the elimination sentence: same bytecode, only timing changed,
   so the buffer (not compiler/CPU) is the x86 mechanism. Then swear
   the oath: never ship this variant.

## Step 4: release/acquire chain (intact — sufficient, not universal)

1. Open `ReleaseAcquire`: plain `data` plus `FLAG.setRelease` /
   `FLAG.getAcquire` over 50000 sequence steps.
2. Run; confirm `release->acquire chain intact over 50000: true`.
3. State the scope aloud: one-directional chains hold — this is the
   shape release/acquire is *for*. Dekker is not that shape (lab 03
   snippet 5: 61-90% under the same modes).

## Step 5: monitor fix (zero by exclusion)

1. Open `MonitorFix`: each store;load pair inside
   `synchronized (LOCK)`.
2. Run three times; confirm `0/20000` and `mutual exclusion forbids
   the anomaly: true`.
3. Compare with step 2: same zero, different mechanism (no overlap vs
   fenced overlap). Choose per shape: flags want volatile, shared
   updates want the lock.

## Step 6: lock in the ladder

Fill one card: anomaly nonzero / volatile 0 / drain 0 (not a fix) /
chain intact / lock 0 — each with its mechanism word (buffer,
ordering, timing, chaining, exclusion). Carry it to lab 03, which
prices every row.
