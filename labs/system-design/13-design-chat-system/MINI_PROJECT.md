# Chat System - MINI PROJECT

## Project: Multi-User Chat with Real Delivery and Honest Recovery

**Time**: 12-16 hours

**Goal**: Build a chat system where messages are ordered, delivery is
resumable, presence expires correctly, and a client can disconnect for 10
minutes and miss nothing.

### Scope

```
MessageLog (partitioned, append-only)
InboxFanout (per-user delivery)
PresenceRegistry (TTL)
ResyncProtocol (gap detection)
ChatSendHandler (idempotent send)
ConnectionBuffer (bounded, with backpressure)
```

### Step 1: Message Log and Ordering (2 h)

Implement `MessageLog`. Required tests:

- 1,000 concurrent sends into one conversation: assert sequences are
  `1..1000` with **no gaps and no duplicates**.
- Two conversations: assert per-conversation sequences are independent (no
  shared counter). A global counter is a bug you want to catch now.
- Assert that nothing is ever updated in place. Add a code comment stating the
  append-only invariant.

### Step 2: Idempotent Send (1 h)

Implement `ChatSendHandler`. Required tests:

- The same `clientMsgId` sent 50 times concurrently produces exactly ONE
  message, and all 50 callers get the same sequence.
- The same `clientMsgId` with a **different body** returns the original result
  (does not create a second message). Decide and document whether this should
  be an error instead — write the reasoning.
- A retry arriving after the dedup TTL must create a new message. Assert the
  TTL is longer than your simulated client retry horizon.

### Step 3: Inbox Fan-out vs. Broadcast (2 h)

Implement both and measure. This is the lab's central decision.

```
broadcast: 1 append, N deliveries per message
inbox:     N appends, N per-user reads
```

Required tests:
- A 1,000-member group receives a message: assert all 1,000 inboxes contain it
  and that send latency did **not** scale with group size (fan-out is async).
- Per-user delivery state is independent: user A draining does not advance
  user B. This is what makes reconnect work.
- A client with 50 conversations drains across all of them and asserts
  **no duplicates and no gaps**.

### Step 4: Resync After Disconnect (2 h)

Implement `ResyncProtocol`. Required tests, in order:

1. Client disconnects at seq 10, 25 messages arrive, client reconnects with
   `lastSeen=10`. Assert it receives exactly 11..35 in order.
2. Client's `lastSeen` is **older than retention**. Assert
   `truncatedHistory=true` rather than a silently short list.
3. Messages arrive **during** resync. Assert no gap is created between the
   resync response and the live stream (the classic race; you will need to
   handle it and say how).

**Checkpoint:** test 3 is the bug that produces "message missing on my phone".

### Step 5: Presence (1 h)

Implement `PresenceRegistry` with a fake clock. Tests:

- Heartbeat, then advance the clock past TTL without a leave: user disappears.
- Explicit leave: disappears immediately.
- Heartbeat is idempotent.
- 10,000 users heartbeat; assert memory is bounded and eviction is lazy and
  correct.

Derive the TTL from measured jitter and write the derivation in a comment.

### Step 6: Backpressure Under a Slow Client (1 h)

Implement `ConnectionBuffer`. Tests:

- One client reading at 5% of production rate for 60 s. Assert memory stays
  flat and the connection closes with `SLOW_CONSUMER`.
- On reconnect + resync, assert zero messages are lost. **This is the
  critical test** — it proves the backpressure policy is safe.
- Assert per-connection memory is under the documented budget and compute the
  fleet's total socket memory.

### Step 7: Ordering Rule Enforcement (1 h)

Add the client's message-ordering logic and prove the rule:

```
sort by (conversation_id, conversation_sequence)
NEVER by arrival time, NEVER by client timestamp
```

Required test: deliver messages out of order across conversations and assert
the final rendered thread is correctly ordered. Then add a test with a
deliberately wrong client (sorting by arrival) and show it produces a visibly
scrambled thread. That failing test documents why the rule exists.

### Step 8: Load Test and Metrics (1 h)

Drive 5,000 messages/s with a Zipfian conversation-size distribution. Report:

| Metric | Value |
|--------|-------|
| Send p50/p99 (should be independent of group size) | |
| Delivery lag p50/p99 | |
| Fan-out writes/s | |
| Hot-partition rate | |
| Store bytes/message | |

### Deliverables

1. MessageLog with a 1,000-concurrent-send ordering test.
2. Idempotent send with the same-key-different-body policy documented.
3. Inbox fan-out with a 1,000-member group test proving send latency is
   group-size-independent.
4. Resync with all three tests, including the during-resync race.
5. Presence with TTL derivation and bounded memory.
6. Backpressure with a flat-memory test and a zero-loss reconnect test.
7. Ordering rule with the deliberate-failure test.
8. Load test report and metrics.

### Stretch

- Add end-to-end encryption (X25519 key agreement + per-message keys) and
  measure the ~30% storage and bandwidth overhead from the math file.
- Add a relay tree so no node fans out to more than 20 peers, and measure the
  added hop latency versus the egress saving.