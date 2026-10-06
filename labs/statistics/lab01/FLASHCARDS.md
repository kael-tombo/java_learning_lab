# Descriptive Statistics - Flashcards (60 cards)

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | When should you quote the median instead of the mean? | Whenever the distribution is skewed or heavy-tailed, such as latency, income or claim size. |
| 2 | Why divide by n minus one? | Because the sample mean already consumed one degree of freedom, so n−1 gives an unbiased estimator of the population variance. |
| 3 | What is Welford's algorithm for? | Computing mean and variance in one pass with numerical stability that a sum-of-squares formula lacks. |
| 4 | What does IQR measure? | The spread of the middle 50% of the data, which is why it is unaffected by outliers. |
| 5 | What is the 1.5 IQR fence for? | Flagging points worth inspecting; it is a screen, not an automatic deletion rule. |
| 6 | Can two datasets share a mean and standard deviation but differ completely? | Yes; the two numbers discard shape, which is why distribution comparison is a separate tool. |
| 7 | What is Simpson's paradox in a reporting context? | An aggregate trend reverses inside every segment, because segment sizes differ. |
| 8 | Which summary works for categorical data? | The mode; means and medians are undefined without an ordering. |
| 9 | What is Mean, median, mode? | The mean uses every value and is dragged by outliers. |
| 10 | What is Population versus sample variance? | Dividing by n gives the average squared deviation of the population you have. |
| 11 | What is Welford's algorithm? | A single-pass update, mean ← mean + (x − mean)/n and M2 ← M2 + (x − mean)(x − mean_new), gives numerically stable variance. |
| 12 | What is Quantiles and IQR? | Q1, Q2, Q3 divide the ordered sample into quarters; IQR = Q3 − Q1 measures the middle 50% and is unaffected by outliers. |
| 13 | What is Shape is part of the summary? | Skewness and kurtosis tell you whether a mean describes anything. |
| 14 | What is Summaries are lossy? | Mean and standard deviation destroy shape. |
| 15 | In this lab, what does `x̄ = (1/n)Σxᵢ` mean? | Mean: uses every value, sensitive to outliers |
| 16 | In this lab, what does `median = middle order statistic` mean? | Median: robust to outliers and skew |
| 17 | In this lab, what does `s² = Σ(xᵢ − x̄)² / (n−1)` mean? | Sample variance: unbiased estimator of population variance |
| 18 | In this lab, what does `σ² = Σ(xᵢ − μ)² / n` mean? | Population variance: divisor n for a complete population |
| 19 | In this lab, what does `IQR = Q3 − Q1` mean? | Interquartile range: spread of the middle 50% |
| 20 | In this lab, what does `outlier if x < Q1 − 1.5 IQR or x > Q3 + 1.5 IQR` mean? | Fence rule: flag, do not delete automatically |
| 21 | In this lab, what does `skew = m₃ / s³` mean? | Sample skewness: sign and magnitude of asymmetry |
| 22 | In this lab, what does `M2 update: M2 += (x−mean)(x−mean_new)` mean? | Welford: stable single-pass variance |
| 23 | You see 'Latency reported as mean 240 ms ± 60 ms' in production. What is the cause and the fix? | mean plus sd on a heavy right tail Fix: report p50, p90, p99 and describe the tail |
| 24 | You see 'Variance computed by summing squares then subtracting' in production. What is the cause and the fix? | catastrophic cancellation Fix: use Welford or a two-pass algorithm |
| 25 | You see 'Sample variance divided by n' in production. What is the cause and the fix? | biased-low spread quoted as the population value Fix: use n−1 for sample variance and say which you used |
| 26 | You see 'Outliers silently removed before summarising' in production. What is the cause and the fix? | the interesting rows deleted by a fence rule Fix: flag them, inspect them, report both with and without |
| 27 | You see 'Averaging across SKUs gives 3.4 but no SKU is 3.4' in production. What is the cause and the fix? | Simpson's paradox across segments Fix: report per-segment statistics alongside the aggregate |
| 28 | You see 'Mode reported for a continuous variable' in production. What is the cause and the fix? | binning choices invented the mode Fix: use a density estimate or say the distribution is unimodal |
| 29 | Which Java API is the backbone of: streaming mean, variance and count without holding the data | `DoubleSummaryStatistics` |
| 30 | Which Java API is the backbone of: median and quartiles from a sorted copy | `Arrays.sort for order statistics` |
| 31 | Which Java API is the backbone of: frequency counting with a single pass | `Map<Double,Integer> for mode counts` |
| 32 | Which Java API is the backbone of: detecting discrete distributions before choosing a summary | `HashMap for quantile type frequencies` |
| 33 | Which Java API is the backbone of: one immutable result so summaries travel together | `record Summary(double mean, double median, double mode, double sd, double iqr, double p90)` |
| 34 | Why does Mean, median, mode matter operationally? | The mean uses every value and is dragged by outliers. |
| 35 | Why does Population versus sample variance matter operationally? | Dividing by n gives the average squared deviation of the population you have. |
| 36 | Why does Welford's algorithm matter operationally? | A single-pass update, mean ← mean + (x − mean)/n and M2 ← M2 + (x − mean)(x − mean_new), gives numerically stable variance. |
| 37 | Why does Quantiles and IQR matter operationally? | Q1, Q2, Q3 divide the ordered sample into quarters; IQR = Q3 − Q1 measures the middle 50% and is unaffected by outliers. |
| 38 | Why does Shape is part of the summary matter operationally? | Skewness and kurtosis tell you whether a mean describes anything. |
| 39 | Why does Summaries are lossy matter operationally? | Mean and standard deviation destroy shape. |
| 40 | In the Descriptive Statistics pipeline, what happens next? Load the data and check size, null count and type before sum... | Load the data and check size, null count and type before summarising anything. |
| 41 | In the Descriptive Statistics pipeline, what happens next? Compute the centre three ways: mean, median, mode, and compa... | Compute the centre three ways: mean, median, mode, and compare them. |
| 42 | In the Descriptive Statistics pipeline, what happens next? Compute dispersion with variance, standard deviation, IQR an... | Compute dispersion with variance, standard deviation, IQR and range. |
| 43 | In the Descriptive Statistics pipeline, what happens next? Inspect shape: histogram, quantiles, skewness and kurtosis.... | Inspect shape: histogram, quantiles, skewness and kurtosis. |
| 44 | In the Descriptive Statistics pipeline, what happens next? Apply the 1.5 IQR fence and inspect every flagged row rather... | Apply the 1.5 IQR fence and inspect every flagged row rather than deleting it. |
| 45 | In the Descriptive Statistics pipeline, what happens next? Report a distribution-appropriate summary: p50/p90/p99 for s... | Report a distribution-appropriate summary: p50/p90/p99 for skewed data, mean ± sd for symmetric. |
| 46 | Exercise focus: Implement the summaries | Centre and dispersion, correctly. |
| 47 | Exercise focus: Numerical stability lab | See the naive formula fail. |
| 48 | Exercise focus: Quantiles and the fence | Percentiles plus outlier screening. |
| 49 | Exercise focus: Shape statistics | Decide which summary family to use. |
| 50 | Exercise focus: Streaming statistics | One pass, no retention. |
| 51 | Exercise focus: Segment versus aggregate | Find the reversal. |
| 52 | State the Sample versus population variance result for Descriptive Statistics. | Values [2,4,5,4,5]: mean 4. Deviations [-2,0,1,0,1], sum of squares 6. Population variance 1.2, sample variance 1.5, sample sd 1.2247. Reporting 1.2 as a sample variance is the common error. |
| 53 | State the Numerical stability: why naive variance fails result for Descriptive Statistics. | Ten values around 1,000,000 with sd 100: sum x²/n is about 1e12, mean² is 1e12, and their difference is 1e4. Double precision keeps about 4 of 16 digits, so the naive variance can be off by tens of percent. Welford is exact to machine precision. |
| 54 | State the Quartiles and the IQR fence result for Descriptive Statistics. | Sorted [1..9] plus 100: Q1 = 3, Q3 = 8, IQR = 5, upper fence 15.5, so 100 is flagged. Sorted [1..100] uniformly: Q1 = 25.75, Q3 = 75.25, IQR = 49.5, upper fence 149.5, so nothing is flagged. |
| 55 | State the Percentiles versus mean plus standard deviation result for Descriptive Statistics. | Latency [10, 10, 12, 14, 900]: mean 189.2, sd 400.1, median 12, p90 738. Quoting 189 ± 400 suggests typical values near 189; the median says a typical request takes 12 ms and the tail is the problem. |
| 56 | State the Skewness and kurtosis result for Descriptive Statistics. | Latency [10,10,12,14,900]: m3 dominated by 900, skewness about 2.5, so mean is unrepresentative. Log-transforming latency gives near-zero skew and makes a mean ± sd defensible on the log scale. |
| 57 | What does skewness of 2.3 tell you? | Strong right skew: a small number of very large values pull the mean well above the median. |
| 58 | Why is a histogram alone insufficient? | Bin width is a free parameter that can create or hide modes; compare across bin choices. |
| 59 | What is a trimmed mean for? | A compromise that uses ordering to reduce outlier influence without discarding data entirely. |
| 60 | How do you report a percentile? | State the estimation convention, since different definitions interpolate differently. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
