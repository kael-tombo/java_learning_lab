# Quiz: Distributed Locks

15 questions covering `THEORY.md`, `INTERNALS.md`, and `CODE_DEEP_DIVE.md`.
Answers follow.

## Questions

1. Why does a `ReentrantLock` fail to provide mutual exclusion across five service
   instances?
2. What do the `NX` and `PX` arguments of `SET key value NX PX 30000` each do?
3. Why must `release` be a Lua script that compares the value before deleting,
   rather than a plain `DEL`?
4. A holder is paused by a 12-second GC stop with a 10-second TTL. Describe the
   interleaving that violates mutual exclusion.
5. Why can no TTL value fix the GC-pause problem?
6. What is the majority requirement in Redlock, and how many of five instances
   must succeed?
7. Why does Redlock still fail, according to Kleppmann's objection?
8. What is a fencing token, and which component must enforce it?
9. Walk through the fencing sequence: Node A gets token 33, stalls, Node B gets
   token 34, Node A wakes. What happens to each write?
10. With mean work duration 1 s and a 5 s lease, what is the probability that a
    lease expires mid-work, and roughly how often does that occur?
11. What formula should size a lease TTL, and what does the safe-margin ratio
    measure?
12. In the Redlock availability table, what fraction of 5-node configurations keeps
    the lock service available, and why can the lock never be *more* available than
    the operation it protects?
13. Why is a database `SELECT ... FOR UPDATE` fundamentally safer than a
    Redis lease?
14. What is the retry-storm problem, and why does full jitter fix it?
15. Why is an idempotency key a more robust correctness mechanism than a lock, even
    when mutual exclusion is intact?

## Answers

1. Each instance has its own lock object in its own JVM. Nothing is shared, so
   five threads in five processes all pass the check simultaneously and a balance
   can go negative. Mutual exclusion across machines requires shared state —
   a database, Redis, or a consensus service.
2. `NX` means set only if the key does not already exist, which makes acquisition
   atomic and the single point of contention. `PX 30000` sets a 30,000 ms
   time-to-live so a crashed holder cannot hold the lock forever.
3. A plain `DEL` can delete a lock that has since expired and been re-acquired by
   another node, destroying a lock you do not own. The value comparison makes
   release conditional on still holding it. It must also be atomic — a client-side
   `GET` then `DEL` leaves a window between the two round trips.
4. Node A acquires with a 10 s TTL, then stalls. At t=10 s the lock expires. Node
   B acquires it and enters the critical section. At t=12 s Node A resumes, still
   believes it holds the lock, and enters the same critical section. Both
   processes the payment; mutual exclusion is violated.
5. Because a stop-the-world pause or a network partition has no upper bound the
   client can reason about. Any TTL shorter than the worst-case pause is unsafe,
   and a TTL long enough for the worst case makes every crash block the resource
   for that long. The failure is not in the TTL; it is in the lease model itself.
6. A majority — at least 3 of 5 independent masters, acquired sequentially with a
   short per-instance timeout. Failure on a majority means release everything
   acquired and report failure.
7. Clock drift and process pauses. Elapsed time for acquiring and releasing exceeds
   the TTL, so clocks on different nodes disagree about whether a lease is still
   valid, and a paused holder can resume believing it still holds the lock. With
   5 masters and 50 ms drift there may be no elapsed time at which no clock
   considers another node's lock expired.
8. A monotonically increasing integer issued every time the lock service grants a
   lock. It must be enforced by the resource being protected — the database or
   storage layer — which records the highest token seen and rejects anything lower.
   A lock service alone cannot enforce it, because the stalled holder writes
   directly to the store.
9. Node A's token 33: rejected, because the store has already recorded token 34.
   Node B's token 34: accepted. The lost update becomes impossible rather than
   unlikely — the enforcement lives in the store, not in the client.
10. `P(W > T) = e^(-T/mean) = e^-5 ≈ 0.67%` — roughly one lease expiry per 150
    acquisitions. At 10,000 acquisitions per second that is around 67 overlapping
    critical sections per second, assuming nothing else prevents them.
11. `requiredTTL > work_duration_p99 + clock_drift_bound + network_RTT`. The
    safe-margin ratio `TTL / work_duration_p99` measures how much headroom exists;
    a ratio around 3 or more is the usual target, and below 2 the lease is
    marginal.
12. 50% of 5-node configurations keep a majority alive. It cannot be more
    available because the lock sits in the critical path: if the lock service is
    unavailable, the operation cannot proceed regardless — which is why the
    practical conclusion is to avoid needing a lock at all.
13. The lock lives with the data it protects. It is held by the transaction and
    released by commit or rollback, not by a timer, so there is no lease to expire
    and no paused holder. The costs are throughput and the blocking of other work
    on the same rows, plus the practical restriction that the lock does not extend
    across stores.
14. When a dependency is unhealthy, every client retries at once, so the service
    receives a burst proportional to the number of clients precisely when it can
    least afford it. Exponential backoff with full jitter spreads retries over a
    random interval within each window, reducing the burst from all clients to
    roughly one effective concurrent retry.
15. A lock prevents concurrent execution optimistically; an idempotency key makes
    the *effect* happen exactly once regardless. Locks fail open under the failure
    modes above — expiry, pause, partition, split brain — while a deduplicated
    write is correct even when two callers do execute simultaneously. Correctness
    that does not depend on coordination is strictly stronger.
