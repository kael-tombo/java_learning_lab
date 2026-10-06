# Lab 07: RLHF & Preference Optimization — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Bradley-Terry Loss and Its Gradient (E)

Implement `rewardModelLoss(rChosen, rRejected)` and its derivative w.r.t. both
inputs.

**Verify**: at `rChosen == rRejected` the loss is `ln 2` and gradients are `+/-0.5`.

---

## Exercise 2: Reward Model Training Loop (M)

Train a linear reward model on features (length, has_code_block, has_disclaimer,
lexical_diversity) over 500 synthetic preference pairs. Use logistic loss + Adam.

**Verify**: held-out pair accuracy > 0.80, and the learned weights rank "long" as
positive — demonstrating the length bias on purpose.

---

## Exercise 3: Position Bias Demonstration (M)

Split pairs so the chosen answer is always presented first. Train two reward
models (balanced vs biased data) and compare their chosen/rejected scores.

**Expected**: the biased model inflates the chosen score regardless of content.

---

## Exercise 4: Length Control (M)

Add a length penalty: `r' = r - lambda * length_tokens`. Sweep `lambda` and plot
held-out accuracy versus mean output length.

**Expected**: a visible Pareto frontier; accuracy peaks then falls.

---

## Exercise 5: GAE Advantage Estimation (M)

Implement TD residual and generalized advantage estimation over a synthetic
trajectory with rewards and values.

**Verify**: with `gamma=1, lambda=1`, `A_t = V(s_t)` (up to the final bootstrap);
with `lambda=0`, `A_t = delta_t`.

---

## Exercise 6: PPO Clipped Surrogate (M)

Implement the clipped objective and its gradient for a single sample, then a
mini-batch update over a small policy.

**Verify**: when the advantage is positive and `ratio > 1+eps`, the gradient is zero
(clipped); when negative and `ratio < 1-eps`, also zero.

---

## Exercise 7: KL-Constrained Policy Optimization (H)

Implement one gradient step maximizing `reward - beta * KL(pi||pi_ref)` on a toy
discrete policy. Sweep `beta` in {0, 0.01, 0.1, 1.0, 10.0}.

**Expected**: `beta = 0` diverges; `beta = 10` never moves from the reference.

---

## Exercise 8: Reward Hacking Experiment (H)

Construct a proxy reward that rewards keyword density and verbosity. Optimize a
policy against it and inspect samples.

**Expected**: outputs become keyword-stuffed and bloated; document 3 concrete
symptoms and the unrewarded metric that reveals them.

---

## Exercise 9: Over-Optimization Curve (H)

Run the toy optimization for many steps. Track the proxy reward **and** an
unrewarded "true quality" metric (e.g. a held-out classifier). Plot both.

**Verify**: the curves cross; the optimum is where true quality peaks, not where
reward peaks.

---

## Exercise 10: DPO Loss and Gradient (E)

Implement `dpoLoss(logpChosen, logpChosenRef, logpRejected, logpRejectedRef, beta)`
and both gradients. Verify: if policy == reference, all log-ratios are zero, loss is
`ln 2`, and gradients are `+/- beta/2` scaled by the sequence probabilities.

---

## Exercise 11: Implicit Reward Extraction (M)

Given a trained DPO policy and its frozen reference, compute
`r*(x,y) = beta * log(pi_theta/pi_ref)` for a batch of outputs and verify the
recovered rewards satisfy the Bradley-Terry ordering of the training pairs.

**Expected**: recovered rewards reproduce `P(y_w > y_l) = sigmoid(r_w - r_l)`.

---

## Exercise 12: Precomputed Log-Ratios (M)

Implement a store that precomputes `(logpChosenRef, logpRejectedRef)` once per pair,
so training only needs policy forward passes. Verify identical loss values with and
without the store.

---

## Exercise 13: ORPO-Style Odds-Ratio Loss (M)

Implement the ORPO loss (`-log sigmoid(log odds(chosen) - log odds(rejected))` plus
an SFT term) as a reference-free alternative. Compare convergence against DPO on
the same pairs.

---

## Exercise 14: SimPO / Length-Normalized Reward (M)

Implement a reference-free reward with length normalization:
`r = beta/|y| * log pi_theta(y|x) - gamma`. Train and compare to DPO.

**Expected**: similar quality with no reference model in memory.

---

## Exercise 15: Pair Quality Analysis (M)

Build tooling that reports: annotator agreement, pair difficulty (does the base model
already win?), near-duplicate rate, and the chosen-length bias in the dataset.

**Verify**: flags a dataset whose chosen answers average 2x the rejected length.

---

## Exercise 16: Judge Calibration (H)

Implement pairwise judging on a synthetic task and compare judge preference to
ground-truth labels. Report accuracy and find where it fails (verbosity, order).

---

## Stretch A: Iterative RLHF Loop (H)

Alternate: optimize -> sample from the new policy -> collect "new preferences" with
a rule-based judge -> rebuild the reward model -> repeat for 3 rounds. Track both
reward and true quality.

**Expected**: reward keeps rising; true quality plateaus then degrades without
refreshed preference data.

---

## Stretch B: KL Controller (H)

Implement an adaptive controller that adjusts `beta` to hold KL near a target. Show
total reward is higher at matched KL versus a fixed `beta`.

---

## Stretch C: Best-of-N as a Preference Proxy (H)

Implement best-of-N sampling using the reward model as the selector, then compare its
win rate against single-sample DPO output at equal token cost.

---

## Stretch D: Reward Model Ensemble (H)

Train 3 reward models on disjoint data splits, average their scores, and measure
the held-out pair accuracy gain versus a single model.

---

## Stretch E: Unlearning via Preference (H)

Construct preference pairs that prefer the *absence* of a memorized fact
("I don't know" over the memorized answer), train with DPO, and measure the fact's
recall rate before/after while checking collateral capability loss.

---

## Stretch F: Constitutional Iteration (M)

Implement a simplified critique-and-revise loop against 3 written principles:
generate -> critique citing the violated principle -> revise -> score. Compare
win rate against human-written preference pairs on the same prompts.