# Real-Time Collaboration - Vision

## Why This Lab Exists
Real-time collaboration is where distributed systems theory stops being an
exercise. Two users editing the same character at the same moment is a
concurrency problem with no locks, and every shortcut (last-write-wins,
naive polling, unbounded broadcast) produces a bug the user sees immediately.
This lab exists to make concurrent editing tractable.

## The Mental Model
Collaboration has three layers, and conflating them is the root of most bugs:

```
  1. TRANSPORT   how updates move        (WebSocket, fan-out, backpressure)
  2. MERGE       how conflicts resolve   (OT, CRDT, or server authority)
  3. PRESENCE    who is here            (ephemeral, lossy, disposable)
```

Presence is the easy one and gets the most engineering attention. Merge is the
hard one and gets a weekend. Priorities are usually inverted.

## The Merge Spectrum

| Approach | Guarantees | Cost | Convergence |
|----------|-----------|------|-------------|
| Server authority (OT) | intent-preserving, serialised | central bottleneck | guaranteed |
| CRDT (Yjs/Automerge) | commutative, no coordination | metadata growth | guaranteed, local-first |
| Last-write-wins | none | trivial | only for last-writer's value |
| Locks | strong, terrible UX | contention, death | n/a |

Choosing wrong here is unrecoverable: mixing an OT client with a CRDT server
corrupts documents silently, and migrating later means every client updates at
once.

## The Concepts That Actually Matter
- **Operational transformation** vs **CRDT** — the fork in the road.
- **Convergence**: all replicas reach byte-identical state after applying the
  same set of updates in any order.
- **Idempotence of operations**: `apply(op); apply(op)` must equal `apply(op)`.
  Retries and re-delivery are guaranteed, so this is not optional.
- **Snapshot + delta**: shipping full state over a socket does not scale past
  demo size.
- **Vector clocks** per document, not globally — a global clock makes unrelated
  documents contend.

## What You Should Be able To Do
- Implement a text OT transform and prove convergence under interleaved edits.
- Explain what property a CRDT (commutative, associative, idempotent) buys and
  what it costs in metadata.
- Backpressure a WebSocket properly instead of buffering until OOM.
- Reconcile a reconnecting client: resync logic, sequence gaps, duplicate
  suppression.
- Separate presence (best effort) from document state (must be correct) and
  justify the split in your design.
- Compute the bandwidth cost of a delta stream at a realistic edit rate.

## The Anti-Goals
- Not polling dressed up as real-time. If you cannot push, say so.
- No unbounded per-connection queues.
- Do not "solve" collaboration with a lock. Locks destroy the reason users
  wanted real-time editing in the first place.

## Success Criteria
You can specify a collaboration design with: transport and its backpressure
policy, merge algorithm and its convergence proof sketch, snapshot/delta
protocol, resync procedure, presence TTL, and a measured bandwidth figure per
active session.

## How To Use This Lab
1. `THEORY.md` for the architecture and patterns.
2. `MATH_FOUNDATION.md` for fan-out cost, bandwidth, propagation latency.
3. `CODE_DEEP_DIVE.md` for OT, delta streams, backpressure, presence.
4. `MINI_PROJECT.md` to build a converging collaborative editor.
5. `REAL_WORLD_PROJECT.md` for a document editor at scale.