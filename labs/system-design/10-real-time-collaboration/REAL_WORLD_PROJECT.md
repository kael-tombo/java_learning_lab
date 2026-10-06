# Real-Time Collaboration - REAL WORLD PROJECT

## Project: Multi-Region Document Collaboration at Scale

**Time**: 3-4 weeks (team of 4)

**Scenario**: A collaborative editing product replacing Google Docs-style
suites for enterprise customers. Requirements in tension:

- 60,000 concurrent editing sessions at peak, concentrated in 3 regions.
- p95 keystroke-to-remote-ack under 150 ms across continents.
- 99.99% availability for opening a document (reading).
- Document history retained indefinitely, auditable for enterprise.
- Regional data residency (EU documents never leave the EU).

### Step 1: Choose the Merge Algorithm and Defend It to the Last Comment

This decision is unrecoverable: mixing OT clients with CRDT servers corrupts
documents silently, and migrating forces every client to update simultaneously.

```
                  OT                              CRDT
metadata growth   O(ops since snapshot)         grows with concurrent edits
coordination      server serialises             none; local-first possible
tie-break risk    REAL - inconsistent breaks   none by construction
undo/redo         hard across concurrency      hard across concurrency
offline editing   possible but awkward         natural
implementation    high risk                     moderate
```

**Recommendation to argue for:** OT server-side (single authoritative
transformer) for document text, because you need a total order for audit and
enterprise version history, and because local-first CRDT conflicts with
residency (a local replica is a residency problem).

Deliverable: a written decision record with the alternatives, the rejected
option and why, and the migration cost of changing your mind.

### Step 2: Architecture

```
Client (OT engine, offline queue)
   |  WebSocket (wss)
   v
Region Edge (session affinity, TLS, backpressure)
   |
   v
Region Authoritative Server (OT transform, document log, presence)
   |                                    |
   +--> Durable log (append-only)        +--> Presence (TTL store, ephemeral)
   |
   v
Region Replica (read-only followers for "open document")
   |
   v
Cold tier (compacted snapshots + full history, object storage)
```

Region-local by design for residency. Cross-region work is async replication of
the log only — never a cross-region read of live state.

### Step 3: The Document Log — Design for Ten Years

Documents are appended-only event logs. Requirements:

- **Total order per document** (the OT output order), globally sequenced per
  region.
- **Compaction**: snapshot when `log_size > 2 * state_size`, then cold-tier the
  superseded operations. History must remain *queryable* even after compaction
  — compact the replay path, not the audit path.
- **Deterministic replay**: given the same operation set in the same order,
  state must be byte-identical. Assert this in a nightly job against production
  logs; a mismatch means a non-determinism bug that will surface as a support
  ticket in six months.
- **Region sequence numbers**, never timestamps, for ordering. Cross-region
  merge uses a documented tie-break.

**Deliverable:** replay verification running nightly, with the mismatch report.

### Step 4: Read Path Availability (99.99% for Opening a Document)

Opening a document is a read-heavy path and must not depend on the writer:

- Read-only replicas serve opens; they lag, and the lag is bounded and reported.
- If a replica is too far behind (`applied < required_min`), fall back to the
  authoritative server, not to a truncated read.
- Cold tier serves historical versions (always eventually consistent by
  definition — there is no "current" in the cold tier).
- Opening must work with zero writes. Prove it: run the entire open path with
  the authoritative server in read-only maintenance mode.

### Step 5: Fan-Out and Backpressure at 60,000 Sessions

From `MATH_FOUNDATION.md`, naive broadcast is quadratic. Measure the real
fan-out factor:

```
sessions_per_document distribution:
  p50 = 2 collaborators
  p95 = 8
  p99 = 140    (a document with 140 live cursors is real)
  max = 900
```
Design consequences:

1. Per-document subscriber sets (not global broadcast) — the only change that
   matters.
2. **Relay tree above a threshold**: documents with > 50 subscribers get a
   dedicated relay so no single node fans out to hundreds of peers.
3. Binary delta compression on the wire; measure and report the ratio (expect
   3-6x on keystroke deltas).
4. Cursor/presence updates are **coalesced and rate-limited** to ~10/s per
   session. Never send presence at keystroke rate — this is pure waste and it is
   a common mistake.

Per-connection buffer bounds (1 MB), overflow closes with a resumable code, and
the disconnect code distinguishes backpressure from network failure.

### Step 6: Residency and Data Placement

- Document log, snapshots, presence, and backups all region-pinned for EU
  tenants.
- The region router **rejects** cross-region document access rather than falling
  back. A silent fallback here is a compliance incident.
- Account migration between regions (EU -> US) is an explicit, audited
  operation: export the log, re-key, verify, cut over, delete source with a
  documented retention decision.

### Step 7: Failure Drills

1. **Authoritative server fails mid-edit.** Verify clients reconnect to another
   region leader within the RTO, that no edit is lost (the log is durable), and
   that resync is correct.
2. **Slow consumer on 200 sessions.** Assert server memory stays flat, sessions
   close with `SLOW_CONSUMER`, and reconnect + resync restores correctness.
3. **Clock skew of 5 s on one node.** Verify nothing relies on timestamps for
   ordering (this drill is the justification for sequence numbers).
4. **Cold-tier read during compaction.** Verify a document open during snapshot
   compaction is still correct.
5. **Replay a production log** and assert byte-identical state. Any difference
   is a critical bug.

### Deliverables

1. Merge-algorithm decision record with alternatives and migration cost.
2. Region-pinned architecture with the log, snapshot, and cold-tier design.
3. Nightly deterministic-replay verification with a mismatch report.
4. Read path that works with the writer in maintenance mode (proven by drill).
5. Fan-out design with measured per-document subscriber distribution and
   compression ratios.
6. Residency controls with a router that rejects cross-region access, plus an
   audited account-migration runbook.
7. Five drill reports with timelines, including the replay-verification result.
8. Metrics: active sessions, ops/sec, transform backlog p99, resync rate,
   SLOW_CONSUMER rate, replay mismatch count.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Merge choice | "We use OT" | Decision record with rejected option + cost |
| Fan-out | Global broadcast | Per-document sets + relay tree above threshold |
| Presence | Sent at keystroke rate | Coalesced, rate-limited, TTL-bounded |
| Ordering | Timestamps | Sequence numbers; clock-skew drill passes |
| History | Compacted and forgotten | Replay path compacted, audit path retained |
| Residency | "Multi-region" | Router rejects cross-region; migration audited |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 6455 — *The WebSocket Protocol*: the normative definition of the
  upgrade handshake, frames, ping/pong keepalive, and close codes. Cite the
  section number when you need to justify keepalive intervals or a specific
  close code for backpressure disconnects.
  https://www.rfc-editor.org/rfc/rfc6455.html
- RFC 9297 — *An Extension for WebSockets to Detect Loss of TCP Connection
  Integrity*: why a half-open WebSocket is indistinguishable from an idle one,
  and what that means for presence TTL derivation and session timeouts.
  https://www.rfc-editor.org/rfc/rfc9297.html

Both are stable standards documents. Pin the section number rather than the
landing page, and note that many client libraries implement their own close
codes in the private range — verify which your clients actually send.