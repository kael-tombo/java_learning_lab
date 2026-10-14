# Exploratory Analysis - Flashcards

## Q1. Name the five EDA loop steps.

A: Question, display, summarize, stratify, record - then repeat. Products
are understanding and hypotheses, not verdicts.

## Q2. What are the grouped means and checks?

A: North 30.0 (n=3), south 40.0 (n=3), overall 35.0; checks: 3+3 = 6, and
35.0 lies between the group means.

## Q3. State the Simpson numbers.

A: A: 90.0 vs 86.7 (treat leads). B: 73.0 vs 68.8 (treat leads). Pooled:
77.34 vs 82.57 (control leads). Mix decides the pool.

## Q4. What mechanism flips the pooled winner?

A: Different composition: controls concentrate in easy ward A (270/350),
treated in hard ward B (263/353). Pooled weights differ per arm.

## Q5. What is the reporting rule for pooled rates?

A: Never alone: stratum rates beside pooled, with the mix explanation.
Unstable sign means report strata, pool never.

## Q6. The three correlations?

A: age/spend 0.9932316263764919, age/visits -0.9853034458841585,
spend/visits -0.990942442678138. Strong, symmetric, causally mute.

## Q7. Why can't r show causation?

A: r is symmetric (r_xy = r_yx, a cosine) and atemporal; causation needs
time order, mechanism, and confounder control by design.

## Q8. Shape demo numbers?

A: Sorted [1,1,2,2,3,3,4,9,15], mean 4.444444444444445, median 3.0, bins
6,1,1,1: right skew with two strays, three signals agreeing.

## Q9. What makes a group mean trustworthy?

A: Its n, the overall-mean-between-groups check, and survival under
stratification - a mean of 3 is suggestive, never conclusive.

## Q10. What ends each EDA loop?

A: A written record: question, display, numbers with n, strata checked,
and what would change the conclusion.

## Q11. Who founded EDA and when?

A: John Tukey, "Exploratory Data Analysis", 1977: displays and resistant
summaries before models.

## Q12. Who named Simpson's paradox, when?

A: E. H. Simpson, 1951 paper on interaction in contingency tables:
aggregation can reverse within-stratum association.

## Q13. What does Anscombe 1973 license in EDA?

A: Distrusting any summary - even r 0.99 - until a display confirms the
claimed form.

## Q14. Small n, loud what?

A: Loud humility: vivid but fragile - report n attached, fragility named,
headlines refused.
