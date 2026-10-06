# Experimentation - Quiz

## Question 1
Why is A/B testing the default for product experiments?
A) It is the only way
B) Randomized assignment isolates the treatment effect from confounders — strongest causal evidence you can ship
C) It is fastest
D) It needs no users

**Answer**: B

## Question 2
What is the null hypothesis in an A/B test?
A) The treatment helps
B) No difference between treatment and control
C) The treatment hurts
D) The treatment is random

**Answer**: B

## Question 3
Why must sample size be computed before running the test?
A) It is required
B) To power the test for a minimum detectable effect — underpowered tests miss real effects, and peeking at results inflates false positives
C) It is faster
D) It changes the metric

**Answer**: B

## Question 4
What is p-hacking?
A) A fast algorithm
B) Trying many metrics/subgroups and reporting the significant ones — inflates false discovery rate
C) A metric
D) A plot

**Answer**: B

## Question 5
Why is "peeking" at intermediate results dangerous?
A) It is slow
B) Repeated significance tests at each look inflate the chance of a false positive; use sequential testing or fix the sample size
C) It changes the metric
D) It leaks

**Answer**: B

## Question 6
What is the multiple-comparisons problem?
A) It is faster
B) Testing many hypotheses guarantees some significant results by chance — control with Bonferroni/FDR
C) It changes the metric
D) It is a metric

**Answer**: B

## Question 7
Why is unit of randomization important?
A) For aesthetics
B) Randomizing by pageview while analyzing users contaminates — effects spill between units (interference)
C) It changes the metric
D) It is faster

**Answer**: B

## Question 8
What is SRM (sample ratio mismatch)?
A) A metric
B) The observed traffic split deviates from the intended 50/50 — signals bucketing or assignment bugs
C) A type of model
D) A plot

**Answer**: B

## Question 9
Why can't you just compare last week's metrics to this week's after a change?
A) It is faster
B) Seasonality, trends, and external events confound the difference — you need a contemporaneous control
C) It changes the metric
D) It is a metric

**Answer**: B

## Question 10
What does a confidence interval around the effect tell you?
A) The p-value
B) The range of effects consistent with the data — narrower = more precision; a CI crossing zero = inconclusive
C) The power
D) The sample size

**Answer**: B

## Question 11
Why run an A/A test?
A) To test the metric
B) To validate the experimentation pipeline — assigning users randomly to identical variants should show no effect
C) To speed up
D) To save users

**Answer**: B

## Question 12
What is the minimum detectable effect?
A) The smallest effect the test can reliably distinguish from zero given power — set by sample size
B) The largest effect
C) The p-value
D) The metric

**Answer**: A

## Question 13
Why beware of novelty/primacy effects?
A) They are faster
B) A new feature may initially inflate/deflate metrics; long-run behavior differs — run long enough or use a new-vs-returning split
C) They change the metric
D) They are a model

**Answer**: B

## Question 14
Why pre-register the metric and hypothesis?
A) It is required
B) It prevents p-hacking by fixing the analysis plan before seeing results
C) It speeds up
D) It changes the metric

**Answer**: B

## Question 15
What is interference (SUTVA violation)?
A) A model failure
B) One user's treatment affects another user's outcome — randomizing individuals underestimates/overestimates the true effect
C) A metric issue
D) A plot issue

**Answer**: B
