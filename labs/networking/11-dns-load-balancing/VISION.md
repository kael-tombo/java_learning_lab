# VISION — DNS & Load Balancing: The Layer Everyone Ignores
> Where this lab takes you: from "add a DNS record" to understanding caching, failover, and why a TTL decision is an availability decision.

## The Arc
1. **Resolution** — recursive vs iterative, root → TLD → authoritative, and what each hop caches.
2. **Records** — A, AAAA, CNAME, SRV, TXT, and the delegation/lookup differences that matter.
3. **Caching** — TTL semantics, resolver behaviour, and stale-answer behaviour.
4. **Load balancing** — round robin, weighted, least-connections, and DNS-level limitations.
5. **Operations** — health checks, failover, TTL tuning, and the propagation delay you cannot avoid.

## Milestones (checkable)
- [ ] M1: trace a full resolution from a client to an authoritative server and note every cache.
- [ ] M2: explain why a CNAME chain adds latency and what it breaks.
- [ ] M3: measure the effect of TTL on a failover and on cache hit rate.
- [ ] M4: implement weighted round robin and least-connections balancing.
- [ ] M5: design a health check that does not send a thundering herd when a node returns.

## Core Competencies
- Record types, delegation, and which query type returns which cached answer.
- TTL trade-offs: fast failover versus cache efficiency and query load.
- Balancing algorithms and their behaviour under skew and long-lived connections.
- Health checking, including the failure mode where a check itself becomes the outage.

## Anti-Goals
- A 24-hour TTL on a service that must fail over quickly.
- Round-robin DNS presented as reliable load balancing for long-lived connections.
- Health checks with no interval budget, creating a thundering herd on recovery.

## Interview Lens
- "Your DNS change hasn't propagated. Explain every cache in that path."
- "Round-robin DNS is hurting us. What's actually wrong?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: dig through each hop, measure cache behaviour.
- Wk2 QUIZ/FLASHCARDS to 90%+; balancing algorithm benchmarks.
- Wk3 MINI_PROJECT: a DNS server plus a balancer with health checks.
- Wk4 REAL_WORLD_PROJECT: multi-region failover with measured propagation.

## Done = You Can
- Diagnose a resolution problem by identifying which cache is holding a stale answer,
  and design a TTL policy from an explicit failover objective.
