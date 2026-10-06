# neural-networks-deep — Exercises

Difficulty: **E** easy, **M** medium, **H** hard. Java 21, no dependencies. All backprop
is hand-written; all numerical checks have a tolerance.

## Module 01 — Perceptron

- [ ] **E1.1** Perceptron on a linearly separable 2D set. Plot the decision boundary as
      text; assert zero errors at convergence.
- [ ] **E1.2** XOR with a plain perceptron. Run 1,000 epochs and record that the error
      never reaches zero.
- [ ] **E1.3** Pocket algorithm on XOR. Show it finds a low-error solution and report the
      step at which the pocket last improved.
- [ ] **E1.4** Implement the convergence bound: log `||x||` for each sample and the margin
      `gamma`; compare the observed update count to `O((R/gamma)^2)`.
- [ ] **M1.5** Multiclass perceptron (one-vs-all). Report accuracy on 3 classes and the
      number of updates.
- [ ] **M1.6** Add a margin: perceptron learning only on points with `y(w'x+b) <= 1`.
      Observe the update count increase.
- [ ] **H1.7** Solve a 3D separable problem and verify the found hyperplane is not
      maximal-margin. Compare against a perceptron initialized from many random seeds and
      report the spread in margin.

## Module 02 — MLP and Backpropagation

- [ ] **E2.1** One hidden layer, sigmoid activation, squared loss. Verify the forward pass
      against hand-computed values for a 2-3-1 network.
- [ ] **E2.2** Gradients by finite differences: perturb each weight by `1e-5` and compare
      with the analytic gradient. Require relative error < 1e-6.
- [ ] **E2.3** Numerical gradient check on a 3-layer network with 20+ parameters. Report
      the maximum relative error.
- [ ] **M2.4** Depth experiment: sigmoid networks of depth 2, 5, 10, 20. Plot the gradient
      norm at each layer's output on a single batch. Show the exponential decay.
- [ ] **M2.5** Same experiment with ReLU. Show the decay is gone (linear in depth).
- [ ] **M2.6** Derive and implement the softmax cross-entropy backward pass; show the
      gradient equals `p - y` with no intermediate cancellation.
- [ ] **H2.7** Implement backprop with a generic activation interface; verify the same
      code path trains sigmoid, tanh, ReLU, and GELU networks.
- [ ] **H2.8** Overfit 10 samples with a 500-unit hidden layer. Report train loss ~0 and the
      point at which validation loss starts rising.

## Module 03 — Activation Functions

- [ ] **E3.1** Implement sigmoid, tanh, ReLU, leaky ReLU, ELU, SELU, Swish, GELU.
- [ ] **E3.2** Plot each function and its derivative on the same axes. Show sigmoid and
      tanh saturating and ReLU being piecewise constant.
- [ ] **E3.3** Verify each derivative against finite differences.
- [ ] **M3.4** Plot sigmoid's second derivative; find the max magnitude (0.25) and the
      inputs where it peaks.
- [ ] **M3.5** Activation benchmark on the same MLP across all eight activations: epochs to
      a target loss, wall time, and final test accuracy. Report a table.
- [ ] **M3.6** Dead ReLU experiment: set a large negative bias on 20% of units and measure
      how many remain at exactly zero gradient after 50 epochs.
- [ ] **H3.7** Compare Swish with beta in {0.5, 1, 2, 5} and report the effect on final
      loss and on the negative-side gradient magnitude.
- [ ] **H3.8** GELU exact versus tanh-approximation; report max absolute difference over
      `[-5, 5]`.

## Module 04 — Loss Functions

- [ ] **E4.1** MSE, MAE, Huber with delta in {0.5, 1, 2}, cross-entropy, focal with gamma
      in {0, 1, 2, 5}. Plot each against residual magnitude.
- [ ] **E4.2** Show MSE's sensitivity to a single outlier versus MAE's stability. Report
      gradient magnitudes at the outlier.
- [ ] **M4.3** Focal loss on a 1:100 imbalance. Report recall and precision at gamma 0
      versus gamma 2.
