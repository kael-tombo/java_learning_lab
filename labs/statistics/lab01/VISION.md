# Descriptive Statistics - Vision & Where This Is Going

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

## 1. The Future State

Descriptive statistics survives as the first line of every analysis and the last sanity check before every model. The frontier is summary statistics that carry their own uncertainty and shape, so a single number can no longer mislead.

The test of that future state is boring: a new engineer ships a change to descriptive statistics on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Centre, dispersion, shape and percentiles are reported together.
- The divisor and quantile convention are stated with the numbers.
- Flagged outliers are inspected and reported, never silently dropped.
- Segment statistics accompany every aggregate.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Summarise | Mean, median, mode, standard deviation, IQR. |
| L2 | Check shape | Skewness, kurtosis, percentiles, histogram with declared bins. |
| L3 | Stream | Stable one-pass statistics for data you cannot hold. |
| L4 | Communicate | Reports that cannot be quoted misleadingly, with segment context. |

## 4. Behaviours to Build

Compare the mean to the median first; a gap tells you shape matters. Compute variance stably. Never let a summary outlive the convention used to compute it.

## 5. Anti-Vision (the failure mode we are avoiding)

- A dashboard of means with no distributions.
- Outliers removed before anyone looked at them.
- Population variance of a sample quoted as the population value.
- An aggregate metric quoted after a segment reversal was observed.

## 6. Technology Shifts That Change the Work

1. Resistant and robust statistics as defaults in streaming analytics.
1. Summary statistics carrying uncertainty rather than point estimates.
1. Automatic shape-aware reporting that picks the summary family.
1. Streaming sketches for datasets that cannot be retained.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement the full summary set with a numerically stable variance.
- **60 days.** Add shape statistics, quantiles and the outlier fence with row inspection.
- **90 days.** Build a reporting tool whose output cannot mislead and add streaming statistics.

## 8. How To Tell You Are Actually Getting Better

- I can explain why my variance is numerically stable.
- I state the divisor and quantile convention.
- My summary would be obviously wrong to read if the shape changed.
- I have segment context for every aggregate I quote.

## 9. Principles That Should Not Change

- **Compute mean, median** Compute mean, median and mode and know when each is the honest summary
- **Distinguish population from sample variance** Distinguish population from sample variance and defend the divisor
- **Compute quantiles, IQR** Compute quantiles, IQR and detect outliers with the 1.5 IQR rule

> A summary is a claim about a distribution; the moment it is more precise than the data, it stops being useful.
