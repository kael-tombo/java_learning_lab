# Chat System - Vision

## Why This Lab Exists
Chat looks like messaging, but it is three systems wearing one UI: a durable
ordered log (messages), a low-latency ephemeral presence layer (who is online),
and a real-time delivery fan-out (WebSockets). Teams that build it as "a
database plus polling" discover, at scale, that the write path has a hot key per
conversation and the read path has a quadratic fan-out. This lab exists so those
two problems are designed for up front.

## The Mental Model
Separate the three concerns and give each the right primitive:

```
  MESSAGE LOG   durable, ordered, total order per conversation
                -> partitioned log, not a table with autoincrement
  PRESENCE      ephemeral, best-effort, TTL
                -> TTL key-value store, never the message store
  DELIVERY      real-time, lossy under backpressure, resumable
                -> WebSocket + delta sync
```

The most common architectural error is putting presence in the message
database. Presence is high-churn and worthless after 30 seconds; message data
is the opposite.

## The Hard Part Is Ordered Fan-Out

```
  conversation of N members:
    write path   = 1 append  (cheap, partitioned by conversation_id)
    read path    = N deliveries per message (this is the cost)

  N=100 group chat, 10 msg/s:
    1,000 deliveries/s from ONE conversation  -> hot key, one partition
```
So the write path is partitioned (scales with conversations) but the delivery
path fans out within a partition. Real systems handle this with **per-user
inboxes** rather than per-conversation broadcast, which converts the group
problem into N appends and lets delivery be a per-user read. That is the central
design decision in the lab.

## Consistency Is Per-Surface
- Sending a message: linearizable within a conversation.
- Delivering to another member's device: eventual, seconds.
- Presence: meaningless to be exact; seconds of staleness is invisible.
- Typing indicators: ephemeral, coalesced, droppable.

## What You Should Be able To Do
- Choose partitioned log vs. per-user inbox and justify with the fan-out
  arithmetic.
- Guarantee per-conversation ordering and explain what breaks globally.
- Design presence with a derived TTL and keep it out of the message store.
- Handle reconnect: last-seen sequence, gap detection, resync.
- Handle group fan-out cost and explain delivery-order trade-offs.
- Implement end-to-end encryption and state precisely what it does and does not
  protect (it removes server-side moderation and search).

## The Anti-Goals
- Not polling. If you cannot push, say so honestly and label the system as
  near-real-time.
- Do not rely on wall-clock timestamps for message ordering.
- No unbounded per-connection queues; backpressure closes sockets, it does
  not buffer until OOM.

## Success Criteria
You can specify a chat system with: log partitioning and ordering scope,
delivery strategy (broadcast vs inbox) with fan-out numbers, presence design
with TTL derivation, resync protocol, retention and compliance, and the
consistency promise for each of the three surfaces.

## How To Use This Lab
1. `THEORY.md` for architecture and patterns.
2. `MATH_FOUNDATION.md` for fan-out, storage growth, throughput, TTL.
3. `CODE_DEEP_DIVE.md` for partitioning, inbox fan-out, presence, resync.
4. `MINI_PROJECT.md` to build a working multi-user chat.
5. `REAL_WORLD_PROJECT.md` for a production messaging platform.