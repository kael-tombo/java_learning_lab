# REAL-WORLD PROJECT — Reactive: SSE Outage on Earnings Burst

## Incident Scenario
Earnings-day burst (12x ticks) OOMs the SSE ticker fleet in 4 minutes; slow
mobile clients wedge the shared flux, retries amplify the flood, and a hidden
blocking `priceRepo.findById` on the event loop freezes even `/health`.

## Symptoms
- Heap vertical then `OutOfMemoryError`; unbounded `onBackpressureBuffer`.
- One slow subscriber stalls multicast; disconnects never cancel upstream.
- `retry()` infinite on failing FX-rate call — self-DDoS.
- BlockHound absent; JDBC call inside `map` parks all event-loop threads.
- `traceId` lost across `publishOn` — logs unjoinable during incident.

## Investigation Tasks
1. Live: `jcmd <pid> Thread.print` × 3 — event-loop threads in
   `socketWrite`/`BLOCKED` on JDBC; `jcmd <pid> GC.heap_dump` for buffer pile.
2. JFR: `jcmd <pid> JFR.start duration=180s filename=react.jfr settings=profile`;
   inspect `jdk.ObjectAllocationInNewTLAB` (tick backlog), `jdk.ThreadPark`,
   `jdk.SocketWrite`, `jdk.JavaMonitorEnter` on shared sink.
3. Backpressure audit: `grep -rn "onBackpressure\|request(\|retry(\|block()" src/`;
   list every unbounded buffer and infinite retry.
4. Repro: burst generator 12x 2 min against staging; watch heap slope +
   slow-client (throttled SSE) impact on fast clients.
5. Blocking proof: enable BlockHound in staging — record violation stack.
6. Logs: `grep "Dropped\|Overflow\|Retry" app.log | sort | uniq -c`; confirm
   retry storm volume vs upstream capacity.
7. Cancel check: disconnect SSE mid-burst, verify upstream demand decreases
   (JFR/custom `doOnCancel` counter).

## Root Cause
Unbounded demand + shared hot flux with no isolation + blocking I/O on loop +
infinite retry + no slow-consumer policy — burst converts to heap + loop
starvation + retry amplification.

## Resolution
- Immediate: cap buffer (drop/latest + metric), disable infinite retry,
  move JDBC off loop (boundedElastic/R2DBC), shed slow clients (timeout).
- Short-term: per-symbol isolation, jittered budgeted retries, Context
  traceId propagation, cancel-aware sinks, `/health` on separate scheduler.
- Long-term: burst SLO + chaos (burst game day), BlockHound in CI, JFR
  backpressure dashboard, load-shed (429) policy.

## Runbook
```
1. Thread.print + JFR + heap_dump before restart; note loop stacks.
2. Flip to bounded overflow + retry-budget build on canary.
3. Verify heap flat + loop free on next burst replay.
4. Enable slow-client shed; confirm fast clients clean.
5. Postmortem: burst SLO + BlockHound gate.
```

## Metrics
- 12x burst 5 min: heap flat (< 1GB), OOMs = 0, slow clients shed cleanly.
- Event-loop block time = 0 (BlockHound); retry volume within budget.
- SSE p99 < 1s at burst; `/health` 200 throughout.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Spring WebFlux reference: https://docs.spring.io/spring-framework/reference/web-reactive.html
- Flow API (demand model): https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Flow.html
