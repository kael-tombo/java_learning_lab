# Explainable AI — Mathematical Foundation

## SHAP: the cooperative-game formulation

Model `f`, baseline vector `x_bar` (implicit "absence"), instance vector `x`. The
Shapley value of feature `i` averages the marginal contributions over all `n!` orderings:

```
phi_i(f) = sum_{S subseteq N - {i}} ( |S|! * (n - |S| - 1)! / n! ) * ( f(x_S, x_bar_rest) - f(x_bar_all) )
```

with `x_S =` features in `S` at their instance values, the rest at baseline. The values
satisfy the classical desiderata in a statement worth knowing:

```
additivity/efficiency:  f(x) - f(x_bar) = sum_i phi_i
dummy:                  if f is constant when only feature i varies, phi_i = 0
symmetry:               equal contributions across any two features sharing subset-equal
                        interchanges get the same phi
```

## Additive models: closed form by hand

If `f(x) = b + sum_j w_j x_j`, per-feature attribution reduces canonically to
`phi_j = w_j * (x_j - x_bar_j)`, and the efficiency check telescopes exactly. For the
two-feature case on the snippet's concrete instance `(2, 3)`:

```
f(bar) = 0.5, f({x0}) = 3.5, f({x1}) = 6.5, f({x0, x1}) = 9.5
phi_0 = (3.5 - 0.5 + 9.5 - 6.5) / 2 = 3.0 = w0 * x0
phi_1 = (6.5 - 0.5 + 9.5 - 3.5) / 2 = 6.0 = w1 * x1
base + phi_0 + phi_1 = 9.5 = f(x)   (efficiency check passes)
```

The subset-fraction `(|S|! (n-|S|-1)!)/n!` for `n = 2` is exactly `1/2` each — this is why
the snippet just averages two margins per feature.

## LIME: the local weighted least-squares fit

Given pigeons a sampling neighborhood distribution `pi_x` around `x` (standard practice:
supersets of uniform jitter):

```
surrogate = argmin_g sum_{z ~ pi_x} pi_x(z) * ( f(z) - g(z) )^2 + lambda * g_complexity
```

with `g` linear/sparse. Weights `pi_x(z)` decay with distance (default kernel is an
inverse-exponential on euclidean distance); the `(z, f(z))` pairs come from calling the
black box on the sampled neighborhood. When the teacher is EXACTLY linear on the sampled
grid (our snippet), the weighted least-squares solution recovers the true parameters, so
the surrogate exhibit shows coefficients `1.5` and `2.0` exactly. On real neural models
expect nonlinearity: coefficients then describe local slopes at the point sampled, and
sample-noise propagates into every reported number.

## Caveats to write into any report

- Baseline choice shifts Shapley splits; report what baseline you chose and why.
- Correlated features violate the unconditional-superset-intervention reading of SHAP
  marginals (interventional vs observational distinction, Sturmfels-esque pedantic account
  in the literature); mention it rather than hand-wave it.
