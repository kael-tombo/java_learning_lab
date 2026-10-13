# How It Works: JMM Foundations

## The mechanism in one paragraph

Every demo in this lab is a happens-before chain: program order links
writes to a release action, a synchronization rule links release to
acquire across threads, program order links acquire to the reads. The
JIT and CPU may reorder anything *except* across those links. Follow
the links and the exact numbers (1499500, 41541750, 2000000) stop being
surprising — they are what the chain forces.

## StartEdge: 1499500, link by link

1. Main thread: 1000 element writes, program-ordered before `start()`.
2. `t.start()` hb the child's first action (JLS thread-start rule).
3. Child: 1000 reads, program-ordered after its first action.
4. Transitivity (hb is a transitive closure) orders every write before
   every read. Checksum must equal 1499500: sum of `i * 3 + 1` over
   1000 elements. No volatile, no lock — the lifecycle edge alone.

## JoinEdge: 41541750, the mirror

1. Worker: 500 writes (`result[i] = i * i`), program-ordered before exit.
2. Worker's last action hb the `join()` return (JLS join rule).
3. Main: sum loop, program-ordered after `join()`.
4. Every square is visible; sum must equal 41541750. Start and join
   compose a round trip: main-to-worker then worker-to-main, which is
   why thread-per-task handoffs need no other synchronization.

## LockEdge: 2000000, the chain

1. Each `synchronized (LOCK)` body is one link: unlock hb the next lock
   of the same monitor (JLS monitor rule).
2. 2M unlocks chain into one total order across 8 threads — mutual
   exclusion (no two bodies overlap) plus visibility (each body sees
   all prior bodies).
3. Count must equal 2000000 exactly. Contrast volatile++ (same threads,
   no exclusion): millions of lost updates, because ordering without
   atomicity cannot fix read-modify-write.

## LatchEdge: publication without locks

1. Writer: `url`, `timeout`, `ports` writes, program-ordered before
   `countDown()`.
2. `countDown()` hb the `await()` return (documented j.u.c. rule).
3. Reader: field reads, program-ordered after `await()`.
4. All four field checks pass. The latch is a one-shot edge: same
   release/acquire skeleton as volatile, packaged for startup handoff.

## CausalityFloor: the guarantee below the guarantees

With no edge at all (plain `box[0]` writer/reader, 100000 iterations),
the reader sees arbitrary staleness — repeats, skips, backward steps —
but every value lies in `[0, 100000]` and the out-of-range counter stays
0. JLS 17.4.8 requires a causal derivation for each value: speculation
may reorder real writes early, never invent constants from nowhere. The
floor holds precisely so that racy code is unpredictable but never
magical.

## The invariants to carry forward

- No hb between conflicting accesses means race, full stop — output
  anecdotes cannot overrule the verdict.
- Hb composes transitively; draw the three links (write -> release ->
  acquire -> read) for any handoff before trusting it.
- Causality bounds values, edges bound order; most bugs confuse the two.
