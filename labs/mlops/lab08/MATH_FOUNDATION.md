# Model Monitoring & Observability - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab08  |  **Level:** Advanced

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

## Notation

| Symbol | Meaning |
|---|---|
| `PSI = Σ (a_i - b_i) ln(a_i / b_i)` | Population stability index - bucketed distribution distance |
| `KL(P||Q) = Σ P log(P/Q)` | Kullback-Leibler divergence - asymmetric, infinite when support differs |
| `JS(P,Q) = 0.5 KL(P||M) + 0.5 KL(Q||M)` | Jensen-Shannon - symmetric, bounded |
| `slope = Δpsi / Δt over window` | Drift trend - better than threshold for alerting |
| `quality(t) = metric(scores at t, labels arriving by t + lag)` | Delayed evaluation - explicit about label lag |
| `retrain if sustained_breach AND quality_drop AND interval > min_interval` | Trigger - evidence-based |

## Why the Math Matters

Drift statistics and monitoring windows are a detection problem with a label-lag constraint; the mathematics is divergence, trend estimation and the maturity of the evaluation sample.


---

## 1. Population stability index

```text
PSI = sum_i (a_i - b_i) * ln(a_i / b_i)
conventions: <0.1 stable, 0.1-0.25 moderate, >0.25 significant
add epsilon to empty buckets to avoid infinities
```

PSI is a bucketed analogue of a symmetrised KL divergence. It is convenient for alerting and sensitive to bucketing, so the numbers are only comparable when the buckets are identical across windows.

**Worked example.** Reference 0.50/0.50, current 0.55/0.45: PSI = 0.05*ln(1.1) + (-0.05)*ln(0.9) = 0.0048 + 0.0053 = 0.0101. Stable. At current 0.70/0.30, PSI = 0.20*ln(1.4) + (-0.20)*ln(0.6) = 0.0673 + 0.1022 = 0.1695, moderate.


---

## 2. Symmetric divergence choice

```text
KL(P||Q) = sum P ln(P/Q)  -> infinity if supp(Q) misses supp(P)
JS(P,Q) = 0.5 KL(P||M) + 0.5 KL(Q||M), M = (P+Q)/2 -> bounded by ln 2
```

KL's asymmetry and infinite values make it awkward for a monitoring dashboard. Jensen-Shannon is symmetric and bounded by ln 2, so every window's number means the same thing.

**Worked example.** A feature that appeared only in the current window: KL is infinite; JS is at most ln 2 = 0.693, so it produces a large finite alert rather than a broken dashboard.


---

## 3. Drift trend versus threshold

```text
psi_t for t in window
slope = (psi_last - psi_first) / window_length
alert if slope > s for k consecutive windows
```

A single crossing conflates seasonality with change. Requiring a sustained positive slope across consecutive windows separates a trend from an excursion.

**Worked example.** PSI series 0.03, 0.05, 0.06, 0.09: one crossing at 0.09, below threshold. Slope positive across 4 windows: alerts as a trend. Series 0.03, 0.28, 0.04, 0.03: a spike that returns, correctly not alerting.


---

## 4. Delayed-label evaluation

```text
quality(t) = metric(scores at time t, labels for those predictions)
available labels(t) = fraction matured by t
report quality with a maturity caveat
```

Because labels arrive late, the most recent window has almost no labels and its metric is unreliable. Any monitoring that ignores maturity will either be noisy or will silently exclude recent data.

**Worked example.** 30-day churn label with a 30-day lag: today's window has 0% of labels, so reporting today's accuracy is meaningless. The last fully matured window is 60 days back; report it as such and monitor PSI daily for the gap.


---

## Cheat Sheet

- `PSI = Σ (a_i - b_i) ln(a_i / b_i)` - Population stability index
- `KL(P||Q) = Σ P log(P/Q)` - Kullback-Leibler divergence
- `JS(P,Q) = 0.5 KL(P||M) + 0.5 KL(Q||M)` - Jensen-Shannon
- `slope = Δpsi / Δt over window` - Drift trend
- `quality(t) = metric(scores at t, labels arriving by t + lag)` - Delayed evaluation
- `retrain if sustained_breach AND quality_drop AND interval > min_interval` - Trigger

## Numerical Traps

- Comparing PSI across windows built with different bucket edges.
- Evaluating recent performance as if its labels had already arrived.
- Alerting on a single threshold crossing during a seasonal peak.
- Using KL where the support differs, producing infinite values.
- Monitoring every column instead of the features the model depends on.

## Self-Check Problems

1. Compute PSI for a reference and current distribution with 5 buckets, including the empty-bucket case.
2. Show JS is bounded by ln 2 for two extreme distributions.
3. Given 30 days of PSI, decide threshold versus slope alerting and justify it.
4. For a 30-day label lag, design a monitoring plan that reports usable quality daily.
5. Design a retrain trigger with drift, quality and a minimum interval, and show two cases where it fires and two where it does not.
