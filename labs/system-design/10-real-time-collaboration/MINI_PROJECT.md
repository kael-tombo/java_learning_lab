# Real-Time Collaboration - MINI PROJECT

## Project: A Converging Collaborative Text Editor

**Time**: 12-16 hours

**Goal**: Build a multi-client editor where two people can type in the same
document at the same time and **both end up with identical text** — proven by a
property test, not by inspection.

### Architecture

```
        Client A                Server (authoritative)              Client B
      +-----------+           +----------------------+            +-----------+
      | local doc | <--WS--> |  op log (ordered)     | <--WS--> | local doc |
      | OT apply  |           |  transform vs backlog|            | OT apply  |
      +-----------+           |  snapshot + presence |            +-----------+
                              +----------------------+
```

### Step 1: Operation Types and Apply (2 h)

```java
public record TextOp(int position, int length, String text) {}
```
Implement `apply(doc, op)` as a pure function. Write a brute-force reference
implementation with explicit index arithmetic and assert the fast version
matches on 100,000 random cases. You cannot trust any later test if `apply`
itself is unverified.

### Step 2: The Transform (4 h — the core)

Implement `transform(a, b, priorities)` from `CODE_DEEP_DIVE.md`. Then, before
anything else:

```
Property test: for 100,000 random (doc, a, b):
  apply(apply(doc, a), transform(a, b))  ==  apply(apply(doc, b), transform(b, a))
```

**Checkpoint: this test passes before you build a single server class.** It is
the definition of a correct transform, and it is where you will find your bug.

Handle the tie-break cases explicitly and centrally (see the deep dive): both
servers must make the *same* choice, or they produce different documents.

### Step 3: The Authoritative Server (3 h)

Server state: document text, version counter, and a bounded backlog of recent
operations.

On receiving `op` from a client at `baseVersion`:
```
1. If baseVersion == currentVersion -> apply directly, ack, broadcast.
2. Else -> transform `op` against every backlog entry after baseVersion,
   in order. Then apply, ack, broadcast.
3. If baseVersion is older than the backlog -> REJECT with RESYNC_REQUIRED.
   Do NOT silently apply a stale operation: that is how documents diverge.
```

Required tests:
- Two clients at the same version, concurrent inserts at the same position →
  identical final text on both sides and on the server.
- Stale base version → clean resync response, not corruption.
- Backlog overflow → client is told to resync (this is a design decision; state
  it).

### Step 4: The Convergence Test Across N Clients (2 h)

The real test. Simulate `k` clients each issuing random operations with random
delays, collect every operation, and verify that all replicas — plus the
server — converge to identical text.

```
for (k in {2, 5, 20}) {
  for (seed in 0..1000) {
    schedule = randomInterleaving(k, 200 ops)
    results = applyAll(schedule)
    assert allReplicasEqual(results)
  }
}
```

**This is the deliverable that proves the system works.** 3,000 schedules. Any
failure gives you a minimal reproduction.

### Step 5: Backpressure and Resync (2 h)

Implement `ConnectionBuffer`. Then:

- Simulate a client that reads at 10% of production rate. Assert the buffer
  bounds memory, the connection is closed with `SLOW_CONSUMER`, and the server
  heap does **not** grow unboundedly.
- Assert the reconnect + `applyResync` path recovers to correct state, including
  the case where a delta is redelivered (the duplicate-application bug).

Memory assertion: run 50,000 slow clients and assert heap stays flat. This is
the test that catches the OOM in production.

### Step 6: Presence (1 h)

Implement `PresenceRegistry` with TTL. Assert:
- Explicit leave removes immediately.
- A client that vanishes without disconnecting disappears within the TTL.
- Heartbeats are idempotent.

Derive the TTL from measured jitter and write the derivation in a comment.

### Step 7: Observability (1 h)

Metrics: active sessions, ops/sec, broadcast fan-out per op, transform
backlog depth, buffer utilisation p99, SLOW_CONSUMER disconnects/sec, resyncs
per minute, convergence check pass/fail.

The metric that matters most is **transform backlog depth**: it is the early
warning that clients are lagging and resyncs are about to spike.

### Deliverables

1. Verified `apply` plus a brute-force reference and 100k-case equivalence test.
2. `transform` passing the TP1 property test over 100,000 random cases.
3. Authoritative server with backlog transformation and stale-version rejection.
4. N-client convergence test: 3,000 schedules, all replicas identical.
5. Backpressure with a heap-stability test under 50k slow clients.
6. Resync (snapshot + delta) with a duplicate-delta test.
7. Presence with TTL and derived expiry.
8. Metrics dashboard.

### Stretch

- Add an undo/redo that is correct across concurrent edits (this is where OT
  implementations usually break — redo requires re-transforming against the
  current backlog).
- Implement a CRDT alternative (a sequence CRDT with unique IDs) and benchmark
  both for metadata growth and convergence.