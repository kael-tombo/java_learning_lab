# Lab 12: Caching Strategies & Cache Invalidation — Flashcards

~60 cards. Most answers are a number, a TTL, or a failure mode.

---

## Patterns

Q: Cache-aside?
A: App checks the cache; on miss it loads from the origin and populates. The app owns both reads and writes. The default for read-heavy data; the origin is hit on every miss.

Q: Write-through?
A: Writes go to cache and origin synchronously. Cache is never stale; read path is always a hit. Cost: every write pays the cache latency, and you must have exactly one write path.

Q: Write-behind (write-back)?
A: Write goes to cache; the origin write is asynchronous. Fast writes, but the cache is now the source of truth — eviction or a crash loses data. Requires durability on the cache.

Q: Read-through?
A: Cache fetches from the origin itself on a miss. The app only ever talks to the cache. Convenient; hides the origin and complicates testing/debugging.

Q: Refresh-ahead?
A: Recompute a value before it expires, on a timer or a hint, so a hot key never becomes a miss. The standard fix for cache breakdown.

Q: Which pattern makes the cache the source of truth?
A: Write-behind. Everything else keeps the origin authoritative.

Q: What is the invariant for write-through?
A: Exactly one way to write, and every mutation goes through it. ORM bulk updates, migrations, and admin tools break this silently.

Q: When is caching the wrong idea?
A: Read/write ratio near 1, write-invalidations as frequent as reads (you pay both sides for no gain), origin already fast enough to meet the SLO, or the data has near-zero staleness tolerance.

---

## TTL policy

Q: How do you choose a TTL?
A: From the *measured* business staleness tolerance per field, with a safety factor. Not from a global default, and not from the cheapest number.

Q: Sensible staleness tolerances?
A: Country/currency lists: hours–days. Product descriptions: minutes. Inventory availability: 1–5 s. Price: seconds. Stock balance: sub-second. Account balance: zero — do not cache.

Q: TTL jitter — why and how much?
A: Without it, keys populated together expire together and cause an avalanche. Jitter ±10–20% of the TTL (e.g. `300s ± 30s`) spreads expiry into a window longer than a typical load ramp.

Q: Jitter formula?
A: `ttl = base × (1 + U(−j, +j))`, e.g. `base=300s, j=0.1 → 270–330s`. Plus a *random* initial value per key so first-population times do not align either.

Q: TTL vs `refreshAfterWrite` (Caffeine)?
A: `expireAfterWrite` = hard TTL; `refreshAfterWrite` = the value is served stale and asynchronously refreshed once the write age passes the threshold. The combination gives `refresh < expire`, which is exactly serve-stale-while-revalidate with a hard bound.

Q: Hard max-stale?
A: After it, fail loudly or serve a defined degraded value. Unbounded staleness is a silent correctness bug.

---

## Invalidation

Q: Delete-on-write vs update-on-write?
A: `DEL` is O(1) and race-free for the value itself. Read-modify-write of a cached object loses concurrent updates and can write back a stale value; avoid it for anything with concurrent writers.

Q: Why not update the cache directly on write?
A: Two concurrent updates to the same key lose one; and the cache value can disagree with the DB if the transaction rolls back after the cache write. `DEL` + next-read-load is simpler and correct.

Q: Version/epoch invalidation?
A: A monotonic version published on write; each cache entry records the version it was loaded at and is served only if the local version matches. The broadcast is a hint; the version comparison is the guarantee.

Q: TTL as a safety net?
A: Yes — even with perfect invalidation, a TTL bounds the damage from a missed event, a lost broadcast, or a buggy write path. Use it deliberately, and alert when an entry is served past its expected staleness.

Q: Delete related keys?
A: Any key derived from the same entity (list pages, counts, search results) must be invalidated too. Versioned *entity* keys make this tractable; enumerate-and-delete does not scale past a handful of keys.

