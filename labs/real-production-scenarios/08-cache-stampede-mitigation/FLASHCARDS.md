# FLASHCARDS — Lab 08: Cache Stampede

| Front | Back |
|---|---|
| Stampede | Mass simultaneous misses flooding DB |
| Thundering herd | Synonym for stampede on expiry |
| Hot key | Single key with disproportionate QPS |
| Hit ratio cliff | e.g., 98%→40% at expiry moment |
| Singleflight | Coalesce concurrent loads into one |
| Waiter timeout | Bound for coalesced waiters (~2s) |
| Stale fallback | Serve expired value when loader fails |
| SWR | Stale-while-revalidate: stale + async refresh |
| Jittered TTL | ttl×(1±0.15) spreads expiry |
| Probabilistic refresh | Early refresh by beta×latency before expiry |
| refreshAfterWrite | Caffeine async refresh, non-blocking reads |
| Negative cache | Cache misses 30–60s |
| Fill semaphore | Cap concurrent DB loads (e.g., 10) |
| Hot-key split | Replicate key to N suffixes |
| Redis INFO stats | Hits, misses, expired, evicted counters |
| SLOWLOG GET | Recent slow Redis commands |
| Hitrate formula | hits/(hits+misses) |
| Miss storm alert | misses/s >10x baseline |
| DB pool >80% | Stampede downstream signal |
| Same-SQL spans | Trace signature of stampede |
| Loader timeout | Caps single DB load duration |
| Caffeine L1 | In-process cache, 60s TTL typical |
| Redis L2 | Shared cache, 300s TTL typical |
| Null race | Concurrent refresh returning null |
| Retry amplifier | Retries multiply DB load 2–3x |
| 429+Retry-After | Overflow response when fill saturated |
| Stale header | e.g., `X-Cache: STALE` for visibility |
| Beta in xfetch | Aggressiveness of early refresh |
| TTL variance cost | Some keys staler/fresher — acceptable |
| Key suffix routing | e.g., product:123#1..8 round-robin |
| Flush danger | Manual FLUSHDB causes instant cold stampede |
| Cold deploy | New fleet with empty L1 → L2/DB surge |
| Warm-up | Preload hot keys before serving |
| Read replica | Offload stampede reads from primary |
| Pool exhaustion | DB conns saturated by fill queries |
| Slow-query surge | DB latency spike during stampede |
| Expired_keys spike | Redis expiry burst metric |
| Evicted_keys | LRU pressure signal (distinct from expiry) |
| Client list | redis-cli CLIENT LIST for conn audit |
| Big-key risk | Large values slow refresh, widen window |
| Compression | Reduces big-key refresh cost |
| Dogpile | Alternate term for stampede |
| Coalescing map | Key→Future registry structure |
| Future dedup | Concurrent callers share one future |
| Timeout + cancel | Waiter gives up, loader may continue |
| Async refresh pool | Dedicated executor for background loads |
| Bulk warm | Batch preload after deploy |
| Canary for cache | Roll cache-code to subset first |
| Hit-ratio SLI | e.g., >95% for hot tier |
| Miss budget | Allowed fills/s before throttle |
| Backpressure | Queue/shed instead of flooding DB |
| Post-mortem fix | Jitter + singleflight + SWR standard |
| Interview math | N waiters → 1 query; show QPS division |
| SWR staleness | Bounded e.g., 60s documented |
| Correctness bound | Which keys allow stale (catalog yes, balance no) |
| Stampede vs leak | Spike at expiry vs gradual growth |
| Detection trio | Hit cliff + hot key + DB surge |
| Recovery proof | Hit back >95%, DB conns normal 10 min |
