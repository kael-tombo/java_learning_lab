# Distributed Locks - MINI PROJECT

## Project: Break a Distributed Lock, Then Fix It Properly

**Time**: 8-12 hours

**Goal**: Build a Redis-style lease, break it in three realistic ways, then
rebuild it with fencing tokens and show the damage is now impossible.

### Step 1: The Naive Lease (1 h)

Implement the version from `CODE_DEEP_DIVE.md`:

```java
set(key, token, NX, PX, ttl)   // acquire
// DEL key                                 // WRONG release
```

Add an in-memory fake Redis with a TTL scheduler so you can control time.
Deliverable: it works and passes the happy-path test. Do not fix anything yet.

### Step 2: Break It Three Ways (3 h)

Each of these is a real production bug. Write the test that demonstrates it,
then fix it.

**Bug A — non-atomic release.**
```java
// Two nodes, A holds the lock, A's TTL expires, B acquires it.
// A wakes up and runs: DEL key   -> deletes B's lock.
// Fix: Lua compare-and-delete, or an equivalent atomic compare.
```
Test: A acquires, TTL expires, B acquires, A releases. Assert B still holds the
lock. Fails before the fix.

**Bug B — expiry while working.**
```java
// Critical section takes 3x the TTL. Another node enters concurrently.
```
Test: set TTL = 100 ms, sleep 150 ms inside the critical section with a second
client attempting acquisition. Assert the second client succeeded while the
first was still "working". This is the single most common lock bug in the wild.

**Bug C — GC / pause beyond TTL.**
Simulate with `Thread.sleep` standing in for a long STW pause. Same assertion
as Bug B, and note the node does not even get a chance to notice.

### Step 3: Add a Watchdog and Derive the TTL (2 h)

Implement auto-renewal at `TTL/3`. Then, using the formulas in
`MATH_FOUNDATION.md`, derive the TTL from *measured* inputs:

```
measured work p99        = ____ ms   (instrument the critical section)
worst observed STW pause = ____ ms
max RTT to lock server   = ____ ms
clock skew bound         = ____ ms
--> TTL = sum * 3   (safety factor, justify it)
```

Assert the watchdog renews successfully and that killing the process mid-work
releases the lock within `2T/3` (not `T`). Write that bound down and confirm
it with a test.

### Step 4: Add Fencing Tokens (2 h)

```java
// The lock service returns a monotonically increasing token.
// Every write to the protected store carries the token.
// The store rejects any write whose token is below its high-water mark.
```

Required tests:

1. A acquires (token 1), A pauses past TTL, B acquires (token 2). A now writes
   with token 1. Assert: **the write is REJECTED**.
2. Same scenario without the fencing check. Assert the write is accepted, and
   the data is now corrupt. Keep this test — it is the reason fencing exists.
3. Concurrent acquisition from 50 threads. Assert exactly one holds the lock at
   any instant, checked by an in-critical-section counter that must never
   exceed 1.

### Step 5: Show the Lock Was the Wrong Tool (1 h)

Solve the same problem at rung 1 and rung 2, and compare:

- **Rung 1**: a `UNIQUE` constraint preventing duplicate rows. No lock.
- **Rung 2**: `UPDATE jobs SET status='RUNNING' WHERE id=? AND status='NEW'`
  and check the affected-row count. Exactly one caller wins. No lock.

Measure: for each of the three designs, report contention throughput
(operations/sec with 20 contending clients) and worst-case latency. Record
which one you would actually ship and why.

### Step 6: Observability (1 h)

Emit `lock_acquire_attempts`, `lock_acquire_failures`,
`lock_hold_duration`, `lock_wait_duration` (separately!), `lease_expired`
count, and `fencing_rejections`. Then answer with data:

- Is this lock contended or is the critical section slow?
- What is the ratio of wait time to hold time?

### Deliverables

1. Naive lease plus three failing tests that prove the bugs.
2. Lua-based atomic release, watchdog, and a TTL derived from measured inputs.
3. Fencing tokens with the "write rejected" test and the "without fencing the
   data is corrupt" control test.
4. A 50-thread contention test proving mutual exclusion.
5. A rung-1/rung-2/rung-5 comparison with throughput and latency numbers.
6. Lock metrics and a written answer: contended or slow, and what you changed.

### Stretch

- Implement Redlock across 5 simulated Redis nodes with configurable clock
  drift, and empirically find the drift value at which mutual exclusion breaks.
  Compare that to the theoretical bound.
- Replace the lock entirely with a lease-based work queue (at-least-once +
  idempotent workers) and measure the improvement.