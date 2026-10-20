# Multi-Task Learning — Quiz

Answers stated directly; standard formulations only.

**Q1. What is the MTL objective's canonical form?**
A: A weighted sum `L = sum_t w_t * L_t` of per-task losses over shared parameters.

**Q2. Why does naive equal weighting misbehave?**
A: Loss scales differ between task families (MSE vs cross-entropy); the memo conventional
pitfall is that the biggest-magnitude term dominates the shared update.

**Q3. What does uncertainty weighting trade?**
A: It treats per-task noise sigma as learned and multiplies each loss by `1/(2 sigma^2)`
(plus the `log sigma` carelessness guard) — noisy tasks are down-weighted automatically.

**Q4. What does gradient surgery (the projection rule) do that balancing cannot?**
A: Reweighting only rescales directions; projection removes a conflicting gradient's
component along another task's gradient, aiming orthogonal after surgery.

**Q5. When do we say negative transfer is happening?**
A: One task's performance degrades while others improve under shared training — observed
by per-task loss trajectories separating in the wrong direction.

**Q6. In our two-head example, which number demonstrates domination?**
A: `|gA|/|gB| = 21.0611` at `(0.5, 0.5)` initial weights: the regression gradient norm is
21x the classifier's.

**Q7. State one per-task speed signal used by GradNorm-style methods.**
A: Ratio of a task's current loss to its own initial value (relative slope), used to push
weights toward tasks lagging their own trajectory.

**Q8. What does the learner share in the snippet architecture?**
A: One set of parameters `(w1, w2)`: the "shared trunk" is the whole model here; heads
differ only by which of the two losses' gradients they contribute.

**Q9. Write the per-task gradient norm under weighting.**
A: `||w_t * g_t|| = w_t * ||g_t||` — weights rescale magnitudes, never directions, which is
exactly the observation of Exercise runs.

**Q10. Name two symptoms of negative transfer.**
A: A head's loss flattening while the others improve, or a head's loss rising under the
joint step; both visible in per-task loss trajectories.

**Q11. When can the projection rule be the wrong tool?**
A: With mild conflicts, surgery removes too much of a task's push; balancing first and
surgery only for hard conflicts is the practical escalation order.
