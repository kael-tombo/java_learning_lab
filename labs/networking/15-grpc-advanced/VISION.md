# VISION — gRPC Advanced: Operating Contracts at Scale
> Where this lab takes you: from "the basics work" to load balancing, schema governance, and the failure modes that only appear in production.

## The Arc
1. **Channels & subchannels** — how a channel picks a connection, and how that interacts with load balancing.
2. **Interceptors** — the cross-cutting layer, and the ordering rules that matter.
3. **Reliability** — deadlines, retries, hedging, and the discipline of propagating rather than resetting.
4. **Schema governance** — evolution rules enforced in CI, and versioned packages.
5. **Performance & operations** — cost measurement, streaming at scale, and observability.

## Milestones (checkable)
- [ ] M1: explain how gRPC load balancing picks a connection and why `ROUND_ROBIN` needs a resolver.
- [ ] M2: write an interceptor chain and justify the ordering.
- [ ] M3: propagate a deadline across three hops and prove it is never extended.
- [ ] M4: design retry and hedging policy and explain the double-write risk.
- [ ] M5: build a CI gate that rejects a client-breaking schema change.

## Core Competencies
- Channel/subchannel architecture, name resolution, and load balancing policies.
- Interceptor ordering, context propagation, and what belongs at which layer.
- Deadlines as the primary reliability primitive; retries and their safety conditions.
- Schema evolution, breaking-change detection, and multi-language stub governance.

## Anti-Goals
- Retrying a non-idempotent method without an idempotency key.
- Resetting a deadline at each hop, which defeats the whole mechanism.
- Enabling retry everywhere "for resilience" without a safety analysis.

## Interview Lens
- "Your gRPC service works locally and fails in production. What differs?"
- "How do you roll a schema change to 40 services without breaking anyone?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: channels, interceptors, deadlines.
- Wk2 QUIZ/FLASHCARDS to 90%+; retries, hedging, breaking-change detection.
- Wk3 MINI_PROJECT with a load-balanced channel and an interceptor chain.
- Wk4 REAL_WORLD_PROJECT: a service mesh contract platform with governance.

## Done = You Can
- Operate a gRPC platform where the reliability primitives are deliberate, the contract
  is governed, and the failure modes are instrumented before they happen.
