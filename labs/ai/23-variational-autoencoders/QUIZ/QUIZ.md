# Variational Autoencoders — Quiz

Standard answers, no trick questions; key made explicit.

**Q1. State the ELBO decomposition.**
A: `ELBO(x) = E_{q(z|x)}[ log p(x|z) ] - KL( q(z|x) || p(z) )`, a valid lower bound on
`log p(x)`.

**Q2. Why is the true log-likelihood intractable for flexible decoders?**
A: The marginal `integral p(x|z) p(z) dz` over all latent codes has no closed form, so we
optimize the computable bound instead.

**Q3. What does the second reading of ELBO (`log p(x) - KL(q || p(z|x))`) imply about
tightness?**
A: The gap is exactly the encoder's mismatch with the true posterior; choosing
`q = p(z|x)` makes the bound tight.

**Q4. Write the 1D Gaussian pair's KL.**
A: For `q = N(mu, sigma^2)` vs `N(0,1)`:
`0.5 * (sigma^2 + mu^2 - ln sigma^2 - 1)`.

**Q5. What problem does reparameterization solve?**
A: The decoder becomes differentiable in the encoder's parameters — `z = mu + sigma*eps`
moves the randomness out of the computation graph.

**Q6. What is encoder (posterior) collapse?**
A: The KL term drags `q(z|x)` onto the prior for many `x`; codes stop carrying
information and the decoder stops relying on `z`.

**Q7. In our sweep, which variance closed the gap to zero and why?**
A: `sigma^2 = 0.5` (with `mu = 1` for `x = 2`), because `N(1, 0.5)` is the true posterior
of the model there.

**Q8. Does raising beta above 1 sharpen or smooth reconstructions?**
A: Larger beta over-penalizes the KL, pulling codes toward the prior — reconstruction
typically softens; that trade is the beta-VAE idea at conceptual level.

**Q9. When does a beta-modified objective stop being a bound?**
A: At any `beta != 1` it is a different (still useful) objective; only the plain form
majorizes `log p(x)`.

**Q10. Reparameterization in one line?**
A: Draw `z = mu + sigma * epsilon`, epsilon from a fixed normal, so gradients reach the
encoder's parameters through `mu` and `sigma`.
