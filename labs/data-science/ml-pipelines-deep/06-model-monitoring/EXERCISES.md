# Model Monitoring - Exercises

1. Run A06Psi; shift actual bin 3 from 0.08 to 0.12 and recompute PSI.
   - Expect PSI to roughly double with bin 3 dominating; report both values.
2. In B06Ks, move one current sample by +0.2 and recompute KS.
   - Note how a single point moves the maximum gap and its location.
3. Recompute C06Alerts with fp halved (tighter threshold) and fn doubled; report the new precision/recall.
   - Expect precision up and recall down: the canonical alert tradeoff.
4. Build an hourly rollup: counts, null rate, and positive rate from a small inline event list.
   - Print one line per hour with all three numbers.
5. Implement maturity filtering: tag windows younger than 6 days provisional and exclude them from the mean.
   - Show the official mean changing once immature windows are excluded.
6. Write a slice check: compute positive rate per segment and flag the segment that moved most.
   - Print per-segment rates plus the argmax segment name.
7. Draft a runbook entry for a drift page: triage order, pipeline checks, and rollback pointer.
    - Keep it to ten lines an on-call engineer can follow at night.
8. Simulate a silent monitor: stop event emission for three hours in a toy stream
   and show which check fires first — value monitors stay green while volume alerts page.
    - Report the detection lag of each monitor type in windows.
9. Build a per-slice dashboard table: three segments by two metrics from inline data,
   then inject a slice-only regression and confirm the aggregate barely moves.
    - Print aggregate and per-slice numbers side by side.
10. Fit per-slice thresholds: given two slices with different base rates, set one shared
    threshold and one per-slice pair, then compare false-page counts on a quiet week.
    - Expect the shared threshold to over-page the volatile slice; report both counts.
11. Write the maturity-annotated chart: plot a metric line with provisional points marked
    and official points solid across a six-day label-landing curve.
    - Confirm the provisional segment would have misled a reader without marks.
12. Draft the reference-refresh review: given a pipeline unit change, write the reason,
    the new snapshot id, and the back-comparison result against the old reference.
    - Keep it to five lines a reviewer can approve or reject.
13. Expire a trial monitor: take a paging rule with measured precision below the bar,
    demote it to dashboard, and document what would re-promote it.
    - State the precision number, the bar, and the re-promotion condition.
14. Detect feedback-loop contamination: tag training rows whose labels came from model
    approvals, compute their share, and show the retraining gate decision.
    - Expect the gate to block while looped labels dominate; report the share.
   - Keep it to ten lines an on-call engineer can follow at night.

## Submission check
- All programs compile with `javac --release 21 -encoding UTF-8` and print pure ASCII.
