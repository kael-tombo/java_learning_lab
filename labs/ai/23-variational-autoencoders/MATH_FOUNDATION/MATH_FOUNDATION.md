# Variational Autoencoders — Mathematical Foundation

## The lower bound (exact decomposition statement)

For data point `x`, prior `p(z)`, decoder `p_theta(x|z)`, and encoder `q_phi(z|x)`:

```
log p_theta(x) >= ELBO(x) = E_{q_phi(z|x)}[ log p_theta(x|z) ] - KL( q_phi(z|x) || p(z) )
```

Equivalently, `ELBO = log p_theta(x) - KL(q_phi(z|x) || p_theta(z|x))`, revealing that the
bound is exactly tight when the encoder equals the true posterior. Both readings are the
standard pair: reconstruction term minus penalty, and log-evidence minus mismatch.

## Gaussian closed forms used everywhere in this lab

Prior `p(z) = N(z; 0, 1)`, posterior `q(z|x) = N(z; mu, sigma^2)`. Then

```
KL( N(mu, sigma^2) || N(0,1) ) = 0.5 * ( sigma^2 + mu^2 - ln(sigma^2) - 1 )
```

If the decoder likelihood is Gaussian `p(x|z) = N(x; z, tau^2)` with scalar `x`,
`tau^2 = 1`, and `q = N(mu, sigma^2)`:

```
E_q[ ln N(x; z, tau^2) ] = -0.5 * ( (x - mu)^2 + sigma^2 ) - 0.5 * ln(2 * pi * tau^2)
```

The second term averages to the mixture density: with `z ~ N(mu, sigma^2)` and decoder
variance 1, the distribution `p(x) = N(x; mu, sigma^2 + 1)` is a convolution products of
two normals, which is how the snippet computes the exact marginal likelihood
`log p(x)` to compare against the bound.

## Reparameterization

Write `z = mu + sigma * epsilon, epsilon ~ N(0, I)`; the Monte Carlo estimate

```
ELBO_hat(x) = log p_theta(x | mu + sigma * epsilon) - KL(q || p)
```

is differentiable in `theta, phi` because sampling enters through `epsilon`, which carries
no learned parameters. Our MC snippet averages 50,000 draws of this one-sample form.

## The reconstruction/regularization trade-off

Introducing a coefficient `beta >= 0` on the KL term (the "beta-VAE" reweighting) shifts
capacity between terms: larger `beta` pulls the posterior toward the prior (smoother,
more disentangled codes at the cost of reconstruction sharpness). The direction of the
trade is the robust part of that literature; magnitude-dependent claims should be treated
as dataset-specific. Keep this conceptual, as in the exercises.

## Pitfall in the bound's reading

`ELBO` is a bound on a single datapoint's log-likelihood, NOT on the total dataset
evidence unless you sum per-point; do not average bounds across points and then compare
against pooled marginal densities.
