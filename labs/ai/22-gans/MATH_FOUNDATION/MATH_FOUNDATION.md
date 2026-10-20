# Generative Adversarial Networks — Mathematical Foundation

## The minimax objective (standard formulation)

With generator $G(z; theta_g)$ and discriminator $D(x; theta_d)$, uniform noise prior
$p_z$, and data distribution $p_{data}$, the original objective is the saddle-point
problem:

```
min_G max_D  V(D, G)
V(D, G) = E_{x ~ p_data}[ log D(x) ] + E_{z ~ p_z}[ log(1 - D(G(z))) ]
```

- `D` maximizes: assigns log-probability 1 to real, 0 to fake.
- `G` minimizes the same expression; in the widely used non-saturating variant, `G`
  instead ascends `E_z[ log D(G(z)) ]`, which keeps gradients alive when `D` is confident.

## The two standard closed-form results

For a fixed generator, the family of functions `D` that maximize `V` complete the
discriminator's optimal form as an integral over the real-line/finite support domain:

```
D*(x) = p_data(x) / ( p_data(x) + p_model(x) )
```

Substituting `D*` back converts the value into the Jensen-Shannon divergence between
`p_data` and `p_model` (up to a factor of 2 and constants). It follows that the game is
minimized exactly when the two distributions coincide — the generator set at equilibrium
satisfies the "distributions match" condition, and `D*(x) = 1/2` for every `x` in the
support. These claims hold under the idealized assumptions of an infinitely capable
discriminator evaluated pointwise; real networks violate them, which is why the search is
delicate.

## Gradients implemented in our toy

For the scalar setup with a linear-logistic discriminator `D(x) = sigmoid(w * x + b)`,
one real point `x_data` and one generated point `g`:

```
dV/dw = (1 - D(x_data)) * x_data - D(g) * g
dV/db = (1 - D(x_data)) - D(g)
non-saturating G ascent on g:  dg = (1 - D(g)) * w
```

The last expression is the derivative of the surrogate `-log D(g)` with respect to the
generated point: `d(-log D)/dz = -(1 - D)` composed with `dz/dg = w` and a sign flip for
ascent. Each factor is a plain chain-rule identity about the logistic curve, which is what
makes the toy fully auditable by hand.

## Caveats worth memorizing

- The JSD interpretation requires evaluating `V` at `D*`, unreachable in finite training.
- The generator's objective is non-monotone over `g` when `w` keeps growing; explainable
  drift past the data point is observed in Snippet 1's log of this folder.
