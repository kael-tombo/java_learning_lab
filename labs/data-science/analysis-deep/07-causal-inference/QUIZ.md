# Causal Inference - Quiz

## Question 1
Why is correlation not causation?
A) Correlations are rarely significant
B) A common cause (confounder) or reverse causation can produce the association
C) Correlation requires causation
D) It is always the treatment

**Answer**: B

## Question 2
What is a confounder?
A) The outcome
B) A variable that influences both treatment and outcome, inducing spurious association
C) The treatment
D) The instrument

**Answer**: B

## Question 3
Why is randomization the gold standard for causal evidence?
A) It is faster
B) It balances observed and unobserved confounders in expectation — treatment assignment independent of potential outcomes
C) It needs no controls
D) It guarantees significance

**Answer**: B

## Question 4
When do you need causal inference instead of prediction?
A) Never — prediction always suffices
B) When you need to estimate the effect of an intervention (what happens if we change X), not just forecast
C) Only for time series
D) For plots

**Answer**: B

## Question 5
What does a DAG (directed acyclic graph) encode?
A) The data
B) Assumed causal relationships — used to identify which variables must be controlled for (backdoor paths)
C) The model
D) The metric

**Answer**: B

## Question 6
Why is "controlling for" a variable that is caused by the treatment harmful?
A) It is always fine
B) It blocks part of the effect you want to measure (overcontrol bias)
C) It speeds up
D) It removes the outcome

**Answer**: B

## Question 7
What is the "backdoor path" criterion?
A) A path through the database
B) A set of variables that, when conditioned on, blocks every non-causal path between treatment and outcome
C) A path through the UI
D) A path through the cache

**Answer**: B

## Question 8
Why can't you estimate a causal effect from observational data without assumptions?
A) Observational data is noisy
B) The identifying assumptions (no unmeasured confounding, positivity, consistency) are untestable — they must be argued
C) It is slower
D) It changes types

**Answer**: B

## Question 9
What is an instrumental variable?
A) The outcome
B) A variable that affects the outcome only through the treatment — used when treatment is confounded
C) A confounder
D) A mediator

**Answer**: B

## Question 10
Why does difference-in-differences require parallel trends?
A) It is faster
B) The assumption that, absent treatment, treated and control groups would have moved similarly — without it the estimate is biased
C) It is required by pandas
D) It removes seasonality

**Answer**: B

## Question 11
What is selection bias?
A) A slow model
B) The sample is not representative because selection into the sample depends on the outcome or its causes
C) A type of outlier
D) A metric issue

**Answer**: B

## Question 12
Why is regression adjustment for confounders enough in an RCT?
A) It is never enough
B) Randomization already balances confounders; adjustment reduces variance, not bias
C) It is required
D) It removes leakage

**Answer**: B

## Question 13
What is survivorship bias?
A) A model that always predicts the majority class
B) Drawing conclusions from a sample that excludes failures because they didn't survive (e.g. only successful companies analyzed)
C) A slow algorithm
D) A metric issue

**Answer**: B

## Question 14
Why is "controlling for everything" bad advice?
A) It is slow
B) Conditioning on colliders or mediators opens bias paths — you must condition on the right set from a causal model
C) It removes the outcome
D) It is faster

**Answer**: B

## Question 15
What is the difference between ATE and CATE?
A) They are the same
B) ATE is the average effect over the whole population; CATE is the effect for a subgroup — CATE can differ dramatically
C) CATE is always larger
D) CATE is a metric

**Answer**: B
