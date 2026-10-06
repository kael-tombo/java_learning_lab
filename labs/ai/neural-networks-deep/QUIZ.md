# neural-networks-deep — Quiz

15 multiple-choice questions across the ten modules. Answer key and score guide at the
bottom.

## Questions

**Q1.** The perceptron convergence theorem states that convergence is guaranteed when:
- A) The learning rate is small enough
- B) The data is linearly separable
- C) The data is Gaussian
- D) There are more classes than dimensions

**Q2.** Why does a 10-layer sigmoid network suffer from vanishing gradients?
- A) The weights are too large
- B) Sigmoid's derivative peaks at 0.25, so the product of per-layer Jacobians scales by
      roughly 1e-6 by depth 10
- C) The learning rate decays too fast
- D) Squared error is not convex

**Q3.** Which initialization variance keeps forward activation variance constant through
`L` ReLU layers?
- A) `1/fan_in`
- B) `2/fan_in` (He)
- C) `2/(fan_in + fan_out)` (Xavier)
- D) Zero

**Q4.** Zero-initializing all weights in a symmetric network causes what?
- A) Immediate NaN
- B) All hidden units stay identical forever, because their gradients are identical
- C) The loss to be exactly zero
- D) The learning rate to have no effect

**Q5.** Inverted dropout at training time multiplies activations by `1/(1-p)`. Why?
- A) To reduce gradient magnitude
- B) So that the expected activation is unchanged and no rescaling is needed at inference
- C) To increase the effective learning rate
- D) To prevent dead units

**Q6.** Adam's bias correction (`m_hat = m/(1-beta1^t)`) exists because:
- A) The moments are noisy
- B) At early steps `m` and `v` are biased toward zero, which would make the first update
      far too large
- C) Adam needs it to avoid overflow
- D) It implements weight decay

**Q7.** What is the key difference between AdamW and Adam with L2 added to the loss?
- A) AdamW uses a different learning rate schedule
- B) AdamW applies weight decay decoupled from the adaptive gradient scaling, so the
      decay is not divided by `sqrt(v_hat)`
- C) AdamW does not use momentum
- D) AdamW only works with sparse gradients

**Q8.** Which normalization layer does **not** depend on batch statistics at inference, and
  is therefore the default for transformers?
- A) BatchNorm
- B) LayerNorm
- C) Batch renorm
- D) Weight standardization

**Q9.** Why is pre-norm preferred over post-norm in deep transformers?
- A) It is faster
- B) The residual path is clean, so gradients flow through the identity without passing
      through normalization at every layer
- C) Post-norm cannot be implemented
- D) It uses fewer parameters

**Q10.** Focal loss with `gamma = 2` is most useful when:
- A) The classes are balanced
- B) There is heavy class imbalance and many easy negatives dominate the gradient
- C) The labels are continuous
- D) The model is overfitting

**Q11.** A training loss that decreases smoothly but validation loss rises after epoch 12
  indicates:
- A) Learning rate too high
- B) Overfitting; add regularization or early stop
- C) Bad initialization
- D) Vanishing gradients

**Q12.** Why does a residual connection make very deep networks trainable?
- A) It reduces the parameter count
- B) The effective Jacobian becomes `(I + J_F)`, closer to identity than to a vanishing
      product, so gradients reach early layers undiminished
- C) It normalizes activations
- D) It removes the need for nonlinear activations

**Q13.** Forgetting to call `.eval()` on a BatchNorm network causes:
- A) No effect at all
- B) Inference to use batch statistics instead of running statistics, giving silently
      different and usually worse outputs
- C) A crash
- D) The learning rate to change

**Q14.** Gradient clipping by global norm primarily protects against:
- A) Slow convergence
- B) A single batch producing an enormous update that destroys the weights
- C) Overfitting
- D) Small batches

**Q15.** After structured pruning of whole channels, actual inference speedup is often less
  than the FLOP reduction suggests. Why?
- A) Pruning introduces numerical error
- B) Removing channels leaves dense, poorly-utilized memory layouts; real speedup needs
      kernel support and layout change
- C) Structured pruning cannot reduce FLOPs
- D) Speedup depends only on parameter count

## Answer Key

| Q | Answer | Why |
|---|--------|-----|
| 1 | B | Separability is the theorem's hypothesis; the learning rate only affects speed. |
| 2 | B | `0.25^10 ≈ 1e-6` per-path decay, compounded with weight norms. |
| 3 | B | ReLU halves forward variance; He doubles the gain to compensate. |
| 4 | B | Identical units receive identical gradients and stay identical. |
| 5 | B | The scaling preserves the expectation so inference is a plain forward pass. |
| 6 | B | Without correction the step at `t=1` is roughly `g/eps`, orders of magnitude too large. |
| 7 | B | Decoupling prevents the adaptive denominator from altering the effective decay rate. |
| 8 | B | LayerNorm normalizes within a sample, so batch composition cannot change it. |
| 9 | B | Pre-norm keeps the residual path free of normalization, so gradients do not traverse it. |
| 10 | B | `(1-p_t)^gamma` suppresses easy examples, letting rare hard ones dominate. |
| 11 | B | Classic overfitting signature; the fix is capacity control, not a schedule change. |
| 12 | B | `I + J_F` has eigenvalues shifted toward 1, which is the gradient-path property. |
| 13 | B | Training mode recomputes batch statistics, changing the normalization at inference. |
| 14 | B | Clipping caps the step norm, containing rare huge-gradient batches. |
| 15 | B | Arithmetic savings do not translate to wall-clock without layout and kernel changes. |

## Score Guide

| Score | Verdict |
|-------|---------|
| 15/15 | Ready to design and debug architectures. Push into module 09 and 10. |
| 12-14 | Solid grasp. Revisit your misses against THEORY.md sections. |
| 9-11 | Knows the pieces, not the interactions. Redo Q2, Q5, Q7, Q9. |
| 6-8 | Re-read THEORY.md, then redo EXERCISES for modules 02, 06, 08. |
| 0-5 | Restart with modules 01, 02, 03 before touching optimizers. |

## Scoring Notes

- Single answer per question; no partial credit.
- Retake only after re-reading the relevant module.
- Mastery threshold: 13/15 with no misses on Q3, Q5, Q7, Q9, Q12.
