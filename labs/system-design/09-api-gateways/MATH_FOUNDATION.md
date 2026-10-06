# API Gateways - Math Foundation

## Latency Budget: The Whole Exercise in One Table

A gateway adds a hop. Budget for it explicitly, because "the API got slow" is
usually "the gateway got slow".

```
end_to_end = edge(TLS + WAF) + auth(JWKS* + crypto) + route(discovery)
              + service + response_shaping
              + network_RTT * hops
```

| Component | Budget (p95) | Notes |
|-----------|--------------|-------|
| TLS termination (with session resumption) | 5 ms | Non-resumed is 3-5x |
| WAF / rule evaluation | 3 ms | Grows with rule count |
| JWKS verification (cached keys) | 0.3 ms | **Assumes cache hit** |
| Route match (hash lookup) | 0.01 ms | |
| Service discovery lookup (cached) | 0.05 ms | |
| Downstream RTT | 20 ms | Intra-region |
| Downstream service time | 80 ms | |
| Response shaping | 2 ms | |
| **Total** | **~110 ms** | |

### The JWKS Trap

```
  JWKS cache miss path: fetch from issuer, parse, verify
    -> +1 network RTT to the issuer (20-80 ms) and a hard dependency on it

  P(cache miss) at TTL=1h with hourly rotation:
    = 1 rotation/hour -> a miss burst at every rotation boundary
    + refresh-on-unknown-kid for the overlap window

  -> cache TTL must EXCEED the rotation interval, and refresh must be
     on-demand (unknown kid) rather than purely periodic
```
Fetching JWKS per request adds a cross-network dependency to the
authentication path. That dependency can be down while your services are fine,
producing a total outage caused entirely by the gateway.

## Fan-Out: Aggregation Cuts Round-Trips

```
  Round-trips without a BFF = N services called serially by the client
  Round-trips with a BFF    = 1 (or 2 with pagination)

  latency_without_BFF = sum over i of (RTT_i + service_i)
  latency_with_BFF    = max over i of (RTT_i + service_i)   // parallel

  N = 5, each service 20 ms RTT + 60 ms service time:
    serial   = 5 * (20 + 60) = 400 ms  + 5 client round trips
    parallel = 1 * (20 + 60) =  80 ms
    -> 5x latency improvement, 5x fewer client round-trips
```

### But Parallelism Is Not Free

```
  gateway_connection_usage = concurrent_requests * fanout
  5,000 concurrent requests, fanout 5 -> 25,000 open connections

  downstream capacity check:
    per-gateway instance handles R concurrent requests
    each holding F connections for S seconds
    Little's Law: concurrency = throughput * service_time
      500 req/s * 0.08 s * 5 fanout = 200 connections per instance
```
A BFF multiplies the downstream connection pressure by the fan-out factor.
This is why a BFF needs its own connection pool sizing and often its own
circuit breakers per downstream service.

### Tail Latency of a Fan-Out

```
  p99 of a parallel fan-out of N is much worse than N * p50.

  If service p50 = 60 ms and p99 = 400 ms:
    N = 1:  p99 = 400 ms
    N = 5 parallel: P(all 5 under 400ms) = 0.99^5 = 0.951
                     -> p99 of the fan-out ~= 1,500-2,000 ms
```
So a 5-service fan-out has a p99 that is roughly **4-5x a single service's p99**,
not 1x. This is why per-field timeouts and null fallbacks are not optional: the
tail is where your aggregation endpoint lives.

## Request Rate and Instance Sizing

```
  instance_count = ceil( peak_rps / per_instance_rps * safety )

  peak = 12,000 rps, per instance = 800 rps (measured, p95 CPU < 60%)
  safety = 1.4 for headroom and deploys
  -> 12000 / 800 * 1.4 = 21 instances

  if per_instance_rps is guessed rather than measured, this number is fiction.
  Measure at the latency target, not at the throughput maximum.
```

### Headroom Reasoning

```
  safety factor covers:
    - one instance failing during a deploy    (~1/N)
    - traffic spikes (marketing events)       (2-5x normal)
    - slow instances during rolling restart

  1.4 is a floor. Consumer-facing platforms often need 2x.
```

## Rate Limiting Capacity

