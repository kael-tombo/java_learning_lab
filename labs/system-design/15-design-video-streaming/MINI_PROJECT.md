# Video Streaming - MINI PROJECT

## Project: A Streaming Pipeline You Can Actually Measure

**Time**: 12-16 hours

**Goal**: Build a small VOD pipeline — encode ladder, sign, serve, buffer,
measure — and produce a QoE dashboard whose numbers you can defend.

### Scope

```
UrlSigner         signed manifest and segment URLs
ManifestBuilder   master + media playlists, ladder
AdaptivePlayer    buffering + ABR with cooldown
PlaybackTelemetry QoE percentiles and segmentation
SegmentWarmer     prewarming policy
SimulatedCDN      cache with configurable hit ratio and latency
```

Use a simulated CDN and simulated network (or `ffmpeg` if available for
encoding) so the lab focuses on the design rather than on transcoding setup.

### Step 1: Encode a Bitrate Ladder (2 h)

Encode one source (use any public-domain clip, ~2 minutes) into 4-5 renditions.
**Required:** measure the *actual* average bitrate of each output and compare
it to the target.

```
target 2,800 kbps -> actual?  (encoders routinely land 10-25% high)
```
Assert that each rendition is a genuine step above the previous one. Then
adjust the ladder to the measured values and record the change. The manifest
must describe the files you actually produced, not the ones you wished for.

### Step 2: Manifests (1 h)

Generate the master playlist with `ManifestBuilder`. Required tests:

- Every rendition in the manifest resolves to an existing playlist file.
- Declared `BANDWIDTH` matches the measured bitrate (assert with a tolerance).
- Subtitles are separate segment references, not one big file.
- Audio renditions are separate groups, so an audio-only download fetches zero
  video bytes. **Assert the byte counts.**

### Step 3: Signed URLs (2 h)

Implement `UrlSigner` and sign manifests and segments.

Required tests:

- A valid signature verifies; a tampered path, expiry, or signature fails.
- An expired URL fails.
- **Constant-time comparison**: assert `constantTimeEquals` does not early-return
  (review the code and add a test comparing equal-length and unequal-length
  inputs).
- Entitlement: a non-subscribed user cannot obtain a signed URL.
- Expiry is short (e.g. 5 min for segments). Assert an expired segment URL
  fails and document the leak window.

**Critical check:** verify your CDN/asset path treats the signature as a
*header*, not part of the cache key. Then write a test asserting two different
signatures for the same segment produce the SAME cache entry. Getting this
wrong drops your hit ratio to zero, and it is the most common mistake.

### Step 4: Simulated CDN and Hit Ratio (2 h)

Build a cache with configurable TTL, cache-key policy, and edge latency.
Measure hit ratio under three conditions:

| Condition | Expected hit ratio |
|-----------|-------------------|
| All segments, TTL 1 day, signature in path | very low (every URL unique) |
| All segments, TTL 1 day, signature as header | ~high |
| Manifests uncacheable | manifest misses every time |

Record origin bytes served in each case. **This single experiment is the
justification for the whole architecture** — put the numbers in the write-up.

Also measure: what happens to origin QPS as segment duration drops from 10 s to
6 s to 2 s? Plot it.

### Step 5: Adaptive Player With Cooldown (2 h)

Implement `AdaptivePlayer`. Test against a simulated bandwidth profile:

1. Constant 5 Mbps: assert it settles on a stable rung and stops switching.
2. Bandwidth oscillating between two rungs: assert switching is damped and
   `looksOscillating()` returns false.
3. Network drops to 500 kbps mid-stream: assert it downshifts within the
   cooldown and does not stutter beyond target.
4. Network recovers to 10 Mbps: assert it eventually climbs back.

**Required:** measure how long it takes to climb back after recovery. Report it
— that is the cost of a large buffer, and it is a user-visible quality problem.

Then try the naive version (no cooldown, instantaneous estimate) on the same
profile and count the switches. Report the difference. Keep this as a documented
control.

### Step 6: Buffering and Rebuffer (1 h)

Implement buffer accounting with segment duration as a parameter. Test:

- 6 s segments, 18 s target buffer. Simulate a 3 s network stall: assert
  playback continues (no rebuffer).
- Simulate a 25 s stall: assert rebuffer occurs and is measured correctly.
- Vary segment duration (2 s / 6 s / 10 s). Record rebuffer count and time-to-
  first-frame for each. Report the trade.

### Step 7: QoE Telemetry (2 h)

Emit per-session telemetry and build the dashboard:

- Startup time p50/p95/p99 (not average).
- Rebuffer ratio p50/p95/p99.
- Rendition distribution and switch counts.
- **Segmented by region x device class x rung.** Required: create one
  artificially broken segment (e.g. one region with 5 s startup) and verify the
  dashboard surfaces it while the overall average still looks fine.

This is the deliverable that proves segmentation matters: a dashboard that hides
a broken 4% is not a dashboard.

### Step 8: Warming Policy (1 h)

Implement `SegmentWarmer` and `shouldWarm`. Report:

- Bytes warmed per release.
- Misses avoided in the first hour.
- The crossover point where warming stops paying for itself.

Assert warming covers the **init segment first** — without it the player cannot
start at all, which is a much worse failure than a slow first rendition.

### Deliverables

1. A measured bitrate ladder with actual-vs-target adjustment.
2. Manifests validated against real files, with audio-only byte assertions.
3. Signed URLs with tamper/expiry/entitlement tests and the cache-key
   demonstration.
4. CDN hit ratio comparison showing the signature-in-path trap, plus origin
   bytes per segment duration.
5. ABR with cooldown, plus the naive-version control comparison.
6. Buffering behaviour across segment durations with time-to-first-frame.
7. QoE dashboard with percentiles and segmentation, including a deliberately
   broken segment that the dashboard catches.
8. Warming policy with the crossover analysis.

### Stretch

- Implement a real low-latency path (2-4 s) with a modified playlist and
  measure end-to-end latency against your simulated network.
- Add DRM ( Widevine/FairPlay/PlayReady) key delivery with per-session licence
  and verify that a signed *manifest* URL without a valid licence returns 403
  at the packager, not just at the API.