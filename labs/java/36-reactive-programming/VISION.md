# VISION — Reactive Programming (Flow, Reactor)

## Vision Statement
**Reactive is backpressure made explicit** — model streams as demand-driven
pipelines so bursts queue boundedly instead of OOMing, and blocking never
hides inside a `map`.

---

## Mental Models
### 1. Publisher → Operator → Subscriber
`Flux/Mono` (or `Flow`) are lazy blueprints; nothing runs until subscribe.
Cold (replayable) vs hot (live multicast) changes everything about reuse.
### 2. Demand Drives Flow
Subscriber requests N; upstream honors it. Unbounded `request(Long.MAX)` +
fast producer = OOM. `onBackpressureBuffer/Drop/Latest` is an explicit loss
policy, not a default.
### 3. Block Belongs on Bounded Pools
Blocking I/O inside operators starves event loops — `subscribeOn/publishOn`
with `boundedElastic` isolation, or use R2DBC/reactive drivers end-to-end.
### 4. Errors Are Signals
`onErrorResume/Retry` with budgets; `retry` without backoff/jitter is a
DDoS machine. Timeouts + deadlines on every async edge.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Need reactive? | High-fanout streaming or SSE/gateway; CRUD can stay MVC |
| Which type? | `Mono` for 0/1, `Flux` for N; never `Flux` for single |
| Blocking call? | Isolate on bounded pool or go reactive driver |
| Burst risk? | Explicit backpressure strategy + overflow test |
| Retry? | Budgeted + jittered, idempotent only |

---

## Career Trajectory
- **L1:** Flux/Mono creation, map/flatMap, subscribe, StepVerifier.
- **L2:** Backpressure operators, schedulers, error/retry design.
- **L3:** R2DBC/Kafka-reactive pipelines, hot sharing, context propagation.
- **L4:** Streaming architecture (gateway, fan-out, load-shedding SLOs).

---

## 4-Week Path
```
W1: Reactor basics, lazy vs eager, StepVerifier + virtual time.
W2: Backpressure labs (buffer/drop/latest), overflow tests.
W3: Schedulers, blocking isolation, R2DBC or WebClient pipeline.
W4: Price-ticker streaming capstone (burst test + JFR proof).
```
## Success Metrics
- [ ] Burst 10x handled with bounded policy, no OOM
- [ ] No blocking on event loop (BlockHound clean)
- [ ] Retry/timeout budget documented and tested
