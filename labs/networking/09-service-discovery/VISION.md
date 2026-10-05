# VISION — Service Discovery: Finding a Moving Target
> Where this lab takes you: from "hardcode the URL" to a registry that is a distributed system, because that is what it becomes.

## The Arc
1. **Why** — the problem: instances appear, disappear, and scale; static config cannot track it.
2. **Patterns** — client-side vs server-side discovery, and the load balancer as a discovery mechanism.
3. **Registries** — registration, deregistration, heartbeats, and the split-brain problem.
4. **Kubernetes** — DNS-based discovery, headless services, and the StatefulSet case.
5. **Consistency** — what a client should do when the registry is wrong, and cache TTLs.

## Milestones (checkable)
- [ ] M1: explain why a client-side discovery cache is a correctness risk, not just staleness.
- [ ] M2: implement registration with heartbeats and demonstrate stale-entry eviction.
- [ ] M3: build a health-checked lookup that excludes an instance failing its check.
- [ ] M4: resolve a service via Kubernetes DNS and explain headless versus ClusterIP.
- [ ] M5: describe what happens to in-flight requests when every instance dies at once.

## Core Competencies
- Discovery patterns and when the platform already provides the answer.
- Registry semantics: heartbeats, leases, ephemeral registration, and self-preservation.
- Client-side caching trade-offs and circuit breaking on discovery failure.
- Stateful workloads: stable network identity, ordered startup, and StatefulSet DNS.

## Anti-Goals
- A registry that is a single point of failure with no client-side fallback.
- Deregistration only on graceful shutdown, with no heartbeat-based eviction.
- Assuming Kubernetes DNS exists for a headless service you have not defined.

## Interview Lens
- "What happens when your service registry is down but your services are up?"
- "How does a StatefulSet get a stable identity, and do you need one?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: registry implementation, heartbeats, eviction.
- Wk2 QUIZ/FLASHCARDS to 90%+; Kubernetes DNS experiments.
- Wk3 MINI_PROJECT with a registry and a client library.
- Wk4 REAL_WORLD_PROJECT: service discovery for a real platform.

## Done = You Can
- Operate a discovery layer that stays correct during deploys, crashes, and registry outages.
