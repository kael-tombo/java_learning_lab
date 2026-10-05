# MINI PROJECT — Networking: Resilient Fetch Service

## Goal (2 weeks, ~8–10h)
Build a `fetch-service` that fans out to 5 upstream HTTP APIs with timeouts,
hedged retries, breakers, and a virtual-thread server sustaining 5k concurrent
clients.

## Requirements
### Functional
1. `HttpClient` (HTTP/2, pooled) calling 5 mock upstreams (WireMock):
   catalog, pricing, inventory, reviews, ads — with per-route timeouts.
2. Resilience per route: timeout (connect 1s, read 2s), max 2 retries with
   jittered backoff (idempotent GETs), circuit breaker (5 fails/30s open),
   bulkhead (max 20 concurrent per upstream), fallback (cached/stub).
3. Server: `HttpServer` or Netty on virtual threads (`Executors.newVirtualThreadPerTaskExecutor`);
   endpoints `/aggregate?sku=X` (fan-out + 800ms deadline) and `/health`.
4. Custom TCP probe: length-prefixed ping frame to a mock inventory socket;
   handle partial reads + version byte correctly.
5. TLS: local self-signed `SSLContext` for one upstream; hostname verifier
   correct in dev, documented for prod (no trust-all in default profile).

### Non-functional
- Chaos test: kill 2 upstreams mid-run — p99 degrades, nothing cascades.
- 15+ tests: timeout fires, retry-once-then-fallback, breaker opens/closes,
  partial-frame reassembly, mTLS/wrong-host rejection.
- Load: 5k concurrent `/aggregate` (k6/loop driver) with latency histogram.
- README: timeout/retry/breaker table + thread-model diagram.

## Phases
### Week 1 — Client + Resilience (4–5h)
- Steps: HttpClient setup, per-route policy, WireMock faults, fallback cache.
- Deliverable: chaos run 1 (one upstream down) stays green.

### Week 2 — Server + Load (4–5h)
- Steps: virtual-thread server, TCP framing, TLS route, 5k load run.
- Deliverable: histogram + breaker-trip log + final config.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Timeouts | All routes bounded + tested | Mostly | Missing |
| Retry/breaker | Budgeted + breaker verified | Present | Infinite retry |
| Concurrency | 5k conns, virtual/NIO sound | Works small | Thread-per-conn |
| Framing/TLS | Partial-read + verified TLS | Basics | Trust-all |
| Tests + load | 15+ + histogram + chaos log | 10+ tests | No chaos proof |

Pass >= 70. Stretch: JFR `jdk.SocketRead/Write` latency memo; hedged request
(fastest-of-2); `jcmd Thread.print` starvation analysis.
