# Chat System - REAL WORLD PROJECT

## Project: Enterprise Messaging Platform with Regulatory Retention

**Time**: 4-5 weeks (team of 4)

**Scenario**: A messaging platform for 12M monthly actives, competing with
Slack and Teams. Requirements in tension:

- 3.2M concurrent connections at peak, p99 delivery < 400 ms globally.
- Enterprise customers require 7-year retention with legal hold and export.
- Some tenants require end-to-end encryption, which removes server-side search
  and moderation.
- Group sizes up to 5,000 (a broadcast channel is effectively a group).
- Cross-region latency must be under 250 ms for EU and APAC customers.

### Step 1: Capacity Model From Measured Distributions

Do not design from averages. Produce the measured distributions first:

```
conversation size distribution (p50 / p95 / p99 / max)
message size distribution (p50 / p95 / max)
messages per conversation per day
peak concurrent connections by region
```

Then compute, from `MATH_FOUNDATION.md`:

```
weighted_fanout = sum over size buckets of (share * N)
storage = DAU * msgs/day * bytes * retention
connections = online * devices_per_user * concurrent_per_device
socket_memory = connections * bytes_per_connection
```

**Deliverable:** the capacity model with each figure traced to a measurement,
plus the resulting fleet shape (gateways, brokers, stores per region). Flag
where the fleet is sized by **connections** rather than by message rate — for
chat that is usually the answer, and it surprises people.

### Step 2: Delivery Architecture Decision

Write the decision record comparing:

| Approach | Write cost | Delivery cost | Resume | Order |
|----------|-----------|---------------|--------|-------|
| Broadcast per connection | 1 | N per message | hard (connection state) | natural |
| Per-conversation log + fan-out relay | 1 | N, bounded per node | medium | natural |
| Per-user inbox | N | per-user read | easy (client-supplied state) | per-conversation only |
| Per-user inbox + relay tree | N | per-user read | easy | per-conversation only |

Argue explicitly for the per-user inbox despite N-write amplification, because
the fan-out is calculated from 46x effective group size while an inbox read is
a single indexed lookup. Then justify the relay tree (degree 20, depth 2-3) for
channels above a subscriber threshold.

**Deliverable:** the decision record, the fan-out arithmetic, and the
measured broadcast-vs-inbox comparison from a load test.

### Step 3: Ordering and Client Rendering Rules

There is no global message order in an inbox design, so the client contract must
be explicit and versioned:

```
1. Sort by (conversation_id, conversation_sequence). NEVER by arrival time.
2. Never use client wall-clock timestamps for ordering (clocks are unsynced).
3. Sequence gaps trigger a resync request, not a blank space in the thread.
4. Out-of-order delivery is normal and must render silently in the right place.
```

Ship a "render correctness" client test suite: deliver messages shuffled across
conversations and assert the rendered thread. Also ship the negative case (a
client sorting by arrival time) as documentation of why the rule exists.

### Step 4: Presence and Typing at 3.2M Connections

- Presence in a regional TTL store, never in the message database.
- TTL derived from measured jitter on your worst supported network (not from a
  round number). Document the derivation and the memory cost.
- Typing indicators and read receipts are **ephemeral and coalesced**: never
  persisted, never replayed on reconnect, dropped when the socket is busy.
  Sending them at message rate is pure waste and the single biggest avoidable
  egress cost in chat systems.
- Presence aggregated per region; a user's region is derived from their session,
  not from a lookup per request.

**Deliverable:** presence/typing architecture with measured memory cost and an
egress comparison (message-rate presence vs. coalesced presence).

### Step 5: Retention, Legal Hold, and Erasure

Enterprise retention is a data model, not a cron job. States, all first-class:

```
ACTIVE            visible, retained per policy
LEGAL_HOLD        retention suspended for named custodians
DISPUTED          erasure requested but conflicting with hold/contract
ERASED            payload removed, tombstone + ordering preserved
```

Required behaviour:

- `LEGAL_HOLD` suspends **all** deletion, including user erasure requests.
- `DISPUTED` is surfaced to the user with a reason and a support path. Never
  silently resolve in either direction.
