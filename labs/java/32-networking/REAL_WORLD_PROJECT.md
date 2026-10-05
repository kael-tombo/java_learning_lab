# REAL-WORLD PROJECT — Networking: Slow Upstream Freezes Checkout

## Incident Scenario
Checkout hangs every payday: one upstream (fraud-check) slows to 30s and the
whole fleet parks — threads exhausted, health checks fail, LB drains all pods
at once.

## Symptoms
- `HttpClient` created per request (no pooling); no read timeout set.
- Platform-thread-per-request server (200 threads) all `BLOCKED`/`WAITING`.
- Retries: 5x immediate on POST `/charge` — duplicate charges upstream.
- No breaker; one slow route consumes every worker; p99 30s+, then 503s.
- TLS handshake 900ms (no session reuse, oversized truststore load per call).

## Investigation Tasks
1. Threads first: `jcmd <pid> Thread.print` × 3 (10s apart) — count threads
   in `HttpClient.send` / socketRead; confirm pool exhaustion.
2. JFR: `jcmd <pid> JFR.start duration=180s filename=net.jfr settings=profile`;
   inspect `jdk.SocketRead`, `jdk.SocketWrite`, `jdk.TLSHandshake`,
   `jdk.ThreadPark`, `jdk.JavaMonitorEnter`.
3. Heap: `jcmd <pid> GC.heap_dump` — look for `HttpClient`/`ConnectionPool`
   per-request garbage confirming no client reuse.
4. Config audit: `grep -rn "HttpClient.new\|timeout\|retry\|Bulkhead" src/`;
   list every outbound call with its timeout values (or absence).
5. Logs: `grep "SocketTimeout\|HttpConnectTimeout\|status=503" app.log`;
   correlate fraud-check latency histogram with checkout p99.
6. Repro: WireMock delay 25s on fraud route; 100 concurrent checkouts —
   show thread dump saturation vs fixed build with timeouts+bulkhead.
7. TLS: JFR `jdk.X509Validation` + handshake durations; check client reuse.

## Root Cause
Unbounded blocking I/O on a fixed platform-thread pool: no timeouts, no pool
reuse, aggressive non-idempotent retries, no isolation — one slow dependency
becomes a fleet-wide deadlock plus duplicate side effects.

## Resolution
- Immediate: cap concurrency (bulkhead), 2s fraud timeout + cached fallback,
  disable POST retries, scale pool + shed load on `/health` separation.
- Short-term: shared pooled `HttpClient`, per-route timeouts, jittered
  backoff (GETs only) + idempotency keys, breaker (fail-fast), virtual
  threads or NIO server, TLS session reuse.
- Long-term: deadline propagation (trace + timeout budget), dependency SLOs,
  chaos drills (slow-upstream game days), socket/TLS JFR dashboards.

## Runbook
```
1. Thread.print + JFR socket/TLS capture before restart.
2. Flip fraud route to timeout+fallback; disable charge retries.
3. Bulkhead + breaker canary; verify threads free in next dump.
4. Roll shared-client + virtual-thread server fleet-wide.
5. Postmortem: timeout/breaker lint + chaos schedule.
```

## Metrics
- p99 checkout < 800ms with fraud 25s-slow; 0 thread-exhaustion events.
- Duplicate charges = 0; breaker trips visible in dashboard.
- 5k-concurrency soak passes; TLS handshake p99 < 100ms (reused).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- HttpClient API: https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/package-summary.html
- Networking tutorial: https://docs.oracle.com/javase/tutorial/networking/TOC.html
