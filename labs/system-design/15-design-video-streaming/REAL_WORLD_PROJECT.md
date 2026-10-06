# Video Streaming - REAL WORLD PROJECT

## Project: Global VOD + Live Streaming Platform

**Time**: 4-6 weeks (team of 5)

**Scenario**: A streaming platform with a 90,000-title VOD catalogue, 40
concurrent live channels, and 2.1M peak concurrent viewers. Requirements in
tension:

- VOD startup p95 < 2 s globally, including first-time titles.
- Live latency < 6 s for the sports tier.
- CDN cost < 30% of revenue while grossing $4.2M/month of subscription.
- 8 delivery regions with data-residency constraints in two of them.
- 4K and HDR for a premium tier at roughly 4x the bitrate.

### Step 1: Cost Model First (the number that constrains everything)

Produce and defend:

```
Storage (from MATH_FOUNDATION):
  mezzanine + 6 renditions = 20.4 GB/hour
  90,000 titles, avg 42 min = 63,000 hours
  = 63,000 * 20.4 GB = 1.29 PB
  + 20% version headroom = 1.54 PB

Bandwidth:
  2.1M peak concurrent, avg bitrate 4.1 Mbps (mix of tiers)
  peak = 2.1e6 * 4.1e6 / 8 = 1.08 TB/s = 3.9 PB/hour at peak
  average (assume 35% of peak) = 1.36 PB/hour = 32.6 PB/month
  -> at $0.04/GB average blended, ~$1.3M/month before optimisation

Origin exposure (what you must NOT pay CDN rates for):
  at 95% hit: 1.63 PB/month to origin
  at 98% hit: 0.65 PB/month to origin
  -> a 3% hit-ratio improvement saves ~$39k/month with ZERO engineering
```
**Deliverable:** the cost model with each figure traced to a measurement, and
the ranked list of levers by cost impact. Put cache hit ratio at the top of
that list — it will be, and it surprises everyone.

### Step 2: Encoding Pipeline

```
ingest -> mezzanine (archive) -> ladder encode (AV1 + HEVC fallback)
       -> package (CMAF/fMP4, aligned segments)
       -> segment storage -> manifest generation -> cache purge -> warm
```

Decisions to document:
- **AV1 vs HEVC**: ~64% storage and egress saving, materially longer encode
  time. Justify by tier: AV1 for the standard tier, HEVC for the premium tier
  where devices are newer.
- **Mezzanine retention**: delete after packaging + verification window.
  Keeping 1.29 PB of mezzanines "just in case" is the most common cost leak.
- **Alpine/transmux-only** where the source codec is already acceptable:
  zero quality loss, minutes instead of hours.
- **Aligned segments** across renditions (required for seamless switching).

**Required:** a verification step in the pipeline that plays every rendition
start, middle, and end, and gates publication on it. A published asset with a
broken final segment is a support ticket for every viewer who reaches the end.

### Step 3: CDN Architecture and Origin Protection

```
viewer -> edge PoP (local) -> tier-1 edge (regional) -> origin shield -> storage
```

Origin protection is the security requirement:

- Origin is **not internet-reachable**. Only CDN egress ranges are permitted.
- Origin requires a signed header from the CDN, separate from the asset
  signature.
- Bucket policy denies unsigned requests outright.

**Required:** prove it. Attempt to fetch an asset directly from storage with no
signature; assert a 403. Attempt with a valid asset signature but no CDN header;
assert a 403. Attempt with a signature for asset A used against asset B; assert
a 403.

Cache configuration, with each setting justified:

| Setting | Value | Reason |
|---------|-------|--------|
| Segment TTL | 30 days | Content is immutable |
| Manifest TTL | 60 s, revalidated | Allows emergency rotation |
| Cache key | path + bytes range, **not** signature | Signature must not fragment the cache |
| Behaviour on origin 5xx | serve stale if available | A transient origin blip should not break playback |
| Negative caching | 60 s for 404s | Stops origin hammering for expired assets |

Measure hit ratio per region and per asset class. A new release's hit ratio is
the interesting number — it is the warming metric.

### Step 4: Signed URLs and Entitlement

```
signing policy:
  manifest URL   TTL 60 min   (short: manifests must be revocable)
  segment URL    TTL 5 min    (short: bounds leak window per asset)
  live segment   TTL 2 min    (very short: live content is current-state)
  signature in header, not query string            (cache-key integrity)
  signed per-session where possible               (sharing resistance)

entitlement checked BEFORE signing:
  subscription tier -> allowed renditions, resolution cap, HDR eligibility
  geography         -> allowed regions (residency!)
  concurrency       -> per-account device limit
  DRM               -> if DRM enabled, licence is separate from the URL signature
```

**Required:** verify that DRM is enforced at the **packager**, not only at the
API. A signed manifest URL without a valid licence must fail at segment
retrieval. Write the test that proves it.

