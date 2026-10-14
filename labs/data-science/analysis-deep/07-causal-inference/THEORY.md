# Causal Inference Theory

## 1. Correlation vs causation

Two variables move together (correlation) for three possible reasons:
A causes B, B causes A, or a third factor C drives both. Data alone
shows the co-movement; only design plus assumptions separate the cases.
"Conditioning on more variables" does not automatically help - adjusting
for a mediator or a collider can create bias rather than remove it.

## 2. Potential outcomes framing

For a binary treatment, each unit has two potential outcomes: Y(1) if
treated, Y(0) if not. The causal effect for that unit is Y(1) - Y(0),
but only one is ever observed - the fundamental problem of causal
inference. All methods estimate averages (e.g. the average treatment
effect) under assumptions that stand in for the missing half of data.

## 3. RCTs: the gold standard

Randomized controlled trials assign treatment by chance. Randomization
balances observed and unobserved confounders between arms in
expectation, so the simple difference in means estimates the average
causal effect without further adjustment. Blinding and pre-registration
protect the design from human interference and outcome shopping.

## 4. Confounding and Simpson's paradox

A confounder causes (or proxies) both treatment and outcome. Pooling
across its levels can reverse the true pattern: each subgroup favors
one option while the aggregate favors the other. CODE_DEEP_DIVE.md
verifies a concrete case (hospital success rates reversing on pooling).

## 5. Propensity-score matching (concept)

The propensity score e(X) = P(treated | covariates X) summarizes who
gets treated. Matching or stratifying treated and control units with
similar scores mimics a trial on observables. Assumption, stated
plainly: no unmeasured confounding - matching fixes only what was
measured. No theorems are claimed beyond this concept.

## 6. Difference-in-differences structure

With a treated and a control group observed before and after:

  effect = (treat_post - treat_pre) - (ctrl_post - ctrl_pre)

Subtracting the control change removes shared time trends. Assumption:
parallel trends - without treatment, both groups would have moved
together. It cannot be proven from the two data points; pre-period
history can only make it more or less plausible.

## 7. Regression discontinuity and instruments (concepts)

- Discontinuity: treatment assigned by a cutoff (exam score >= 70 gets
  tutoring). Units just above and below are nearly comparable, so the
  jump in outcomes at the cutoff estimates a local effect.
- Instruments: a variable Z (say, draft lottery) pushing treatment.
  Requirements: relevance (Z moves treatment) and exclusion (Z affects
  the outcome only through treatment). Exclusion is a subject-matter
  argument, never a statistical proof.
