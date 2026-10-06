# API Gateways - Quiz

15 questions. Answer before checking the key at the bottom of each section.

---

## Section A: Architecture (Q1-5)

**Q1.** What is the single sentence that decides whether logic belongs in an API gateway?

**Q2.** Name the four gateway layers in the order a request passes through them.

**Q3.** Why is the aggregation (BFF) layer described as optional, and when is it clearly worth building?

**Q4.** A gateway calls the database during request handling. List two distinct production problems this causes.

**Q5.** Your platform has 200 services and a new engineer adds rate limiting to one of them. What problem does that create, and what is the gateway's role?

---

## Section B: Security (Q6-8)

**Q6.** A client sends a valid JWT plus `X-User-Id: admin`. What must the gateway do, and what is the vulnerability if it does nothing?

**Q7.** What does "the gateway must verify, not decode" mean, and what code is insecure here: `Base64.decode(parts[1])` followed by forwarding `payload.sub` as the user?

**Q8.** Your gateway verifies JWTs but also forwards inbound `X-Internal-Call: true`, which services trust. Name the attack and the fix.

---

## Section C: Latency and Fan-Out (Q9-11)

**Q9.** Client timeout is 1,000 ms. Gateway self-budget is 50 ms. What downstream timeout should the gateway set, and why must it be *shorter* than the caller's?

**Q10.** Why must a deadline be propagated as an absolute timestamp rather than as a duration?

**Q11.** Five services are aggregated in parallel, each with p99 = 400 ms. Is the fan-out's p99 approximately 400 ms? Explain.

---

## Section D: Reliability (Q12-15)

**Q12.** What is wrong with a gateway that retries `POST /payments` on timeout?

**Q13.** Why does a circuit breaker alone not protect gateway capacity, and what should accompany it?

**Q14.** Your identity provider rotates signing keys hourly. What breaks, and what is the specific mechanism that fixes it?

**Q15.** Gateway p95 latency tripled while overall CPU stayed at 55%. Give the first three things you look at and why each is more likely than a CPU issue.

---

## Answer Key

**A1.** The gateway answers *"can this request proceed?"*, never *"is this request
correct?"*. The moment it needs domain data to make a decision, it has become a
service. Cross-cutting, identical-for-every-service policy goes in; anything
requiring domain knowledge does not.

**A2.** (1) Edge — TLS, WAF, IP allowlist, request ID, body/header limits, trace
init. (2) Authentication — signature, expiry, issuer, audience, scope
extraction. (3) Routing — matching, discovery, load balancing, deadline
propagation, rate limiting, breakers. (4) Aggregation — optional BFF composing
multiple calls.

**A3.** It exists to reduce client **round-trips and fan-out**, not to host logic.
It is clearly worth building when clients are mobile or bandwidth-constrained
(many round-trips are expensive) and clients are first-party (you control the
release). For browsers with CORS solved, the latency gain rarely justifies the
aggregation failure surface.

**A4.** (1) Every request to the platform now depends on that database's
availability and latency — including requests unrelated to accounts, so its
outage becomes a platform outage. (2) Slow queries accumulate gateway
connections, exhausting its pool and turning a database problem into a gateway
problem. Add: you now cannot reason about the database's capacity without also
reasoning about the gateway's.

**A5.** It creates 200 independent, disagreeing implementations of one policy —
different algorithms, keys, thresholds, and failure modes. Clients then get
inconsistent treatment depending on which service they hit, and the platform has
no single place to enforce or observe the limit. The gateway owns enforcement so
the policy is defined once; services may still add *domain-specific* limits the
gateway cannot know (e.g. per-order), but not platform-wide ones.

**B6.** **Drop the inbound `X-User-Id` and derive identity from the verified
token.** Otherwise this is authentication bypass: anyone with any valid token can
claim to be any user, because the service trusts a client-supplied header over
the gateway's verified claim. Identity headers must be in a **deny-list of
inbound headers** that the gateway always strips.

**B7.** Decoding is not verification. `Base64.decode(parts[1])` performs no
signature check, no expiry check, no issuer check, no audience check. An attacker
can craft any payload they like — including `{"sub":"admin"}` — and it will be
forwarded as the authenticated user. It must also pin the algorithm: accepting
the header's `alg` allows `alg: none` and the RS256-to-HS256 confusion attack
(using the public key as an HMAC secret).

**B8.** An attacker sets `X-Internal-Call: true` to bypass authentication or
reach admin-only endpoints, because a trusted service acts on that header
without re-verifying. Fix: strip `X-Internal-Call` (and every other inbound
identity/privilege header) at the edge, and require internal callers to
authenticate with a service identity (mTLS or a service token) rather than a
trustworthy-looking header.

**C9.** 950 ms. It must be shorter than the caller's timeout so the gateway
returns a *useful* error while it still has budget to shape the response. If the
downstream timeout equals the client timeout, the client has already given up
and the gateway's response is discarded — you lose the chance to return a proper
status, log the failure cleanly, or return `Retry-After`.

**C10.** Because a duration **restarts at every hop**. A 950 ms duration relayed
through three hops permits 2,850 ms of work while the client abandoned at
1,000 ms. An absolute deadline timestamp is inherited and decremented, so the
total across all hops is bounded by the original deadline regardless of path
length. Without this, wasted work compounds down the call chain.

**C11.** No. The response is as slow as the slowest of five, so the fan-out's
distribution is much worse: P(all five under 400 ms) = 0.99^5 = 0.951, meaning
the fan-out's p95 is already at the single service's p99, and its p99 is
several times worse (~700-1,500 ms). This is why per-field timeouts and null
fallbacks are structural requirements for aggregation rather than polish.

**D12.** A timeout tells you nothing about whether the request was processed. The
charge may have succeeded, so retrying can double-charge the customer. Combined
with client retries, amplification of `3 * 2 * 3 = 18x` requests reaches the
processor. Fix: retry only idempotent requests (or those with an idempotency
key), only at one layer, only on connection-level failures, and with jitter.

**D13.** A breaker is per *dependency state*, not per *gateway capacity*. A
dependency that is slow but not failing generates no errors, so the breaker never
opens and requests pile up holding gateway connections. Breakers protect the
dependency from a bad gateway; **concurrency limits** protect the gateway's own
capacity. You need both. Also, per-instance breakers can all open at once, so
they do not by themselves prevent a fleet-wide stall.

**D14.** A token signed with the new `kid` arrives, the cached JWKS has only the
old key, and it returns **401** — for up to the full cache TTL. With an hourly
rotation and a 6-hour cache, every rotation is a scheduled authentication
outage. The fix is **refresh-on-unknown-kid**: on an unrecognised `kid`, do a
single-flight, rate-limited JWKS refetch, keep serving cached keys during the
refresh, and set the TTL to exceed the rotation interval. This also matters
during an emergency key rotation, which is exactly when you need it to work.

**D15.** First, **auth-stage latency specifically** — a JWKS unknown-`kid` storm
after a rotation turns every request into a fetch to the identity provider, and
CPU stays low while latency triples. Second, **per-downstream-service latency
breakdown** — one degraded service shows up as a gateway aggregate spike while
the gateway itself looks idle; the aggregate is a symptom, not a location.
Third, **circuit breaker state per service** — a half-open probe storm can
saturate a service with concurrent probes. A CPU-based explanation is last
because 55% CPU leaves substantial headroom, and because a CPU problem would
show up as a *throughput* ceiling rather than a 3x latency jump at unchanged
traffic.