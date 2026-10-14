# Step by Step - Your First A/B Readout

## Step 1. Collect the four numbers

x_A, n_A, x_B, n_B (conversions and visitors per arm). The AbTest demo
uses 1200/10000 vs 1320/10000 - replicate with your own counts.

## Step 2. Check the split first

Run the SRM chi-square on (n_A, n_B) against the planned ratio. If it
flags, stop: diagnose the assignment bug before reading any metric.

## Step 3. Compute d, SE, z, p

d = p_B - p_A; SE from the two-proportion formula; z = d/SE;
two-sided p via normal CDF. Expect AbTest's values (z 2.55739,
p 0.01055) when using its inputs - mismatch means a code bug.

## Step 4. Write the interval in plain units

d +/- 1.96*SE = [0.00280, 0.02120]: "between +0.28pp and +2.12pp".
Decide whether the whole range, or just part of it, clears your ship
threshold.

## Step 5. Size the next test

Use the SE table pattern (SampleSize): at p = 0.10 the MDE halves each
time n quadruples. Solve for the n your next hypothesis needs before
launching it.

## Step 6. Guardrail review

List every guardrail with its own interval. One veto-grade regression
outweighs a goal win - write the veto down explicitly or it gets
negotiated away.

## Step 7. Log and decide

One row: hypothesis, horizon, n per arm, MDE, d with CI, SRM p,
decision. Future you will thank present you.

## Checkpoint table

| Step | Artifact | Check |
|---|---|---|
| 1 four numbers | x_A, n_A, x_B, n_B | counts, not rates |
| 2 SRM | chi2, p | p >= 0.01 or stop |
| 3 readout | d, SE, z, p | matches AbTest on its inputs |
| 4 interval | d +/- 1.96 SE | low end vs threshold |
| 5 next sizing | n from MDE | planned before launch |
| 6 guardrails | per-metric intervals | vetoes written down |
| 7 log row | hypothesis..decision | future-readable |

An empty cell means the step was skipped; skipped SRM voids the readout.
