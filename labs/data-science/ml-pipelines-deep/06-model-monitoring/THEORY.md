# Model Monitoring - Theory

Monitoring detects when a deployed model or its inputs stop matching expectations.

## What can shift
- Data drift: the distribution of inputs changes while the true input-output mapping stays fixed.
- Concept drift: the mapping itself changes, so old decision boundaries go stale even with familiar inputs.
- Label delay: ground truth arrives after the prediction, so measured quality lags reality.

## Comparing distributions
- PSI bins a feature or score, then sums (actual - expected) * ln(actual / expected) across bins. It is a relative shift size: larger means more change.
- The two-sample KS statistic is the largest absolute gap between the empirical CDFs of reference and current samples.
- Both are treated as concepts for tracking change, not as universal pass/fail numbers; binning and sample size move them.

## What to track
- Prediction-distribution tracking: score mix, positive rate, null and out-of-range rates per feature.
- Slice metrics: quality per segment (region, device, cohort) so aggregate stability does not hide a broken slice.
- Pipeline health: input volume, schema violations, feature build latency, serving errors.

## Ground truth and feedback
- Evaluate on mature labels only; fresh windows undercount outcomes that arrive late.
- Feedback loops arise when model decisions shape the data later used for training (for example approvals becoming training labels).
- Log predictions with model version and feature snapshot so incidents can be replayed.

## Alerts
- Alert precision is the fraction of pages worth acting on; alert recall is the fraction of real incidents that paged.
- Noisy monitors get ignored, so each alert links to a runbook with triage steps and rollback pointers.
- Prefer a few high-precision alerts plus dashboards for the rest.