- [ ] **M4.4** Cross-entropy versus 0/1 loss as a training objective; report convergence
      steps and final accuracy.
- [ ] **M4.5** Label smoothing with eps in {0, 0.05, 0.1, 0.2}. Report accuracy,
      calibration error, and NLL.
- [ ] **M4.6** Implement triplet loss with margin and train a 4-layer embedding network on
      a synthetic dataset where clusters have known identity. Report recall@1.
- [ ] **H4.7** Contrastive loss with a temperature parameter; contrast against triplet on
      the same data and report the retrieval metric.
- [ ] **H4.8** Show that MAE's constant gradient makes final-epoch convergence slow;
      propose and measure a fix.

## Module 05 — Regularization

- [ ] **E5.1** L2 weight decay by adding to the loss; verify the gradient has the extra
      `2*lambda*W` term.
- [ ] **E5.2** Implement inverted dropout with the `1/(1-p)` scaling and verify that at
      inference no rescaling is needed.
- [ ] **E5.3** Overfit a small dataset with and without L2. Report the generalization gap.
- [ ] **M5.4** Dropout rates 0, 0.2, 0.5, 0.8. Report test accuracy; find the
      over-regularization point.
- [ ] **M5.5** Early stopping with patience 5. Report the best epoch and the test accuracy
      at that epoch versus the final epoch.
- [ ] **M5.6** Data augmentation (rotation/noise/shift) on a synthetic image task; report
      the test accuracy gain.
- [ ] **H5.7** Compare L2-in-loss under Adam versus AdamW's decoupled decay. Report the
      final weight norms; they differ meaningfully.
- [ ] **H5.8** Show regularization without a validation split makes model selection noise.
      Run model selection against test data and measure the optimism.

## Module 06 — Weight Initialization

- [ ] **E6.1** Zero initialization: train a 2-3-2-1 network and show hidden units stay
      identical. Report the weight deltas.
- [ ] **E6.2** Small random init (`0.01 * normal`) on a 20-layer net: report NaN by epoch
      3.
- [ ] **E6.3** Implement Xavier, He, and LeCun. For each, log per-layer activation
      variance and per-layer gradient variance through 20 layers.
- [ ] **M6.4** Show He init keeps forward variance constant where Xavier halves it under
      ReLU.
- [ ] **M6.5** Kaiming normal vs Kaiming uniform on a ReLU net; report both variances.
- [ ] **M6.6** Orthogonal initialization on a recurrent net; verify that a 100-step product
      of matrices does not explode or vanish.
- [ ] **H6.7** Derive Xavier from the two variance-preservation conditions and check the
      derivation numerically.
- [ ] **H6.8** Activation-scale sweep: multiply the output layer of one hidden layer by
      {0.5, 1, 2} and record how training time to threshold changes.

## Module 07 — Optimizers

- [ ] **E7.1** Plain SGD on a quadratic; show the oscillation at a high learning rate and
      the exact convergence at the analytic rate `eta = 1/L`.
- [ ] **E7.2** Momentum on the same quadratic; show the oscillation is damped.
- [ ] **E7.3** Nesterov: implement the look-ahead and compare convergence against momentum
      on an ill-conditioned quadratic.
- [ ] **E7.4** AdaGrad on a quadratic with one large-gradient direction; show the
      accumulator permanently shrinks that direction's step.
- [ ] **M7.5** RMSProp; sweep `rho` in {0.9, 0.99, 0.999}.
- [ ] **M7.6** Adam with bias correction. Show that removing bias correction makes the
      first update enormous; report the ratio.
- [ ] **M7.7** AdamW vs Adam+L2. Report final weight norm and test accuracy for both.
- [ ] **M7.8** Full benchmark on one MLP: SGD, Momentum, RMSProp, Adam, AdamW. Report
      steps to target loss, wall time, and final loss.
- [ ] **H7.9** Cosine schedule with linear warmup on a small transformer. Compare with a
      constant rate; report both curves.
- [ ] **H7.10** Gradient clipping by global norm. Show that without it a single large batch
      destroys the weights on a deep net.

