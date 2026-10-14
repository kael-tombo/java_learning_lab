# Exploratory Analysis - Theory

## 1. The EDA workflow (after Tukey)

Exploratory data analysis iterates: pose a question, display the relevant
data, summarize robustly, stratify by plausible confounders, record what was
seen - then repeat. It precedes modelling and confirmatory testing, and its
products are understanding and hypotheses, not p-values. The loop is
skeptical by design: every display is an attempt to be surprised.

## 2. Distribution shape reading

From a sorted column and its bins, read center (median vs mean gap),
spread (bulk width vs fences), gaps (empty bins), and strays (isolated
values). The shape demo sorts to [1,1,2,2,3,3,4,9,15]: bulk 1-4, gap, then
9 and 15. Mean 4.444444444444445 exceeds median 3.0: right skew confirmed
two ways (gap pattern plus mean/median gap). Shape vocabulary - symmetric,
skewed, bimodal, heavy-tailed - routes every later choice of summary and
model.

## 3. Grouped aggregation and its sanity checks

Split-apply-combine: partition rows by a key (region), apply a summary
(mean), combine into a comparison (30.0 vs 40.0). Three checks are
mandatory: group n values sum to total n (3+3 = 6); the overall mean (35.0)
lies between the group means; and group sizes are reported, because a mean
of 3 carries different weight than a mean of 3,000. Unguarded group-bys on
tiny cells manufacture confident-sounding noise.

## 4. Simpson's paradox, concretely

Treatment beats control in ward A (90.0% vs 86.7%) and in ward B (73.0% vs
68.8%), yet pooled treatment (273/353 = 77.34%) loses to pooled control
(289/350 = 82.57%). Mechanism: ward A (high success for everyone) holds
most controls (270 of 350), while ward B (low success) holds most treated
(263 of 353) - group mix, not efficacy, decides the pooled rate. Whenever
strata differ in both composition and baseline rate, pooled comparisons are
guilty until stratified.

## 5. Correlation versus causation

Age/spend r 0.99, age/visits r -0.99, spend/visits r -0.99: strong,
mutually consistent, and causally mute. Correlation is symmetric and
atemporal; causation needs time order, a mechanism, and confounder control
(design, stratification, or experiment). EDA's job is to surface candidate
relationships with their confounders attached - age here explains all three
pairwise links - never to certify causes.
