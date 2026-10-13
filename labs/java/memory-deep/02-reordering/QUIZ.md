# Quiz: Reordering

## Q1: What outcome does SC forbid for Dekker, and why?

**Answer:** r1 == r2 == 0. In any total order respecting both threads'
program orders, at least one load follows the opposite store, so at
least one read sees 1. The (0,0) cell has probability exactly 0 under
SC — one observation refutes SC for the platform.

## Q2: Snippet 1 prints forbidden (0,0) in ~79% of 20000 rounds. Verdict?

**Answer:** Racy, as designed: nonzero anomalies prove StoreLoad
reordering is routine on this x86. The 1% bar (`bad > iters / 100`)
holds at ~79x margin; the exact count is machine-specific, the nonzero
verdict is portable.

## Q3: Same bytecode + 1 ns parkNanos drain prints 0/20000. What is proven?

**Answer:** The store buffer is the mechanism on x86. Compiler and OoO
theories predict no change from timing alone (identical instructions);
the buffer theory predicts exactly this (FIFO drains before the load).
Diagnostic, not a fix — the program is still racy (no hb edge).

## Q4: Free-running variant shows ~0% anomalies. Fixed?

**Answer:** No: collision rate collapsed (phase-lock/misses), verdict
unchanged (still no edge). Rate is a harness property; race is a
program property. Restore the volatile-flag rendezvous and the
anomalies return.

## Q5: Volatile-both-fields prints 0/20000. Mechanism?

**Answer:** Ordering: volatile stores emit the StoreLoad fence
(`XCHG` on x86) and the JMM SC-for-volatiles rule forbids exactly the
exhibited pair — portably, on every platform, same source.

## Q6: Monitor variant prints 0/20000. Same mechanism as Q5?

**Answer:** No: exclusion, not ordering. Each store;load pair runs
inside one `synchronized (LOCK)`, so the pairs never overlap — no
simultaneity for the buffers to exploit. Same zero, different reason.

## Q7: Release/acquire Dekker still shows 61-90% anomalies. Explain.

**Answer:** Pairwise chains do not compose into a total order: each
release->acquire pair orders locally while the cross observations slip
through the buffers. Sufficient for message-passing (snippet 4: 50000
intact), insufficient for mutual observation. Only full volatile (both
sides) or exclusion closes Dekker.

## Q8: Which TSO pair escapes on x86, and what passes by accident?

**Answer:** Only StoreLoad escapes (Sewell et al., 2010). Plain
message-passing (`data` then `flag`) passes on x86 because StoreStore
is preserved — accident of the table, fail on ARM where it is not.
Dekker needs the one freed pair and fails loudly on the same machine.
