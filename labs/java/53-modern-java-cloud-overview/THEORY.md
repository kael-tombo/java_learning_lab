# THEORY — Modern Java in the Cloud

## 1. The container contract (5 rules)

1. **One process per container**; stateless — session/data live outside.
2. **Cgroup-aware JVM**: `-XX:MaxRAMPercentage=75.0` (not `-Xmx`) so heap
   tracks the container limit; expose the rest to metaspace/direct/thread
   stacks. Check `java -XshowSettings:system` output inside the image.
3. **Layered image**: dependencies layer cached, app classes on top —
   rebuilds ship kilobytes, not hundreds of MB.
4. **Non-root user**, read-only FS where possible; `USER 65532`.
5. **Health endpoints**: liveness (`/actuator/health/liveness`) vs
   readiness (dependencies up?) — orchestrators kill/route on these.

## 2. Startup budgets: JVM vs native vs CRaC

- Classic JVM: 2–10 s (Spring) — fine for long-lived services, painful
  for scale-to-zero/functions.
- GraalVM native: 50–200 ms, ~½ RAM — ahead-of-time closed world
  (reflection config!) for bursty/scale-to-zero paths.
- CRaC (Coordinated Restore at Checkpoint): snapshot warm JVM, restore in
  ms — keeps full JVM dynamism. Choose per workload, not per religion;
  one codebase can ship both artifacts.

## 3. Virtual threads change the methods chapter

Platform-thread pools forced reactive/async code for throughput. Virtual
threads (1M+ cheap threads, carrier-mapped) let plain blocking code
(`JdbcTemplate`, `RestClient`) saturate I/O — simpler code, same density.
Rule: blocking + virtual threads first; reactive only for backpressure
shaping or existing ecosystems. Pinning caveat (`synchronized` pins
carriers — prefer `ReentrantLock`) belongs in every review checklist.

## 4. Observability is the API

Logs to stdout (JSON), metrics via Micrometer (RED: rate/errors/duration
per endpoint), traces via OpenTelemetry (W3C propagation across service
boundaries), JFR flight recordings for deep dives. If a deploy can't show
its traces in the cloud console, it isn't production — labs 54–56 each
wire this to CloudWatch / Cloud Monitoring / App Insights.