## Module 08 — Normalization Layers

- [ ] **E8.1** BatchNorm forward pass on a 4-sample, 3-channel batch. Verify the normalized
      activations have zero mean and unit variance per channel.
- [ ] **E8.2** Running statistics: update in training mode, use in eval mode. Report the
      difference in output when `.eval()` is forgotten.
- [ ] **M8.3** LayerNorm over the feature dimension; verify it is independent of the other
      samples in the batch.
- [ ] **M8.4** GroupNorm with `G` in {1, 2, 4, 8} on a small CNN; report accuracy and
      batch-size sensitivity.
- [ ] **M8.5** RMSNorm versus LayerNorm: verify identical forward when gamma is initialized
      to 1 and beta to 0, then compare speed.
- [ ] **M8.6** BatchNorm with batch size 1; show the variance estimate is degenerate and
      inference still works via running statistics.
- [ ] **H8.7** Pre-norm vs post-norm residual block at depth 30 without warmup. Report the
      loss curve for each; post-norm should diverge.
- [ ] **H8.8** Backprop through BatchNorm. Verify the gradient includes the cross-sample
      covariance term — the part most hand-written implementations omit.

## Module 09 — Advanced Architectures

- [ ] **E9.1** Residual block; verify `y = F(x) + x` and that a block with `F` zeroed is
      the identity.
- [ ] **E9.2** Train a 2-layer and a 20-layer plain net; then a 20-layer residual net.
      Report the gradient norms at the input layer.
- [ ] **M9.3** DenseNet-style dense connectivity on a small net; report parameter count
      versus a plain net at equal accuracy.
- [ ] **M9.4** Inception-style parallel branches at three scales; concatenate and verify
      shape arithmetic.
- [ ] **M9.5** Squeeze-and-excitation block. Report the channel-attention weights and the
      accuracy delta when added to a baseline CNN.
- [ ] **M9.6** ConvNeXt-style block (LayerNorm, 1x1 expand, depthwise 7x7, GELU, 1x1
      project) versus a plain conv block at equal parameters.
- [ ] **H9.7** Ablation study: remove residual, remove normalization, remove GELU from the
      architecture in module 09 exercises. Report which removal hurts most.
- [ ] **H9.8** Depth vs width at fixed FLOPs on one task. Report the accuracy frontier.

## Module 10 — Model Compression

- [ ] **E10.1** L1 unstructured pruning to 50% sparsity; count nonzeros and measure the
      accuracy drop.
- [ ] **E10.2** Compare magnitude pruning by global, per-layer, and per-channel thresholds.
- [ ] **M10.3** Fine-tune after pruning to recover accuracy. Report epochs needed.
- [ ] **M10.4** Quantize weights to INT8 (symmetric, per-tensor scale). Report the
      accuracy delta and the memory reduction.
- [ ] **M10.5** FP16 quantization; report accuracy delta and memory.
- [ ] **M10.6** Post-training quantization with a calibration set; compare against
      quantization-aware training on the same net.
- [ ] **M10.7** Knowledge distillation: train a small student on the teacher's **logits**
      only. Compare against training the student on hard labels alone.
- [ ] **H10.8** Structured pruning: remove whole channels, then measure the actual
      speedup versus theoretical FLOP reduction.
- [ ] **H10.9** Combined pipeline: prune 50%, quantize INT8, distill. Report the
      cumulative accuracy and size, and identify which step cost the most.

## Cross-Module

- [ ] **X1** Full debug loop: take a deliberately broken network (wrong transpose, missing
      residual) and find each bug using only gradient norms and a gradient check.
- [ ] **X2** Ablation grid over activation x optimizer x init on one task. Report the best
      and worst combinations and whether the ranking is consistent across two tasks.
- [ ] **X3** Training-curve diagnosis: given five curves, classify each as
      underfitting/overfitting/learning-rate-too-high/unstable-init and justify.
- [ ] **X4** Reproducibility: same seed, same result. Achieve it by threading one `Random`
      through init, shuffling, and dropout.
