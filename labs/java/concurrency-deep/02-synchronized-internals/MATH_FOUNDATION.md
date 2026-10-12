# Math Foundation: Synchronized Internals

## Pairing invariant
- For every dynamic entry e (monitorenter, count c_e reentrant depth), exits x satisfy Σx = Σc_e on ALL paths incl. exceptions: the compiler's exception-table monitorexit is the constructive proof. Audit = counting, not hoping.

## Happens-before edge (JLS 17.4)
- unlock(M) -hb-> lock(M) for later acquisitions; with program order (po) on both sides: a -po-> unlock(M) -hb-> lock(M) -po-> b implies a -hb-> b (transitivity). Visibility claims must exhibit this chain with the SAME M; different monitors give no chain — write the M or drop the claim.

## Contention collapse arithmetic
- One monitor, critical section C seconds: max throughput ≤ 1/C ops/s regardless of thread count N. Example: C = 1μs -> ≤ 1M ops/s; N = 64 threads each offering 100k/s (6.4M/s demand) still commit ≤ 1M/s; the rest queue/park. Adding threads past 1/C only grows EntryList depth and park traffic.

## Uncontended vs inflated (orders, defensible)
- Fast path ≈ one mark-word CAS (~10-20ns scale) vs inflated ≈ mutex + park (microseconds + scheduler delay). Ratio ≥ 100x per acquisition episode — the quantitative reason to keep sections tiny and unshared.

## Rule
Every formula above is defended in plain words beside it. No formula here predicts wall-clock time — all bound orderings, counts, or scaling shapes.

## Pairing proof, worked on paper
- Method `inc(boolean boom)` from CODE_DEEP_DIVE.md snippet 1: one `monitorenter` at block entry, `monitorexit` #1 before normal return, `monitorexit` #2 as the exception-table handler target.
- Count: entries E = 1 per invocation; exits X = 1 on every path (normal takes #1, throwing takes #2) — ΣX = ΣE holds path-wise, which is stronger than on-average.
- Reentrant depth d: nested entry on the same monitor by the same thread raises the count to d, requiring d exits — `Thread.holdsLock` plus exit counting is the audit, not code review vibes.
- Consequence: "throwing leaks the monitor" has no legal bytecode execution — the claim is refuted by construction, and any leak report means hand-patched or pre-verification bytecode.

## Throughput ceiling, worked twice
- Guard G with critical section C = 1μs: ceiling = 1/C = 1M ops/s. Offered load N = 64 × 100k/s = 6.4M/s still commits ≤ 1M/s; the excess parks in `_EntryList`/`_cxq`.
- Shrink C to 250ns (move formatting and I/O out): ceiling = 4M ops/s — a 4x capacity gain with zero extra threads, purely from section arithmetic.
- Split one guard into two independent guards (disjoint invariants): each keeps its own 1/C ceiling — aggregate 2/C, the quantitative case for guard splitting.
- Fairness note: no FIFO promise means per-thread share is unspecified — size timeouts and queue bounds from the ceiling, never from "N threads so each gets 1/N".

## Cost-ratio derivation (orders, defensible)
- Fast path ≈ one mark-word CAS ≈ tens of ns (~10-20ns scale after warmup); inflated path ≈ mutex + park/unpark ≈ microseconds plus scheduler delay.
- Ratio per acquisition episode ≥ 100x — so one accidental inflation episode (e.g. logging inside the block under load) dominates a million fast-path acquisitions in the budget.
- Elision ratio is infinite in the limit: a removed lock costs 0ns — which is why escape analysis (keeping guards thread-local) beats every hand-optimization of the locked body.
- Coarsening math: k adjacent same-monitor blocks cost ~k CAS episodes; merged they cost ~1 — batching adjacent guarded updates is a divisor, not a tweak.

## Visibility chain, symbolically
- Same-monitor publication: w(X) -po-> unlock(M) -hb-> lock(M) -po-> r(X) ⟹ r(X) observes w(X) — write the M or drop the claim.
- Different monitors M1 ≠ M2: unlock(M1) and lock(M2) compose to nothing — no hb arrow exists, so same-fields-different-locks is a race wearing a disguise.
- wait/notify piggyback: notifier's writes -po-> notify (under M) pair with waiter re-acquiring M after `wait()` — post-`wait()` reads see pre-`notify()` writes on the same monitor.
