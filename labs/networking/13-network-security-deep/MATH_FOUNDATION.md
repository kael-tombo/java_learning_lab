# Network Security Deep - MATH FOUNDATION

## 1. Blast radius as graph connectivity

Segmentation is edge removal on a directed graph of services.

```
  Reachable(R) = BFS over edges from compromised node R
  Flat network:  |R| = N - 1
  Blast radius reduction = 1 - (|R|segmented) / (N - 1)
```

Worked example, N = 400 services, each segmented to reach 3 others:

```
  Flat:      |R| = 399 per service
  Segmented: |R| = 3 per service
  Total reachable pairs:  flat 400 x 399 = 159,600  ->  segmented 400 x 3 = 1,200
  Reduction = 1 - 1200/159600 = 1 - 0.00752 = 0.9925  ->  99.25%
```

The reason to compute it as **total pairs** rather than per-service: a policy set is
usually good for most services and catastrophic for one. A single service reaching 200
others contributes more pairs than all the well-segmented services combined, and the
average hides it. Report the **maximum** and the **distribution**, not just the mean:

```
  max blast radius = 200   <-- this is the finding
  mean = 5.2, p95 = 18    <-- the mean looks fine and is misleading
```

## 2. Maximum blast radius in a k-segmented network

If an attacker can chain through k-reachability, the reachable set is not `k` but grows
with path length. Worst case (full chain, no cycles):

```
  |R| <= 1 + k + k^2 + ... + k^(d-1) = (k^d - 1) / (k - 1)
```

where `d` is the maximum number of hops the attacker can take.

```
  k = 3, attacker can chain 4 hops:  1 + 3 + 9 + 27 + 81 = 121 services
  k = 1 (no chaining at all):        1 + 1 + 1 + 1 + 1 = 5 services
```

This is the quantitative reason **chaining matters**: with k = 3, four hops of lateral
movement reach 121 of 400 services, not 12. A defence that limits per-service fan-out to 3
is only meaningful if fan-out in the *chain* is also limited — which argues for zone
grouping (services only talk within a zone, plus an explicit small set of cross-zone
flows) rather than a flat per-service limit.

## 3. Certificate lifetime as a revocation-window trade-off

With lifetime `T` and an at-risk population of `N` credentials, a compromise discovered
at a uniformly random time within a certificate's life has expected remaining validity:

```
  E[remaining] = T / 2
```

So shortening lifetime halves the exposure window — and increases issuance rate:

```
  issuance rate = N / T
```

Compare two options for 400 workloads:

| Option | T | issuance/day | E[exposure] on compromise |
|---|---|---|---|
| Long-lived | 30 days | 13 | 15 days |
| Short-lived | 1 day | 400 | 0.5 days |
| Ephemeral + short | 6 hours | 1,600 | 3 hours |

The trade-off is now explicit: short lifetimes buy a **30x** reduction in exposure for a
**30x** increase in issuance load. That is a capacity decision for the CA, made
deliberately — and the reason a horizontally-scaled CA with an HSM-backed key is a
prerequisite rather than an optimisation.

Adding **revocation** changes the picture. If revocation is effective within `R` seconds,
exposure becomes:

```
  E[exposure with revocation] = min(remaining, R) = R   (if R < T/2)
```

So for a 1-day lifetime, a 60-second revocation SLA reduces expected exposure from
12 hours to 60 seconds — a 720x improvement, at the cost of a revocation path that must
actually work globally in 60 seconds. Both controls are worth having, and the second one is
only worth having if it is measured.

## 4. TLS handshake cost and the reuse threshold

Handshake bytes and round trips, TLS 1.3:

```
  Full handshake:     1 RTT,  ~3 KB (ClientHello + cert chain + Finished)
  Resumed (PSK):      1 RTT,  ~0.5 KB
  0-RTT (QUIC):       0 RTT,  data in first flight
  Warm connection:    0 RTT,  no handshake bytes
```

The reuse threshold — when a new connection is cheaper than re-establishing an old one:

```
  reuse if:  expected_requests x cost_per_request < handshake_cost
```

For a page with `n` requests, a fixed handshake cost of `H`, and marginal per-request cost
`c` (DNS, TCP, TLS, and the first congestion window of slow start):

```
  reuse if  n x c < H
```

