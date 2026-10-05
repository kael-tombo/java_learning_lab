# MINI_PROJECT — Reproduce, Detect, Fix Pool Exhaustion

## Objective
Exhaust a 3-slot Hikari pool with a leak, diagnose from metrics + stacks, fix and verify. ~80 min.

## 1. Setup (15 min)
Spring Boot + Hikari + Postgres (or H2 for leak-only path). Set max=3, timeout=5s, leakDetection=8s. Expose actuator metrics.

## 2. Inject (15 min)
```java
@GetMapping("/leaky") String leaky() throws Exception {
  Connection c = ds.getConnection();  // never closed on purpose
  c.createStatement().execute("SELECT pg_sleep(2)");
  return "ok"; // LEAK: slot never returned
}
```
Hammer: `seq 1 10 | xargs -P10 -I{} curl -s localhost:8080/leaky`.

## 3. Detect (20 min)
- `curl actuator/metrics/hikaricp.connections.active` → 3/3, pending rising.
- Logs: timeout exceptions + leak warnings with `OrderDao:line` stacks.
- `jstack`: threads parked at `getConnection`. Screenshot all three.

## 4. Fix (20 min)
Rewrite with try-with-resources; add slow-query guard (`SET statement_timeout=3s`).
Rerun hammer — active drains to 0 idle, pending 0, p99 normal.

## 5. Size (10 min)
Given 12 pods + DB max 100, compute per-pod max with 20% headroom (answer: 6). Document PgBouncer trigger point (>50% DB conns idle).

## Deliverables
Metric screenshots, leak stack, fix diff, sizing math, postmortem paragraph.

## Grading
Reproduce (25%), detect trio (35%), fix+verify (25%), sizing (15%).
