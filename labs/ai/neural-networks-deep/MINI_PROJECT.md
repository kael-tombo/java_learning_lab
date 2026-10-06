# neural-networks-deep — Mini Project

## Project: A Neural Network Library in Java 21

Build a small but complete neural network library from the perceptron up: an MLP with a
hand-written backward pass, eight activations, five initializers, eight optimizers, four
normalization layers, a residual architecture, and a compression suite — with a gradient
checker gating every component.

## Goal

A `Main` that trains several networks on synthetic and small real tasks, runs a gradient
check on every model, produces training curves, and writes `REPORT.md` with an ablation
study. No frameworks, no dependencies.

## Requirements

### Phase 1: Core and Gradient Checker
- [ ] `Mat`: matmul, transpose, flat layout, norms.
- [ ] `Rng`: a seeded generator (implement xorshift; `java.util.Random` will not do) so
      results are reproducible across platforms.
- [ ] `GradCheck` with central differences; a test that fails the build if any parameter's
      relative error exceeds 1e-6.

### Phase 2: Perceptron
- [ ] Binary perceptron with learning rate and margin option.
- [ ] Multiclass one-vs-all.
- [ ] Pocket algorithm on XOR.
- [ ] Convergence-bound logging: `R`, `gamma`, observed updates versus `O((R/gamma)^2)`.

### Phase 3: MLP Forward
- [ ] Configurable layer sizes, linear output layer.
- [ ] Eight activations with cached pre-activations.
- [ ] Mini-batch sampler with a seeded shuffle.
- [ ] Forward-pass verification against hand-computed values for a 2-3-1 net.

### Phase 4: MLP Backward
- [ ] Backward pass for squared, cross-entropy, Huber, and focal losses.
- [ ] Gradient check green on all four losses, all eight activations, three depths.
- [ ] Gradient-norm-per-layer logging used as the debugging instrument for the rest of
      the project.

### Phase 5: Activations
- [ ] sigmoid, tanh, ReLU, leaky ReLU, ELU, SELU, Swish (sweep beta), GELU (exact and
      tanh-approx, with the difference reported).
- [ ] Derivative plot data exported as text.
- [ ] Benchmark table: epochs to target loss, wall time, final accuracy.

### Phase 6: Initialization
- [ ] zero, small-random, Xavier, He, LeCun, orthogonal.
- [ ] Per-layer activation and gradient variance logging through 20 layers.
- [ ] Demonstrate: zero init leaves hidden units identical; small random NaNs by epoch 3;
      He holds variance where Xavier halves it.

### Phase 7: Optimizers and Schedules
- [ ] SGD, Momentum, Nesterov, AdaGrad, RMSProp, Adam, AdamW.
- [ ] Constant, step decay, cosine, linear warmup + cosine.
- [ ] Adam bias-correction demonstration with and without.
- [ ] AdamW vs Adam+L2: report final weight norm and test accuracy for both.
- [ ] Global-norm gradient clipping.

### Phase 8: Normalization
- [ ] BatchNorm (train and eval modes), LayerNorm, GroupNorm, RMSNorm.
- [ ] BatchNorm backward with the covariance terms, gradient-checked.
- [ ] Demonstrate the forgot-`.eval()` failure: report output difference.
- [ ] Pre-norm vs post-norm residual block at depth 30.

### Phase 9: Architectures
- [ ] Residual block with a shape assertion; a block with `F` zeroed verified as identity.
- [ ] Dense connectivity variant and Inception-style parallel branches.
- [ ] Squeeze-and-excitation channel attention.
- [ ] Depth-vs-width study at fixed FLOPs.

### Phase 10: Compression
- [ ] Global, per-layer, and per-channel magnitude pruning with fine-tuning recovery.
- [ ] INT8 per-channel and FP16 quantization with accuracy deltas.
- [ ] Post-training versus quantization-aware training on the same net.
- [ ] Knowledge distillation from logits versus hard-label training.
- [ ] Cumulative compression pipeline with per-step accuracy attribution.

### Phase 11: Ablation Study
- [ ] Grid over activation x optimizer x init x normalization on one task.
- [ ] Second task to test whether rankings transfer.
- [ ] Report the best and worst configurations and rank consistency.

### Phase 12: Report
- [ ] Training curves as text plots.
- [ ] `REPORT.md`.

## Directory Layout

