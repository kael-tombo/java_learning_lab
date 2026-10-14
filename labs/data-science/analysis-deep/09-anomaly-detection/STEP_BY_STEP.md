# Step by Step - First Detector

## Step 1. Assemble normal history

Collect a clean window of normal operation (sensor readings, login
rates). Exclude known incident periods - training on incidents teaches
the detector that outages are normal.

## Step 2. Compute center and spread

Mean/sd and Q1/Q3/IQR on the clean window (AnomBase: mean 11.864,
sd 5.739, Q1 9.900, Q3 10.300, IQR 0.400 on its toy data). Note skew
before choosing which rule to trust.

## Step 3. Flag and compare rules

Apply |z| > 3 and the Tukey fences; list flags per rule. On the demo
data both flag index 7 (30.000) - agreement on the obvious case builds
trust before harder ones.

## Step 4. Score a labeled week

If labels exist, sweep three thresholds and tabulate P/R (PrCurve rows:
0.667/0.500, 0.600/0.750, 0.500/1.000). No labels? Have an operator
grade the top-20 flags - precision-at-20 is the honest substitute.

## Step 5. Do the Bayes sanity check

Estimate prevalence from history, plug into PPV with your measured
sens/fpr. BaseRate's shape (99 true vs 999 false per 100k) is typical -
scale to your volumes into alerts-per-day.

## Step 6. Set tiers, not a line

Page on critical, queue medium for shift review, log the rest. Write
the runbook line for each tier: who acts, in how many minutes, with
what rollback.

## Step 7. Schedule re-fitting

Bulk behavior drifts; stale center/spread decays precision. Calendar
the re-fit (monthly for stable systems, weekly for fast ones) and the
precision review that justifies keeping each tier.

## Checkpoint table

| Step | Artifact | Check |
|---|---|---|
| 1 history | clean normal window | incidents excluded |
| 2 center/spread | mean/sd + Q1/IQR | skew noted |
| 3 flags | per-rule flag lists | agreement assessed |
| 4 sweep | P/R table | costs pick the row |
| 5 Bayes | PPV + alerts/day | nine-of-ten said aloud |
| 6 tiers | page/batch/log + runbooks | volumes fit on-call |
| 7 schedule | re-fit calendar | precision review attached |

An empty cell means the step was skipped; skipped Bayes voids the launch.
