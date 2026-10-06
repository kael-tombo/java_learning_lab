# Scalability - Vision

## Why This Lab Exists
"Scale up until you can't" is a strategy with a known, expensive endpoint.
Every scalability decision is really a bet about *which axis* you are short on:
CPU, memory, disk IOPS, network bandwidth, or — most commonly, engineering
attention. This lab exists to make that bet explicit and arithmetic-backed.

## The Mental Model
Scaling is a funnel. Every request traverses:

```
  Client -> Edge/CDN -> App Tier -> Cache -> Primary Store -> Replicas
```

You relieve pressure at the **narrowest** point first, because that is where
the fewest moving parts sit. A CDN absorbs static bytes that would otherwise
cost an app-tier node. A cache absorbs reads that would otherwise cost a
database connection.

## Three Axes, One Choice
- **Vertical** — bigger box. Simple, immediately effective, hits a ceiling
  fast, and you cannot scale a single-threaded hot function past 64 cores.
- **Horizontal** — more boxes. Requires statelessness, which requires moving
  session state somewhere, which is its own project.
- **Diagonal** — shed or defer work (queues, backpressure, sampling) so the
  system degrades predictably instead of collapsing.

## What You Should Be Able To Do
- Compute required capacity from QPS, payload size, and a stated p99 target.
- Choose a sharding key from access-pattern evidence, not from vibes.
- Size a connection pool and show the Little's Law arithmetic behind it.
- Explain what breaks *first* as you scale out (usually fan-out connections).
- Recognise when the correct answer is "no, the load is fine; your query is
  the problem."

## The Anti-Goals
- Not throughput-maximalist design. A system that serves 10k rps and burns a
  full team on operations has failed.
- No cargo-cult sharding. Sharding is a cost, not a badge.
- Averages are not latency. This lab thinks in p99 throughout.

## Success Criteria
Given a workload description and an SLO, you produce a capacity plan with
headroom, a bottleneck analysis, and a named scaling axis — and you can defend
each number.

## How To Use This Lab
1. `THEORY.md` for the scaling vocabulary.
2. `MATH_FOUNDATION.md` for queueing, Amdahl, Little's Law.
3. `CODE_DEEP_DIVE.md` for the load generator and sharding sketches.
4. `MINI_PROJECT.md` to build a measurably scaling pipeline.
5. `REAL_WORLD_PROJECT.md` for a multi-tenant capacity plan.
