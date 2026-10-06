# Support Vector Machines - Vision & Where This Is Going

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

## 1. The Future State

The SVM survives as the conceptual bridge between convex optimisation, kernels and modern representation learning — its influence is in kernel methods, Gaussian processes and the intuition behind large-margin losses, not in new deployments of libsvm.

The test of that future state is boring: a new engineer ships a change to support vector machines on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- C and gamma come from a validation surface, with the plateau documented.
- Support-vector fraction is logged as a health signal.
- Scores are Platt-calibrated before any probability is published.
- The n at which we switch algorithms is written down in the model card.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Fit a linear SVM | Separate two classes, report the margin and support vectors. |
| L2 | Go non-linear | Add the RBF kernel, tune gamma, understand the length scale. |
| L3 | Tune honestly | Sweep C×gamma with CV, calibrate the margin, watch the support-vector fraction. |
| L4 | Know when to stop | Recognise the scalability cliff and switch to a linear kernel or a tree ensemble. |

## 4. Behaviours to Build

Prefer the linear kernel until you have evidence otherwise. Scale before you fit. Treat the validation surface as a plateau, not a peak.

## 5. Anti-Vision (the failure mode we are avoiding)

- libsvm defaults shipped without ever looking at gamma.
- A margin quoted as a 0.87 'probability'.
- 500k rows of kernel SVM because nobody checked the memory math.
- The best single point on a noisy grid chosen as 'the' hyperparameter.

## 6. Technology Shifts That Change the Work

1. Kernel approximations and Nyström features extending SVMs to larger data.
1. Large-margin losses inside neural objectives, where the SVM view informs design.
1. Gaussian processes for calibrated uncertainty on small datasets, same kernel machinery.
1. Differentiable SVM heads inside end-to-end and adversarial-robustness work.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement linear and RBF kernels; verify a Gram matrix is positive semi-definite numerically.
- **60 days.** Implement SMO with KKT stopping and reproduce a hand-solved two-point case.
- **90 days.** Run a C×gamma sweep with cross-validation, Platt-calibrate the output, and document the memory cliff.

## 8. How To Tell You Are Actually Getting Better

- I can write the dual objective from memory.
- I can say what each alpha is doing without hesitating.
- My hyperparameters came from a surface I can show.
- I can state where this algorithm stops being practical and why.

## 9. Principles That Should Not Change

- **State the primal** State the primal and dual formulations of the hard- and soft-margin problems
- **Explain the geometric meaning of the margin** Explain the geometric meaning of the margin and why support vectors alone determine the boundary
- **Implement the kernel trick for linear, polynomial** Implement the kernel trick for linear, polynomial and RBF kernels

> Understanding the margin is worth more than adding one more classifier to your toolkit.
