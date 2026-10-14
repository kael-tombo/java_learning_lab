# Step by Step - A Small Causal Analysis

## Step 1. Write the question and the table

Treatment (drug yes/no), outcome (recovered yes/no), confounder
(severity mild/severe). Tabulate counts per treatment-by-stratum cell
before computing anything pooled.

## Step 2. Compute stratum-specific gaps

Recovery gap within mild and within severe separately (see Confound
output: -0.1000 and +0.1000). These are the only numbers that hold
severity fixed.

## Step 3. Compute the naive pooled gap

Overall treated minus control rate (-0.3267 here). Keep it as the
demonstration of bias, never as the answer.

## Step 4. Weight into one adjusted number

Multiply each stratum gap by its population share and add: the
-0.0067 adjusted diff. State the assumption: severity (and nothing
else unmeasured) confounds.

## Step 5. Cross-check with a second design

If time data exists, compute DiD as well (DiD program: 10.00 on its
toy data). Agreement across designs with different assumptions is
worth more than precision within one.

## Step 6. Probe sensitivity

Ask how strong an unmeasured confounder must be to erase the result.
If a weak one suffices, say the finding is fragile - that sentence is
part of the analysis, not an appendix.

## Step 7. Write the conclusion with its license

"Adjusted diff -0.01, assuming no unmeasured confounding." One line,
number plus assumption, nothing more claimed than shown.

## Checkpoint table

| Step | Artifact | Check |
|---|---|---|
| 1 question table | treatment x stratum counts | confounder named |
| 2 stratum gaps | per-stratum diffs | severity held fixed |
| 3 naive gap | pooled diff | labeled bias-demo only |
| 4 adjusted | weighted diff | assumption written |
| 5 second design | DiD number | assumptions differ |
| 6 sensitivity | fragility note | breaking strength quoted |
| 7 conclusion | number + license | one sentence |

An empty cell means the step was skipped, and a skipped step voids the
causal read - the table is the analysis, not its decoration.
