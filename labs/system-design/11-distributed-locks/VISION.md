# Distributed Locks - Vision

## Why This Lab Exists
Distributed locks are the most popular and most dangerous primitive in
microservices. They are appealing because they look like `synchronized`, and
they are dangerous because they are not: `synchronized` is *correct by
construction*, while a distributed lock is correct only under timing
assumptions you do not control. This lab exists so that when you reach for a
lock, you reach for the right *kind*, or better, avoid needing one.

## The Mental Model
A lock is a consensus problem wearing a friendly costume:

```
  "only one node may proceed"
  =>  "all nodes must agree who proceeds"
  =>  needs a quorum  =>  needs 2f+1 nodes  =>  inherits consensus's limits
```

Consequences you inherit for free:
- Availability drops (you need a quorum, not one node).
- Latency rises (at least a quorum round trip).
- Clocks enter the picture, and clocks lie.

## The Ladder (use the lowest rung that works)
1. **No lock at all.** Use a unique constraint, an idempotency key, an atomic
   database operation (`UPDATE ... WHERE status='NEW'`), or a compare-and-swap.
   This is the correct answer far more often than teams admit.
2. **Optimistic concurrency.** A version column; on conflict, retry. The lock
   is "whoever wins the CAS", and correctness comes from the database.
3. **Advisory lock (DB row lock).** `SELECT ... FOR UPDATE`. Slow and exact,
   scoped to one database, and honest about it.
4. **Redis lease with fencing token.** Fast, requires an idempotent or
   fencing-capable resource, and the TTL must be longer than your worst GC
   pause plus your worst work duration.
5. **Consensus-backed lock (etcd/Consul/ZooKeeper).** Correct, available under
   `f` failures, slower. Use when the resource cannot tolerate a stale holder.
6. **Redlock.** Probabilistic. Bounded-clock dependent, and only safe when
   paired with fencing.

## The Three Failure Modes Everyone Hits
- **Expiry while working** — your lease ends, someone else starts, you finish
  and corrupt state.
- **GC pause beyond the TTL** — you never even learn you lost the lock.
- **Uncoordinated release** — you release *their* lock. Fix: compare-and-delete
  with a unique token, atomically (Lua script in Redis).

## What You Should Be able To Do
- Decide whether a proposed locking need can be solved at a lower rung.
- Implement a Redis lease with `SET key token NX PX ttl` and a Lua compare-delete.
- Explain exactly how fencing tokens make an expired holder *harmless* rather
  than merely unlikely.
- Derive a defensible TTL from your p99 work duration plus pause budget.
- Explain why Redlock is not "obviously correct", and what it actually requires.
- Diagnose a system that is lock-contended (queue time vs. hold time).

## The Anti-Goals
- Never assume mutual exclusion implies correctness; you also need
  idempotency, because the network will retry you.
- No lease TTL picked as a round number like 30s. Derive it.
- Do not use a lock where a `UNIQUE` constraint would do. Constraints are
  exact; locks are probabilistic in every implementation except row locks.

## Success Criteria
For any locking proposal you review, you can name the rung, the failure mode it
does *not* prevent, the derived TTL with its inputs, and whether fencing is
present. If the proposal is at rung 1 or 2, you can say why that is sufficient.

## How To Use This Lab
1. `THEORY.md` for JVM lock limits, Redis basics, Redlock, fencing.
2. `MATH_FOUNDATION.md` for TTL derivation, expiry probability, contention.
3. `CODE_DEEP_DIVE.md` for the lease, watchdog, Lua release, fencing.
4. `MINI_PROJECT.md` to break and then fix a real lock.
5. `REAL_WORLD_PROJECT.md` for locking in a live payments platform.