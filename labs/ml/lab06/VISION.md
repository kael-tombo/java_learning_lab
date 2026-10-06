# Naive Bayes Classifier - Vision & Where This Is Going

**Track:** ml  |  **Lab:** lab06  |  **Level:** Intermediate

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

Naive Bayes survives where the count model is genuinely the right shape: text, spam, document routing and any high-dimensional sparse problem with limited labels. The frontier is not the base classifier but its hybrids — NB-SVM, complement NB and calibration wrappers — which inherit its speed while borrowing discriminative strength.

The test of that future state is boring: a new engineer ships a change to naive bayes classifier on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- The variant is chosen explicitly and justified by the feature representation.
- Scoring is log-space everywhere and smoothing is on by default with a documented alpha.
- Per-class precision/recall/F1 is reported because text is imbalanced.
- Any published probability has been calibrated, or the score is labelled a score.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Classify | Implement multinomial NB with smoothing and report accuracy. |
| L2 | Be rigorous | Log space, in-fold vectoriser, per-class metrics, alpha swept. |
| L3 | Calibrate | Platt-scale the log-odds and report the ECE change. |
| L4 | Extend | Complement NB, NB-SVM, and a streaming incremental fit. |

## 4. Behaviours to Build

Match the variant to the data representation. Treat the naive assumption as a documented bias. Never publish an uncalibrated posterior.

## 5. Anti-Vision (the failure mode we are avoiding)

- Inverting the conditional by accident: P(x|y) treated as P(y|x).
- Smoothing switched off 'to keep it pure'.
- Accuracy quoted on a corpus with 2% positives.
- A vocabulary refit on the full corpus inside a CV loop.

## 6. Technology Shifts That Change the Work

1. NB-SVM and log-count ratio features blending generative priors with discriminative training.
1. Complement and one-vs-rest NB variants for imbalanced text.
1. FastText-style linear models with subword features as the practical successor for text classification.
1. Calibration as a standard pipeline stage rather than an afterthought.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement multinomial NB in log space and prove the underflow it avoids.
- **60 days.** Implement all three variants and compare them on data suited to each.
- **90 days.** Add Platt calibration, a streaming fit, and an explainability endpoint showing per-token contributions.

## 8. How To Tell You Are Actually Getting Better

- I can state which independence assumption each variant makes.
- My scores are computed in log space and I can prove it.
- I can measure my calibration error before and after.
- I report macro-F1, not just accuracy.

## 9. Principles That Should Not Change

- **State the three Naive Bayes variants** State the three Naive Bayes variants and what each assumes about feature type
- **Derive Gaussian, multinomial** Derive Gaussian, multinomial and Bernoulli likelihoods
- **Explain why the naive step is a modelling choice, not an implementation shortcut** Explain why the naive step is a modelling choice, not an implementation shortcut

> A count model you understand completely is worth more than a complex model whose assumptions you cannot state.
