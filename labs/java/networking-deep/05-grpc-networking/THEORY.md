# gRPC Networking — Theoretical Foundation

## Core Concept (transport + IDL, version-agnostic)

gRPC = HTTP/2 transport + Protocol Buffers IDL + generated stubs. The
`.proto` file declares services and messages once; codegen produces a
server base class and client stubs in every language. Wire format is binary
(protobuf), multiplexed over long-lived HTTP/2 connections — one channel
carries concurrent calls without head-of-line blocking.

## The Four Call Shapes (from the IDL, not the library)

```proto
service Directory {
    rpc Lookup (Name) returns (Entry);            // unary
    rpc Watch (Name) returns (stream Entry);      // server streaming
    rpc Upload (stream Chunk) returns (Summary);  // client streaming
    rpc Chat (stream Msg) returns (stream Msg);   // bidirectional
}
```

Unary is RPC-shaped; the streaming shapes are flow-controlled message
pipes with application-level framing already handled (no TCP-framing work —
protobuf length-prefixing is inside the transport).

## Stubs, Channels, and Lifecycle

- **Channel** (`ManagedChannelBuilder`): the long-lived connection pool —
  one per server, shared process-wide, `shutdown()` + `awaitTermination`
  on exit (leaked channels hold threads).
- **Stubs**: blocking (waits, simplest), future (`ListenableFuture`),
  async (observer callbacks). Same IDL, three ergonomics; backpressure
  semantics differ (blocking waits, async observes `onReady`).
- **Deadlines** propagate per call (`withDeadlineAfter`) — across process
  boundaries, unlike socket timeouts. No deadline = a wedged downstream
  wedges you.
- **Interceptors** (client + server) carry auth tokens, tracing, retries;
  retry policy needs idempotency analysis (non-idempotent RPCs must not
  retry blindly).

## Key Invariants

1. IDL first: wire compatibility is a `.proto` evolution discipline
   (never reuse field numbers; additive changes only).
2. One shared channel per server; stubs are cheap and threadsafe.
3. Every call needs a deadline — timeouts don't cross processes by default.
4. Streaming calls need explicit completion (`onCompleted`) and cancellation
   (`cancel`) paths, or they leak call state.
5. Status codes (not exceptions) cross the wire — map `StatusRuntimeException`
   codes to domain outcomes at the boundary.
