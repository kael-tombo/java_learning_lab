# VISION — gRPC: Contracts, Streams, and Deadlines
> Where this lab takes you: from "protobuf over HTTP/2" to designing a streaming API that degrades predictably.

## The Arc
1. **Contract first** — `.proto` as the source of truth; schema evolution rules.
2. **Code generation** — stubs, message types, and keeping generated code out of your domain.
3. **HTTP/2 & protobuf** — multiplexing, headers, and the wire format.
4. **Streaming** — unary, server-stream, client-stream, bidi, and when each is right.
5. **Operations** — deadlines, retries, interceptors, load balancing, and observability.

## Milestones (checkable)
- [ ] M1: define a schema, generate stubs, and write a unary call with a deadline.
- [ ] M2: explain what breaks if you rename a field, and how to evolve safely.
- [ ] M3: implement server streaming with flow control and a cancellation path.
- [ ] M4: add interceptors for logging, auth, and metrics, and measure their cost.
- [ ] M5: describe how gRPC retries interact with a non-idempotent method.

## Core Competencies
- Protobuf wire format, field numbers as the contract, and reserved fields.
- Streaming semantics, flow control, and the lifecycle of a long-lived call.
- Deadlines as the core reliability primitive, propagated rather than reset.
- Interceptor ordering and what each layer should and should not do.

## Anti-Goals
- Regenerating stubs in every module without pinning the plugin version.
- Hand-editing generated code.
- Retrying a non-idempotent method without an idempotency key.

## Interview Lens
- "Why is the field number the contract and not the field name?"
- "Your streaming RPC leaks threads. Where exactly?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: schema, codegen, first unary call.
- Wk2 QUIZ/FLASHCARDS to 90%+; streaming and deadline experiments.
- Wk3 MINI_PROJECT: a service with unary, server-stream, and bidi.
- Wk4 REAL_WORLD_PROJECT: a migration or a new internal platform API on gRPC.

## Done = You Can
- Design a protobuf contract that will survive two years of evolution, and operate a
  streaming service without leaking threads or dropping deadlines.
