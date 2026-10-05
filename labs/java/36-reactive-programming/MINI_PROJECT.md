# MINI PROJECT — Reactive: Burst-Safe Price Ticker

## Goal (2 weeks, ~8–10h)
Build a WebFlux `ticker-service` ingesting 50k ticks/s from a mock feed,
serving SSE + snapshot REST, surviving 10x bursts with explicit backpressure.

## Requirements
### Functional
1. Ingest: `Flux` from mock `TickGenerator` (bursty profile) via
   `Flux.create` with overflow strategy configurable (buffer-1k/drop/latest).
2. Serve: SSE `/ticks/{symbol}` (hot shared `share()`), `GET /snapshot`
   (`Mono`), backpressure-propagating to slow SSE clients (no unbounded queue).
3. Persist (optional R2DBC): latest per symbol; blocking JPA forbidden on
   event loop (BlockHound fails build on violation).
4. Resilience: per-symbol timeout 2s, retry max-2 jittered on idempotent
   fetch, `onErrorResume` fallback to last snapshot, `/health` stays 200.
5. Context: `traceId` via Reactor `Context` from filter to log (tested).

### Non-functional
- Burst test: 10x 30s spike — memory flat, dropped-count metric exact,
  slow-client disconnect handled without affecting others.
- 15+ StepVerifier tests: overflow policy, retry budget, timeout fallback,
  hot-share (2 subscribers, 1 upstream), context propagation.
- JFR/thread proof: `jcmd Thread.print` shows event-loop free; no blocking.
- README: backpressure decision (why buffer/drop/latest) + marble diagrams.

## Phases
### Week 1 — Pipeline (4–5h)
- Steps: cold→hot flux, operators, StepVerifier suite, SSE endpoint.
- Deliverable: steady-state stream with tests green.

### Week 2 — Burst + Isolate (4–5h)
- Steps: overflow policies, BlockHound, R2DBC/snapshot, burst run.
- Deliverable: burst report (dropped vs buffered counts + heap chart).

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Backpressure | Explicit + tested + measured | Present | Unbounded |
| Hot/cold | Correct share, proven | Works | Double subscribe |
| Blocking | BlockHound clean, isolated | No obvious block | JPA on loop |
| Errors | Budgeted retry + fallback | Handled | Infinite retry |
| Tests + burst | 15+ + 10x report | 10+ tests | No burst proof |

Pass >= 70. Stretch: Kafka-reactive source; JFR `jdk.ThreadPark` loop-health
memo; load-shed (429) on sustained overflow.
