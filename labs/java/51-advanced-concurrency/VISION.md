# VISION — Advanced Concurrency Patterns

## Vision Statement
**Compose async work without callback hell** — futures, reactive
streams, and actors are one toolbox: backpressure, error paths, and
cancellation designed up front, not debugged at 2 a.m.

---
## Mental Models
### 1. Future = Value With Time
`CompletableFuture` chains transform values; exceptions are values
too — handle them in the chain, never with stray `get()`.
### 2. Backpressure or Bust
Unbounded `flatMap`/queue + fast producer = OOM. Bounded buffers,
`Semaphore`/`Bulkhead`, and reactive request-n pace the pipe.
### 3. Scheduler = Placement
`subscribeOn`/`publishOn`/executor choice decides which pool blocks.
Virtual threads absorb blocking; bounded pools protect CPU.
### 4. Supervision > Retry Loops
Actors/structured scopes restart with policy (backoff, circuit open);
naked `while(true) retry` amplifies outages.

---
## Decision Framework
| Question | Rule |
|----------|------|
| 2–5 dependent I/Os? | CF chain / structured scope + timeout |
| Infinite stream? | Reactive (Flux) with bounded prefetch |
| Stateful entity? | Actor (Akka-style) with mailbox cap |
| Mixed? | Scope at boundary, reactive inside stream |

---
## Career Trajectory
- **L1:** CF chains, exceptionally/handle, timeouts.
- **L2:** Bulkheads, hedged requests, reactive basics + backpressure.
- **L3:** Custom operators, schedulers, actor supervision, JFR diagnosis.
- **L4:** Fleet async standards, load-shed + chaos for pipelines.

---
## 4-Week Path
```
W1: CF kata — chains, errors, timeouts, orphans measured.
W2: Reactive lab — Flux pipeline with prefetch/drop + latency test.
W3: Actor/supervision mini-system with mailbox caps + backoff.
W4: Unified gateway (scope + reactive + bulkhead) + chaos report.
```
## Success Metrics
- [ ] Every async path has timeout + bounded queue + error mapping
- [ ] Burst test sheds load (429/drop) instead of OOM
- [ ] Cancellation propagates through chain/stream/actor
- [ ] JFR shows no pinning, no unbounded thread growth

## What This Is Not
Picking "reactive everywhere." It is matching pattern to shape.

> Mantra: **Bound the pipe, name the failure, cancel the rest.**
