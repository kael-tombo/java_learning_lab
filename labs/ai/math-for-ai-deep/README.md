# math-for-ai-deep

Deep track for the mathematics of AI in Java 21 — ten modules from vector spaces through
matrices, eigendecomposition and SVD, vector calculus, probability, Bayesian inference,
information theory, optimization, gradient descent variants, and numerical computing.

Every derivation is followed by the numeric check that catches the mistake. Every algorithm
is implemented and verified against a mathematical identity, not against a reference library.

## Track Contents

Ten sub-modules, each with its own theory, exercises, quiz, and an `*Algorithm.java` plus
test pair under `src/`:

| # | Module | Focus |
|---|--------|-------|
| 01 | `01-vectors-spaces` | Linear combinations, span, basis, inner products, orthogonality, Gram-Schmidt |
| 02 | `02-matrices-operations` | Multiplication, transpose, inverse, determinant, LU, matrix norms |
| 03 | `03-eigenvalues-svd` | Eigenvalue decomposition, PCA derivation, SVD theorem, truncated SVD |
| 04 | `04-gradient-vector-calc` | Partials, gradient, Jacobian, Hessian, directional derivative, chain rule |
| 05 | `05-probability-distributions` | Bernoulli, Binomial, Poisson, Gaussian, mixtures, exponential family |
| 06 | `06-bayesian-inference` | Bayes theorem, conjugate priors, MAP, Beta-Binomial, Gaussian-Gaussian |
| 07 | `07-information-theory` | Entropy, cross-entropy, KL, Jensen-Shannon, mutual information |
| 08 | `08-optimization-fundamentals` | Convexity, local vs global optima, duality, KKT |
| 09 | `09-gradient-descent-variants` | Batch GD, SGD, mini-batch, momentum, Nesterov, AdaGrad, RMSProp, Adam, AdamW |
| 10 | `10-numerical-computing` | IEEE 754, stability, catastrophic cancellation, log-sum-exp |

## Track-Level Documents

| File | What it is |
|------|-----------|
| `INDEX.md` | Module list with one-line focus per module |
| `THEORY.md` | Object, key property, and where AI breaks, for each of the ten modules |
| `EXERCISES.md` | ~85 tagged exercises plus five cross-module tasks |
| `QUIZ.md` | 15 multiple-choice questions with answer key and score guide |
| `FLASHCARDS.md` | 60-row recall table |
| `MATH_FOUNDATION.md` | Full derivations with worked numbers: conditioning, Gram-Schmidt stability, SVD optimality, AD, exponential family, max-entropy, conjugacy, ELBO, KKT, convergence rates, numerical analysis |
| `CODE_DEEP_DIVE.md` | Java implementations: Jacobi eigen, one-sided Jacobi SVD, Cholesky, reverse-mode AD tape, log-sum-exp, Kahan summation, KL/JS, conjugate updates, VI with a monotonicity assertion |
| `VISION.md` | Mastery path, milestones, anti-goals, 30-day plan |
| `MINI_PROJECT.md` | A mathematical toolkit for ML: 12 phases, 19 milestones |
| `REAL_WORLD_PROJECT.md` | Forecasting and anomaly platform built on mathematical guarantees |
| `MATH_FOR_AI_INTERVIEW_GUIDE.md` | Interview preparation |

## Why This Track Exists Separately From The Modelling Tracks

Modelling tracks teach you which algorithm to reach for. This one teaches you **why the
algorithm is numerically well-behaved, and when it silently is not**. The gap between those
two is the difference between:

- `cond(A'A) = cond(A)^2` known versus unknown — which decides whether your least-squares
  solve returns an answer or noise.
- Modified versus classical Gram-Schmidt — which decides whether your QR orthogonalizes.
- Jensen-Shannon versus KL — which decides whether your drift monitor is usable.
- An ELBO you report with its gap versus one you report alone.

## The Five Facts Worth Memorizing

1. **`cond(A'A) = cond(A)^2`.** Never solve the normal equations.
2. **`log sum exp(x) = m + log sum exp(x - m)`.** Without it, softmax overflows at 709.
3. **`D_JS` is bounded, symmetric, zero iff equal.** Use it for drift, not KL.
4. **Beta-Binomial: `alpha + s`, `beta + f`.** Conjugacy is two additions.
5. **`eta <= 2/L` for L-smooth objectives.** Above that, divergence is guaranteed.

## How to Work Through This Track

1. **Read `THEORY.md`**, then **`MATH_FOUNDATION.md`** front to back. This is the one track
   where reading the maths is the point rather than a prerequisite.
2. **Work `EXERCISES.md`** in module order. Every exercise asks you to *verify* something,
   and the verification is the learning.
3. **Retake `QUIZ.md`** until 13/15 with no misses on the condition number, symmetry, KL/JS,
   and ELBO questions.
4. **Drill `FLASHCARDS.md`** daily — this track has the most formula recall of any.
5. **Implement from `CODE_DEEP_DIVE.md`**. The AD tape, the Jacobi SVD, and the
   stability-vs-naive-summation demonstrations are worth writing by hand once.
6. **Build the mini project.** The self-test suite that verifies every identity in
   `MATH_FOUNDATION.md` is the deliverable.
7. **Design the real-world project** — the mathematics becomes the specification, which is
   the point.

## Verification Habit

For every algorithm in this track, write a test that checks a mathematical property, not a
stored expected value:

| Property | Check |
|----------|-------|
| Orthogonality | `\|Q'Q - I\|` below a tolerance |
| Eigen | `\|AP - P D\|` below a tolerance |
| SVD | reconstruction error `=` tail sum of squared singular values |
| Cholesky | `\|L L' - A\|` below a tolerance, **and** failure on non-SPD input |
| AD | forward vs reverse vs finite differences agree |
| Entropy chain rule | `\|H(X,Y) - H(X) - H(Y\|X)\|` below a tolerance |
| KL | non-negative, zero iff equal |
| ELBO | monotonically non-decreasing |
| GD | observed convergence matches the analytic contraction factor |

A test with a hard-coded expected value tells you the code has not changed. A test with a
property tells you the code is correct.

## What You Will Be Able To Do

- Derive any result in a modern ML paper and implement it, verifying against the
  mathematical identity rather than against a library.
- Diagnose a numerical problem (non-convergence, NaN, orthogonality loss, precision
  collapse) and name the condition responsible.
- Choose the right tool for the job: QR over normal equations, SVD over eigendecomposition,
  Cholesky over inversion, Jensen-Shannon over KL, modified Gram-Schmidt over classical.
- Build a reverse-mode AD tape and train a network on it without writing a backward pass.
- Plan compute from convergence theory rather than from trial and error.
- Explain to a colleague, and defend in review, why a numerical choice is the right one.
