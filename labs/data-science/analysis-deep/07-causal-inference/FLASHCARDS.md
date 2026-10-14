# Flashcards - Causal Inference

Q: Correlation vs causation in one line?
A: Co-movement has three explanations: A->B, B->A, or common cause C.

Q: What is the fundamental problem of causal inference?
A: Only one of Y(1), Y(0) is observed per unit; the other is missing.

Q: Why are RCTs the gold standard?
A: Randomization balances observed and unobserved confounders in
expectation, so mean differences estimate causal effects directly.

Q: What is a confounder?
A: A common cause (or proxy) of treatment and outcome that biases naive
comparisons.

Q: State Simpson's paradox.
A: Each stratum favors one option while the pooled aggregate favors the
other, because stratum mix differs across options.

Q: What is a propensity score?
A: e(X) = P(treated | covariates X); matches units with similar
treatment probability.

Q: Matching's key assumption?
A: No unmeasured confounding - it fixes only measured covariates.

Q: Write the DiD estimator.
A: (treat_post - treat_pre) - (ctrl_post - ctrl_pre).

Q: DiD's identifying assumption?
A: Parallel trends: groups would have moved together absent treatment.

Q: Regression discontinuity idea?
A: Cutoff-assigned treatment; compare units just above vs below for a
local effect.

Q: The two IV requirements?
A: Relevance (Z moves treatment) and exclusion (Z affects outcome only
through treatment).

Q: Naive contrast = ?
A: ATE plus selection bias - the decomposition that motivates all design.

Q: Why never adjust for a collider?
A: Conditioning on a common effect induces association and creates bias.

Q: What ends every causal report?
A: The number plus its assumption, stated in the same sentence.
