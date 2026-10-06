# Support Vector Machines - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What determines an SVM's decision boundary? | Only the support vectors, weighted by their dual coefficients αᵢ. |
| 2 | Why standardise features for an RBF kernel? | The kernel uses squared Euclidean distance, so unscaled units let one dimension dominate and effectively shrink γ for the rest. |
| 3 | What does C control? | The price of each unit of margin violation: large C fits the training data, small C tolerates a wider, smoother margin. |
| 4 | What is a support vector? | Any training point with αᵢ > 0 — a point on or inside the margin. Removing them changes the boundary. |
| 5 | Is the SVM output a probability? | No, it is a signed distance-like margin. Wrap it in Platt scaling if a probability is required. |
| 6 | What does the kernel trick avoid? | Explicitly computing the feature map, which is what makes infinite-dimensional maps usable. |
| 7 | Why is SMO used? | Optimising all α jointly has no closed form; updating two at a time makes each subproblem solvable analytically. |
| 8 | When does an SVM beat a random forest? | Compact datasets with few features, clear margins, and a need for a smooth boundary without normalisation assumptions. |
| 9 | What is Maximum margin? | The decision boundary sits midway between the two closest convex hulls; the margin width is 2/\|\|w\|\|. |
| 10 | What is Soft margin and the C trade-off? | Adding slack ξᵢ with penalty C · Σξᵢ allows violations. |
| 11 | What is The dual form and support vectors? | Training solves max over α of Σαᵢ − 0. |
| 12 | What is The kernel trick? | Replace xᵀxˢ with K(xˢ). |
| 13 | What is Feature scaling is mandatory? | RBF and polynomial kernels use squared distances. |
| 14 | What is SMO and why it is hard? | SMO optimises two α values at a time so each subproblem has a closed form. |
| 15 | In this lab, what does `min 0.5\|\|w\|\|² s.t. yᵢ(wᵀxᵢ + b) ≥ 1` mean? | Hard-margin primal: maximum-margin separator |
| 16 | In this lab, what does `min 0.5\|\|w\|\|² + CΣξᵢ s.t. yᵢf(xᵢ) ≥ 1 − ξᵢ` mean? | Soft-margin primal: slack variables priced by C |
| 17 | In this lab, what does `f(x) = Σ αᵢyᵢK(xᵢ,x) + b` mean? | Decision function: prediction depends only on support vectors |
| 18 | In this lab, what does `K(x,z) = exp(−γ\|\|x−z\|\|²)` mean? | RBF kernel: infinite-dimensional feature map |
| 19 | In this lab, what does `margin width = 2/\|\|w\|\|` mean? | Geometric margin: objective minimises \|\|w\|\| to widen it |
| 20 | In this lab, what does `αᵢ ∈ [0, C], Σαᵢyᵢ = 0` mean? | Dual constraints: 0 < α identifies support vectors |
| 21 | In this lab, what does `K(x,z) = (xᵀz + r)^d` mean? | Polynomial kernel: finite-degree expansion |
| 22 | In this lab, what does `gamma = 1/(2σ²)` mean? | RBF bandwidth: set from feature variance when not tuned |
| 23 | You see 'Accuracy collapses after standardisation of one feature' in production. What is the cause and the fix? | features were left unscaled so one unit dominated Fix: standardise everything, and add a scaling-invariance test |
| 24 | You see 'gamma = 100 blows up training time' in production. What is the cause and the fix? | RBF bandwidth far too small, nearly every point becomes a support vector Fix: use gamma = 1/(p·Var) as a starting point and validate |
| 25 | You see 'C = 1e6 memorises the training set' in production. What is the cause and the fix? | hard-margin behaviour by construction Fix: sweep C down; check the support-vector fraction |
| 26 | You see 'Scores look like probabilities but are not' in production. What is the cause and the fix? | SVM outputs are margins, not calibrated probabilities Fix: wrap in Platt scaling if a probability is needed |
| 27 | You see 'Kernel matrix OutOfMemoryError' in production. What is the cause and the fix? | n² doubles exceeds heap at n ≈ 40k Fix: switch to linear kernel, approximate kernels, or a different algorithm |
| 28 | You see 'Results change between identical runs' in production. What is the cause and the fix? | SMO initialisation uses an unseeded Random Fix: seed the initialisation and assert reproducibility |
| 29 | Which Java API is the backbone of: K(x,z) becomes a lambda you can swap and unit-test in isolation | `FunctionalInterface for kernels` |
| 30 | Which Java API is the backbone of: worst-violating α chosen first, the standard heuristic | `PriorityQueue<Double> for SMO selection` |
| 31 | Which Java API is the backbone of: precomputed K for small n; the dominant memory cost | `double[][] kernelMatrix` |
| 32 | Which Java API is the backbone of: enforcing 0 ≤ α ≤ C and the equality constraint | `Arrays.fill + clipping in the α update` |
| 33 | Which Java API is the backbone of: deterministic α initialisation for reproducible training | `SplittableRandom` |
| 34 | Why does Maximum margin matter operationally? | The decision boundary sits midway between the two closest convex hulls; the margin width is 2/\|\|w\|\|. |
| 35 | Why does Soft margin and the C trade-off matter operationally? | Adding slack ξᵢ with penalty C · Σξᵢ allows violations. |
| 36 | Why does The dual form and support vectors matter operationally? | Training solves max over α of Σαᵢ − 0. |
| 37 | Why does The kernel trick matter operationally? | Replace xᵀxˢ with K(xˢ). |
| 38 | Why does Feature scaling is mandatory matter operationally? | RBF and polynomial kernels use squared distances. |
| 39 | Why does SMO and why it is hard matter operationally? | SMO optimises two α values at a time so each subproblem has a closed form. |
| 40 | In the Support Vector Machines pipeline, what happens next? Standardise features, then encode categoricals — kernels see... | Standardise features, then encode categoricals — kernels see raw distances. |
| 41 | In the Support Vector Machines pipeline, what happens next? Choose a kernel: linear for text/high-dim, RBF for compact n... | Choose a kernel: linear for text/high-dim, RBF for compact numeric data, polynomial for interaction counts. |
| 42 | In the Support Vector Machines pipeline, what happens next? Run SMO-style coordinate ascent over α with a shrinking lear... | Run SMO-style coordinate ascent over α with a shrinking learning rate and a tolerance on KKT violation. |
| 43 | In the Support Vector Machines pipeline, what happens next? Recover b from the support vectors in the margin band and cl... | Recover b from the support vectors in the margin band and clip α into [0, C] each sweep. |
| 44 | In the Support Vector Machines pipeline, what happens next? Tune C and gamma on a validation grid; plot the surface, do ... | Tune C and gamma on a validation grid; plot the surface, do not eyeball a single point. |
| 45 | In the Support Vector Machines pipeline, what happens next? Inspect the support vectors: they are the rows your model is... | Inspect the support vectors: they are the rows your model is made of, and often a data-quality story. |
| 46 | Exercise focus: Hard-margin SVM by hand, then in code | Solve the small case analytically and reproduce it with SMO. |
| 47 | Exercise focus: Implement the kernel trick | Add polynomial and RBF kernels and confirm they change the boundary. |
| 48 | Exercise focus: Tune C and gamma properly | Replace eyeballing with a validation surface. |
| 49 | Exercise focus: Support-vector forensics | Understand which rows the model actually uses. |
| 50 | Exercise focus: Margin as a calibrated input | Wrap the SVM in Platt scaling and measure the gain. |
| 51 | Exercise focus: Compare SVM against the rest of the track | Benchmark the boundary shapes head to head. |
| 52 | State the Primal to dual result for Support Vector Machines. | For a 3-point linearly separable set, the dual has a unique solution with two non-zero α (the support vectors); the third point's α is exactly 0 and it can be deleted without moving the boundary. |
| 53 | State the The margin and its geometric meaning result for Support Vector Machines. | \|\|w\|\| = 2 gives a margin of 1.0; \|\|w\|\| = 10 gives 0.2. A support vector moved 0.01 along the normal cannot change \|\|w\|\| much, but a point that leaves the margin band enters as a new α and can. |
| 54 | State the Kernel expansion result for Support Vector Machines. | Polynomial with d=3, r=1, x.z=2: K = 27, and the expansion is 8x₁³ + 12x₁²x₂ + 6x₁x₂² + x₂³ + 6x₁² + 12x₁x₂ + 6x₂ + 3x₁ + 3x₂ + 1. |
| 55 | State the KKT conditions and SMO convergence result for Support Vector Machines. | Two interior points violating by 0.01 and -0.02: SMO picks both, solves the 2x2 quadratic exactly, and the total KKT violation drops by ~0.03 in a single update. |
| 56 | State the Soft margin C and the classification error trade-off result for Support Vector Machines. | Separable data with C = 1e6: train error 0, support-vector fraction 0.98, test error 0.19. Dropping C to 0.1 gives 0.94 support vectors and test error 0.04. |
| 57 | State the Scalability, and the practical ceiling result for Support Vector Machines. | n = 10,000 needs 800 MB for the matrix; n = 40,000 needs 12.8 GB and likely OOMs on a 16 GB pod. n = 1,000,000 is unthinkable for a kernel SVM. |
| 58 | What is the practical memory ceiling for kernel SVMs? | The O(n²) kernel matrix: 40,000 rows × 8 bytes ≈ 12.8 GB, so real limits are in the low tens of thousands. |
| 59 | gamma in the RBF kernel, intuitively? | A length scale. Small gamma = distant influence and a smooth boundary; large gamma = local influence and wiggly boundaries. |
| 60 | Why do polynomial kernels make sense for text? | String kernels define a similarity over n-gram counts, which is exactly the xᵀz term raised to a degree. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
