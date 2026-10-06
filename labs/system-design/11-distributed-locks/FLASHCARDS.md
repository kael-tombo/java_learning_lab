# Flashcards: Distributed Locks

60 quick-reference cards. Format: `Q:` question | `A:` answer.

## The Problem
1. Q: Why does `ReentrantLock` fail across service instances? | A: Each JVM has its own lock; nothing is shared, so all pass the check.
2. Q: What is a distributed lock? | A: Mutual exclusion whose state lives in a shared external store.
3. Q: Which stores are commonly used? | A: Relational DB (`FOR UPDATE`), Redis (`SET NX PX`), ZooKeeper/etcd/Consul (consensus).
4. Q: What is the symptom of getting this wrong? | A: Double-charging, oversold inventory, negative balances — duplicate effects.
5. Q: What does mutual exclusion require? | A: Agreement on who holds the lock — so a lock is a consensus problem in disguise.
6. Q: Lock safety vs availability? | A: Safety is binary and non-negotiable; availability is traded against it.

## Redis Basics
7. Q: How do you acquire a Redis lock? | A: `SET resource_name unique_id NX PX 30000`.
8. Q: What does `NX` do? | A: Set only if not exists — makes acquisition atomic.
9. Q: What does `PX` do? | A: Sets the TTL in milliseconds, so a crash cannot hold the lock forever.
10. Q: What does Redis return on successful acquire? | A: `OK`. `NULL` means another node holds it.
11. Q: What must the value be? | A: A unique per-acquisition ID (UUID), never a constant like `"lock"`.
12. Q: How do you release a Redis lock? | A: A Lua script: delete the key only if its value equals your ID.
13. Q: Why must release be atomic? | A: A client-side `GET` then `DEL` leaves a race window between round trips.
14. Q: What does a plain `DEL` on release risk? | A: Deleting a lock that expired and was re-acquired by someone else.
15. Q: Why is `SETNX` alone insufficient? | A: It has no TTL — a crashed holder deadlocks the resource permanently.
16. Q: Why not use `SETNX` then `EXPIRE`? | A: Two round trips; a crash between them leaves a permanent lock.
17. Q: Do `GETSET` and `SETNX` differ in atomicity? | A: No. Both are single atomic commands.

## Leases and Failure Modes
18. Q: What is the lease model? | A: The holder must finish before the TTL expires, or correctness is lost.
19. Q: Lease sizing formula? | A: `requiredTTL > work_p99 + clock_drift_bound + network_RTT`.
20. Q: Safe margin ratio? | A: `TTL / work_p99` — target 3× or more.
21. Q: Why no TTL fixes a GC pause? | A: Pause duration is unbounded; any lease is either unsafe or impractically long.
22. Q: Walk the GC-pause race. | A: A holds, stalls, lease expires, B acquires, A resumes and also enters — both in the critical section.
23. Q: What is the lease-expiry probability formula? | A: `P(W > T) = e^(-T / mean_work_duration)`.
24. Q: `e^-5` with a 1 s mean and 5 s TTL? | A: 0.67% — about 1 in 150 acquisitions.
25. Q: Why do retries need exponential backoff *and* jitter? | A: Backoff spreads demand; jitter desynchronises clients so they do not retry together.
26. Q: What is a retry storm? | A: All clients retry simultaneously, burdening a service that is already unhealthy.
27. Q: What is full jitter? | A: Random delay within `[0, min(cap, base·2^k)]` — not just a fixed schedule.

## Redlock
28. Q: What problem does Redlock solve? | A: Single Redis master is a single point of failure; async replication can lose a lock.
29. Q: The exact failure Redlock addresses? | A: A acquires on master, master crashes before replicating, replica is promoted, B is granted — both hold it.
30. Q: How many independent masters in Redlock? | A: 5, with no replication between them.
31. Q: Redlock majority requirement? | A: At least 3 of 5 must grant the lock.
32. Q: How are the masters contacted? | A: Sequentially, each with a very short timeout.
33. Q: What if a majority fails? | A: Release everything acquired and report failure.
34. Q: Why must partial acquisition be rolled back? | A: A stranded lock blocks every later acquisition for the full TTL.
35. Q: Redlock availability with 5 nodes? | A: 50% of configurations keep a majority alive.
36. Q: Why is the lock never more available than its critical section? | A: The lock sits in the critical path — no lock, no operation.
37. Q: Kleppmann's objection to Redlock? | A: Clock drift and process pauses; there may be no instant when all clocks agree the lease is valid.
38. Q: Does Redlock prevent the double-write? | A: No. It reduces windows; fencing tokens eliminate the possibility.

## Fencing Tokens
39. Q: What is a fencing token? | A: A monotonically increasing integer issued on each grant.
40. Q: Who must enforce the token? | A: The database or storage system — the resource being protected.
41. Q: Why can't the lock service enforce it alone? | A: The stalled holder writes directly to the store, bypassing the lock service.
42. Q: How does the store use the token? | A: Records the highest seen and rejects any write with a lower token.
43. Q: Rejection status code? | A: `412 Precondition Failed` (or equivalent in storage APIs).
44. Q: Redlock + fencing — what is the residual risk? | A: Essentially none for the stalled-write case; partitions and operator error remain.
45. Q: What does fencing eliminate that TTLs cannot? | A: The split brain where two holders both believe they own the lock.

## Database Locks
46. Q: How do you lock a row in a database? | A: `SELECT ... FOR UPDATE NOWAIT` inside the transaction.
47. Q: Why is this fundamentally safer? | A: The lock lives with the data; no timer, no lease, no paused holder.
48. Q: When is it released? | A: On commit or rollback — not by expiry.
49. Q: `NOWAIT` vs `WAIT`? | A: `NOWAIT` fails fast with ORA-00054; `WAIT n` blocks up to n seconds.
50. Q: Main drawbacks? | A: Throughput, blocking other work on the same rows, and no cross-store reach.
51. Q: Can a DB lock replace a distributed lease for payments? | A: Often yes, if the state is in that database.

## Idempotency
52. Q: What is an idempotency key? | A: A unique request ID that makes a repeated operation apply its effect once.
53. Q: Why is it stronger than a lock? | A: Locks fail open under expiry, pause, and partition; idempotency is correct even if two run.
54. Q: Does a lock guarantee exactly-once? | A: No. It guarantees at-most-one concurrent execution at best.
55. Q: Does idempotency replace mutual exclusion? | A: It replaces correctness, not exclusion — side effects still need care.
56. Q: Typical answer to "we need a distributed lock"? | A: "You need an idempotency key, partitioning, or less shared state."

## Choosing
57. Q: Prefer which store when? | A: DB for small scale, Redis for speed with fencing, consensus for strong guarantees.
58. Q: Rule of thumb on need? | A: If you cannot state the fencing token check, you do not have a correct lock.
59. Q: Rule of thumb on scope? | A: If the lock is on the critical path, redesign before tuning it.
60. Q: How do you prove a lock correct? | A: Chaos tests that partition every node in turn and count mutual-exclusion violations.
