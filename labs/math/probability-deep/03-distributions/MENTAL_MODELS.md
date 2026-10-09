# Mental Models: Probability Distributions

## 1. A Distribution Is a Shape Contract
Choosing Binomial, Poisson, Normal or Pareto is a claim about mechanism: n independent yes/no trials, rare independent events in a fixed interval, sums of many small effects, or multiplicative growth with no characteristic scale. The parameters are then the *only* free content — Binomial is fully pinned down by (n, p). Ask "what process generates this?" before "which distribution fits best?"

## 2. Density Is a Landscape, Probability Is Land Area
The density gives height; probability is the area under it. Two densities may cross without either distribution being "larger" — what matters for decisions is area over the region you care about (loss above a threshold, not which curve is higher at the mean).

## 3. Standardization: One Ruler to Compare All
Z = (X − μ)/σ turns any normal into N(0, 1). One reference bell curve carries every table (and every `1.96`); the transformation is the reason "how many standard deviations" is a universal currency for normal families — and useless for Pareto, where σ may not exist.

## 4. Conjugate Pairs Are Algebraic Fixed Points
Binomial × Beta, Poisson × Gamma, Normal × Normal: with a prior from the right family, the posterior stays in that family, updating only the parameters (lab 08). It is not magic — it is the likelihood having the same functional form as the prior.

## 5. The Exponential Is Memorylessness
If waiting time T ~ Exp(λ), then P(T > s + t | T > s) = P(T > t): having waited 10 minutes tells you nothing about the remaining wait. This is the *only* continuous distribution with that property, so a decreasing hazard in your data (long-tail failures that survive long) is direct evidence against the exponential.

## 6. Families Have Fingerprint Moments
Binomial: Var = np(1−p) ≤ np/4 (mean/4 ceiling). Poisson: Var = mean. Normal: any. Lognormal: Var = (e^{σ²} − 1)·mean², so the coefficient of variation is bounded below by √(e^{σ²} − 1). Plot sample variance against sample mean: equality suggests Poisson, sub-quadratic suggests binomial, super-quadratic suggests lognormal or negative binomial.

## Model 4: every distribution answers one question about mechanism

- *How many until the first success?* → Geometric.
- *How many successes in fixed trials?* → Binomial.
- *How many arrivals in fixed time?* → Poisson.
- *How long until k arrivals?* → Gamma/Erlang.
- *How long until the first arrival, memoryless?* → Exponential.
- *What is the max of n noisy measurements?* → Gumbel / extreme-value.
The distribution name encodes the data-collection protocol. Start from "what was physically counted or timed," and the family is usually forced — not chosen by fit.

## Model 5: support is a modeling commitment

A distribution's support (integer lattice, positive reals, whole line, simplex) silently asserts facts about the world. If you fit a normal to a bounded scale score, you have asserted that scores beyond the bounds have positive density. In a simulation this produces impossible values downstream (negative wait times). Ask: can my quantity ever be negative? zero? bounded above? Each "yes" eliminates families immediately — before any data is looked at.

## Model 6: discrete vs continuous is a resolution question, not a kind question

Counts are discrete because the measurement device stops at whole units. Mass in 3 kg batches is really continuous mass observed through a rounding instrument. The modeling choice follows the *instrument*: Poisson for events you enumerate, continuous densities for quantities you measure. Confusing the two shows up as heaping — bars at integer values in a histogram that was given continuous bins.
