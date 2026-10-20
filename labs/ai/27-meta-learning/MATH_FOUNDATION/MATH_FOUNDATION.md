# Meta-Learning — Mathematical Foundation

## MAML, the conceptual split (exact statements kept minimal)

Given task-level loss `L_T(theta)` and the inner update rule
`U_alpha(theta) = theta - alpha * dL_T^{support}(theta)`:

- Adapted parameters: `theta1 = U_alpha(theta0)` (one or a few inner steps).
- The EXACT outer update would differentiate the query loss through `U_alpha`:
  `theta <- theta0 - beta * d/dtheta0 L_T^{query}(U_alpha(theta0))`.
- The FIRST-ORDER approximation (pseudo-gradient; FOMAML-style) replaces that with the
  gradient at the adapted point:

```
outer_grad = dL_T^{query}(theta1)/d theta1     (no chain through the inner step)
theta2 = theta0 - beta * outer_grad
```

The difference between the two is a second-order term `alpha * H_support * [query
gradient pieces]`, which is why the approximation is called first-order; when inner
curvature is large, FOMAML and true-MAML trajectories visibly diverge — that is fine to
state, we never claim numeric parity.

## Reading our two-task table

For task A (`y = 0.5x`, support `(2,1)`, query `(3,1.5)`) starting at `theta0 = 0`,
inner `alpha = 0.1`, outer `beta = 0.1`:

```
support loss   = (0*2 - 1)^2 = 1
inner grad     = 2 (0*2 - 1) * 2 = -4  ->  theta1 = 0.4
query loss     = (0.4*3 - 1.5)^2 = 0.09
FOMAML grad    = 2 (1.2 - 1.5) * 3 = -1.8
plain grad     = 2 (0 - 1.5) * 3 = -9.0
```

So adaptation matters: with it, the meta-gradient shrinks 5x and the meta-point moves to
`theta2 = 0 - 0.1 * (-1.8) = 0.18`. Task B (`y = -0.5x`, support `(4,-2)`, query
`(5,-2.5)`) shows the dramatic version: inner adaptation FLIPS the outer gradient's sign
(`25.0` plain vs `-55.0` adapted) because one step drove `theta1 = -1.6` far past the
query's optimum.

## Reptile interpolation rule

With inner solutions `a1... = task-final after k inner steps` and strength epsilon:

```
theta_next = theta + epsilon * ( mean_i a_i - theta )
```

At `epsilon = 1` the shared point becomes the mean task optimum exactly; smaller epsilon
is a cautious interpolation. For our recurrence `a <- 0.6 a + c` patterns at `lr = 0.05`
(numpy-free closed form available) the inner fixed points are the `0.5`/`-0.5`. The
`k = 5` solution values `0.46112` and `-0.53888` in the snippet are the fixed points
reached `1 - 0.6^5` / with sign-flipped overshoot — derive both by induction in one line
when you do Exercise 1.

## Convergence skims worth knowing

- MAML-family optimizers have no guarantee to reach a global task-distribution minimizer;
  what IS a theorem-lite is the statement that good initializations place each task's flow
  in a low-curvature basin — quotes stay conceptual here.
- Reptile under SGD-style inner runs acts as shrinkage toward the between-task optimum;
  an empirical, not universal, statement.
