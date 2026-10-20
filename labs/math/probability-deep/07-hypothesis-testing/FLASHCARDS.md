# Flashcards — Hypothesis Testing

## Definition Cards

### Card 1
**Front**: Define Type I error and the size of a test.
**Back**: Type I = rejecting H0 when H0 holds; size
alpha = P(T ∈ R | H0) is computed under the null only, and is fixed
before data arrive.

### Card 2
**Front**: Define Type II error, beta, and power.
**Back**: Type II = failing to reject a false H0; beta = P(T ∉ R | H1);
power = 1 − beta, a function of the true parameter value, not a
constant.

### Card 3
**Front**: State the p-value definition correctly.
**Back**: The probability under H0 of a result at least as extreme as
the observed one (ordering fixed by the test statistic); it is NOT the
probability that H0 is true.

### Card 4
**Front**: What is a rejection region?
**Back**: A pre-declared subset R of the test statistic's values; the
test rejects exactly when T lands in R.

### Card 5
**Front**: What makes a permutation test exact?
**Back**: Under H0 exchangeability, every relabeling is equally likely,
so the p-value equals an exact count of qualifying labelings over the
total C(n+m, n) — no distribution assumptions at all.

## Judge-the-Number Cards

### Card 6
**Front**: n = 10 fair flips, region {k <= 1} ∪ {k >= 9}: alpha?
**Back**: 22/1024 = 11/512 ≈ 0.0215 — a coefficient sum, machine-exact.

### Card 7
**Front**: Same model, one-sided region {k >= 8}: alpha?
**Back**: 56/1024 = 7/128 ≈ 0.0547 — about 28/11 times the two-sided
budget.

### Card 8
**Front**: Testing p = 1/2 vs true p = 3/10 at that region: beta and
power?
**Back**: beta = 4252739841/5000000000 = 0.8505479682; power =
0.1494520318; identical at p = 7/10 (mirror exactness).

### Card 9
**Front**: 3-vs-3 permutation: spaces, one-sided and two-sided p for
mean difference 3?
**Back**: 20 labelings; 1 at d >= 3 → 1/20; 2 at |d| >= 3 → 1/10.

### Card 10
**Front**: 4-vs-4 permutation: label space and two-sided p for
difference 4?
**Back**: C(8,4) = 70 labelings; two extremes qualify → 2/70 = 1/35.

### Card 11
**Front**: Two coins (one fair, one double-headed) — one head
observed: posterior on the loaded coin?
**Back**: P(loaded | heads) = (1/2)/(3/4) = 2/3 — Bayes
denominator built from total probability.

### Card 12
**Front**: Which skill does the lab train on tiny samples?
**Back**: Collecting exact fractions (coefficient sums and label
counts) instead of approximations — every p-value here is a ratio of
counted objects.
