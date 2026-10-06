# neural-networks-deep

Deep track for neural networks in Java 21 — ten modules from the perceptron through
backpropagation, initialization, optimizers, normalization, residual architectures, and
model compression. Every forward and backward pass is hand-written.

## Track Contents

Ten sub-modules, each with its own theory, exercises, quiz, and an `*Algorithm.java` plus
test pair under `src/`:

| # | Module | Focus |
|---|--------|-------|
| 01 | `01-perceptron` | McCulloch-Pitts, Rosenblatt perceptron, convergence theorem, linear separability |
| 02 | `02-mlp-backprop` | Multi-layer, chain rule, backprop derivation, vanishing gradient |
| 03 | `03-activation-functions` | Sigmoid, tanh, ReLU, Leaky/PReLU/ELU/SELU/Swish/GELU benchmarks |
| 04 | `04-loss-functions` | MSE, MAE, Huber, cross-entropy, focal, contrastive, triplet |
| 05 | `05-regularization` | L1/L2, inverted dropout, batch/layer norm, early stopping |
| 06 | `06-weight-initialization` | Zero, random, Xavier, He, LeCun, orthogonal |
| 07 | `07-optimizers` | SGD, Momentum, Nesterov, AdaGrad, RMSProp, Adam, AdamW, convergence analysis |
| 08 | `08-normalization-layers` | BatchNorm, LayerNorm, InstanceNorm, GroupNorm, RMSNorm, ghost BN |
| 09 | `09-advanced-architectures` | Residual connections, DenseNet, Inception, SENet, ConvNeXt |
| 10 | `10-model-compression` | Pruning, INT8/FP16 quantization, knowledge distillation, weight sharing |

## Track-Level Documents

| File | What it is |
|------|-----------|
| `INDEX.md` | Module list with one-line focus per module |
| `THEORY.md` | Mechanism, reason, and failure for each of the ten modules |
| `EXERCISES.md` | ~90 tagged exercises plus four cross-module tasks |
| `QUIZ.md` | 15 multiple-choice questions with answer key and score guide |
| `FLASHCARDS.md` | 60-row recall table |
| `MATH_FOUNDATION.md` | Derivations with worked numbers: perceptron bound, backprop, variance-preserving init, Adam bias correction, BN backward, residual Jacobians, quantization error |
| `CODE_DEEP_DIVE.md` | Java implementations: matmul, activations, initializers, MLP backward, fused cross-entropy, optimizers, schedules, all four norms, residual, compression |
| `VISION.md` | Mastery path, milestones, anti-goals, 30-day plan |
| `MINI_PROJECT.md` | A neural network library: 12 phases, 14 milestones |
| `REAL_WORLD_PROJECT.md` | In-process recommendation ranker under a latency budget |
| `NEURAL_NETWORKS_ACADEMY_GUIDE.md` | Track guide |

## The One Rule

**Gradient-check everything.** Before the training loop, before the loss function, before
the architecture: perturb each parameter by `1e-5`, compare central differences to the
analytic gradient, and require relative error below `1e-6`. Every backprop bug in this
track is catchable in five minutes by that check.

## How to Work Through This Track

1. **Read `THEORY.md`** and note the *reason* each component exists, not just its formula.
   Every design choice here solves a specific failure someone hit.
2. **Run the gradient checker first**, on a two-layer network, before writing any training
   code. Establish the habit.
3. **Work `EXERCISES.md`** in module order, E to H. The gradient-check and
   variance-propagation exercises are the ones that matter.
4. **Retake `QUIZ.md`** until 13/15 with no misses on the initialization, dropout-scaling,
   AdamW, and pre-norm questions.
5. **Drill `FLASHCARDS.md`** daily.
6. **Do `MATH_FOUNDATION.md`** — the derivations of He init and Adam bias correction
   explain why the defaults exist.
7. **Implement from `CODE_DEEP_DIVE.md`** without reading ahead.
8. **Build the mini project**, then design the real-world project for a problem you care
   about.

## Debugging Order

Most "the network is not learning" reports are found in this order:

1. **Shapes and data flow** — print one layer's output at a time.
2. **Gradient norms per layer** — a zero, NaN, or exploding norm names the layer.
3. **Finite-difference gradient check** — localizes the bug to a single derivative.
4. **Learning curve shape** — distinguishes underfit, overfit, bad rate, unstable init.
5. **Data and labels** — last, and more often than expected the answer.

## What You Will Be Able To Do

- Derive and implement forward and backward passes for any feedforward or residual
  architecture, with a numerical check for each.
- Explain why each default exists (He init, `eps` in Adam, inverted dropout scaling,
  pre-norm) and what breaks when you change it.
- Diagnose a network that will not train, using gradient norms and curves rather than
  guesswork.
- Choose activations, initializers, optimizers, and normalization layers against a stated
  constraint rather than by habit.
- Compress a trained model to a budget while reporting what each step costs in accuracy
  and latency.
