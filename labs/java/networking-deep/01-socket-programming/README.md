# Socket Programming

Blocking TCP sockets (`ServerSocket`/`Socket`): the kernel completes the
handshake before `accept()` returns, one thread (or pool slot) owns each
connection, and every protocol needs explicit framing on the byte stream.

## What this lab covers

- **Threading models**: thread-per-connection → bounded pool → NIO
  multiplexing (when each wins; backlog and timeout behavior)
- **Socket options that matter**: `SoTimeout` (no infinite reads),
  `TcpNoDelay` (latency vs batching), half-close for graceful termination
- **Framing**: length prefixes/delimiters over a stream that fragments and
  coalesces arbitrarily — where most socket bugs live
- **Lifecycle**: close order, owner-thread discipline, pool shutdown

## Lab contents

THEORY.md builds the model (handshake → threading → framing → options);
CODE_DEEP_DIVE.md walks echo/pool/NIO servers; EXERCISES.md drills framing
and shutdown; QUIZ.md and FLASHCARDS.md lock in the invariants
(accept-returns-connected, one owner thread, timeouts, framing).

## Prerequisites

Java 17+, `java.net` basics, TCP fundamentals (ports, handshake, streams).
