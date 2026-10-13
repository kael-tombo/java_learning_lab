# Common Mistakes: Reordering

## 1. Testing races without rendezvous

Free-running racers phase-lock or never collide: both threads loop at
their own pace and the overlap window rarely aligns. Barrier phasing
(`CyclicBarrier` per iteration) aligns *starts* but spreads execution
through the barrier's own synchronization. The lab's volatile-flag
rendezvous (`go`/`done1`/`done2` spins with `onSpinWait`) aligns the
store;load windows tightly enough for ~79% anomaly rates. Copy the
rendezvous design; do not improvise it.

## 2. Calling timing a fix

`DelayDrains` (1 ns `parkNanos` between store and load) prints 0/20000
— and fixes nothing. The program is still racy (no hb edge), and on
ARM the anomaly can survive the delay via compiler/CPU reorderings.
Timing changes *rates*; only edges (volatile, monitor) change the
*verdict*. Ship snippet 2 or 5, never snippet 3.

## 3. Assuming x86 does not reorder

It does exactly one pair: StoreLoad. Dekker *is* that pair, which is
why snippet 1 fires at tens of percent on the "strong" platform. Any
argument of the form "x86 is TSO so plain code is fine" confuses three
preserved pairs with four — the missing one is the one Dekker needs.

## 4. Assuming ARM behaves like x86, only slower

ARM frees in principle every pair and charges differently for fences
(`STLR` release vs `DMB`-fenced store; `LDAPR` acquire loads). Code
that is accidentally green on x86 (plain message-passing, snippet
analogue in lab 03: 0/2000) can fail on ARM where StoreStore is not
preserved. The volatile fix is portable; the accident is not.

## 5. Release/acquire as a volatile substitute for Dekker

`setRelease`/`getAcquire` compose one-directional chains (lab 02
snippet 4's 50000-intact message-passing) but do not build the total
order Dekker demands. Lab 03's snippet 5 measures it: 61-90% anomalies
under release/acquire — race intact. Use release/acquire for
pairwise handoff chains, volatile/locks where a total order is needed.

## 6. Locking the wrong granularity

`MonitorFix` puts each side's store;load pair inside one
`synchronized (LOCK)` block. Locking only the stores (or using two
different locks) leaves the cross pair overlapping — anomaly intact.
Exclusion covers the critical section only; the *pair* must be inside.

## 7. Reading anomaly counts as benchmarks

~79% vs ~36% across runs reflects rendezvous tightness, core count,
frequency scaling, and power state — not code quality. The portable
signal is the verdict: nonzero (racy) vs zero (ordered). Assert
`bad > iters / 100` for the anomaly and `bad == 0` for the fixes, as
the snippets do; never assert an exact count.

## 8. Hoisting paranoia: blaming the JIT for a buffer phenomenon

On this platform the compiler is provably innocent (snippet 3's
elimination argument). Blaming hoisting leads to fixes aimed at the
wrong layer (disabling JIT, `-Xint` validation) that "work" by slowing
everything until buffers drain — the most expensive non-fix available.
