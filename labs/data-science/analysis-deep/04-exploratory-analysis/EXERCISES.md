# Exploratory Analysis - Exercises

Verify each answer by running your code; expected values come from
verified reference runs.

## 1. Reproduce grouped means

Rewrite the region group-by from scratch. Expect north n=3 mean 30.0,
south n=3 mean 40.0, overall 35.0, and the n-sum check 3+3 = 6.

## 2. Reproduce the reversal

Recompute all six rates (two wards x two arms plus two pooled). Expect
90.0 vs 86.66666666666667, 73.00380228136882 vs 68.75, pooled 77.33711048158641
vs 82.57142857142857. State the winner per row: treat, treat, control.

## 3. Composition audit

From the ward counts, compute each arm's ward-A share: treated 90/353 =
25.5%, control 270/350 = 77.1%. Explain in two sentences how these shares
elect the pooled winner against the within-ward votes.

## 4. Correlation trio

Recompute with one shared routine. Expect 0.9932316263764919,
-0.9853034458841585, -0.990942442678138. Then shuffle one column (fixed seed
or fixed permutation) and show |r| collapsing - association needs alignment.

## 5. Shape drill

Sort and bin {1,1,2,2,3,3,4,9,15} at width 4 from 0. Expect sorted
[1.0,1.0,2.0,2.0,3.0,3.0,4.0,9.0,15.0], mean 4.444444444444445, median 3.0,
bins 6,1,1,1 totalling 9.

## 6. Stratify-or-pool judgment

Ward B alone (n = 263+80): is the treat lead (4.25 points) more or less
trustworthy than ward A's (3.33 points)? Answer with standard errors of the
differences (larger n wins: B's se is smaller) and name the remaining threat
(unmeasured confounders within wards).

## 7. Confounder hunt

Propose two plausible confounders behind age/spend/visits (income, urban
vs rural) and sketch the stratified display (age bands x region cells) that
would test each. No data needed - design the table.

## 8. Loop record

Write a full EDA record for the region question: question, display, numbers
with n, strata checked (none available at n = 6 - state it), conclusion,
and the one next question you would ask with ten times the data.
