# REAL_WORLD_PROJECT — Matrix Algorithms
> Nightly feature-cross batch: blocked dense multiplication with tiled memory use, checksums, and a size guard.

## System and inputs
- Feature matrices (samples x features, up to 20k x 2k) land in object storage nightly; job computes the Gram matrix for the downstream trainer.
- Job config sets tile size (default 256) and a max-n guard derived from worker memory.
- Golden 3x3/2x2 pairs run as a preflight correctness gate before the big multiply.

## Design
- Blocked (tiled) ijk multiply: tiles stream through L2-sized blocks; B tiles transposed once per job.
- FLOP estimate 2n^3 quoted in the run log for capacity planning; wall time recorded per tile row for skew detection.
- Checksum: row-sum invariant checked per output block against input row/column sums.

## Metrics
- Job wall time and per-tile-row skew (max/mean) with alerts on 2x skew.
- Checksum mismatch count (any nonzero pages immediately).
- Memory high-water mark vs the max-n guard.
- Preflight gate pass/fail (blocks the big job on failure).

## Failure modes
- Input exceeding max-n: guard rejects before allocation with the byte estimate in the error.
- Skewed tile rows (ragged last block): remainder tiles sized explicitly, never assumed uniform.
- Silent corruption: checksum mismatch quarantines the output block and retries once, then fails the job.
- NaN in features: pre-scan rejects the input with column index in the message.

## Rollout
1. Run beside the existing pipeline on 7 nights of history; compare Gram outputs exactly.
2. Cut over one model family; watch skew and memory dashboards.
3. Expand tile tuning (128/256/512) from measured nights, not defaults.

## Acceptance criteria
1. Preflight gate reproduces the lab 3x3 product and the Strassen 2x2 check before every big run.
2. Oversize input is rejected with a byte estimate, verified by a test submitting n = guard + 1.
3. Checksum catches a deliberately flipped output block in a chaos test.
4. Tile-skew dashboard shows max/mean per job run.
5. Rollback is the previous job definition version, runnable in one command.

## Cost and contract notes
- Capacity plan from 2n^3 FLOPs per Gram job; worker count derived from the previous week's median wall time plus 30 percent headroom.
- Preflight gate (lab 3x3 + Strassen 2x2) runs as a blocking CI step on the job image; failure blocks the nightly schedule.
- Output blocks carry row-sum checksums in sidecar files retained 30 days for rerun disputes.
- Contract: job manifest declares (n, tile, max-n guard); the scheduler rejects manifests above guard with the byte math attached.
