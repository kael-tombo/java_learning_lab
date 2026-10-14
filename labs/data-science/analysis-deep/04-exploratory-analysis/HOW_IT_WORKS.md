# Exploratory Analysis - How It Works

## The loop on the region data

Question ("do regions differ?"), display (values per region), summarize
(means 30.0 vs 40.0 with n = 3 each), stratify (nothing further to split at
n = 6 - record that limit), record (north lower, small n, overall 35.0
between the groups). One loop, five steps, findings plus limits written
down together.

## Shape reading on the nine values

Sort: [1,1,2,2,3,3,4,9,15]. Bin at width 4: [0,4) holds 6, then three bins
hold 1 each. Mean 4.444444444444445 vs median 3.0. Three independent
signals (gap pattern, isolated bars, mean/median gap) converge on right
skew with two strays - any single signal could be noise, three agreeing
are a finding.

## The paradox check, mechanically

Compute stratum rates first (90.0 vs 86.7; 73.0 vs 68.8), then pooled rates
(77.34 vs 82.57), then composition (treated 90+263, control 270+80).
Direction flips between strata and pool: paradox confirmed. The fix is
presenting stratum rates as the headline with pooled shown only beside the
mix explanation - never pooled alone.

## Correlation triage on the five customers

Compute all three pairwise r values in one pass each: 0.9932316263764919,
-0.9853034458841585, -0.990942442678138. Note the sign pattern (age up,
spend up, visits down) suggests one latent driver, age, rather than three
separate stories. Downgrade "spend drives visits" to "both track age until
a design says otherwise."

## Recording standard

Each loop ends with: question, display choice, numbers with n, strata
checked, and what would change the conclusion. Unexamined strata and
unstated n are the two debts EDA must never carry into modelling.

## What breaks without the loop

Skip display and the strays 9 and 15 enter a model as regulars. Skip
stratify and the pooled 82.57-vs-77.34 headline ships. Skip record and next
quarter nobody knows why ward B was oversampled. Each omission has a price;
the loop is priced in minutes against decisions worth far more.
