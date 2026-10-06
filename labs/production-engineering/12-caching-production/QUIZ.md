# Lab 12: Caching Strategies & Cache Invalidation — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. Cache-aside vs write-through vs write-behind — what does each change?**
- A) They are the same
- B) Cache-aside: app reads cache, on miss reads DB and populates (app owns the load); write-through: write goes to cache and DB synchronously, cache is never stale; write-behind: write goes to cache, DB write is async, so cache is authoritative and you risk loss/inconsistency
- C) Only write-through is safe
- D) Write-behind is just write-through with a delay

**Answer: B** — Cache-aside is the default for read-heavy data. Write-behind's risk is real data loss on cache eviction; treat it as "the cache is the database", which carries consequences.

---

**Q2. Why does write-through require the cache to be a full write path, including deletes and TTLs?**
- A) It does not
- B) Because every mutation must go through the cache layer; if any code path writes to the DB directly, the cache silently diverges. A TTL is your safety net for the paths you missed — which is why write-through is usually paired with a short TTL as well
- C) Because caches cannot read
- D) TTLs are only for read caches

**Answer: B** — "Only one way to write" is the invariant. Audit it, because ORM bulk operations, migrations, and admin tools all bypass application code.

---

**Q3. What is the TTL decision really?**
- A) Pick a small number for safety
- B) `TTL ≈ staleness_tolerance × safety`, where the real cost of staleness is measured per field. A country list can be cached for a day; a stock balance for 200 ms. Staleness tolerance is a business property, not an engineering preference
- C) One global TTL
- D) TTL should always equal the DB transaction timeout

**Answer: B** — One global TTL is the most common caching mistake after not having a cache at all. Different fields have wildly different tolerances.

---

**Q4. Why does a cache stampede (thundering herd) happen, and what actually fixes it?**
- A) Because the cache is too small
- B) When N keys expire simultaneously, N concurrent misses hit the origin and, for cache-aside, all N write the same value. Fixes: (1) jittered TTLs so expiry is spread, (2) single-flight/lock so only one loader runs, (3) serve stale while revalidating, (4) early recomputation (refresh before expiry)
- C) Because of network latency
- D) Because of slow GC

**Answer: B** — Jitter is the cheapest fix and the one most often missing. Without it, a synchronized expiry is a scheduled origin overload.

---

**Q5. What does "serve stale while revalidate" buy, and what is its risk?**
- A) Nothing
- B) It lets you serve the (slightly stale) cached value while one request refreshes in the background, so latency never depends on the origin. Risk: if the origin is down and you never bound staleness, you serve arbitrarily old data — so pair it with a hard max-stale window after which you fail or degrade visibly
- C) It doubles memory
- D) It invalidates on write

**Answer: B** — Unbounded staleness is a silent correctness failure. The hard max-stale window is the part people omit.

---

**Q6. Multi-level cache (L1 in-process, L2 Redis): what is the main risk?**
- A) L1 is faster but not shared, so invalidation must reach every JVM's local cache — and a broadcast over 200 pods is neither instant nor reliable
- B) L2 is slower than L1
- C) L1 cannot store objects
- D) L2 does not support TTL

**Answer: A** — L1 invalidation is the hard part. Options: pub/sub invalidation with a version-number check, very short L1 TTL, or message-driven local cache updates (the most reliable, at the cost of coupling).

---

**Q7. How does a version/epoch-based invalidation solve the multi-level problem?**
- A) It does not
- B) Publish an invalidation event carrying a monotonically increasing version; each L1 entry stores the version it was loaded at, and a request is served only if the local version matches. The broadcast is a hint, not a guarantee — the version check is the guarantee
- C) It compresses better
- D) It increases hit rate

**Answer: B** — A missed broadcast costs you a version mismatch and a reload, not incorrect data. That asymmetry is why it is the pattern to use.

---

**Q8. What is negative caching, and what does it prevent?**
- A) Caching failures
- B) Caching "this key does not exist" for a short TTL so a flood of lookups for absent keys does not hit the DB. It must be bounded (short TTL) and must be invalidated on create, or the create will not be visible
- C) Caching negative latency
- D) Deleting keys

