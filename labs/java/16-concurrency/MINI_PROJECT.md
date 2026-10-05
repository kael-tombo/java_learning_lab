# MINI PROJECT — Concurrency: Rate-Limited Crawler

## Goal (2 weeks, ~8–10h)
Build a correct, bounded, observable web crawler with an executor, backpressure, retry, and a deadlock-free shutdown — then prove sizing with numbers.

## Requirements
### Functional
1. Crawl N URLs with `ExecutorService` (fixed pool) + bounded `ArrayBlockingQueue`; `CallerRunsPolicy` or custom metric-incrementing rejection handler.
2. `ConcurrentHashMap<String,Status>` dedupe via `computeIfAbsent`; `LongAdder` fetched/failed counters; `CompletableFuture` fetch→parse→store chain with timeout (`orTimeout`).
3. Retry with bounded exponential backoff (max 3); poison-pill / `shutdownNow` + `awaitTermination(30s)` graceful stop; idempotent store.
4. Fake fetcher with latency + failure injection (deterministic seed) for tests; rate limiter (Semaphore, max 10 concurrent fetches).
5. CLI: seed file, depth, pool size, queue size; live progress line (done/queued/errors).
### Non-functional
- No `Thread.sleep` as sync, no unbounded structures, no ignored `InterruptedException` (restore flag).
- 16+ tests: dedupe race (100 threads × same URL → 1 fetch), rejection path, shutdown no-hang, retry-then-success, timeout path.
- README: Little's-law sizing note (threads ≈ throughput × latency) + queue/reject choice.
- Stress run: 5k URLs fake-fetch, report throughput + p95 fetch latency.

## Phases
### Week 1 — Correct Core (4–5h)
- Pool + queue + dedupe + store + shutdown.
- Deliverable: 500-URL crawl, zero dupes, clean exit.
### Week 2 — Resilience + Numbers (4–5h)
- Retry/backoff, limiter, timeouts, stress + sizing memo.
- Deliverable: 5k-URL report + rejection counts.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Bounding | Pool+queue+reject coherent | Bounded | Unbounded anywhere |
| Concurrency primitives | computeIfAbsent/LongAdder/CF | Correct basics | synchronized-everything |
| Shutdown/interrupt | Clean + tested | Clean untested | Hangs on Ctrl-C |
| Resilience | Backoff+timeout+limiter tested | Present | Missing |
| Tests + numbers | 16+ tests, stress report | 10+ tests | Happy-path only |

Pass ≥ 70. Stretch: deadlock-injection drill + `jstack` diagnosis writeup; dynamic pool resize experiment.
