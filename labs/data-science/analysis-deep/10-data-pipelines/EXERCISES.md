# Exercises - Data Pipelines

## 1. Prove the fixed point (runnable)

Copy PipeIdem, apply batch2 twice more, assert the map still equals
{o1=9.5, o2=4.0, o3=7.25} with rows = 3 after each. Print PASS with the
map contents - that print is your idempotency proof.

## 2. Append vs upsert (runnable)

Replace the map with an ArrayList add per record, replay batch2, and
count rows (expect 7 with duplicates). State in one sentence why blind
append can never be replay-safe.

## 3. Threshold policy (runnable)

Copy PipeQuality, add policy: quarantine if nullRate > 0.10 or drift >
1.0. Show the demo batch quarantines (0.333 > 0.10), then craft a clean
6-row batch that passes and print both verdicts.

## 4. Compat matrix (runnable)

Extend PipeSchema with: removed field (v3 drops amount), renamed field
(quantity for amount), widened type (int->long for id, policy: allowed
with cast documented). Print COMPATIBLE/BREAKING per case with the rule
cited (subset, name match, or explicit widening policy).

## 5. Late-data windows (paper)

Events with event-time hours {1, 2, 2, 5} arrive in order 1, 5, 2, 2
(one batch, late twos). Show the width-2 tumbling means under
event-time vs arrival-time assignment differ, and state which your
pipeline uses and where late data goes (lateness window or side output).

## 6. Backfill promotion checklist (paper)

Write the six-line promotion gate: staging row delta, key overlap,
value-mismatch rate, check outcomes, code version pin, approver sign.
No promotion without all six filled - ceremony is the feature.

## 7. Throughput sizing (paper + runnable)

Batches of 6 rows merge in negligible time; scale the thought: 6M rows
with 10% duplicates replayed. Compute expected stored rows under keyed
merge (6M) vs blind append (6.6M) and state the serving-store cost of
the wrong choice in one sentence.

## 8. Contract negotiation (paper)

Team A wants to rename amount to total; team B reads amount daily. Write
the migration plan: v2 adds total (additive), dual-read window dates,
B's cutover commit, v3 drops amount. Four dated lines, no lock-in.
