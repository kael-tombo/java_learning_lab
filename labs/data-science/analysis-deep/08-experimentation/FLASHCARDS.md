# Flashcards - Experimentation

Q: Parts of an A/B test?
A: Hypothesis, randomization unit, control/treatment, goal and guardrail
metrics.

Q: Goal vs guardrail metric?
A: Goal decides ship/no-ship; guardrail health numbers can veto a win.

Q: Two-proportion SE formula?
A: sqrt(p_A(1-p_A)/n_A + p_B(1-p_B)/n_B).

Q: 95% CI for the difference?
A: d +/- 1.96*SE; excludes 0 exactly when p < 0.05.

Q: Power in one sentence?
A: Chance of detecting a true effect; bigger effect needs smaller n.

Q: SE scaling with n?
A: 1/sqrt(n) - 4x traffic halves the error bar and roughly the MDE.

Q: MDE planning constant for 80% power at 5%?
A: About 2.8*SE (1.96 significance + 0.84 power quantile).

Q: Why is peeking harmful?
A: Repeated looks multiply false-positive chances; one 0.05 test each
peek is not a 0.05 procedure.

Q: Fixes for peeking?
A: Fixed horizon decided upfront, or sequential methods with adjusted
boundaries.

Q: What is SRM?
A: Sample-ratio mismatch: arm counts diverging from the planned split,
signaling broken assignment.

Q: SRM check statistic?
A: chi2 = sum (O-E)^2/E on arm counts; small p flags.

Q: Novelty vs primacy?
A: Curiosity boost for the new vs habit drag for the old; both fade -
run past them.

Q: Randomization unit pitfall?
A: Analyzing at a finer grain than assignment understates variance.

Q: Significant but CI [0.0028, 0.0212] - ship?
A: Only if +0.28pp (the low end) still clears the ship threshold.
