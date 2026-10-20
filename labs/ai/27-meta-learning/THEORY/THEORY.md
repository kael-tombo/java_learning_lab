# Meta-Learning — Theory

**Meta-learning** ("learning to learn") reframes training so the outer objective is a task
performance: the model should quickly adapt to NEW tasks from a few examples. The inner
loop handles one task; the outer loop updates the initialization or other shared pieces.

## The canonical framing

- The task distribution `p(T)` supplies small datasets: within a task, a *support set*
  for adaptation and a *query set* for evaluation.
- The outer learner is anything shaped across tasks: a good initialization (model-based
  family), a metric kernel (similarity-based family), or an adaptation network (amortized
  family). This lab implements the initialization family on scalar tasks only.

## First-order approximation

Exact gradients through adaptation are expensive; the standard approximation drops the
second-order term and reads the outer gradient directly at the adapted point:

- Inner step on one minibatch: `theta' = theta - alpha * dL_support/d theta`.
- Outer step on query data evaluated at `theta'`, but with the gradient computed
  one-step-local (the pseudo-gradient).
- Later literature refines this idea (memory, attention variants, learned optimizers);
  none of these re-introduced results is claimed numerically here.

## Reptile: the simple sibling

Instead of split support/query, Reptile-style approaches simply run several SGD steps toward
each task's optimum, then interpolate the shared initialization toward the average of the
inner solutions. Both methods rely on the same intuition: a good starting point is one
from which any nearby task is a short downhill walk — mathematically, the initial point
minimizes a trade-off between post-adaptation loss across the task distribution.

## The two failure statements everyone needs

- Inner-loop instability: with too-large `alpha`, inner adaptation diverges and the outer
  signal is garbage (we show divergence numerically in one exercise at lr 0.1 on a
  curvature-32 task).
- Overfitting to the training tasks: the initialization can memorize the task family
  instead of learning fast adaptation; the check is on held-out tasks with genuinely
  different optima.

## What this lab provides

Two snippets: one first-order meta-step computed by construction (no autograd), and one
interpolation run; both on tasks `y = a*x` with slopes `+0.5` and `-0.5` so sign flips in
the outer gradient are visible directly in stdout. All numbers hand-checkable; nothing
about large networks is claimed or measured here.
