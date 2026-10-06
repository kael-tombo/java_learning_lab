# Video Streaming - Vision

## Why This Lab Exists
Video streaming is a CDN problem wearing an application costume. The
application's job is small — produce variants, sign URLs, track playback — and
99% of the bytes are delivered by someone else's edge. Teams that build
sophisticated origin infrastructure for a workload that should be 95% edge
cache hits ship a system that is more expensive and no faster. This lab exists
so the architecture matches the actual byte distribution.

## The Mental Model
Split the problem into three unrelated ones:

```
  ENCODING   (offline, minutes per title, embarrassingly parallel)
  DELIVERY   (CDN, cache-hit-ratio dominated, protocol details matter)
  PLAYBACK   (client, buffer management, seeking, quality switches)
```

Each has a different bottleneck, a different scaling axis, and a different
failure mode. Conflating them produces designs optimised for the wrong one.

## Where the Bytes Actually Go

```
  bitrate ladder:  240p / 360p / 480p / 720p / 1080p / 4K
  users self-select quality based on bandwidth
  ~85-90% of viewing time is at the user's max sustainable bitrate

  session at 4 Mbps for 40 minutes = 4 Mb/s * 2400 s = 1.2 GB per session
  10,000 concurrent sessions      = 12 TB/hour from ORIGIN if cache misses
```
That last number is why cache hit ratio is *the* metric of this system. A 95%
hit ratio means the origin serves 5% of 12 TB = 600 GB/hour. A 90% ratio
doubles it, for free, with no engineering effort. **CDN cache ratio is a
product-quality decision disguised as an infrastructure number.**

## The Two Structural Facts
1. **Video is huge and immutable.** Perfect for CDN caching with long TTLs.
   The content does not change, so invalidation is almost never needed — which
   is exactly what makes CDN economics work.
2. **Playback is unpredictable and bursty.** A single "skip to 2:00:00" is a
   6 MB range request into the middle of a file. You cannot predict which byte
   ranges will be needed, so you need segmented objects and good range
   support, not long-lived TCP connections.

## Delivery Protocols Are a Real Decision
- **Progressive HTTP** + HLS/DASH segments: universal, adaptive, poor for
  low-latency; a 6-30 s segment latency.
- **Low-latency HLS (LL-HLS)**: shorter segments, more requests, 2-5 s latency.
- **WebRTC**: ~1 s latency, but no CDN offload in the classic sense and
  expensive egress.
- **CMAF/fMP4**: the segment format everyone converged on; the thing that makes
  codec-switching seamless.

Latency budget drives protocol, protocol drives cost, cost drives CDN
selection. State the trade rather than defaulting to "HLS because everyone
does".

## What You Should Be able To Do
- Build a bitrate ladder and compute storage and encoding cost from it.
- Compute CDN cost from cache hit ratio, egress volume, and region mix, and
  explain which lever moves it most.
- Design signed URL authorisation (expiry, scope, path binding) and explain why
  unsigned URLs are a business decision, not just a security one.
- Explain why `Range` requests and segmented objects matter for seeking, and
  measure the cost of an unseekable stream.
- Design playback telemetry: rebuffer ratio, startup time, and how to derive
  QoE from them.
- State the difference between a VOD and a live design and why live needs a
  different origin strategy (low-latency origin, no long cache TTL).

## The Anti-Goals
- Not an over-engineered origin. If your origin serves more than ~10% of bytes,
  the design is wrong.
- No unsigned URLs on paid content; it converts a revenue problem into a
  bandwidth bill.
- No single-rendition serving. Adaptive bitrate is not a nice-to-have; one
  rendition means one bad network gives a bad experience with no fallback.

## Success Criteria
You can specify a streaming platform with: rendition ladder and storage cost,
CDN architecture with a target and measured hit ratio, signed URL contract,
segment format and protocol choice with latency justification, origin
protection rules, and a QoE metric set with thresholds.

## How To Use This Lab
1. `THEORY.md` for architecture and patterns.
2. `MATH_FOUNDATION.md` for bitrate ladders, QoE models, cache math, cost.
3. `CODE_DEEP_DIVE.md` for signed URLs, manifests, buffering, range handling.
4. `MINI_PROJECT.md` to build and measure a streaming pipeline.
5. `REAL_WORLD_PROJECT.md` for a production VOD and live platform.