```
neural-networks-deep/
  src/com/ailab/nn/
    core/{Mat,Rng,GradCheck,Curves}.java
    activations/{Act,DAct}.java
    init/Init.java
    optim/{Optimizer,Sgd,Momentum,Nesterov,Adagrad,Rmsprop,Adam,AdamW,Schedules}.java
    losses/Losses.java
    layers/{Dense,Flatten,Residual,SqueezeExcite}.java
    norm/{BatchNorm,LayerNorm,RmsNorm,GroupNorm}.java
    models/{Perceptron,Mlp,Resnet,Distiller}.java
    compress/{Prune,Quantize,Distill}.java
    Main.java
  out/curves.txt
  out/ablation.csv
  REPORT.md
```

## Milestones

1. **M1** — matrix core, seeded RNG, gradient checker.
2. **M2** — perceptron and pocket algorithm on XOR.
3. **M3** — MLP forward, hand-verified.
4. **M4** — MLP backward, gradient check green on 4 losses x 8 activations x 3 depths.
5. **M5** — eight activations with derivative verification and a benchmark table.
6. **M6** — six initializers with per-layer variance logs.
7. **M7** — eight optimizers plus four schedules, with the Adam bias-correction demo.
8. **M8** — four normalization layers, gradient-checked, eval-mode bug demonstrated.
9. **M9** — residual, dense, Inception, SENet blocks.
10. **M10** — pruning suite with recovery fine-tuning.
11. **M11** — INT8 and FP16 quantization, PTQ vs QAT.
12. **M12** — distillation beating hard-label training on the same student.
13. **M13** — ablation grid across two tasks.
14. **M14** — `REPORT.md` written.

## Acceptance Criteria

- [ ] Gradient check passes at relative error below 1e-6 for every loss/activation/depth.
- [ ] Re-running `Main` produces byte-identical output (seeded RNG everywhere, no
      `java.util.Random`).
- [ ] Zero initialization leaves hidden units bit-identical; demonstrated and reported.
- [ ] He init holds activation variance across 20 ReLU layers; Xavier halves it.
- [ ] Adam without bias correction produces a visibly larger first step.
- [ ] AdamW's final weight norm differs measurably from Adam + L2.
- [ ] BatchNorm backward matches the finite-difference gradient including covariance terms.
- [ ] The `.eval()` omission changes outputs measurably.
- [ ] Pre-norm trains at depth 30 where post-norm diverges without warmup.
- [ ] A residual block with `F` zeroed is exactly the identity.
- [ ] Pruning to 50% sparsity costs less than 1 point of accuracy after fine-tuning.
- [ ] INT8 per-channel quantization costs less than 0.5 points.
- [ ] Distillation beats hard-label training on the same student architecture.
- [ ] Every compression step reports its accuracy and size delta separately.

## Stretch Goals

- [ ] Convolutional layer with im2col and a hand-written backward, gradient-checked.
- [ ] GRU cell forward and backward on a sequence task.
- [ ] A small transformer block (MHA + pre-norm + FFN) trained from scratch.
- [ ] Learning-rate range test: find the largest stable rate by doubling until divergence.
- [ ] Label smoothing and focal loss in the ablation grid.
- [ ] Gradient-check failure used deliberately to localize an injected bug.
- [ ] Checkpointing and resume with identical final loss.
- [ ] Mixed precision with a loss-scaling scheme.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Loss becomes NaN by epoch 3 | Initialization too large, or missing normalization |
| Hidden units identical | Zero or symmetric initialization |
| Gradient check fails on layer 3 only | Transposed weight, or a mask using `>=` instead of `>` |
| Train loss fine, validation poor | Overfitting; regularization is the answer, not more capacity |
| Divergence with post-norm at depth 30 | Pre-norm, or add warmup |
| BatchNorm works in training, breaks in serving | `.eval()` not called, so running stats unused |
| AdamW behaves like a weaker regularizer than expected | Decay placed inside the adaptive denominator |
| Swish trains slightly worse than expected | Derivative missing the `beta*x` term |
| Pruning improves validation but hurts test | Pruning acted as regularization; re-tune the rest |
| INT8 accuracy collapse | Per-tensor scale with one outlier channel |
| Distillation no better than hard labels | Temperature too low; the dark knowledge is lost |
| Results differ between runs | Unseeded randomness anywhere in the pipeline |

## Definition of Done

`REPORT.md` contains: the gradient-check results as a matrix of loss x activation x depth
with maximum relative errors, the perceptron convergence data against the theoretical bound,
per-layer activation and gradient variance under each initializer over 20 layers, the
activation benchmark table, the optimizer comparison (steps to target, wall time, final
loss, final weight norm), the Adam bias-correction demonstration, the AdamW versus Adam+L2
comparison, the normalization layer results including the eval-mode failure measurement and
the pre-norm/post-norm curves at depth 30, the architecture ablations, the compression
pipeline with per-step accuracy and size deltas, the distillation result, the two-task
ablation grid with rank consistency, and a list of known failure modes with mitigations.
