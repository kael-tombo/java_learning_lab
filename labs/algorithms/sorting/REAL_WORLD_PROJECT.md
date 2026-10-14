# REAL_WORLD_PROJECT — Sorting Track
> Clickstream sessionizer: sorts up to 50M events nightly by (user, timestamp) with a dupe-tolerant method, checksums, and skew alerts.

## System and inputs
- Raw events land hourly as CSV shards; nightly job sorts by composite key (user id, epoch ms) with stable order for same-ms ties.
- Shard sizes vary 10x day over day; adversarial case is pre-sorted bot traffic plus heavy-dupe event types.
- Output feeds session-gap analysis requiring exact tie order preserved from ingestion sequence numbers.

## Design
- In-memory path (single 64 GB worker): 3-way quicksort variant for dupe-heavy shards, mergesort path when stability audit demands it.
- Overflow path: 16-way external merge with 256 MB run buffers when a shard exceeds the memory guard.
- Correctness: per-shard checksum (count + key hash chain) verified before and after sorting; mismatch quarantines the shard.

## Metrics
- Nightly wall time and per-shard skew (max/mean sort time) with alerts at 3x skew.
- Comparison counts sampled per shard to detect distribution shifts (bot-traffic signature).
- External-merge spill rate (should be near zero on normal nights).
- Stability audit: tie-order preservation check on 1-in-1000 sampled keys.

## Failure modes
- Pre-sorted adversarial shard hits quicksort worst case: method router picks 3-way/mergesort by a pre-scan entropy check.
- OOM on a 10x shard: memory guard diverts to external merge before allocating the full array.
- Checksum mismatch: shard quarantined, job continues on the rest, page on second mismatch.
- Clock-skew timestamps (future epochs): validation band rejects events outside [now-90d, now+1h] with counts reported.

## Rollout
1. Shadow-sort 14 nights of history; byte-compare against the existing pipeline output.
2. Cut over one region; watch skew and spill dashboards for a week.
3. Fleet-wide with the entropy router armed.

## Acceptance criteria
1. Shadow fortnight shows zero unexplained byte diffs (tie order included).
2. Adversarial pre-sorted + dupe shard sorts within the overflow budget without OOM (chaos test).
3. Quarantine path proven by a deliberately corrupted shard.
4. Stability audit passes on the sampled keys every night it runs.
5. Rollback replays the previous pipeline image on the same inputs.

## Cost and contract notes
- Worker sizing from the slowest shard in the shadow fortnight plus 40 percent headroom; spill-path costed separately.
- Session-gap analysis depends on tie order, so the stability audit result ships with every nightly manifest.
- Shard manifests carry (method used, ms, comparisons, checksum) for post-hoc distribution-shift analysis.
- Contract: nightly manifest declares per-shard method and spill flag; downstream jobs refuse manifests without checksums.