Q: Never cache a whole aggregate?
A: If two writers can touch disjoint parts of an aggregate, an aggregate-level key makes one write invalidate everything and creates lost-update races. Key on the read model that was actually queried.

---

## Stampede / penetration / avalanche / breakdown

Q: Cache stampede?
A: One key expires while high traffic waits; every concurrent request becomes a miss and hits the origin simultaneously.

Q: Stampede fixes, ranked by cost?
A: 1) TTL jitter. 2) `sync`/single-flight so one loader runs. 3) Refresh-ahead. 4) Serve stale while revalidating with a hard bound. 5) Origin protection (bulkhead, rate limit) so a stampede cannot take the origin down.

Q: Cache penetration?
A: Requests for keys that do not exist bypass the cache entirely and hammer the origin.

Q: Penetration fixes?
A: Negative caching with a short TTL and invalidation on create; input validation; a bloom filter for large key spaces; never cache-and-return-success for absent keys.

Q: Cache avalanche?
A: Many keys expiring together (deploy, mass update, or a non-jittered TTL) send a large fraction of traffic to the origin at once.

Q: Cache breakdown?
A: One extremely hot key expires and its entire read volume hits the origin.

Q: Breakdown fix?
A: Hot keys should effectively never expire on the request path: refresh on a timer, serve stale while revalidating, or use `softTtl` (Caffeine) so refresh happens on a background thread.

Q: Can a stampede take down the origin?
A: Yes — the origin is the only thing absorbing the miss. That is why stampede protection is an *availability* control, not a performance nicety.

---

## Multi-level caching

Q: L1 (in-process, Caffeine) + L2 (Redis)?
A: L1 gives microsecond reads with no network; L2 is shared so it survives restarts and is consistent across pods. Hit ratio compounds.

Q: Main risk of L1?
A: Invalidation must reach every JVM. A 200-pod broadcast over pub/sub is neither instant nor reliable — you will miss messages.

Q: How to make L1 invalidation safe?
A: Version/epoch check per entry (correctness), plus a short L1 TTL (bounds staleness), plus message-driven local cache updates where the domain warrants it (strongest, most coupling).

Q: L1 TTL recommendation relative to L2?
A: Short — seconds to a minute. L1's job is to absorb bursts, not to be the source of truth.

Q: What does `sync = true` in Caffeine do?
A: Serialises concurrent loads for the same key: one thread loads, others wait. Exactly the single-flight behaviour needed for stampede protection.

Q: Eviction policy for Caffeine?
A: Size-based (`maximumSize`) plus a time-to-idle expirer for hot keys; `expireAfterAccess` for L1 keeps hot keys resident and drops cold ones.

Q: Sizing a Caffeine cache?
A: `(max_size × avg_entry_bytes) ≤ heap_budget`, e.g. 10,000 entries × 5 KB = 50 MB. Budget it as part of the container memory limit, not on top of it.

Q: Redis `maxmemory` policy?
A: `allkeys-lru` / `allkeys-lfu` for a pure cache; `volatile-*` if you share an instance with data-bearing keys. Never `noeviction` for a cache — it turns cache pressure into write failures.

Q: Serialisation cost in a Redis cache?
A: Real CPU per operation and a measurable p99 contribution. JSON is slower and larger than Kryo/Protobuf/Hessian; measure before choosing. In Java, consider whether you need a cache at all before adding one that re-encodes every value.

---

## HTTP caching (do not confuse it with yours)

Q: What does `Cache-Control: max-age=60` control?
A: The HTTP cache (browser, CDN, proxy) only. It has no effect on your L1/L2 cache.

Q: `private` vs `public`?
A: `private` forbids shared caches storing it; `public` explicitly permits shared storage. Personalised responses need `private` or `no-store`.

Q: `no-store` — when mandatory?
A: Any response that varies by identity (auth, tenant, user-specific fields). Otherwise a shared cache can serve one user's data to another.

