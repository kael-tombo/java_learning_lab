# Real-World Project - Records Import Service (fundamentals)

Production-style build: a batch importer for student records that must survive restarts, bad input, and load.
## Problem statement
Nightly CSV drops (up to 1M rows) must land in clean summaries by morning. Rows are dirty: bad numbers,
out-of-range scores, duplicate IDs, truncated files. Reruns after crashes must not double-count.
## Architecture
- Reader: streams lines via BufferedReader, never loads the whole file; owns throughput SLO (50k rows/s).
- Validator: parses scores, rejects out-of-range values, collects `bad=<line>` diagnostics; owns error-budget SLO.
- Store: idempotent upsert keyed by student ID in a HashMap-backed index; owns correctness SLO (no duplicates).
- Reporter: writes summary + histogram; atomic rename on success so partial outputs never publish.
## Milestones (4)
1. Slice: happy-path import of 1k clean rows with one end-to-end check printing row counts.
2. Harden: per-line try/catch, range validation, non-zero exit codes, rerun-safe upsert.
3. Observe: stdout results, stderr diagnostics, wall-time and max-heap log lines per run.
4. Scale: 1M-row benchmark; fix the top bottleneck (buffering, boxing, or map resizing).
## Ops checklist
- [ ] Run from a fixed command: `javac --release 21 -encoding UTF-8` build, `java -cp out Importer file.csv`.
- [ ] Load test with generated 1M-row file; record wall-time and peak heap.
- [ ] Runbook: truncated file, all-rows-bad file, rerun-after-crash; expected exit code each.
## Data contract
- Input: UTF-8 CSV `id,name,score` with a header row; CRLF line endings tolerated.
- Scores are ints 0-100; anything else is a bad line with diagnostics, never a crash.
- Output: summary plus histogram, published by atomic rename only on success.
- Reruns key by student id: same id overwrites, counts stay exact after crashes.
- Empty input yields a zero-row summary and exit code 0.
## Deliverables
- Repo with source, self-check tests, benchmark numbers, 1-page ops note.
- Interview story: one incident (e.g. duplicate counts after rerun) in STAR form with the metric that proved the fix.
- Extension: `--strict` mode failing fast with the offending line number.
- Extension: duplicate-ID report listing every colliding row.
- Extension: progress log every 100k rows for long runs.
