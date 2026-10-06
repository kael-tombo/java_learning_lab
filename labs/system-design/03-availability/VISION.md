# Availability - Vision

## Why This Lab Exists
Availability is the one property a customer notices only when it is missing.
Every component you add — a replica, a queue, a cache, a third-party API — also
adds a new way to be down. This lab exists to make availability an *engineered
number* with a budget, rather than an aspiration in a slide deck.

## The Mental Model
Availability is arithmetic, not vibes. Two identities do most of the work:

```
  MTTF = MTBF / (1 - A)              A   = MTBF / (MTBF + MTTR)
  Chain:   A = A1 x A2 x ... x An     Parallel: A = 1 - (1 - Ai)^n
```

Chain availability multiplies, so **every extra hop is expensive**. Ten 99.9%
dependencies in series give 99.0%. Parallel redundancy saturates fast, which is
why N+2 beats N+1 at the margin and N+1 beats N at all.

## Four Levers, In Order
1. **Remove the single point** — redundancy, multi-AZ, no shared fate.
2. **Detect fast** — health checks that probe *behaviour*, not liveness.
3. **Fail fast and isolate** — circuit breakers, bulkheads, timeouts.
4. **Degrade gracefully** — serve stale, serve partial, serve cached.

You do not get to skip a lever. A replica without a breaker is a faster
correlated outage.

## What You Should Be able To Do
- Compute end-to-end availability from a dependency graph and find the
  dominant contributor.
- Choose RTO/RPO per tier and justify the cost of each.
- Design health checks that catch a degraded-but-alive process (the common bug).
- Size a failover and prove it does not double your error rate (thundering
  herd / flapping).
- Convert an SLO into an error budget and a burn-rate page threshold.

## The Anti-Goals
- Not "active-active everywhere". Blind multi-writer buys a split-brain
  problem you will pay for later.
- Availability of a *cache* is not availability of the *system*.
- No 100% SLA. It is unimplementable, uncosted, and makes every real
  conversation about trade-offs disappear.

## Success Criteria
Given a dependency graph, you can produce: end-to-end availability, the top
three reliability contributors, a failover design with a measured MTTR, and an
error budget with a burn-rate alerting policy.

## How To Use This Lab
1. `THEORY.md` for SLIs/SLOs/SLAs, redundancy, failover, DR.
2. `MATH_FOUNDATION.md` for MTBF, MTTR, N+2, cost of HA.
3. `CODE_DEEP_DIVE.md` for circuit breaker, health check, failover.
4. `MINI_PROJECT.md` to build an HA product service.
5. `REAL_WORLD_PROJECT.md` to run a full failover game day.