# Statistics: Descriptive, Inferential, and Hypothesis Testing

## 1. Descriptive Statistics

### 1.1 Measures of Central Tendency
- Mean: average of values
- Median: middle value (sorted)
- Mode: most frequent value

### 1.2 Measures of Dispersion
- Range: max - min
- Variance: average squared deviation
- Standard deviation: √variance
- Interquartile range: Q3 - Q1

### 1.3 Five-Number Summary
- Minimum, Q1, Median, Q3, Maximum

## 2. Data Visualization

### 2.1 Charts
- Histogram: frequency distribution
- Box plot: five-number summary
- Scatter plot: bivariate data
- Pie chart: proportions

### 2.2 Correlation
- Pearson correlation coefficient: r
- r = Cov(X,Y) / (σX·σY)

## 3. Probability Distributions in Statistics

### 3.1 Sampling Distributions
- Distribution of sample statistics
- Central Limit Theorem

### 3.2 Common Distributions
- t-distribution: small samples
- Chi-square: variance
- F-distribution: ratio of variances

## 4. Hypothesis Testing

### 4.1 Null Hypothesis (H0)
Default assumption

### 4.2 Alternative Hypothesis (H1)
What we're trying to prove

### 4.3 Test Statistics
- z-test: known σ, large n
- t-test: unknown σ, small n
- chi-square: categorical data

### 4.4 Errors
- Type I: Reject H0 when true (α)
- Type II: Accept H0 when false (β)

## 5. Confidence Intervals

### 5.1 Formula
x̄ ± z(α/2) · σ/√n

### 5.2 Interpretation
If repeated sampling, (1-α)% of intervals contain true parameter

## 6. Regression Analysis

### 6.1 Simple Linear Regression
- ŷ = β₀ + β₁x
- β₁ = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)²

### 6.2 R-squared
- Proportion of variance explained
- R² = 1 - SSE/SST

## Sourced field notes (fetched Oct 2026 — verify before citing)

- StatQuest Video Index — Statistics Fundamentals (Josh Starmer) — https://statquest.org/video_index.html — "Hypothesis Testing and the Null Hypothesis", "p-values: What they are and how to interpret them", and "Confidence Intervals" entries map onto lab §4 (H0/H1, z/t/chi-square tests, Type I/II errors) and §5 (x̄ ± z·σ/√n); watch them before the hypothesis-testing drills.
- StatQuest "The Central Limit Theorem" + "Standard Deviation vs Standard Error" — https://statquest.org/video_index.html — clarifies lab §3.1 sampling distributions and the §5 confidence-interval denominator (σ/√n); use the CLT video to check when t- vs. z-intervals apply.
- StatQuest "Covariance / Pearson's Correlation" + "The Essence of Linear Regression / R-squared explained" — https://statquest.org/video_index.html — grounds lab §2.2 (r = Cov(X,Y)/(σX·σY)) and §6 (ŷ = β₀ + β₁x, R² = 1 − SSE/SST); follow the regression playlist when implementing the least-squares slope formula.
- StatQuest "Boxplots, Clearly Explained" + "Bootstrapping Part 1–2" — https://statquest.org/video_index.html — pairs with lab §1–2 (five-number summary, histograms, box plots); use the boxplot video to validate Q1/median/Q3/IQR computations on lab datasets.