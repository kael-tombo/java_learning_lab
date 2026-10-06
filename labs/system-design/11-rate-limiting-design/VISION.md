# Rate Limiting Design - Vision

## Why This Lab Exists
Rate limiting is the cheapest load shedding mechanism you will ever deploy, and
also the one most often deployed wrongly: global instead of per-tenant, fixed
window instead of sliding, counted after the expensive work instead of before,
and fail-*open* on error. Each mistake produces either a self-inflicted outage
or a hole in your abuse protection. This lab exists so the limiter is designed
as a load-shedding and fairness system, not a counter.

## The Mental Model
A rate limiter answers: *who may do what, how often, and what happens when they
exceed it?* Three decisions, in this order:

```
  1. IDENTITY   which key is limited (user? tenant? IP? API key? endpoint?)
  2. ALGORITHM  token bucket, leaky bucket, sliding window, concurrency limit
  3. FAILURE    when the store is unavailable, allow or deny?
```

The third is the one people skip, and it decides whether a Redis blip takes
down your whole service.

## Algorithms Are Trade-offs, Not Preferences

| Algorithm | Smoothness | Memory | Allows bursts | Cost |
|-----------|-----------|--------|---------------|------|
| Fixed window | bursty at boundary | O(1) | up to 2x limit | lowest |
| Sliding window log | smooth | O(limit) | no | highest |
| Sliding window counter | smooth-ish | O(1) | slight | low |
| Token bucket | smooth, bursty-allowed | O(1) | yes, up to bucket | low |
| Leaky bucket | strictly paced | O(1) | no | low |
| Concurrency limit | n/a | O(active) | no | lowest |

Note that fixed window permits **2x your limit** across a boundary. If your
limit is a security control, that doubling is a real hole.

## Three Different Jobs
1. **Fairness** — one tenant cannot starve others. Needs per-tenant limits.
2. **Overload protection** — protect *yourself* from a traffic spike. Needs a
   global concurrency limit plus graceful degradation.
3. **Abuse / cost control** — stop a single actor. Needs identity plus
   escalation, not a flat cap.

These three want different keys and often different algorithms. Design all three;
do not conflate them.

## What You Should Be able To Do
- Choose an algorithm per surface from burstiness, memory, and correctness needs,
  and defend the choice with the boundary-behaviour arithmetic.
- Implement token bucket with correct lazy refill and a monotonic clock.
- Explain why `Math.random()` jitter on the retry is mandatory to prevent
  retry synchronisation.
- Decide fail-open vs. fail-closed per endpoint class and write that down.
- Size the store: keys, memory, and the network cost of one decision per request.
- Combine a local in-process limiter with a global one, and explain why the
  local one is not sufficient on its own.

## The Anti-Goals
- Not "add Redis and call it done." A per-request round trip to Redis has a
  latency and availability cost you must own.
- Never fail open on an authentication endpoint; never fail closed on a
  read-only catalogue.
- No limiter that counts *after* the work is done. Counting after is billing,
  not protection.

## Success Criteria
You can specify a rate-limiting policy per route with: key, algorithm,
parameters and their derivation, fail mode, response contract
(`429` + `Retry-After` + rate-limit headers), and the cost in store operations
per request.

## How To Use This Lab
1. `THEORY.md` for the architecture and pattern catalogue.
2. `MATH_FOUNDATION.md` for burst behaviour, token math, sizing, jitter.
3. `CODE_DEEP_DIVE.md` for token bucket, sliding window, concurrency limit.
4. `MINI_PROJECT.md` to build and stress-test a limiter.
5. `REAL_WORLD_PROJECT.md` for platform-wide limiting and abuse control.