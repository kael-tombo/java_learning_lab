# Column-Buffer Analytics CLI on a Dynamic Array

A batch analytics tool that keeps one growing column of integers in a
hand-rolled dynamic array, answers range scans and appends, and tails a
log ring without ever touching ArrayList in the hot path.

The question this build answers: how far a doubling-resize buffer carries
an analytics CLI before scan latency or heap pressure forces paging to disk.

## Workload under test
- Append-only ingest from CSV batches, 100k to 5M rows per run.
- Scan queries: full-column fold (sum/mean) plus bounded range slices.
- Tail view: last-K rows served from a fixed ring beside the column.

## Storage design
- Contiguous int/long backing store, doubling on overflow, explicit
  trim-to-size after ingest so idle heap stays flat.
- Presized construction from the CSV row count estimate; every resize
  event appends a record (old cap, new cap, copy nanos) to a resize log.
- Amortized append cost stays O(1); indexed read stays O(1) worst case.

## Build sequence
1. DynamicArray core: get, set, push, slice, trim, resize log.
2. CSV loader with row-count presizing and malformed-row quarantine.
3. Scan engine: fold, range slice, tail-K from the ring.
4. CLI flags for initial capacity, growth factor, and scan width.
5. Snapshot save/load so a cold start resumes the same buffer.

## Evidence to collect
- Append throughput across 1M pushes and the resize-event count.
- Scan latency for full folds vs 1k-wide slices at 1M rows.
- Heap after ingest vs after trim, via runtime accounting.
- Oracle check: every scan result equals the ArrayList reference run.

## What good looks like
- Zero mismatches against the oracle on 50k mixed ops.
- Resize count within one of floor(log2(N/initCap))Grouping check.
- Documented knee where doubling copies dominate append time.
- Cold reload reproduces the pre-shutdown scan answers exactly.

## Failure drills
- CSV with ragged rows and trailing commas must quarantine, not abort.
- Slice bounds past the end clamp and report instead of throwing.
- Snapshot written mid-ingest still loads; partial tail is flagged.
- Oversized single batch triggers presize rather than repeated doubling.

## Hand in
- Source, seeded CSV generator, resize log sample, heap notes.
- One-page note: SLO table, the doubling knee, rollback to ArrayList.
- Demo: ingest 1M rows, scan, tail, snapshot, reload, rescan.

## Scoring
- Append/scan behavior against stated targets: 12.
- Oracle parity plus resize-log honesty: 10.
- Heap discipline (cap, trim, presize): 8.
