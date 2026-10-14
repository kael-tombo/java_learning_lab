# Telemetry Service with Sketches and Tagged Snapshots

Brief. A telemetry pipeline computes rolling counters, membership
probes, and integrity-tagged snapshots over 10M daily events, plus
pattern search over a text corpus as the second track. Four structures
split the work; each earns its slot with a measurement.

Counter lane. Fenwick tree over per-minute buckets for prefix sums and
sliding windows; answers vs naive prefix array on 5k windows. Update
and query both O(log n), shown with timing vs bucket count.

Membership lane. Bloom filter fronting the event-id store sized by
FPR = (1 - e^(-kn/m))^k; observed FPR on 200k absent ids beside the
formula value. Disk lookups avoided counted on a mostly-absent replay.

Integrity lane. Merkle root over hourly snapshot batches; auditors
verify sampled blocks with O(log n) proofs against the published root.
One tamper drill (flipped byte) must change the root and name the leaf.

Search lane. KMP/Boyer-Moore pattern search over a 50 MB corpus vs
naive scan; matches must equal the naive set exactly, timing quoted per
algorithm at three pattern lengths.

Ops page. Sketch sizing sheet, snapshot cadence, proof-serving latency,
corpus index note, and the failure rules (saturated filter alarm, stale
snapshot version error, empty-pattern rejection).

Marks: counter parity 12, filter-plus-proof agreement 10, search
exactness with timings 8.
## Service extras
- Sizing sheet with formula values.
- Snapshot cadence posted.
- Proof latency measured.
- Corpus version pinned.
- Filter alarm threshold set.
- Tamper drill logged.
- Pattern timings tabled.
- Failure rules reviewed.