- `ERASED` preserves sequence numbers so ordering and thread structure survive
  payload deletion.
- Retention enforcement operates on **cold-tier objects**, and the enforcement
  job itself is auditable and produces a report.

**Deliverable:** the state model, the precedence rule
(`legal hold > contractual > user erasure`) written down, and an enforcement job
that produces a signed report. Demonstrate all four states in a test.

### Step 6: End-to-End Encryption for Selected Tenants

State precisely what E2EE does and does not give:

```
Provides:   server cannot read message content
Lacks:      server-side search, server-side moderation/link preview,
            bot integrations, legal hold on CONTENT, e-discovery
```
Therefore: it cannot be combined with legal hold on content. Write that
conflict down and get it resolved **before** implementation, because it changes
the data model.

Requirements:

- Per-device keys (2-5 devices per user), pre-key bundles stored and rotated.
- Device add/remove must re-key the conversation; removing a device must
  actually revoke it, which means rotation, not deletion.
- Safety-number verification UX, plus the case where users skip it (define the
  degradation).
- E2EE tenants must accept reduced functionality — write the feature-difference
  matrix and get it signed.

**Deliverable:** the threat model, the key lifecycle, the feature-difference
matrix, and the measured ~30% overhead from the math file validated against a
real workload.

### Step 7: Failure Drills

1. **Broker region loss.** Verify clients in that region reconnect to another
   region within RTO, that resync recovers all messages, and that no message is
   lost or duplicated. This is the drill that proves the inbox design works.
2. **Inbox store unavailable.** Verify sends still succeed (append is
   authoritative) and that delivery catches up from the log afterwards. If sends
   fail when the inbox store is down, your write path is coupled to delivery —
   fix that.
3. **Hot channel: 5,000-member broadcast, 50 msg/s.** Verify send latency stays
   flat and the relay tree bounds per-node fan-out. Report egress before and
   after the relay tree.
4. **Slow client at 1% read rate, 10,000 sessions.** Assert gateway memory is
   flat, sessions close with `SLOW_CONSUMER`, and reconnect+resync loses
   nothing.
5. **Ordering attack**: inject a client with a skewed clock sending messages
   with bogus timestamps. Assert ordering is unaffected — proving sequences, not
   clocks, drive order.

### Deliverables

1. Capacity model from measured distributions, with the connection-vs-message
   insight called out.
2. Delivery architecture decision record with the fan-out arithmetic.
3. Versioned client ordering contract plus a render-correctness test suite.
4. Presence/typing architecture with memory and egress measurements.
5. Retention state model with precedence rule and an auditable enforcement
   report.
6. E2EE threat model, key lifecycle, and signed feature-difference matrix.
7. Five drill reports with measured numbers, including the zero-loss resync
   proof.
8. Metrics: concurrent connections, send p99, delivery lag p99, resync rate,
   SLOW_CONSUMER rate, per-node fan-out, retention job age, hold inventory.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Sizing | From averages | From measured distributions; connections identified |
| Delivery | Broadcast per connection | Inbox + relay tree, arithmetic shown |
| Ordering | Timestamps | Per-conversation sequences; clock-attack drill passes |
| Presence | Message rate | Coalesced, TTL-derived, measured egress |
| Retention | Cron job | Four-state model, precedence, audited enforcement |
| E2EE | "Encrypted" | Threat model, revocation, feature-difference matrix |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 6455 — *The WebSocket Protocol*: normative frame format, ping/pong
  keepalive, and close codes. The reference for connection keepalive design at
  3M connections and for choosing a close code that distinguishes backpressure
  from network failure.
  https://www.rfc-editor.org/rfc/rfc6455.html
- Apache Kafka documentation — design and delivery semantics, partition keying,
  and consumer groups: the reference for the partitioned message log backing
  per-conversation ordering, and for the retention/compaction configuration that
  enterprise retention depends on.
  https://kafka.apache.org/documentation/

Pin the section or section number when citing, and re-verify Kafka's compaction
and retention semantics against your major version — default retention settings
alone will silently delete chat history you promised to keep for seven years.