# VISION — Lab 12: Caching Strategies & Cache Invalidation

> From "add Redis" to "here is the staleness I accept, the number it buys, and the failure it prevents."

---

## The Arc

1. **Is caching the right tool** — read/write ratio, origin latency vs SLO, and the capacity case as the honest justification.
2. **Patterns** — cache-aside, write-through, write-behind, read-through, refresh-ahead, and what each makes authoritative.
3. **TTL as a business decision** — staleness tolerance per field, expected vs worst-case staleness, jitter.
4. **Invalidation** — delete vs update, single-write-path discipline, versioned keys, and why enumeration does not scale.
5. **Multi-level caching** — L1/L2 compounding, broadcast unreliability, and the version-check guarantee.
6. **The stampede family** — penetration, avalanche, breakdown, and the distinct fix for each.
7. **Serve stale while revalidate** — refresh-ahead, soft TTL, and the hard max-stale bound.
8. **Keys** — typed keys, every input that changes the response, schema version.
9. **HTTP caching** — the layer you did not control, and the cross-user leak waiting to happen.
10. **Measurement** — per-class hit ratio, load duration as a leading indicator, memory in the container budget.

---

## Why this lab exists

Caching is the most widely deployed and least rigorously reasoned subsystem in most estates. A cache is added because the site was slow, it is tuned by hit ratio alone, and its invalidation is a mix of `@CacheEvict` annotations and optimism.

The specific goal here: **you can decide whether to cache, per data class, and defend that decision with numbers; you can set TTLs from business staleness tolerances; and you can explain the stampede you are protecting against.**

---

## Milestones (checkable)

- [ ] M1: For a real service, produce a per-class table: `λ`, `h`, origin load contribution, staleness tolerance, chosen TTL with jitter, and verdict (cache / do not cache).
- [ ] M2: Compute the break-even hit ratio for one endpoint against its SLO and conclude whether caching helps latency, capacity, or neither.
- [ ] M3: Reproduce a cache stampede on a hot key, then eliminate it with jitter, single-flight, and refresh-ahead — measuring origin load for each.
- [ ] M4: Implement L1 + L2 with version-based invalidation and demonstrate that a dropped broadcast causes a reload, never a wrong answer.
- [ ] M5: Implement negative caching and a bloom filter, and measure the reduction in origin load from non-existent-key lookups.
- [ ] M6: Serve stale while revalidating with a hard max-stale window, and demonstrate the failure mode when the origin is down and the window is unbounded.
- [ ] M7: Budget the cache memory inside a container memory limit and show the OOM-kill that occurs when it is not.

---

## Anti-Goals

- One global TTL for every cached field.
- Un-jittered TTLs.
- Caching a field with near-zero staleness tolerance (balances, entitlements).
- Aggregate-level cache keys with concurrent writers.
- Enumeration-and-delete of derived keys at high update rates.
- Caching a per-user response under a URL-only key.
- Enabling `no-store` on nothing and `Cache-Control` thoughtlessly on personalised responses.
- A cache whose memory is not in the container budget.
- Optimising on global hit ratio while one class dominates origin load.

---

## Interview Lens

- "How do you choose a cache TTL?"
- "What causes a cache stampede and how do you stop it?"
- "How do you invalidate a multi-level cache across 200 pods?"
- "When is a cache a bad idea?"
- "How do you know your cache is helping?"

---

## 30-Day Plan

- **Week 1** — THEORY + ARCHITECTURE_DECISIONS: patterns, TTL policy, invalidation strategies; hands-on with Caffeine and Redis, measuring hit ratio and load duration. M1–M2.
- **Week 2** — EXERCISES: amortisation math, stampede/penetration arithmetic, memory budgeting; QUIZ to 13/15; FLASHCARDS daily. M3.
- **Week 3** — MINI_PROJECT: build the two-level cache, reproduce and fix every stampede variant, and produce per-class evidence. M4–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a caching plan for a real service; teach-back: "our staleness budget, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A per-class cache decision table with break-even hit ratios and chosen TTLs.
2. A stampede reproduction with origin load before and after each mitigation.
3. A multi-level invalidation design where a dropped broadcast is provably safe.
4. A per-class hit-ratio dashboard plus load-duration alerting.
5. A memory budget showing the cache inside the container limit.

---

## Done = You Can

- Argue for or against caching a specific field, with numbers.
- Set a TTL from a business tolerance and defend the jitter.
- Explain which stampede variant you are defending against and why your fix targets that one.
- Prove that a cache failure degrades latency rather than correctness.
