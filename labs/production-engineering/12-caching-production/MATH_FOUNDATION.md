# Lab 12: Caching Strategies & Cache Invalidation — Math Foundation

Caching is an economics exercise: you add latency and complexity on the miss path and buy it back with a hit ratio. The numbers decide whether the cache is worth having.

---

## 1. Amortisation: is a cache worth it at all?

```
E[latency] = h × L_cache + (1 − h) × (L_cache + L_origin)
           = L_cache + (1 − h) × L_origin
saved_per_request = (1 − h) × L_origin
breakeven_hit_ratio: L_cache + (1 − h) × L_origin ≤ SLO_budget
  →  h ≥ 1 − (SLO_budget − L_cache) / L_origin
```

`L_origin = 50 ms`, `L_cache = 0.5 ms` (Redis), SLO budget `60 ms`:
```
h ≥ 1 − (60 − 0.5)/50 = 1 − 1.19  →  any hit ratio satisfies it
```

Same cache, SLO budget `52 ms`:
```
h ≥ 1 − (52 − 0.5)/50 = 1 − 1.03 = −0.03  →  trivially satisfied
```

Tighter: `L_origin = 50 ms`, budget `20 ms`, cache `0.5 ms`:
```
h ≥ 1 − (20 − 0.5)/50 = 1 − 0.39 = 0.61
```
**Conclusion**: a cache only pays when the SLO is tighter than the origin's latency. With a 250 ms SLO and a 5 ms origin, the cache buys nothing on latency — it buys *capacity*, which is a different justification and must be argued as such.

Hit ratio against monthly origin cost, `λ = 5,000 rps`, origin `$0.0004`/query, 30 days:
```
origin_calls/month = 5,000 × 2,592,000 = 1.296 × 10^10
cost_at_h=0       = $5,184
cost_at_h=0.7     = $1,555   →  saves $3,629/month
cost_at_h=0.2     = $4,147   →  saves $1,037/month, plus Redis + code complexity
```

---

## 2. TTL, staleness, and the expected staleness distribution

```
expected_staleness = E[age at read] ≈ TTL / 2   for random access
worst_case_staleness = TTL
```

`TTL = 60 s` → expected staleness 30 s, worst case 60 s. If the business tolerates 5 s, the TTL must be ~5 s, and then:

```
origin_load_per_request = 1/TTL_effective
λ=5,000, TTL=5s   →  1,000 origin requests/s   (origin capacity required: 1,000 rps)
λ=5,000, TTL=300s →  16.7 origin requests/s    (99% saved)
```
That 60× difference in origin load is the entire engineering argument for the staleness trade — and it is a *business* decision about how long a price may be stale.

Combined TTL + refresh-ahead (serve stale while revalidating):
```
effective_origin_rate = 1 / refresh_interval
latency_on_hit = L_cache (never waits for the origin)
hard_bound: staleness ≤ refresh_interval + max_stale
```
Set `refresh_interval = 30 s`, `max_stale = 90 s`: origin load drops 2× versus TTL=60 s while p99 latency stays at `L_cache`.

---

## 3. Jitter and the avalanche window

Without jitter, keys populated in the same second expire in the same second. The origin load as a function of time is a delta; with jitter it is a plateau.

```
no_jitter:  expiry_rate(t) = N × δ(t − TTL)
jitter ±j:  expiry_rate(t) ≈ N / (2 × j × TTL)      spread over the jitter window
```

`N = 100,000 keys`, `TTL = 300 s`, jitter `j = 0.1` (±30 s):
```
no jitter:  100,000 origin requests in one instant  →  origin spikes to 100k/s equivalent
jittered:  100,000 / 60 s = 1,667 origin requests/s sustained
peak_reduction = 100,000/1,667 = 60×
```
**Conclusion**: jitter is the cheapest, highest-leverage cache control, and it is one line of code.

---

## 4. Stampede (cache breakdown) model

```
origin_load_during_stampede = Q_hot × P(miss at that instant) ≈ Q_hot (1 key expired)
origin_capacity             = C
collapse iff Q_hot > C
```

`Q_hot = 40,000 rps` on one key, origin capacity `C = 8,000 rps`:
```
no protection: 40,000 → 5× overload → timeouts, retries → worse
single-flight: 1 loader → 1 origin request; the other 39,999 wait Q_ms
  Q_ms ≈ L_origin = 50 ms  →  p99 rises by 50 ms for that key's requests only
stale-while-revalidate: origin load = 1/refresh_interval = 1/30 = 0.033 rps
  →  effectively zero stampede; p99 unchanged
```
Little's Law on the single-flight variant: `39,999` waiting requests for `50 ms` = `39,999 × 0.05 = 2,000` extra concurrent requests held at the origin for `50 ms`. If your thread pool is 200, that is a 10× oversubscription. **Conclusion**: single-flight alone converts a latency problem into a *concurrency* problem unless the waiters do not hold resources — which is why `sync=true` (blocking the *loader*, not the pool) or stale-while-revalidate is preferable.

