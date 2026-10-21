# gRPC Networking

Contract-first RPC: `.proto` IDL generates stubs and skeletons, protobuf
serializes binary messages, HTTP/2 multiplexes concurrent calls over one
long-lived channel.

## What this lab covers

- **Four call shapes from the IDL**: unary, server-streaming,
  client-streaming, bidirectional (framing handled by the transport)
- **Channels and stubs**: one shared channel per server, blocking/future/
  async stub flavors, shutdown discipline
- **Deadlines and interceptors**: per-call timeouts that cross processes;
  auth/tracing/retry plumbing (retries need idempotency analysis)
- **Evolution discipline**: additive `.proto` changes, never reused field
  numbers; status codes (not exceptions) cross the wire

## Lab contents

THEORY.md builds the model (IDL → channel → stub → deadline);
CODE_DEEP_DIVE.md walks unary and streaming calls; EXERCISES.md drills
deadlines and cancellation; QUIZ.md and FLASHCARDS.md lock in the
invariants (IDL-first, shared channel, deadlines always, explicit stream
completion, status-code mapping).

## Prerequisites

Java 17+, HTTP/2 basics, protobuf concepts. External dependencies: gRPC
and protobuf jars plus IDL codegen (not in the JDK).