Plugging in real numbers: `H = 3 KB`, `c = 350 bytes` (one extra round trip's headers):

```
  n < 3000/350 ≈ 8.6 requests
```

So a connection is worth reusing for a page of more than ~9 requests. A page with 40
assets is well past the threshold; an API call with one request is not. This is the
quantitative reason a CDN benefits from connection reuse and an API gateway mostly does
not, and it is why QUIC's 0-RTT matters most for navigation requests, not API calls.

## 5. Loss, HOL blocking, and the value of per-stream recovery

From the QUIC lab, the expected stall fraction of a TCP connection carrying loss `p`:

```
  stall fraction ≈ p x (BDP / MSS) x (RTO / RTT)
```

With 100 Mbit/s, 100 ms RTT, 1,400-byte MSS, 2% loss, and RTO ≈ 1.5 x RTT:

```
  BDP/MSS = (100e6 x 0.1 / 8) / 1400 ≈ 1.25e6 / 1400 ≈ 893 packets
  stall fraction ≈ 0.02 x 893 x 1.5 = 26.8    -> over 100% (saturated; the approximation breaks)
```

At 20x lower loss the approximation becomes usable:

```
  p = 0.001:  0.001 x 893 x 1.5 = 1.34   -> >100%, still saturated
  p = 0.0001: 0.0001 x 893 x 1.5 = 0.134  -> 13.4% of time stalled
```

At 0.01% loss, a TCP connection is stalled 13% of the time. Under per-stream recovery, with
`S` parallel streams, a stall affects only the stream that lost data:

```
  per-stream stall fraction ≈ 0.134 / S
  unaffected fraction of the page ≈ 1 - 1/S
```

For 20 parallel asset requests: 99.3% of the page's requests are unaffected, versus 0%
under TCP. This is the measured basis for the HTTP/3 argument in the earlier lab, and it
scales with `S` and with `p` — which is exactly why the win is largest on lossy paths with
many parallel requests.

## 6. Probe coverage and confidence

A security test that samples is a test with a confidence level. Testing a random service
per day, from 400 services:

```
  days to cover all services once = 400
  probability a given service is untested after T days = (1 - 1/400)^T
```

```
  T = 30:   (0.9975)^30  ≈ 0.927  -> 7.3% chance a given service was never probed
  T = 90:   (0.9975)^90  ≈ 0.798  -> 20% untested
```

A 15-minute probe cycle covers everything in 4 days, giving >86% confidence that every
service has been probed within a week. This is the arithmetic behind choosing a 15-minute
interval rather than daily, and it is a coverage argument you can put in front of a
reviewer rather than a preference.

To reach a target confidence `C` that every service has been probed within `T` days:

```
  interval <= T x (1 - (1 - C)^(1/T))^-1 ...  solve directly:
  with C = 0.99, T = 7:  n >= ln(1 - 0.99) / ln(1 - 1/400) ≈ 4.6 / 0.0025 ≈ 1,839 probes/week
  probes/week / 7 = 263/day ≈ one every 5.5 minutes
```

## 7. Exercises

1. 500 services, each segmented to reach 4. Compute flat vs segmented reachable pairs and
   the reduction. Then compute the worst-case blast radius with 4 hops of chaining and
   explain why it exceeds `4 x 500 = 2000`.
2. 300 workloads with 30-day certificates and no revocation versus 12-hour certificates
   with 60-second revocation. Compute expected exposure in both cases, and the issuance
   rate each requires.
3. A handshake costs 3 KB; a reused connection costs 0 and a new connection costs 350
   bytes of per-request overhead. Find the request count at which reuse pays, and explain
   why a 40-asset page and a single-call API behave differently.
4. At 0.01% loss, 100 ms RTT, 100 Mbit/s, and 20 parallel streams, compute the fraction of
   time a TCP connection is stalled and the fraction of requests unaffected under
   per-stream recovery.
5. Probing one random service per day across 400 services: what is the probability a given
   service has never been probed after 60 days, and what interval is needed for 99%
   confidence within 7 days?

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 8446 defines the TLS 1.3 handshake sizes and the 1-RTT / 0-RTT structure used to
  derive the connection-reuse threshold in §4.
  https://www.rfc-editor.org/info/rfc8446/
- The bandwidth-delay product and loss-driven stall behaviour underlying §5 follow the
  congestion-control and loss-detection models in RFC 5681 and RFC 9002.
  https://www.rfc-editor.org/info/rfc5681/