---

## 5. Penetration: absent keys

```
origin_load_penetration = λ_invalid × P(key absent)
```

A scanner or a bad integration sends `λ_invalid = 800 rps` for IDs that do not exist:
```
no negative caching:  origin load += 800 rps forever
negative cache (TTL 30s): miss rate ≈ 800 / (800 × 30) = 3.3%  →  origin load += 26 rps
reduction = 30×    (equal to the negative TTL, as expected)
```
Bloom filter variant for a large key space: `memory = m bits`, false-positive rate `p`:
```
m = −n·ln(p)/(ln2)²        n = 10^7 keys, p = 0.001
m = 10^7 × 6.908/0.4805 ≈ 1.44 × 10^8 bits ≈ 18 MB
```
**Conclusion**: for a very large key space, an 18 MB bloom filter removes an unbounded origin load permanently — a better trade than a 30-second negative TTL.

---

## 6. Multi-level cache: compounded hit ratio

```
h_combined = h_L1 + (1 − h_L1) × h_L2
```

`h_L1 = 0.75`, `h_L2 = 0.85`:
```
h_combined = 0.75 + 0.25 × 0.85 = 0.9625
origin_load_reduction = 96.25%   →  origin load 5,000 → 189 rps
```
If L2 were removed: `h = 0.75` → origin load `1,250 rps`. So the L2 contributes a `6.6×` reduction in origin load for one extra network hop and one invalidation problem.

Latency:
```
E[latency] = h_L1×L_L1 + (1−h_L1)×[h_L2×L_L2 + (1−h_L2)×(L_L2+L_origin)]
L_L1 = 5 µs, L_L2 = 0.4 ms, L_origin = 40 ms
= 0.75×0.000005 + 0.25×[0.85×0.4 + 0.15×40.4]   (all in ms)
= 0.000004 + 0.25×(0.34 + 6.06)
= 0.000004 + 1.60 ms   ≈ 1.60 ms
```
The residual `0.15 × 0.25 = 3.75%` of requests cost 40 ms and dominate the mean. To move the mean, you must reduce **miss** rate, not miss latency.

---

## 7. Invalidation fan-out cost

Entity-keyed invalidation is `O(1)`; derived-key invalidation is `O(k)` where `k` = number of derived keys.

```
invalidate_cost = 1 (entity) + k (list pages/counts/search)
origin_refill   = 1 + k × refill_frequency
```

Suppose a product page is cached under 1 entity key + 40 list-page keys + 4 count keys:
```
one product update → 45 evictions
refill rate = product_update_rate × 45
if updates = 50/s  →  2,250 origin requests/s just to refill after invalidation
```
Compare versioned entity keys (invalidations are lazy and version-checked):
```
one update → 1 version bump (a Pub/Sub publish, ~0 cost)
refill happens only on the next actual read of each key
refill rate = read_rate × (1 − h)  →  unrelated to update rate
```
**Conclusion**: at high update rates, enumeration-and-delete creates an origin load *proportional to writes*. Versioning decouples them. This is the single most important architectural choice in multi-level caching.

---

## 8. L1 broadcast correctness and staleness bound

```
P(stale beyond TTL) ≈ P(broadcast missed) × (requests served before next TTL expiry)
bounded_staleness = TTL_L1 + P(miss) × time_to_next_broadcast
```

With `TTL_L1 = 60 s` and a pub/sub reliability of 99.9%:
```
bounded_staleness ≈ 60 s + 0.001 × 60 s ≈ 60.06 s   →  TTL dominates
```
With `TTL_L1 = 5 s` and 99% reliability:
```
bounded_staleness ≈ 5 + 0.01 × 5 = 5.05 s  →  but base staleness is 5 s, which may already exceed tolerance
```
The trade is explicit: shorten the L1 TTL and you rely more on broadcast reliability; lengthen it and you risk serving over-tolerated data. The version check makes the *correctness* safe in both cases; the TTL sets the *staleness*.

---

## 9. Cache memory budget

```
cache_bytes = max_entries × avg_entry_bytes × overhead_factor
```

L1 Caffeine, `max = 100,000`, average serialised entry `3 KB`, overhead 1.3 (objects, maps, metadata):
```
cache_bytes = 100,000 × 3 KB × 1.3 ≈ 390 MB
```
Add L2: 2M keys × 3 KB = 6 GB of Redis, needing `maxmemory` ≥ 6 GB plus eviction headroom (set `maxmemory` and let `allkeys-lru` work — an unconstrained cache is an OOM).

Container budget interaction (see Lab 07): `390 MB` of L1 cache must come out of the heap you configured:
```
heap = 0.6 × memory_limit − native_headroom − cache_bytes
```
Ignoring the cache in the budget is one of the most common causes of the Lab 07 OOM-kill after a "harmless" caching change.

