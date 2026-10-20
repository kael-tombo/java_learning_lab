# Multi-Task Learning — Mathematical Foundation

## The weighted-sum objective (the exact statement)

For tasks `t` with differentiable losses `L_t(theta)`:

```
L(theta) = sum_t w_t * L_t(theta),   w_t > 0
```

The combined gradient decomposes by linearity:

```
dL/dtheta = sum_t w_t * (dL_t/dtheta)
```

so per-task gradient norms `||w_t * g_t|| = w_t ||g_t||` are the quantity that balancing
methods manipulate; the per-task scale of `L_t` itself is arbitrary (MSE, CE, ranking all
differ for equivalent tasks), which is exactly why raw equal weights `w_t = 1` are rarely
meaningful and can need rescaling per task.

## Uncertainty weighting (concept statement)

A likelihood view treats each task's noise as an unknown parameter `sigma_t`; the loss
becomes (homoscedastic version, standard formulation):

```
L = sum_t [ (1 / (2 sigma_t^2)) * L_t + log sigma_t ]
```

Consequences to quote: larger learned sigma shrinks a task's weight as `1/(2 sigma^2)`,
and the `log sigma_t` term stops the trivial sigma-growing collapse when written as above.
In our arithmetic snippet we use the fixed heuristic `sigma_t = sqrt(L_t)` each step (an
in-lore balancing shortcut, not claimed optimal), then renormalize weights to sum to one.

## Gradient surgery: the projection rule

Given two task gradients `g_1, g_2` in conflict (`<g_1, g_2> < 0`), the standard surgery
computes for each conflicting gradient `g_i`:

```
g_i' = g_i - (<g_i, g_j> / ||g_j||^2) * g_j     (take the average if multiple conflicts)
```

After projection, `<g_1', g_2'> = 0` exactly — the attacker's component along the other
gradient is removed so both heads can descend simultaneously. Measured by cosine: from
`-0.898635` to about `-1e-16` numerically on our fixed pair. The non-conflicting case
(more than two tasks, where the classical projection argument needs care) is stated only
conceptually.

## Balanced-weights arithmetic used in the snippet

Given losses `L_A = 3.625`, `L_B = 1.5147`:

```
sigma_A = sqrt(3.625), sigma_B = sqrt(1.5147)
w_A = 1/(2 L_A) = 0.137931, w_B = 1/(2 L_B) = 0.330158
renormalized: w_A/w_B ratio -> (0.2947, 0.7053)
```

The renormalized pair is what Snippet 1 combined; the resulting total gradient is printed
there. Consequence line: rewriting the loss never makes the conflicting directions
agree — reweighting changes *magnitudes*, only the projection rule changes *directions*.

## Chain-rule identities behind the snippets

Regression mean loss `L = mean (w1*x + w2 - y)^2` with gradient
`partial L/partial w1 = (2/n) sum (x * error)`. Logistic loss
`L = -log(1 - p1)... - log(p2)` with gradient `sigma(z) - y` per example. Both standard,
verified by the Python mirror.
