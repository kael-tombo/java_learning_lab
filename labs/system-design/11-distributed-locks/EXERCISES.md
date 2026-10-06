# Exercises: Distributed Locks

Grounded in `THEORY.md` (why JVM locks fail) and `INTERNALS.md` (Redlock and
fencing tokens). `CODE_DEEP_DIVE.md` contains the runnable Redis simulation.

## 1. Demonstrate the Cross-JVM Failure

Write a `PaymentService` with a `ReentrantLock` guarding a balance check and
decrement. Start five instances against a shared in-memory `Map`. Fire fifty
concurrent payments of 100 from a balance of 1,000.
*Check:* with a local lock, the balance goes negative — every instance has its own
lock, so five threads pass the check simultaneously. This is the bug the lab
exists to explain.

## 2. Minimal Redis Lock

Implement `acquire(key, id, ttl)` as `SET key id NX PX ttl` and `release(key, id)`
as a Lua script that deletes only when the stored value equals `id`.
*Check:* two threads contend for one key; exactly one gets `OK`. The loser's
`release` is a no-op rather than deleting the winner's lock.
*Why the Lua script matters:* a `GET` followed by a `DEL` from the client is two
round trips and has a window between them. The script is atomic.

## 3. TTL Expiry Without Ownership Check

Implement the naive version: `release` deletes the key unconditionally.
*Check:* set a 200 ms TTL, hold the lock for 400 ms, release it. The second thread's
lock is destroyed by the first thread's late release.
*Fix:* the value comparison in `release` — this is the single most common bug in
Redis locks in the wild.

## 4. The GC Pause Race

Simulate a holder that sleeps past its TTL while the lock is expired and
re-acquired elsewhere.
*Check:* two holders in the critical section at the same time. Mutual exclusion is
violated, and no amount of TTL tuning fixes it — the pause is unbounded.
*Conclusion:* a lock without fencing is a hope.

## 5. Redlock Majority Acquisition

Run five independent simulated masters. Acquire by trying each with a short
timeout; succeed only on 3 of 5.
*Check:* with two masters down, acquisition fails correctly. With one master down
it succeeds. Record the majority rule as a function, not as a constant.

## 6. Redlock Release on Partial Failure

Acquire on 3 of 5, then fail, then release.
*Check:* all three held instances are unlocked. A partial release leaves a
stranded lock and blocks every subsequent acquisition for the full TTL.

## 7. Fencing Token Rejection

Implement a store that tracks `lastToken`. Every write carries a token; the store
rejects any token below `lastToken` with a `412 Precondition Failed`.
*Check:* the stalled node's write with token 41 is rejected after token 42 has been
written. The lost update is impossible rather than unlikely.
*Contrast:* replay exercise 4 with fencing and confirm the corruption disappears.

## 8. Clock Drift Measurement

Give each simulated node a clock offset and measure how far the Redlock validity
window shrinks.
*Check:* a 50 ms per-node drift over 5 masters makes a 100 ms window unusable —
there is no elapsed time at which no clock believes another node's lock has
expired. This is Kleppmann's objection to Redlock, demonstrated rather than cited.

## 9. Lease Sizing From Work Duration

Measure the p99 duration of the protected critical section, then set
`requiredTTL > p99Work + clockDrift + networkRTT`.
*Check:* with a 1 s mean and a 5 s TTL, `P(W > T) = e^-5 ≈ 0.67%` — roughly one
lease expiry per 150 acquisitions. At 10,000 acquisitions/s that is a constant
stream of expired leases, and therefore of overlapping critical sections.

## 10. Retry Storm Under Partition

Partition the lock service for 10 seconds while 20 workers retry.
*Check:* all workers retry in lockstep at the same instant. Add exponential
backoff with full jitter and measure the spread.
*Result:* the un-jittered version sustains a 20× burst on a service that is
already unhealthy.

## 11. Database Row Lock Alternative

Implement the same mutual exclusion with `SELECT ... FOR UPDATE NOWAIT` in an
in-memory simulation of two sessions.
*Check:* it is correct with no lease, no TTL, and no fencing — because the lock
lives with the data and is released by the transaction, not by a timer.
*Trade-off:* throughput and cross-store applicability. Note that a long-held
transaction blocks other work on the same rows.

## 12. Idempotency Under Double Acquisition

Wrap the critical section in an idempotency key so that even if mutual exclusion
fails, the effect happens once.
*Check:* force two overlapping executions of a `charge(orderId, 100)` and confirm
the account is debited once.
*Conclusion:* correctness by construction beats correctness by lock discipline.
This is the pattern most production systems should reach first.

## Stretch

- Implement Redlock and run a chaos test that partitions each of the five masters
  in turn; log every mutual-exclusion violation. Expect to find at least one.
- Add fencing to the database row-lock implementation and show the fence is
  redundant there — then argue whether that redundancy is worth the complexity.
- Build a hybrid: Redis for admission control, `SELECT ... FOR UPDATE` plus an
  idempotency key for the write. Measure the throughput cost against a pure
  database lock and against a lock-free idempotent design.
- Write the 200-word argument for why the *correct* answer to most "we need a
  distributed lock" questions is "you need an idempotency key, or you need
  partitioning, or you need to stop sharing state".