---

## 10. Serialisation cost

```
serialise_cost = objects_per_s × cpu_per_object
hit_latency_contribution = serialise_cost per cache operation
```

JSON with Jackson, 200-byte object: ~1–3 µs. Kryo: ~0.3–0.8 µs. Protobuf: ~0.2–0.5 µs.
```
λ_cache = 20,000 ops/s
JSON:      20,000 × 2 µs   = 0.04 cores
Kryo:      20,000 × 0.5 µs = 0.01 cores
```
Small, but it lands on the *request path*, competing with business logic, and it is paid on both hit and miss. Note the miss path pays it twice (serialise to store + serialise to return) if you return the serialised form directly.

---

## 11. Cache vs capacity: when a cache is the only way to scale

```
required_origin_capacity_without_cache = λ
required_origin_capacity_with_cache    = λ × (1 − h)
cost_of_cache = cache_infra + engineering + invalidation_ops + staleness_risk
```

`λ = 5,000 rps`, origin capacity today `C = 3,000 rps` → cannot serve peak without work.
`h = 0.90` → required origin capacity `500 rps` → fits with 6× headroom.

```
cheapest alternative: add origin capacity to 6,000 rps
cost = origin_spend × 2   (and DB connection pool, and failure-domain expansion)
```
**Conclusion**: a 90% hit-ratio cache can be the cheapest capacity intervention available — but only when the hit ratio is real. This is the case where the economics favour caching, and it should be argued on this basis rather than on latency.

---

## 12. Hit ratio measurement and per-class attribution

```
h_class = hits_class / (hits_class + misses_class)
origin_load_total = Σ_class λ_class × (1 − h_class)
```

Two classes: `product` `λ=4,000`, `h=0.95`; `basket` `λ=1,000`, `h=0.10`:
```
global h = (3,800 + 100)/5,000 = 0.78
origin_load = 4,000×0.05 + 1,000×0.90 = 200 + 900 = 1,100 rps
```
The global 78% hides the problem: `basket` contributes **82%** of origin load. A global hit-ratio dashboard would show an improving number while the origin stays loaded.

```
improvement if basket h → 0.5:   origin_load = 200 + 500 = 700 rps   (−36%)
```

---

## 13. Quick drills

1. `L_origin=50ms`, `L_cache=0.5ms`, SLO budget 20 ms. Minimum hit ratio? **Answer: `1 − (20−0.5)/50 = 0.61`.**
2. TTL 5 s vs 300 s at λ=5,000. Origin load? **Answer: 1,000 rps vs 16.7 rps — a 60× capacity difference.**
3. `TTL=300s`, 100,000 keys, jitter ±10%. Peak expiry rate? **Answer: no jitter = 100k at once; jittered = 1,667/s. 60× reduction.**
4. Hot key 40,000 rps, origin capacity 8,000. Effect of expiry? **Answer: 5× origin overload. Single-flight leaves +2,000 concurrent waiters.**
5. 800 rps of invalid keys, negative TTL 30 s. Origin load added? **Answer: 800 → ~26 rps.**
6. `h_L1=0.75`, `h_L2=0.85`. Combined hit ratio? **Answer: 96.25%. Origin load 5,000 → 189 rps.**
7. One product update invalidates 45 keys at 50 updates/s. Refill origin load? **Answer: 2,250 rps — proportional to writes. Versioning decouples it.**
8. L1 Caffeine 100,000 × 3 KB × 1.3. Memory? **Answer: ~390 MB — must be inside the heap budget.**
9. `product` h=0.95 λ=4,000; `basket` h=0.10 λ=1,000. Which class dominates origin load? **Answer: basket (900 of 1,100 rps = 82%).**
10. λ=5,000, origin capacity 3,000, h=0.90. Is the cache sufficient? **Answer: origin needs 500 rps — yes, 6× headroom. Best case for a capacity argument.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `E[latency] = L_cache + (1−h)·L_origin` | is a cache worth it for latency? |
| `h_min = 1 − (SLO − L_cache)/L_origin` | break-even hit ratio |
| `expected_staleness = TTL/2`, worst = TTL | TTL policy from business tolerance |
| `expiry_peak_jittered ≈ N/(2·j·TTL)` | TTL jitter as an origin-load control |
| `h_combined = h_L1 + (1−h_L1)·h_L2` | multi-level compounding |
| `invalidate_cost = 1 + k` | why derived-key invalidation scales badly |
| `origin_load = Σ λ_class·(1−h_class)` | per-class attribution, not global |
| `cache_bytes = max_entries × avg_bytes × 1.3` | memory budget; include in the container limit |
| `stampede_origin_load ≈ Q_hot` | hot-key expiry; requires single-flight or refresh-ahead |
| `needed_origin = λ × (1−h)` | the capacity argument for caching |
