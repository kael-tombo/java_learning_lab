# Reflection: Random Variables

## Write your own definitions first
Without looking: define random variable, PMF, PDF, CDF, expectation, variance. Then check which definitions secretly assumed a uniform measure or a specific family (e.g. defining variance only for normals). The right definitions must apply to a die, a waiting time and a measurement error simultaneously.

## Questions to work through
1. X ~ Uniform(−1, 1) and Y = X². Compute f_Y two ways (Jacobian over two branches; CDF differentiation) and show both give 1/(2√y) on (0,1). Which step do you find easiest to drop?
2. E[X + Y] = E[X] + E[Y] always — construct two dependent variables with E[X+Y] correct but Var(X+Y) wrong by 2Cov. How large can the error be relative to Var X + Var Y?
3. Insurance: claims are lognormal(μ = 9, σ = 1) in dollars. Mean e^{9.5} ≈ 13 360, median e⁹ ≈ 8 103. Which number sets the premium, and what does the other tell you about the tail?
4. The MGF M(t) = E[e^{tX}] determines the distribution when it exists — but a moment *sequence* need not: Stieltjes showed (1894) the lognormal is moment-indeterminate, i.e. other distributions share all its moments. What does that say about a model fitted to "mean and variance match, so we're done"?
5. A sample's mean and variance agree across two groups, but a KS test rejects. What has your two-number summary missed?

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| PMF / PDF / CDF (incl. mixed) | | | |
| E[X], Var(X), affine rules | | | |
| E[g(X)] vs g(E[X]) (Jensen) | | | |
| Transformations (Jacobian, two branches) | | | |
| Welford vs E[X²] − μ² | | | |
| Mean vs median on skewed data | | | |

## Milestones
- [ ] Reproduce 1.5 / 0.75 for binomial(3, ½) and 1 / 1/3 for Uniform(0,2) from memory
- [ ] Derive Var(aX+b) = a²Var(X) in three lines
- [ ] Compute the density of X² for X ~ Uniform(−1,1) without notes
- [ ] Explain to a teammate why a PDF may exceed 1 while a PMF may not
- [ ] Name the numerical failure of E[X²] − μ² and the fix

## Questions to answer in writing

1. Write the definition of a random variable in your own words without using the word "random." What essential feature did you keep?
2. Give an example from your own work or studies where you used a mean without checking the distribution. What could have gone wrong, and would you have been able to tell?
3. Explain to a non-statistician why a density can be greater than 1 while a probability cannot. What analogy survives scrutiny?
4. Two colleagues report "the same effect" with SDs of 2 and 20. Under what conditions are their results actually comparable? What would you ask for?

## Common blind spots this lab exposes

- **Treating SD and SE interchangeably.** The SD describes individuals; the SE describes the estimate. Quoting SD as SE makes every conclusion look 10–100× more precise.
- **Forgetting that transforming changes the mean's meaning.** E[log Y] is not log E[Y]; back-transforming a confidence interval requires transforming both endpoints, not the midpoint.
- **Using the 2-SD rule as a law of nature.** It is a property of the normal distribution; for other shapes it can understate the tails badly.
- **Assuming n is the sample size you intended.** Missing values silently reduce n; report the n actually used next to the n recruited.
