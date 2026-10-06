# Lab 07: RLHF & Preference Optimization — Quiz

**Q1.** The three RLHF stages in order are...
- a) RM, SFT, PPO
- b) SFT, reward model, policy optimization
- c) PPO, SFT, RM
- d) DPO, SFT, RM

**Q2.** The reward model trains on...
- a) Expert demonstrations
- b) Preference pairs with a Bradley-Terry loss
- c) Unlabeled prompts
- d) Token-level rewards only

**Q3.** Under Bradley-Terry, `P(y_w > y_l) =` ...
- a) `r(y_w) / r(y_l)`
- b) `sigmoid(r(y_w) - r(y_l))`
- c) `softmax(r(y_w))`
- d) `exp(r(y_w))`

**Q4.** Reward values are only identified up to a constant offset, so you must not...
- a) Store them
- b) Treat them as absolute quality scores across prompts
- c) Sum them
- d) Differentiate them

**Q5.** The KL penalty in RLHF exists to...
- a) Reduce model size
- b) Prevent the policy from running off to game the reward model
- c) Speed up training
- d) Reduce vocabulary size

**Q6.** `beta` too small causes...
- a) No learning
- b) Reward hacking
- c) NaN losses
- d) Slow inference

**Q7.** GAE's `lambda` controls...
- a) The learning rate
- b) The bias/variance tradeoff in advantage estimation
- c) The KL coefficient
- d) Batch size

**Q8.** PPO's clipped objective zeroes the gradient when...
- a) The advantage is zero
- b) The ratio moves beyond the clip band in the improving direction
- c) The KL exceeds beta
- d) The batch is too large

**Q9.** DPO's key operational advantage is...
- a) Better exploration
- b) No sampling, no reward model, and precomputable reference log-ratios
- c) Guaranteed safety
- d) Larger effective batch

**Q10.** In DPO the implicit reward is...
- a) `r_phi(x,y)` from a trained reward head
- b) `beta * log(pi_theta(y|x)/pi_ref(y|x)) + const`
- c) The token-level reward
- d) The KL divergence itself

**Q11.** Reward hacking typically shows up first as...
- a) Lower accuracy
- b) Length inflation and style padding
- c) Higher KL from reference
- d) Slower training

**Q12.** The reward-vs-human-satisfaction curve over optimization steps is...
- a) Monotonically increasing
- b) Inverted U
- c) Flat
- d) Random

**Q13.** Which metric is the honest guard against hacking?
- a) The reward model score
- b) A held-out metric the reward model was not trained on
- c) Training loss
- d) KL divergence

**Q14.** Annotator agreement below ~0.6 on preference pairs implies...
- a) The pairs are excellent
- b) The signal is mostly noise
- c) The reward model is too large
- d) Beta is too low

**Q15.** Position bias in reward modeling is controlled by...
- a) Using a larger reward model
- b) Randomizing the presentation order of the two answers
- c) Training longer
- d) Lowering the learning rate

**Q16.** ORPO differs from DPO in that it...
- a) Uses PPO
- b) Needs no reference model
- c) Requires a reward model
- d) Samples from the policy

**Q17.** Iterative RLHF addresses distribution drift by...
- a) Reusing the same reward model
- b) Re-collecting preferences from the current policy
- c) Increasing beta
- d) Training longer on the same pairs

**Q18.** Judge models used for win-rate evaluation must themselves be...
- a) The same model being evaluated
- b) Periodically re-validated against human preference
- c) Fine-tuned on the eval data
- d) Quantized

---

## Answers

1. **b** — behavior cloning, then preference modeling, then optimization.
2. **b** — chosen/rejected pairs with `-log sigmoid(r_w - r_l)`.
3. **b** — the Bradley-Terry link function.
4. **b** — only differences are identified.
5. **b** — the KL term anchors the policy to the reference.
6. **b** — insufficient regularization lets the policy exploit the RM.
7. **b** — higher lambda = less bias, more variance.
8. **b** — that is exactly the point of clipping.
9. **b** — DPO is offline and reference log-ratios are computed once.
10. **b** — the closed-form reward that makes the reference the KL optimum.
11. **b** — length is the cheapest thing to exploit.
12. **b** — rising reward, falling human satisfaction past the optimum.
13. **b** — an independent metric is the only way to see the divergence.
14. **b** — you cannot learn preferences the annotators disagree about.
15. **b** — randomize order so position carries no signal.
16. **b** — it adds an odds-ratio term to the SFT loss without a reference.
17. **b** — the policy drifts off the reward model's training distribution.
18. **b** — a drifted judge silently invalidates every win rate you report.

## Score Guide

16-18: ready for ai-engineering labs 07 and 09.
12-15: redo Exercises 1, 7, 10.
0-11: reread THEORY sections 2-6.