**Answer: B** — Without negative caching, a traffic pattern of non-existent keys (scanners, bad IDs, or a hot product) is an unprotected origin load. Invalidate on write.

---

**Q9. Why is caching a read model from a replica dangerous?**
- A) It is safe
- B) Replication lag means you cache stale data for as long as the lag; combined with a long TTL you can serve data many seconds old. It is acceptable only for explicitly tolerant data with a TTL bounded by your replication-lag SLO
- C) Replicas cannot be read
- D) It uses more memory

**Answer: B** — Replication lag is not a constant; a failover can make it seconds to minutes. Bound the TTL by the *worst-case* lag you have observed, not the average.

---

**Q10. What does the `Cache-Control` header actually control, and what does it not?**
- A) It controls your server-side cache
- B) It controls the HTTP cache (browser/intermediary) — `max-age`, `s-maxage`, `no-store`, `private`, `stale-while-revalidate`. It does nothing to your in-process or Redis cache; that is your own policy
- C) It controls Redis eviction
- D) It sets a TTL on the JPA second-level cache

**Answer: B** — Conflating the two layers causes the classic bug: `Cache-Control: public, max-age=300` on a per-user response leaks one user's data to another.

---

**Q11. Why is `no-store` on authenticated/personalised responses mandatory?**
- A) It improves performance
- B) Shared caches (CDN, proxy) will otherwise store a per-user response keyed by URL and serve it to the next user — a cross-user data leak. `no-store` (or `private`) is required for any response that varies by identity
- C) It prevents XSS
- D) It compresses better

**Answer: B** — Also key any private cache by user/tenant, never by URL alone.

---

**Q12. What is the correct cache key?**
- A) The URL
- B) The URL plus every input that changes the response — tenant, user (when personalising), locale, feature flags, API version, and any filter/sort/paging parameter. Any omitted input is a cross-request data leak; over-keying costs hit ratio
- C) The entity id only
- D) A hash of the request body

**Answer: B** — The standard defence is a typed key object built by the code that owns the query, so a new parameter forces a key change at compile time.

---

**Q13. Why does "delete on write" beat "update on write" for large values, and what is the subtle failure?**
- A) Delete is always better
- B) `DEL` is O(1) and cannot be applied to the wrong shape; `SET` on a large object risks a race where a concurrent read repopulates the old value between your read and your write. Delete pushes the next read to a fresh load, which is correct
- C) Update is slower
- D) Delete requires a lock

**Answer: B** — The subtle failure of read-modify-write on a cached object: two concurrent updates lose one. For anything with concurrent writers, the cache should be keyed on the entity, never on a whole aggregate snapshot.

---

**Q14. What is a cache penetration / avalanche / breakdown distinction that matters operationally?**
- A) They are synonyms
- B) **Penetration**: lookups for keys that do not exist (fix: negative caching / bloom filter / validation). **Avalanche**: many keys expire together (fix: jittered TTL / early refresh). **Breakdown**: one hot key's expiry sends all traffic to the origin (fix: single-flight, stale-while-revalidate, hot-key never-expiring with background refresh)
- C) They only differ in scale
- D) Only avalanche matters

**Answer: B** — Each has a different fix; treating them as one problem means you apply jitter and still get hammered by penetration.

---

**Q15. The single most common reason a cache makes a system *worse* is?**
- A) The cache is too large
- B) The cache is not actually used — hit ratio is low (or high on the wrong keys), so you pay the memory, the serialisation, the network hop, and the invalidation complexity and gain nothing; worse, on a miss the latency is now `cache + origin`
- C) The cache uses too much CPU
- D) The cache is Redis

**Answer: B** — Measure the hit ratio per key class before optimising. A cache with a 20% hit ratio on a 2 ms origin is a net loss; the fix is to cache the right things, not to tune the wrong cache.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and fix a real cache.
- 12–10: revisit TTL policy, stampede protection, and cache-key design; redo EXERCISES 2–5.
- <10: re-read THEORY + ARCHITECTURE_DECISIONS cold and retake in 48 hours.
