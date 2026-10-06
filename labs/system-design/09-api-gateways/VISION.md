# API Gateways - Vision

## Why This Lab Exists
A platform with 200 services has 200 places to solve TLS, authentication, rate
limiting, logging, and protocol translation — and 200 implementations that will
disagree. The gateway exists to make those policies defined **once** and
enforced **consistently**. This lab exists so you build one that is a policy
enforcement point and not a second monolith.

## The Mental Model
Four layers, each with one job:

```
  EDGE    -> is this request safe to accept?      (TLS, WAF, limits, trace)
  AUTH    -> who is calling?                      (verify, never decode)
  ROUTE   -> where does it go, under what budget? (match, discover, limit)
  AGGREGATE-> can we answer with fewer trips?     (optional BFF)
```

The one sentence that governs every decision:

> **The gateway answers "can this request proceed?", never "is this request
> correct?"**

The moment the gateway needs domain data to decide, it has become a service, and
you now have a monolith with a network hop.

## The Costs You Are Accepting
A gateway is a hop. It is in the critical path of 100% of traffic, so its
outage is a platform outage. Budget for it:

```
  end_to_end = edge + auth + route + service + shaping
  A_platform <= A_gateway
```
That single inequality is the strongest argument both for and against the
gateway: it gives you one place to enforce policy, and it gives you one place
to break everything.

## What You Should Be able To Do
- Decompose a gateway into layers and justify each boundary.
- Verify a JWT properly, and explain what "decode" leaves open.
- Design routing with specificity, timeouts, and deadline propagation.
- Build a BFF with per-field criticality and bounded aggregate deadline.
- Choose fail-open vs. fail-closed per route class and justify it.
- Instrument a gateway so a single broken service is visible in the numbers.

## The Anti-Goals
- No business logic. No database calls. No "can this user refund this order".
- No retries of non-idempotent requests. This is how gateways cause duplicate
  charges.
- No forwarding of inbound identity headers. This is authentication bypass, and
  it is one of the most commonly shipped "gATEWAY" vulnerabilities.

## Success Criteria
You can walk any request through your gateway and account for its latency
budget hop by hop, name the failure mode of each component, and show that
neither the metrics nor the cardinality of your instrumentation will mislead you.

## How To Use This Lab
1. `THEORY.md` for the architecture and the layer boundaries.
2. `MATH_FOUNDATION.md` for latency budgets, fan-out, and sizing.
3. `CODE_DEEP_DIVE.md` for router, JWT verifier, sanitiser, BFF.
4. `EXERCISES.md` for twelve applied problems; `QUIZ.md` to check yourself.
5. `MINI_PROJECT.md` to build one; `REAL_WORLD_PROJECT.md` to run one.