Q: `ETag` + `If-None-Match`?
A: Cheap revalidation: the server returns 304 with no body. Frequently the highest-value HTTP-cache optimisation for read APIs.

Q: `s-maxage` vs `max-age`?
A: `s-maxage` applies to shared caches, `max-age` to the browser. Use both when they should differ.

Q: `stale-while-revalidate` / `stale-if-error`?
A: Tell caches (and CDNs) it is acceptable to serve stale briefly, and to serve stale on error. Directly maps to the serve-stale-while-revalidate pattern at the HTTP layer.

---

## Cache keys

Q: What belongs in a cache key?
A: URL/path + tenant + user (when personalising) + locale + feature flags + API version + every filter/sort/page parameter + schema version.

Q: Why include schema version?
A: So a deploy that changes the response shape cannot serve old-shaped values from cache. Otherwise you get `ClassCastException` or silently wrong fields after every release.

Q: Typed key vs string concatenation?
A: A record/class built by the query owner, so adding a query input forces a key change at compile time. String concatenation silently produces collisions.

Q: Common collision bugs?
A: Forgetting a filter; concatenating without a delimiter (`a=1,b=23` vs `a=12,b=3`); null vs empty string; not normalising date formats.

Q: Should you cache on the SQL query string?
A: Sometimes, but you must also include any post-processing inputs — and query-string caches break the moment someone reformats the SQL. Entity-keyed caching with explicit composition is usually more robust.

---

## Measurement

Q: The metric that matters?
A: Hit ratio *per key class*, plus origin load. A global 70% hit ratio can hide a 0% class that is your hottest endpoint.

Q: Metrics to export?
A: `cache_requests_total{result=hit|miss|error}`, `cache_load_duration_seconds` (load latency = the stampede signal), `cache_eviction_total`, per-key-class hit ratio, origin QPS attributable to cache misses, and entry count vs maximum size.

Q: What does rising load duration indicate?
A: Origin degradation — a leading indicator before the origin's own alerts fire.

Q: Hit ratio too high — a problem?
A: Sometimes: it can mean you are caching data nobody invalidates properly, or you are serving very stale data. High hit ratio plus high business staleness is a correctness problem, not a win.

Q: Memory per cache?
A: `entries × avg_bytes`; measure with `Cache.stats()` / Redis `MEMORY USAGE`, and include it in the container memory budget (this is a frequent contributor to the Lab 07 OOM-kill).

Q: Cardinality risk in cache metrics?
A: Key-class labels must be bounded. Never label a metric with the cache key itself.

---

## Numbers and defaults to memorize

Q: Typical L1 (Caffeine) max size?
A: 10,000–100,000 entries, sized by a heap budget you have actually measured.

Q: Typical TTL jitter?
A: ±10–20% of the base TTL.

Q: Caffeine `refreshAfterWrite` vs `expireAfterWrite`?
A: Set `refreshAfterWrite < expireAfterWrite` to get serve-stale-while-revalidate with a hard bound.

Q: Negative-cache TTL?
A: Short — 5–60 s — and invalidated on create.

Q: Default max page size (which is also a cache-fill cost)?
A: 100. A `limit=10,000` request must not be cacheable; it will fill memory and evict everything useful.

Q: Redis `maxmemory` policy for a cache?
A: `allkeys-lru` or `allkeys-lfu`. Never `noeviction`.

Q: How much of a container's heap should a local cache take?
A: Budgeted explicitly (e.g. 5–15% of heap) and included in the container memory budget.

Q: What latency does an L1 hit add?
A: Sub-microsecond to a few microseconds. L2 (Redis) adds ~0.2–1 ms round trip, network-bound.

Q: Minimum useful hit ratio to justify an L2?
A: If the origin is 50 ms and L2 costs 0.5 ms, break-even hit ratio `h` satisfies `h×0.5 + (1−h)×50 < SLO`; with a 200 ms SLO, almost anything helps; with a 60 ms SLO and origin 50 ms, you need `h > 0.98`. Compute it.
