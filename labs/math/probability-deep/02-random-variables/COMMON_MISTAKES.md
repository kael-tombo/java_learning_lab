# Common Mistakes: Random Variables

### 1. Reading a PDF as a probability
If f(x) = 1.8 on [0, 0.56] then f(0.3) = 1.8 is a *density*; the probability is the integral over an interval: P(X ∈ [0.3, 0.31]) = 0.018. Densities may exceed 1 (Uniform(0, 0.4) has f = 2.5); only intervals carry probability.

### 2. Using E[X²] − (E[X])² wrong side
Variance is E[X²] − μ², not E[X²] − μ. For a fair coin with X ∈ {0,1}: E[X²] = 0.5, μ = 0.5, so Var = 0.5 − 0.25 = 0.25. E[X²] − μ would be 0 — a negative-impossible variance that only shows up when you compare with the standard deviation.

### 3. Averaging non-linear functions
E[g(X)] ≠ g(E[X]). For X ∈ {1, 2} with p = 0.5 each: E[1/X] = 0.75 but 1/E[X] = 2/3. Insurance premiums and expected utility live on the wrong side of Jensen's inequality whenever g is convex: E[X²] > (E[X])² always.

### 4. Applying linearity of variance to dependent variables
E[X + Y] = E[X] + E[Y] *always*; Var(X + Y) = Var X + Var Y only when Cov(X, Y) = 0. Portfolio risk and the variance of a paired difference both turn on the 2Cov(X, Y) term people drop.

### 5. Treating mean as typical for skewed data
X ~ Lognormal(μ = 0, σ = 1): mean = e^{0.5} ≈ 1.649, median = e⁰ = 1. The mean is dragged toward the tail. Income, file sizes and latencies are lognormal — reporting the mean as "typical" overstates the median by 65% in this case.

### 6. Forgetting the support in a transformation
For Y = X² with X ~ Uniform(−1, 1), f_Y(y) = 1/(2√y) on (0, 1) — both branches x = +√y and x = −√y contribute. Taking only one gives half the density and a total mass of 0.5 instead of 1.

### 7. Confusing PMF and CDF roles
A discrete CDF is a staircase: F(2.9) = F(2) if the jumps are at integers, and P(X = 2) = F(2) − F(2⁻) (the jump size). Plugging integer points into a continuous density formula silently returns 0.

### 8. Computing variance as E[X²] − μ² with big means
Data centered near 10⁹ with σ = 10: both terms are ~10¹⁸ and their difference (~10²) sits below double resolution of that magnitude. Use Welford's or the two-pass formula instead of the textbook one-liner.

## Self-check: can you defend each answer?

1. *"Mean 60, SD 12, so roughly 95% of patients fall between 36 and 84."* — Only if the variable is (approximately) normal. Say which assumption licenses the 2-SD rule before using it.
2. *"The random variable is 'the patient.'"* — No. The variable is a number *measured on* the patient (cholesterol level, response code). Name the possible values, then the variable.
3. *"I squared every value, so the mean doubled."* — E[X²] = Var(X) + (E[X])², not (E[X])². For X ~ N(0,1): E[X²] = 1, while (E[X])² = 0.
4. *"Lower variance always means a better estimator."* — Not if the estimator is biased. Compare mean squared error = variance + (bias)², or state why unbiasedness is required.
5. *"These two histograms look similar, so the data are normal."* — Check with a Q-Q plot and a goodness-of-fit test; visual agreement on n = 20 proves little.
