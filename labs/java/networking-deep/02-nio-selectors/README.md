# NIO Selectors

One thread, thousands of connections: `Selector` multiplexes
non-blocking channels by readiness (`OP_ACCEPT`/`OP_READ`/`OP_WRITE`),
trading per-client threads for per-connection state machines.

## What this lab covers

- **The select loop**: register → `select()` → dispatch keys → remove keys
  (the four steps every NIO server shares)
- **The three classic bugs**: blocking channels at registration, unremoved
  keys (busy spin), permanent `OP_WRITE` (writable-always spin)
- **Partial I/O as contract**: per-channel attachments holding read
  accumulators and write backlogs
- **Cross-thread control**: `wakeup()`-paired registration and shutdown

## Lab contents

THEORY.md builds the model (loop → buffers → wakeup); CODE_DEEP_DIVE.md
walks an echo selector; EXERCISES.md drills key handling and attachments;
QUIZ.md and FLASHCARDS.md lock in the invariants (non-blocking first,
remove keys, write-interest only when pending, wakeup pairing).

## Prerequisites

Java 17+, lab 01 (blocking sockets — selectors exist to escape its thread
costs), `ByteBuffer` basics.
