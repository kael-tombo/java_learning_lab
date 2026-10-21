# NIO Selectors — Theoretical Foundation

## Core Concept

`java.nio.channels.Selector` multiplexes thousands of channels onto one
thread: register each `SocketChannel` (configured non-blocking) with interest
ops (`OP_ACCEPT`, `OP_CONNECT`, `OP_READ`, `OP_WRITE`), then `select()` blocks
until ≥1 channel is ready and returns the ready `SelectionKey` set. The
thread dispatches each key and loops — no thread per connection, no
per-client stacks.

## The Select Loop (the only shape that matters)

```java
selector.select();                       // block until readiness
for (SelectionKey k : selector.selectedKeys()) {
    if (k.isAcceptable()) { /* accept, configure non-blocking, register OP_READ */ }
    if (k.isReadable())   { /* read into ByteBuffer; -1 means closed */ }
    if (k.isWritable())   { /* flush pending writes; clear OP_WRITE when drained */ }
    selector.selectedKeys().remove(k);   // MUST remove — the set never clears itself
}
```

Three rules beginners violate: (1) forgetting `configureBlocking(false)`
before registering (throws `IllegalBlockingModeException`); (2) never
removing processed keys (busy-loop on the same set); (3) registering
`OP_WRITE` permanently (selector spins writable-always — register it only
while output is pending).

## Buffers, Partial I/O, and State Machines

Non-blocking reads/writes are *partial by contract*: one `read()` may fill
half the `ByteBuffer`, one `write()` may flush half the queue. Every
connection therefore needs explicit state — a per-channel attachment
(`key.attach(session)`) holding the read accumulator and write backlog —
i.e., a small state machine per connection. Selectors trade threads for
state machines; the complexity moves, it doesn't vanish.

## Wakeup and Shutdown

`selector.wakeup()` unblocks a selecting thread (the cross-thread signal
for registration changes and shutdown); `Selector.close()` releases the
underlying poll/epoll/kqueue handle. A selector thread that never wakes
can't observe new registrations — all cross-thread channel setup must pair
with `wakeup()`.

## Key Invariants

1. Channels must be non-blocking before registration.
2. Processed keys must be removed from the selected set.
3. `OP_WRITE` is registered only while writes are pending.
4. Partial reads/writes are normal — frame and buffer explicitly.
5. Cross-thread changes pair with `wakeup()`.
