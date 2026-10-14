# REAL_WORLD_PROJECT — Online Algorithms
> Admission-controlled CDN edge cache: LRU eviction with a size cap, hit-rate dashboards, and a load-shedding switch.

## System and inputs
- Edge cache nodes serving image renditions keyed by (asset, width, format); each node caps entries at k (configured per memory budget).
- Admission filter: objects larger than 8 MB bypass the cache; query-string variants normalize before lookup.
- Ski-rental logic picks reserved vs on-demand capacity each month from the same break-even rule as the lab.

## Design
- LRU list plus hash index per node; eviction is O(1) amortized per request.
- Weekly offline job replays access logs through Belady OPT to report the headroom ratio faults(LRU)/faults(OPT).
- Break-even job recommends reserved instances when projected cumulative on-demand spend crosses the reservation price.

## Metrics
- Hit rate per node (target set from baseline week, alert on 5-point drop over 1 hour).
- p95 origin-fetch latency and eviction rate per minute.
- Weekly OPT-gap ratio; page when it exceeds the agreed bound two weeks running.
- Monthly compute bill vs break-even recommendation delta.

## Failure modes
- Cache scan (one-off bulk crawl evicts the working set): admission filter plus a small probationary segment absorb it.
- Thundering herd on a cold key: singleflight fetch with 2 s coalescing window.
- Size-cap misconfiguration (k far above memory): startup guard computes entry budget from heap and refuses to boot.
- Reservation commitment made on a traffic spike: break-even job requires 4 stable weeks before recommending.

## Rollout
1. Shadow mode: log eviction decisions without serving from cache (3 days).
2. 5 percent of edge traffic, watching hit rate and origin latency.
3. Full rollout with the OPT-gap job scheduled weekly.

## Acceptance criteria
1. Hit-rate dashboard shows per-node rate, eviction rate, and OPT-gap ratio.
2. Singleflight prevents duplicate origin fetches in a load test with 50 concurrent cold-key requests.
3. Startup guard rejects a k value exceeding the heap-derived budget with a clear error.
4. Break-even job reproduces the lab numbers (200 vs 100) on the reference inputs before touching real billing data.
5. Rollback is one flag flip back to direct-origin serving.

## Cost and contract notes
- Origin egress saved per hit: multiply hit-rate delta by bytes served; report dollars monthly from billing export.
- Reservation recommender outputs (instance family, count, break-even month) as a CSV the finance owner signs off.
- Eviction-log sampling keeps 1 in 1000 decisions with key hash, size, and outcome for OPT-gap audits.
- API contract: GET /cache-status returns version, k, hit-rate-1h, and OPT-gap-week; POST /reservation-advice takes usage CSV.
