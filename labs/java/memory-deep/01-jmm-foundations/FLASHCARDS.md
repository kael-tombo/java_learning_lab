# Flashcards: JMM Foundations

Q: What single question does the JMM (JLS 17.4) answer?
A: Which writes a read is allowed to observe.

Q: State the DRF-implies-SC guarantee in one sentence.
A: Correctly synchronized (data-race-free) programs exhibit only
sequentially consistent behaviors.

Q: What is a data race, precisely?
A: Two conflicting accesses (same variable, at least one write) not
ordered by happens-before.

Q: List the six happens-before sources.
A: Program order; monitor unlock->lock; volatile write->read; thread
start/join (+ interruption aliveness); final-field freeze; documented
java.util.concurrent library edges.

Q: `t.start()` hb what, exactly?
A: Everything the new thread does: start() happens-before the thread's
first action (demo: 1000 writes, checksum 1499500, all visible).

Q: `join()` hb what, exactly?
A: The worker's last action happens-before the join() return (demo:
500 squares, sum 41541750, all visible after join).

Q: Monitor rule in six words?
A: Unlock happens-before later lock (same monitor); demo: 8 x 250000
locked increments total exactly 2000000.

Q: Library edge example with the rule?
A: CountDownLatch.countDown() happens-before the return from await();
demo publishes url/timeout/ports through one countDown.

Q: What does causality (JLS 17.4.8) forbid?
A: Out-of-thin-air values: a read can only see a value someone wrote
(demo: 100000 racy samples all in [0, 100000], weird == 0).

Q: Does causality forbid stale or reordered reads?
A: No — staleness, repeats, skips, and backward steps are all legal
without edges; only invented values are banned.

Q: What is "observable behavior" and why does it matter?
A: Synchronization actions plus external effects; two executions with
identical observables are indistinguishable, which licenses every
optimization preserving them.

Q: What did JSR-133 (Java 5, 2004) fix?
A: Rewrote 17.4 with happens-before; fixed volatile; made volatile-DCL
correct; gave final fields publication safety; added causality rules.

Q: Who led JSR-133?
A: Bill Pugh and Jeremy Manson (spec work) with Doug Lea and the JCP
concurrency group; Brian Goetz carried it into practice and books.

Q: Race-free but nondeterministic — contradiction?
A: No: DRF promises SOME interleaving explains the output, never WHICH
one. Final-state assertions (2000000) are correct; schedule assertions
are not.

Q: Which single change breaks LockEdge's exactness?
A: Any access to `count` outside synchronized (same LOCK): it becomes
an unordered conflicting access — a data race by definition.

Q: Sleeps fix visibility bugs — true or false?
A: False: timing changes collision rates, never the verdict. Only an
hb edge changes unordered to ordered.
