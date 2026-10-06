# Support Vector Machines

**Track:** ml  |  **Lab:** lab04  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Problem This Solves

You want the most confident separator you can draw between two classes, and you want it to generalise from the support vectors alone rather than from every point.

SVMs are the geometric view of classification. Even when you never ship one, the margin, the kernel trick and the dual form show up in every modern kernel method.

## 2. Learning Objectives

- State the primal and dual formulations of the hard- and soft-margin problems
- Explain the geometric meaning of the margin and why support vectors alone determine the boundary
- Implement the kernel trick for linear, polynomial and RBF kernels
- Implement a simplified SMO-style coordinate ascent optimiser
- Choose C and gamma from validation data and explain what each controls
- Recognise when an SVM is the wrong tool: large n, high cardinality, uncalibrated scores

## 3. Core Concepts

### 3.1 Maximum margin

The decision boundary sits midway between the two closest convex hulls; the margin width is 2/||w||. Maximising it minimises ||w||, which is what the primal objective 0.5||w||² does. Points strictly outside the margin never influence the solution.

### 3.2 Soft margin and the C trade-off

Adding slack ξᵢ with penalty C · Σξᵢ allows violations. Large C means almost no violations (risk overfitting); small C tolerates a wide margin (underfitting). C is the misclassification budget priced per unit of margin.

### 3.3 The dual form and support vectors

Training solves max over α of Σαᵢ − 0.5||Σαᵢyᵢ K(xᵢ,xⱼ)||² subject to 0 ≤ αᵢ ≤ C and Σαᵢyᵢ = 0. The solution is w = Σαᵢyᵢxᵢ, so only points with αᵢ > 0 matter. Prediction is f(x) = ΣαᵢyᵢK(xᵢ,x) + b.

### 3.4 The kernel trick

Replace xᵀxˢ with K(xˢ). RBF, exp(−γ||x−xˢ||²), implies an infinite dimensional feature map; polynomial, (xᵀxˢ + r)^d, gives a finite one. SVMs become the natural model for string, graph and protein similarity — anywhere the similarity is already known.

### 3.5 Feature scaling is mandatory

RBF and polynomial kernels use squared distances. Unstandardised features with different units make one dimension dominate the distance and the kernel degenerates. Standardise, and verify with a test that scaling one feature by 1000 changes results.

### 3.6 SMO and why it is hard

SMO optimises two α values at a time so each subproblem has a closed form. Complexity is O(n²–³) per pass in memory for the kernel matrix, which is the practical ceiling: SVMs are for n in the thousands, not millions.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `min 0.5||w||² s.t. yᵢ(wᵀxᵢ + b) ≥ 1` | Hard-margin primal | maximum-margin separator |
| `min 0.5||w||² + CΣξᵢ s.t. yᵢf(xᵢ) ≥ 1 − ξᵢ` | Soft-margin primal | slack variables priced by C |
| `f(x) = Σ αᵢyᵢK(xᵢ,x) + b` | Decision function | prediction depends only on support vectors |
| `K(x,z) = exp(−γ||x−z||²)` | RBF kernel | infinite-dimensional feature map |
| `margin width = 2/||w||` | Geometric margin | objective minimises ||w|| to widen it |
| `αᵢ ∈ [0, C], Σαᵢyᵢ = 0` | Dual constraints | 0 < α identifies support vectors |
| `K(x,z) = (xᵀz + r)^d` | Polynomial kernel | finite-degree expansion |
| `gamma = 1/(2σ²)` | RBF bandwidth | set from feature variance when not tuned |

## 5. How the Pieces Fit Together

1. Standardise features, then encode categoricals — kernels see raw distances.

2. Choose a kernel: linear for text/high-dim, RBF for compact numeric data, polynomial for interaction counts.

3. Run SMO-style coordinate ascent over α with a shrinking learning rate and a tolerance on KKT violation.

4. Recover b from the support vectors in the margin band and clip α into [0, C] each sweep.

5. Tune C and gamma on a validation grid; plot the surface, do not eyeball a single point.

6. Inspect the support vectors: they are the rows your model is made of, and often a data-quality story.

## 6. Assumptions and Invariants

- Features are scaled; otherwise the kernel measures the wrong distance
- Classes are separable in the induced feature space, or soft margin C is chosen deliberately
- n is small enough that an O(n²) kernel matrix fits comfortably
- The similarity function K is a valid positive semi-definite kernel
- Independent samples; SVMs have no notion of order or time
- Class balance handled by class weights or C, since the margin ignores counts

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Accuracy collapses after standardisation of one feature | features were left unscaled so one unit dominated | standardise everything, and add a scaling-invariance test |
| gamma = 100 blows up training time | RBF bandwidth far too small, nearly every point becomes a support vector | use gamma = 1/(p·Var) as a starting point and validate |
| C = 1e6 memorises the training set | hard-margin behaviour by construction | sweep C down; check the support-vector fraction |
| Scores look like probabilities but are not | SVM outputs are margins, not calibrated probabilities | wrap in Platt scaling if a probability is needed |
| Kernel matrix OutOfMemoryError | n² doubles exceeds heap at n ≈ 40k | switch to linear kernel, approximate kernels, or a different algorithm |
| Results change between identical runs | SMO initialisation uses an unseeded Random | seed the initialisation and assert reproducibility |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `FunctionalInterface for kernels` | K(x,z) becomes a lambda you can swap and unit-test in isolation |
| `PriorityQueue<Double> for SMO selection` | worst-violating α chosen first, the standard heuristic |
| `double[][] kernelMatrix` | precomputed K for small n; the dominant memory cost |
| `Arrays.fill + clipping in the α update` | enforcing 0 ≤ α ≤ C and the equality constraint |
| `SplittableRandom` | deterministic α initialisation for reproducible training |

## 9. Where This Sits in the Larger System

- **Lab 03** gives the axis-aligned alternative; compare their boundaries on the same data.
- **Lab 06** offers the generative shortcut when the class-conditional densities are easy.
- **Lab 10** supplies ROC/AUC, which is the right way to compare a margin score across C and gamma.
- **Lab 14 in MLOps** shows how a hyperparameter sweep like C×gamma gets orchestrated.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — State the primal and dual formulations of the hard- and soft-margin problems
- [ ] 0 — cannot yet — Explain the geometric meaning of the margin and why support vectors alone determine the boundary
- [ ] 0 — cannot yet — Implement the kernel trick for linear, polynomial and RBF kernels
- [ ] 0 — cannot yet — Implement a simplified SMO-style coordinate ascent optimiser
- [ ] 0 — cannot yet — Choose C and gamma from validation data and explain what each controls
- [ ] 0 — cannot yet — Recognise when an SVM is the wrong tool: large n, high cardinality, uncalibrated scores

## 11. Summary Checklist

- [ ] I can state the primal, the dual and the kernel form from memory
- [ ] I can explain what support vectors are without looking at the formula
- [ ] I know why standardisation is not optional for RBF
- [ ] I can tune C and gamma from a validation surface
- [ ] I know the score is a margin, not a probability
- [ ] I can state the n at which SVM stops being practical