```
  global limit G = 10,000 rps; N = 21 instances
  local_limit = ceil(G / N) * 1.2 = 572 rps per instance

  store write cost: one decision per request
    12,000 rps at the limit -> 12,000 store ops/s
    local cache with 250 ms TTL absorbs:
      admitted_that_hit_cache / total ~= 1 - (250ms / 250ms) ... practically
      60-90% of decisions hit cache for high-cardinality keys
```
Without a local cache, the rate limiter is a 12,000 ops/s dependency on Redis in
the critical path of every request. That dependency becomes a gateway
single point of failure.

## Header and Token Size Cost

```
  JWT size = base64(header ~ 60 B) + base64(payload) + signature
    claims: sub, iss, aud, exp, iat, scope[], tenant, roles[]
    typical payload = 400-800 B
    total JWT      = 600-1,200 B

  gateway overhead per request:
    Authorization header   1,000 B
    request ID             36 B
    trace context          55 B
    identity headers       120 B
    rate limit headers     80 B
    total                  ~1,300 B

  at 12,000 rps:  15.6 MB/s = 125 Mbps of pure gateway-added headers
```
Relevant at 12,000 rps (a large but normal platform) and irrelevant below
~1,000 rps. Note that passing the raw JWT to services costs bandwidth on every
hop; passing a **normalised identity header** costs one short header instead.
That normalisation is one of the gateway's real jobs.

## Routing Table Scale

```
  200 services, average 4 routes each = 800 route patterns

  lookup cost:
    linear scan     = 800 * ~50 ns  = 40 µs per request   (fine but silly)
    hash by prefix  = O(1) ~ 1 µs
    trie by segment = O(path segments) ~ 3-5 µs

  config reload: rebuild the table atomically
    copy-on-write + single volatile reference swap
    -> zero-downtime config reload, no request sees a half-built table
```

## Circuit Breaker Error Budget

```
  breaker opens when: failures / requests >= threshold over a window

  threshold choice:
    internal service:  50% errors in 20 s   (should never happen; act fast)
    fragile 3rd party: 30% errors in 60 s   (noisy; open earlier)
    optional service:  70% errors in 30 s   (only trip for near-total failure)

  half-open: allow K probe requests
    K = 1  -> slow to confirm recovery
    K = 3  -> faster recovery, slight risk of re-tripping
```

### Breaker Coordination

```
  Breakers are per gateway instance by default -> breakers open independently.

  If 21 instances all open simultaneously -> total outage anyway.
  Some systems propagate breaker state so one instance's decision informs others.
  Trade-off: propagation adds a dependency and can cause a thundering herd of
  half-open probes across the fleet. Start with per-instance breakers.
```

## Auth Crypto Cost

```
  RSA-2048 verify : ~0.1 ms  (asymmetric, expensive)
  RS256 verify    : ~0.05 ms
  ES256 verify    : ~0.03 ms (fastest common asymmetric)
  HMAC-SHA256     : ~0.002 ms

  12,000 rps with RS256 verification: 12000 * 0.05 ms = 600 ms of CPU per second
                                       = 0.6 of one core
```
Authentication is cryptographically cheap. The latency people feel comes from
the *network hop to fetch keys*, not from the verification itself. Optimise the
cache, not the algorithm.

## Capacity of the Gateway Is a Tail Problem

```
  average CPU at the gateway under load: 35%
  p99 CPU during a traffic spike:        95%

  the gateway saturating for 90 seconds during a spike causes:
    - client timeouts across the whole platform
    - retry amplification (clients retry, adding load)
    - circuit breakers opening on healthy services (queueing inflates errors)

  headroom and autoscaling must react on CONCURRENCY and p95 LATENCY,
  not on average CPU.
```

## Retry Amplification (Why Gateway Retries Are Dangerous)

```
  client retries 3x  ->  gateway retries 2x  ->  service retries 3x
  amplification = 3 * 2 * 3 = 18x load at the service layer

  with N services in a retry chain: amplification = client^n
```
Retries must exist at exactly **one** layer, and must apply **only** to
idempotent requests and connection-level failures. A gateway that retries `POST
/payments` on a timeout is the proximate cause of duplicate charges.

## Availability of the Gateway

```
  A_gateway = A_edge_network * A_compute * A_config * A_auth_dependency

  for 99.99% (52.6 min/month):
    each dependency must be ~99.997% or better

  practical design:
    - multiple gateway deployments / regions (active-active)
    - config pushed, not fetched (no dependency on a config service at runtime)
    - JWKS cached with long TTL (auth dependency is the weakest link)
    - service discovery via DNS/mesh, cached, with a static fallback table
```
The last point matters: if service discovery is unavailable and the gateway has
no static fallback, routing stops even though the services are fine.