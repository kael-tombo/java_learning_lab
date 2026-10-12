# Math Foundation: Thread Lifecycle

## State space
- State set S = {NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED}, |S| = 6; exactly one holds per thread at any instant.
- Legal transitions T: NEW->RUNNABLE (start, once); RUNNABLE<->BLOCKED (monitor); RUNNABLE->WAITING/TIMED_WAITING (wait/join/park/sleep); WAITING/TIMED_WAITING->RUNNABLE (event [+expiry]); any->TERMINATED (run ends; sink).

## No-fairness counting
- Among k BLOCKED threads, the winner on release is unspecified: P(any particular thread wins) is implementation-defined, possibly ~0 under starvation. Never compute expected wait from thread count — bound it only with timeouts (tryLock) or fairness-enabled locks.

## Queueing intuition (Little's law, defensible use)
- For a service with arrival rate λ and mean hold time W on one monitor, mean contenders L = λW. Example: λ = 10k/s, W = 50μs -> L = 0.5 waiting on average; double W to 100μs -> L = 1.0. Use to size guards, not to predict exact wakes.

## Sampling math for getState()
- getState() samples an asynchronous 6-valued signal: between your check at t0 and act at t1 the thread may traverse >= 0 transitions, so P(state(t1) = state(t0)) < 1 whenever the thread is live. Any correctness argument conditioned on equality is unsound — this is the formal reason monitoring != control.

## Rule
Every formula above is defended in plain words beside it. No formula here predicts wall-clock time — all bound orderings, counts, or scaling shapes.

## Worked example: Little's law on one monitor
- Setup: requests arrive at λ = 10,000/s; each holds monitor M for W = 50μs of critical section.
- Mean contenders L = λW = 10,000 × 50e-6 = 0.5 threads waiting on average — usually nobody queues.
- Double the section to W = 100μs: L = 1.0 — typically one waiter, and the tail grows long before the mean looks scary.
- Lesson: halving critical-section time halves mean queue depth at fixed arrival rate — the arithmetic behind "shrink the block".
- Guard sizing: provision for several multiples of L (not L itself), because arrivals are bursty and acquisition is unfair — L is a mean, not a max.

## Sampling error, concretely
- Thread T moves RUNNABLE -> BLOCKED -> RUNNABLE inside a 2ms window; you sample `getState()` at t0 and branch at t1 = t0 + 1ms.
- Unless T is dead, P(state(t1) == state(t0)) < 1: the check-then-act gap admits >= 0 transitions, so "if RUNNABLE then assume running" is unsound.
- Formal restatement: `getState()` observes a 6-valued asynchronous signal with no mutual-exclusion coupling to the observer — coordination needs `join`/latch/future edges, not samples.
- Join is the counterexample done right: `t.join()` returns only after TERMINATED is final, so post-join reads need no re-check — finality, not sampling, carries the proof.

## Starvation arithmetic (no fairness, honest bounds)
- k threads BLOCKED on M; each release picks a winner by unspecified policy, so per-release P(you win) has no portable lower bound — worst case 0 over any finite window.
- The only sound bound: bounded entry (`tryLock(t)`, timed `wait`) or documented FIFO fairness converts "eventually" into "within N acquisitions or T ms" — count acquisitions, not threads.
- Design rule: any liveness argument of the form "k waiters, so at most k waits" is rejected unless the lock documents FIFO fairness and you cite it.
- Corollary: BLOCKED-queue length in a dump measures contention pressure, never remaining wait — report it as load, not ETA.

## Daemon-exit counting
- JVM-live set = {non-daemon threads not yet TERMINATED}; exit fires when the set empties — one forgotten non-daemon pool thread keeps it non-empty forever.
- Count exit blockers directly: `Thread.getAllStackTraces().keySet().stream().filter(t -> !t.isDaemon()).toList()` lists exactly the threads holding the JVM open.
- Fix budget: each blocker needs `shutdown()` plus `awaitTermination(T)` or daemonization — count blockers first, then close them one by one.
