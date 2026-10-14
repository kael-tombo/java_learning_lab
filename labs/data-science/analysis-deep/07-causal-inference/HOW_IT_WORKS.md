# How Causal Reasoning Works

## 1. Start with the causal question

"Does X cause Y?" names treatment, outcome, population, and timing.
Vague questions ("does marketing work?") get rewritten until the
intervention is concrete enough to randomize in principle.

## 2. Draw the confounding map

List common causes of treatment and outcome (severity, income, season).
These are the variables a design must neutralize by randomization,
stratification, matching, or differencing - each choice recorded with
its assumption.

## 3. Prefer randomization

If an RCT is ethical and feasible, run one: randomize, pre-register the
outcome, compare means. Every quasi-experimental design below is a
fallback for when randomization is impossible, and says so.

## 4. Without randomization, stratify or match

Group units by measured confounders (exact strata) or by propensity
score, compare treated vs control within groups, then average with
population weights. Report balance tables: if covariates still differ
within groups, the adjustment failed mechanically.

## 5. With time and a control group, difference twice

Compute the DiD double difference. Plot pre-period trends for both
groups side by side - diverging pre-trends falsify parallel trends
before any causal sentence is written.

## 6. With a cutoff, zoom to the threshold

Compare outcomes just above vs just below; check nobody manipulated
their score across the line (bunching tests conceptually) since sorting
around the cutoff destroys comparability.

## 7. State the assumption in the conclusion

Every reported effect ends with its license: "assuming no unmeasured
confounding" / "assuming parallel trends" / "assuming exclusion".
A causal number without its assumption is an unfinished sentence.