### Step 5: Live Pipeline (the part that must not be the VOD design)

```
ingest (SRT/RTMP) -> transcode farm (6 renditions) -> low-latency packager
   -> origin shield -> edge (short TTL, seconds) -> player
```

Why live is different, stated explicitly:

- Cache TTL in **seconds**, not days. Content is current-state, so a cached
  segment older than a few seconds is wrong, not merely stale.
- Origin is continuously hot: the edge only helps viewers in the same PoP.
  The transcode farm, not the CDN, is the scaling constraint.
- Transcoder capacity is the fleet-sizing driver:
  `concurrent_streams * ladder_size = transcodes needed`. Pre-warm transcoders
  ahead of a scheduled event.
- Latency budget from `MATH_FOUNDATION.md`, measured end to end:
  capture -> encode -> segment -> publish -> transit -> player buffer.

**Required:** measure real end-to-end latency from ingest timestamp to first
rendered frame, broken into the six components. Report p50/p95. If p95 exceeds
your promise, say so with the numbers rather than adjusting the promise.

### Step 6: QoE and the Operating Loop

Track, per region x device class x rendition:

- Startup time p50/p95/p99 (TLS session resumption on; measure the win).
- Rebuffer ratio p50/p95/p99 and stall count.
- ABR switch count and oscillation signature.
- Bitrate achieved vs. device capability.
- Playback error rate by error class (403 from DRM, 404, network, decode).

Alert on the **worst segment**, not the average. Build a dashboard where a
single broken region cannot hide inside a good global number. Add a synthetic
probe per region (real playback of a canary asset) so the numbers reflect real
playback, not just client self-reports.

**Deliverable:** the QoE dashboard with a documented alert per metric and a
runbook for each.

### Step 7: Failure Drills

1. **Origin unreachable for 10 minutes.** Verify the edge serves from cache and
   playback continues. Verify new releases queue rather than publish broken.
   Measure the actual hit-ratio-driven survival margin.
2. **CDN provider failure in one region.** Verify failover to the secondary
   provider, measure re-propagation and startup regression, and confirm the
   cache-key policy does not fragment on provider change.
3. **Transcoder farm saturated (all live streams + 200% load).** Verify
   admission control drops new *liveness* streams before it degrades existing
   ones, and that VOD is unaffected (separate capacity pool — this is the
   reason VOD and live must not share a transcoder budget).
4. **Cache purge storm** (a bad deploy triggers a full purge). Verify stale
   serving prevents an origin collapse and that the purge is rate-limited.
5. **Signature key rotation.** Rotate signing keys with an overlap window;
   verify in-flight segments do not break and that the old key is retired.
6. **Player-side bug in one rendition** (wrong codec string in the manifest for
   one tier). Verify error telemetry catches it and the QoE segmentation
   identifies the affected tier without a support ticket.

### Deliverables

1. Cost model with hit ratio as the top lever, figures traced to measurements.
2. Encoding pipeline with codec/retention decisions and a publication gate.
3. CDN architecture with the six cache settings justified, plus origin-protection
   tests (unsigned, missing header, wrong asset).
4. Signing and entitlement policy with TTLs, plus a DRM-at-packager test.
5. Live pipeline with measured six-component latency breakdown and separate
   transcoder capacity.
6. QoE dashboard with per-segment alerts and runbooks.
7. Six drill reports with measured numbers, including the actual survival margin
   during an origin outage.
8. Metrics: startup p95/p99 by region, rebuffer ratio p95, CDN hit ratio,
   origin bytes/s, warming effectiveness, transcode utilisation, 403 rate by
   reason.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Cost | Built it, then looked at the bill | Hit ratio identified as top lever before building |
| Ladder | Targets, not measurements | Measured and adjusted; publication gate verified |
| Origin | Publicly reachable | Shielded, header-authenticated, three attack tests |
| Cache key | Signature in query string | Signature in header, fragmentation test included |
| Live | VOD architecture copied | Short TTL, separate capacity, latency measured |
| QoE | Global average | Worst segment alerted; synthetic probes |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 9110 — *HTTP Semantics*: the normative definition of `Range` and
  `206 Partial Content`, and conditional requests with validators. This is the
  reference for byte-range segment delivery and for the cache-validation
  behaviour your CDN configuration depends on.
  https://www.rfc-editor.org/rfc/rfc9110.html
- AWS Well-Architected Framework — Performance Efficiency and Cost
  Optimization pillars, including media-delivery and caching guidance; the
  reference for the caching decisions and the origin-protection trade-offs in
  this project.
  https://aws.amazon.com/architecture/framework/

Both are reference-quality and versioned. Pin the version/section you read.
Two things to verify with your CDN provider rather than infer from these
documents: how the provider forms its cache key (whether query strings and
range headers are included), and its exact behaviour on origin `5xx` with
respect to stale serving — both materially change this design.