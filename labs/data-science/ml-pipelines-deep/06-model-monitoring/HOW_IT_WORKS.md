# Model Monitoring - How It Works

## Monitoring loop
1. Log predictions with model version, timestamp, feature snapshot, and score.
2. Aggregate hourly or daily: score mix, null rates, volume, error counters.
3. Compare current window against a fixed reference window with PSI or KS-style checks.
4. Page only when a high-precision alert fires; link every page to a runbook.

## Handling label delay
1. Store predictions keyed for later joining with ground truth.
2. Compute quality metrics only on mature windows where labels have mostly arrived.
3. Show provisional metrics for fresh windows marked as incomplete.

## Incident flow
1. Alert fires with slice breakdown (which segment moved).
2. On-call checks pipeline health first (volume drops, schema errors), then model causes.
3. Mitigation is rollback, threshold change, or traffic shift; retraining follows diagnosis.

## Closing the loop
1. Confirmed incidents become test cases pinned in the evaluation set.
2. Thresholds and reference windows update deliberately, not silently.
3. Postmortem records cause, detection lag, and monitor changes.

## Reference lifecycle
1. Choose the reference window from known-good behavior and record the reason.
2. Pin its statistics; every comparison reuses the pinned numbers.
3. Refresh only through review, keeping the old snapshot for back-comparison.

## Slice investigation
1. Read the page: slice name, signal, maturity age, runbook step one.
2. Confirm pipeline health: volume, schema errors, deploy timestamps.
3. Drill into the named slice before touching global thresholds.

## Provisional reporting
1. Mark every window younger than the maturity bar provisional.
2. Dashboards show provisional points distinctly from official ones.
3. Promote a window to official only after labels join past the bar.

## Postmortem capture
1. Record cause, detection lag, and which monitor fired or missed.
2. Pin the incident window as an evaluation case with labels.
3. Retune the rule or reference deliberately; log the reason.
