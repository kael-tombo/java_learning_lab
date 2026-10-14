# Exploratory Analysis - Interview Questions

## Q1. The dashboard says control wins 82.6 to 77.3. You say treat. Defend.

A: Show stratum rates: treat leads both wards (90.0 vs 86.7; 73.0 vs 68.8)
while composition flips the pool (controls 77% in easy ward A, treated 75%
in hard ward B). The pooled number weights by mix, not merit - headline the
strata, show pooled only with the mix audit.

## Q2. Walk me through your first hour with a new dataset.

A: Question list first, then shape displays (sorted, binned, five numbers),
grouped cuts on obvious strata, pairwise correlations with n attached, and
a written loop-record per question. No models, no tests - one hour buys the
map every later method navigates by.

## Q3. r = 0.99 between ad spend and sales. Do we scale spend?

A: Not on r alone: check time order (spend precedes sales?), confounders
(season, age mix, region), and the scatter (curve? lever outlier?). Propose
the experiment or stratified analysis that would earn the causal claim -
0.99 on n = 5 here would be a memo, never a budget.

## Q4. How do you sniff a lurking Simpson in a grouped report?

A: Compare stratum composition across arms: if arm mix differs where
baseline rates differ, recompute within strata. Any sign instability kills
the pooled headline. Build the check into review: composition table beside
every pooled comparison.

## Q5. Group means 30 vs 40 on n = 3 each. Significant?

A: Suggestive, fragile: gap 10 against within-group spans of 40. Report
with n, resist tests at this n (assumptions unverifiable), and size the
follow-up: the next sample should be powered on within-group spread, not on
the observed gap.

## Q6. When do you stop exploring and start modelling?

A: When shapes are known, strata mapped, summaries chosen, and the record
names the model each question earned. Exploring forever is stalling;
modelling before the record is gambling. The record is the handoff.

## Q7. How do you present EDA to non-technical stakeholders?

A: One question per slide: display, numbers with n, strata verdict, limit.
Lead with the reversal-style headline ("wins every ward, loses pooled -
here is why") and keep the method sentence short: composition, not magic.

## Q8. EDA on 100M rows, plain JDK?

A: Stream displays (binned counters, reservoir samples for scatters),
exact grouped means in one pass, correlations via online accumulators, and
stratified cubes only for shortlisted confounders. Same loop, sampled
displays, exact aggregates.
