# neural-networks-deep — Flashcards

60 rows. Cover the answer, recall it, then check. Last column is the module.

| # | Question | Answer | Module |
|---|----------|--------|--------|
| 1 | Perceptron rule? | `w <- w + alpha * y * x` on misclassified points | 01 |
| 2 | Perceptron convergence theorem? | Finite convergence iff the data is linearly separable | 01 |
| 3 | Update-count bound? | `O((R/gamma)^2)`, `R` bounds `||x||`, `gamma` is the margin | 01 |
| 4 | XOR and the perceptron? | Not separable, so it cycles forever; the reason hidden layers exist | 01 |
| 5 | Pocket algorithm? | Keep the best-weight-so-far; the practical non-separable variant | 01 |
| 6 | Forward pass of an MLP? | `h_l = phi(W_l h_{l-1} + b_l)` composed across layers | 02 |
| 7 | Backprop gradient of `W_l`? | `delta_l h_{l-1}'` | 02 |
| 8 | `delta_l` recurrence? | `(W_{l+1})' delta_{l+1} .* phi'(z_l)` | 02 |
| 9 | Backprop cost? | `O(L)` forward and backward, not `O(L^2)` from per-layer derivatives | 02 |
| 10 | Vanishing gradient cause? | `prod_l W_l diag(phi'_l)` decays when both factors are below 1 | 02 |
| 11 | Sigmoid max derivative? | 0.25, at inputs near 0 | 02 |
| 12 | Softmax + CE gradient? | `p - y` against the logits — stable and cancellation-free | 02 |
| 13 | Gradient check? | Finite differences at `eps ~ 1e-5`; relative error below 1e-6 | 02 |
| 14 | Sigmoid? | `1/(1+e^-x)`; saturating, not zero-centred | 03 |
| 15 | Tanh vs sigmoid? | Zero-centred but still saturating | 03 |
| 16 | ReLU? | `max(0,x)`; non-saturating, cheap, dies on always-negative inputs | 03 |
| 17 | Leaky ReLU? | `max(a x, x)`, `a = 0.01`; reduces dying units | 03 |
| 18 | ELU and SELU? | Negative-side curvature (negative mean); SELU self-normalizes with correct init | 03 |
| 19 | Swish? | `x * sigmoid(beta x)`; smooth, gates like ReLU but differentiably | 03 |
| 20 | GELU? | `x * Phi(x)`; the transformer default | 03 |
| 21 | Activation choice rule? | ReLU-family for CNNs, GELU for transformers, sigmoid only for binary output | 03 |
| 22 | Dead ReLU cause? | An input that stays negative, so its gradient is zero forever | 03 |
| 23 | MSE weakness? | Quadratic penalty makes it hypersensitive to outliers | 04 |
| 24 | MAE weakness? | Constant gradient and non-differentiable at 0; converges slowly at the end | 04 |
| 25 | Huber? | Quadratic below delta, linear above — the standard compromise | 04 |
| 26 | Focal loss? | `(1-p_t)^gamma * CE`; suppresses easy examples under imbalance | 04 |
| 27 | Label smoothing effect? | Softer targets, worse NLL, usually better accuracy and calibration | 04 |
| 28 | Triplet loss? | Pull an anchor to its positive, push the negative past a margin | 04 |
| 29 | Distillation signal? | Teacher's full logit distribution carries more than the hard label | 04 |
| 30 | L2 penalty? | `+ lambda ||W||^2`; equivalent to a Gaussian prior | 05 |
| 31 | Inverted dropout? | Scale by `1/(1-p)` during training so inference needs no rescaling | 05 |
| 32 | Dropout's intuition? | An implicit ensemble of subnetworks; also noise-regularized gradient | 05 |
| 33 | Early stopping? | Stop on validation plateau with patience; the cheapest regularization | 05 |
| 34 | Regularization without a validation set? | Noise — model selection must not touch test data | 05 |
| 35 | Zero init failure? | Symmetry: all hidden units stay identical forever | 06 |
| 36 | Xavier variance? | `2/(fan_in + fan_out)` | 06 |
| 37 | He variance? | `2/fan_in` | 06 |
| 38 | LeCun variance? | `1/fan_in` | 06 |
| 39 | Xavier derivation? | Preserve forward variance (`Var*fan_in = 1`) and backward (`Var*fan_out = 1`) | 06 |
| 40 | Orthogonal init use? | RNNs, where a long product of matrices must not explode or vanish | 06 |
| 41 | SGD update? | `w -= eta * g` | 07 |
| 42 | Nesterov difference? | Evaluates the gradient after stepping ahead, then corrects | 07 |
| 43 | AdaGrad weakness? | The accumulator only grows, so learning rate decays monotonically to zero | 07 |
| 44 | RMSProp update? | Divide by `sqrt(rho*accum + (1-rho) g^2)`; an EMA of squared gradients | 07 |
| 45 | Adam moments? | `m` EMA of gradients, `v` EMA of squared gradients, bias-corrected | 07 |
| 46 | Adam epsilon role? | Numerical insurance in the denominator, not the real bias fix | 07 |
| 47 | AdamW difference? | Decoupled decay not divided by `sqrt(v_hat)` | 07 |
| 48 | Warmup purpose? | Avoids the large early gradients that destabilize transformers | 07 |
| 49 | Gradient clipping by norm? | Caps the global update norm, containing rare huge-gradient batches | 07 |
| 50 | BatchNorm statistics? | Per channel over batch and spatial; stored as running means/variances | 08 |
| 51 | BatchNorm inference bug? | Forgetting `.eval()` uses batch statistics instead of running ones | 08 |
| 52 | LayerNorm statistics? | Over features within a sample; independent of batch composition | 08 |
| 53 | GroupNorm use? | Batch-size-robust normalization for CNNs and diffusion | 08 |
| 54 | RMSNorm? | LayerNorm without mean subtraction; cheaper, common in large LLMs | 08 |
| 55 | Pre-norm vs post-norm? | Pre-norm keeps the residual path clean; post-norm needs careful warmup | 08 |
| 56 | Residual block? | `y = F(x) + x`; effective Jacobian `I + J_F` | 09 |
| 57 | DenseNet idea? | Every layer receives every prior feature, maximizing reuse | 09 |
| 58 | Inception idea? | Parallel multi-scale branches concatenated | 09 |
| 59 | SENet idea? | Squeeze global descriptor, then reweight channels — cheap channel attention | 09 |
| 60 | PTQ vs QAT? | PTQ needs real activation calibration and can collapse; QAT recovers most of the loss | 10 |
