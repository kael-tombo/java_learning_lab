# REAL-WORLD PROJECT — Advanced Concurrency: Retry Storm Melts Pricing

## Incident Scenario
Pricing composes 4 downstream calls with nested `CF.get()` (no
timeout), unbounded `flatMap` in the reactive variant, and retry×3
with no backoff. One slow vendor triggers thread pileup → retries
triple load → breaker absent → full outage in 11 minutes.

## Symptoms
- In-flight 200 → 18,000; threads 400 → 9,000; heap + old-gen
  pressure from queued futures; then cascading 503s.
- `Thread.print` shows thousands `WAITING CF.get` + `socketRead`
  with no deadline; JFR `ThreadPark` 92% of samples.
- Reactive path: `flatMap` concurrency unbounded → prefetch queue
  2.1M elements, GC 40% CPU, then OOMKill on two pods.
- Retry metric 3.8x amplification; vendor latency 80ms → 1.4s under
  tripled load (self-inflicted DDoS).
- No bulkhead: pricing threads starve checkout (shared pool).

## Investigation Tasks
1. Blocked census: `jcmd <pid> Thread.print` — count
   `Future.get/socketRead` stacks; confirm missing timeout via code
   grep `\.get\(\)` without timeout arg.
2. JFR: `jcmd <pid> JFR.start name=pipe settings=profile duration=180s
   filename=pipe.jfr`; rank `jdk.ThreadPark`, `jdk.SocketRead`,
   `jdk.JavaMonitorEnter`, `jdk.ObjectAllocation` (queued futures).
3. Reactive queue: heap dump → `FluxFlatMap`/`QueueSubscription`
   size; JFR allocation stacks of envelope objects; confirm
   `maxConcurrency` absent.
4. Amplification: client retry metric (3.8x) × RPS vs vendor capacity;
   trace waterfall shows retry siblings, no jitter/backoff headers.
5. Repro: staging vendor-delay 800ms + burst; old pipeline melts
   <5 min, bulkhead+breaker pipeline sheds cleanly.

## Root Cause
No bounds anywhere: no timeouts, no bulkhead, no backpressure limit,
no breaker, retries without backoff. One slow dependency converts
concurrency into a load multiplier aimed at itself.

## Resolution
- Immediate: shed load (429 at edge), kill retries (1 + jitter),
  isolate pools (pricing vs checkout), restart melted pods gradually.
- Short-term: per-call 300ms + global 2s deadline, bulkhead (50) +
  bounded queue, `flatMap(maxConcurrency=16)` + drop metric, breaker
  (Resilience4j) + hedged pricing for p99 vendor.
- Long-term: async standards (timeout/bound/breaker checklist),
  chaos retry-storm test in CI, in-flight + amplification dashboards.

## Runbook
```
1. Capture Thread.print + JFR 180s + heap dump BEFORE mass restart.
2. Rate-limit edge 30%; disable retries; split pools (canary).
3. Deploy deadline+bulkhead+breaker patch to 10%; verify in-flight flat.
4. Roll 100% gradually; watch retry-amp 3.8x -> ~1.0x, threads flat.
5. Drain queues; replay failed pricings idempotently.
6. Land in-flight/amp/breaker alerts + chaos gate.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| In-flight | 18,000 | <300 | Alert >1k |
| Threads | 9,000 | <500 | Alert >1.5k |
| Retry amp | 3.8x | 1.05x | Alert >1.3x |
| p99 price | timeout (11-min melt) | 220ms | SLO 500ms |
| OOMKills | 2 pods | 0 | Page on any |

## Prevention Checklist
- [ ] Timeout + bulkhead + breaker on every fan-out
- [ ] Bounded reactive operators only (lint `flatMap` arity)
- [ ] Retry = backoff + jitter + budget (never naked ×N)
- [ ] In-flight + amplification dashboards

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- CompletableFuture / Flow API docs: https://docs.oracle.com/en/java/javase/21/docs/api/
- Spring Reactor / resilience reference: https://docs.spring.io/spring-framework/reference/web-reactive.html
