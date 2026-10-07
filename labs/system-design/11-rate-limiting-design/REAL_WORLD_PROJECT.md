# Rate Limiting Design - REAL WORLD PROJECT

## Project: Platform-Wide Rate Limiting and Cost Control

**Time**: 2-3 weeks (team of 3)

**Scenario**: You run a multi-tenant platform with 400 services behind one
edge. Problems, all real:

- A single customer's integration is 40x over its contracted rate and you
  cannot tell which one until the invoice.
- A retry storm from one mobile client version took down an upstream dependency.
- Inference costs are your largest variable expense and are unbounded.
- Security endpoints (login, password reset, OTP) are under continuous attack.
- The legacy per-service limiters disagree, so a client can be rate limited by
  one service and not by another.

### Step 1: Write the Policy Before Writing Code

One table, reviewed by product, security, and finance:

| Route class | Key | Algorithm | Limit | Burst | Fail mode | Why |
|-------------|-----|-----------|-------|-------|-----------|-----|
| `/auth/login`, `/otp` | user **and** source IP | fixed window, strict | 5/min | 0 | **fail closed** | Credential stuffing; bursts are attacks |
| LLM inference | API key | token bucket | contract rate | 1.5x | **fail closed** | Cost scales 1:1 with money |
| Public read APIs | API key | token bucket | plan rate | 1.2x | fail open → local | Availability over marginal abuse |
| Internal svc→svc | service ID | concurrency limit | pool size | n/a | fail open → local | Prevents resource exhaustion |
| Bulk export | tenant | sliding window | plan rate | 0 | fail closed | Expensive, bursty, easy to abuse |

**This table is the primary deliverable.** Everything below implements it, and
it is what you take to the disagreement when a customer complains.

### Step 2: Two-Tier With a Derived Local Limit

```
Edge (global limiter, sharded Redis)
  -> local limiter (in-process, 250 ms decision cache)
     -> service
```

Derivation, written down and reviewed:
```
global G = 10,000 req/s ; N = 40 edge instances
local  L = ceil(G / N) * 1.2 = 300/s per instance
decision cache TTL = 250 ms  -> worst-case local overshoot = L * 0.25 = 75 req
```
The 1.2 factor exists so one instance cannot spend the entire global budget.
**Required test:** drive one instance at 10,000/s and prove other instances
retain at least 80% of their fair share.

### Step 3: Shard the Global Store

A single Redis for 10,000 writes/s is a bottleneck and a blast radius.

```
shard = hash(api_key) % 16
each shard: independent Redis/cluster node, independent keyspace
```
Measure: per-shard throughput should scale close to linearly with shard count.
Assert the hot-shard case too — one customer's API key exceeding every other
key combined. Detect via per-shard key-level metrics and add a second-level
limiter inside the hot shard.

### Step 4: Fail Modes That Are Not Binary

On store unavailability, degrade rather than choose between "allow all" and
"deny all":

```
store OK           -> use global decision
store slow/timeout -> use cached decision if younger than 250 ms
store unreachable  -> fall back to per-instance local limit only
                    -> emit limiter_degraded_total, page if sustained
```
For `/auth/*`, this degradation path is disabled entirely (fail closed) — a
security endpoint does not get a degraded mode.

**Required:** kill Redis during a load test and verify each route class behaves
per the table. Record admitted rates and p99 for each.

### Step 5: Cost Attribution (the part finance actually wants)

Rate limiting without attribution is just throttling.

- Every request carries the resolved identity (API key → tenant → plan) through
  the limiter decision, so usage events are emitted with the same identity that
  was counted.
- Emit a usage event per admitted request: `identity, route_class, plan,
  tokens_used, admitted`.
- Reconcile the sum against the upstream provider's bill. Target: < 0.1%
  variance. Investigate any variance above 0.5% automatically.
- Per-plan overage alerts at 50%, 80%, and 100% of contracted volume, with the
  customer notified at 80%. Alerting late is the same as not alerting.

### Step 6: Abuse Detection Beyond the Limit

Some abuse is under the limit. Detect patterns that a flat cap misses:

- **Distributed low-and-slow**: many IPs, one identity → alert on
  `distinct_ip_count(identity)`.
- **Credential stuffing**: many identities, one IP → alert on
  `distinct_identity_count(ip)`, tighter limit on `/auth/login` per IP.
- **Enumeration**: high rate of distinct resources at a low rate → alert on
  `distinct_resource_count` for read routes.
- **Token-bucket abuse**: a client that consistently stays just under the limit
  is profiling. Long-window rolling volume with a slower limit catches this.

Each signal becomes a *separate* limiter or alert with its own justification.
Do not fold them into the main limit.

### Step 7: Failure Drills

1. **Redis shard down.** Verify requests for keys on that shard degrade to local
   limits, that latency does not spike beyond the deadline, and that
   `limiter_degraded_total` pages.
2. **Retry storm.** 5,000 clients with full jitter vs. no jitter, retrying a
   `429`. Record admitted-rate oscillation for both — the no-jitter run should
   visibly oscillate. This is the evidence that ships the jitter requirement.
3. **Instance count halves.** Verify the local limit no longer divides
   correctly and that the global limiter is now the only thing preventing
   overshoot. This drill usually reveals that the 1.2 factor was too tight.
4. **Hot key.** Point 40% of traffic at one API key. Verify per-shard metrics
   detect it and that a key-level limiter engages.
5. **Clock skew of 3 s** on an edge instance. Verify token buckets use monotonic
   time and remain correct.

### Deliverables

1. The policy table, with product/security/finance sign-off.
2. Two-tier implementation with the derived local limit and the noisy-instance
   test.
3. Sharded global store with measured scaling and hot-key detection.
4. Degraded-mode implementation, verified per route class by drill.
5. Cost attribution pipeline with < 0.1% reconciliation to the provider bill.
6. Pattern-based abuse detection with four signals and their justifications.
7. Five drill reports with numbers, especially the jitter comparison.
8. Metrics: admitted/denied by route class, limiter latency p99, degraded mode
   duration, decision cache hit rate, per-shard throughput, per-key rate.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Policy | One global limit | Per-class table with keys, algorithms, fail modes |
| Local tier | Same limit as global | Derived `G/N * 1.2`, noisy-instance test |
| Failure | Binary fail-open | Route-class-specific degraded modes, drilled |
| Attribution | "We log requests" | Reconciles to provider bill < 0.1% |
| Abuse | Only flat caps | Pattern signals beyond the limit |
| Retries | Fixed backoff | Full jitter with an oscillation comparison |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Redis documentation — *Rate limiting* use case, including the token bucket
  and sliding window Lua-script patterns and the atomicity argument for doing
  the check and the increment in one script. Quote the Lua examples rather than
  paraphrasing the atomicity requirement.
  (link removed)
- RFC 6585 — *Additional HTTP Status Codes*, section 4: the normative
  definition of `429 Too Many Requests` and the `Retry-After` header
  semantics. Cite the section when arguing for `Retry-After` on a `429`.
  https://www.rfc-editor.org/rfc/rfc6585.html

Re-verify the Lua script shapes against your Redis version (cluster-mode
restrictions on script keys apply), and confirm that standardised `RateLimit-*`
response header field names/format are taken from the current spec rather than
from a blog post, since header naming has been standardised after this lab's
template was written.