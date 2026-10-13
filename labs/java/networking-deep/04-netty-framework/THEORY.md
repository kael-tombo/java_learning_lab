# Netty Framework — Theoretical Foundation

## Core Concept (version-agnostic; 4.x architecture)

Netty inverts the socket thread model: a handful of **EventLoop** threads
(each a selector loop, lab 02's shape industrialized) drive **Channels**
through a **ChannelPipeline** of **ChannelHandlers**. Inbound bytes flow
head→tail through decoders to business logic; outbound writes flow
tail→head through encoders to the socket. You write handlers; Netty owns
threads, selection, batching, and backpressure signaling.

## The Fixed Parts: Bootstrap, Groups, Pipeline

- **Bootstrap/ServerBootstrap**: bind/connect entry points; `bossGroup`
  (accepts connections, typically 1 thread) vs `workerGroup` (serves
  traffic, typically 2×CPU threads).
- **ChannelInitializer**: installs the per-connection pipeline exactly
  once at connect time (all state setup lives here, not in handlers'
  constructors).
- **ByteBuf**: Netty's buffer — reader/writer indices (no flip()),
  pooled direct memory by default, and **reference counting**: every
  handler that consumes a buffer must `release()` it (or pass it on —
  ownership transfers exactly once). Leaked buffers are the #1 Netty bug;
  `ResourceLeakDetector` exists for it.
- **Future/ChannelFuture listeners** replace blocking waits: I/O
  completion runs as pipeline callbacks, never as `get()` on the event
  loop (blocking an EventLoop stalls *all* its channels).

## Handler Discipline

- `@Sharable` only for stateless handlers; per-connection state lives in
  the handler instance created per channel (or in channel attributes).
- Inbound (`channelRead`) vs outbound (`write`) halves are separate
  interfaces — implement only the direction you touch.
- Exceptions flow to `exceptionCaught` down the pipeline; an unhandled one
  closes the channel by default — log-or-close explicitly.
- Never block inside a handler: offload to a business `EventExecutorGroup`
  (handler ordering per channel is preserved; blocking the loop is not
  an option).

## Key Invariants

1. Boss accepts, workers serve; counts set at bootstrap.
2. `ByteBuf` ownership transfers exactly once — release or forward, never
   both, never neither.
3. EventLoop threads never block (no `sync()`/`await()` inside handlers).
4. Pipeline order is the protocol: decoders before logic inbound, encoders
   after logic outbound.
5. Graceful shutdown (`shutdownGracefully()`) quiets groups; leaked groups
   hold the JVM like any non-daemon pool.
