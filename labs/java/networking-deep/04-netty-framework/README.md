# Netty Framework

Event-driven networking industrialized: boss/worker `EventLoop` threads
drive `Channel`s through `ChannelPipeline`s of handlers, with pooled
reference-counted `ByteBuf`s. You write handlers; Netty owns threads,
selection, and batching.

## What this lab covers

- **Bootstrap shape**: boss accepts, workers serve; per-connection
  pipelines installed by `ChannelInitializer`
- **ByteBuf ownership**: release-or-forward exactly once (the #1 Netty bug
  class) and `ResourceLeakDetector` as backstop
- **Handler discipline**: `@Sharable` only when stateless; never block an
  EventLoop (offload instead); exceptions to `exceptionCaught`
- **Futures, not waits**: `ChannelFuture` listeners for completion;
  graceful group shutdown

## Lab contents

THEORY.md builds the model (groups → pipeline → buffers → discipline);
CODE_DEEP_DIVE.md walks echo/handler pipelines; EXERCISES.md drills
framing handlers and leak-free forwarding; QUIZ.md and FLASHCARDS.md lock
in the invariants (ownership transfer, no blocking, sharable rules,
shutdown).

## Prerequisites

Java 17+, labs 01–02 (blocking and NIO sockets — Netty automates both),
basic concurrency. External dependency: Netty 4.x jars (not in the JDK).
