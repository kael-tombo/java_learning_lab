# Variational Autoencoders — Theory

A **variational autoencoder** is a generative model that admits a latent variable `z` and
trains a probabilistic decoder `p_theta(x|z)` together with an approximate posterior
`q_phi(z|x)`. Direct maximum likelihood is intractable here because the marginal
likelihood `p_theta(x) = integral p_theta(x|z) p(z) dz` has no closed form for flexible
decoders. The VAE sidesteps it: maximize a lower bound instead of the uncomputable value.

## Architectural picture

- Encoder (inference): maps an input `x` to the *parameters* of a Gaussian over `z` —
  a mean and a variance, not a single code point.
- Latent space: a standard Gaussian prior pulls the distribution of codes toward itself.
- Decoder (generative): a network family that outputs the parameters of a likelihood over
  `x` given a sample of `z`, for instance a Bernoulli per pixel or a Gaussian.

Because the encoder returns only distribution parameters, the model must be trained with
samples of `z`; reparameterization is the trick of writing `z = mu + sigma * epsilon` with
`epsilon` drawn from a fixed normal, so gradient descent sees an additive Gaussian noise
term rather than a sampling node whose derivative is undefined.

## The bound

Training maximizes the evidence lower bound, a quantity that (i) is computable from data
and samples and (ii) never overstates the true log-likelihood. The canonical form says
ELBO equals an expected reconstruction log-likelihood under the encoder's posterior minus
a penalty that keeps the posterior close to its `N(0, I)` reference distribution. Sum the
bound across a minibatch of datapoints and optimize with stochastic gradient methods; this
is the whole training recipe in the original formulation.

## Interpretation and behavior

- With no penalty term, the encoder can memorize... with too strong a penalty, all codes
  become indistinguishable from the prior and the decoder stops using `z` (described below
  with the beta reweighting).
- The gap between the bound and the true log-density equals the mismatch between encoder
  posterior and true posterior for a given `x`; a tighter encoder reduces the gap, and an
  exactly optimal posterior closes it fully — a fact our snippet demonstrates numerically
  with a scalar posterior sweep.
- Encoder collapse (the KL term going to zero) is treated by the beta-reweighting family
  of methods, which trade reconstruction quality for smoother latent structure; that stays
  conceptual here.

## Interface between theory and code

Given a Gaussian prior and Gaussian likelihood-plus-posterior, all bound terms have
closed forms, letting Java reproduce the arithmetic exactly — that is the crux of
CODE_DEEP_DIVE: a numeric demonstration that ELBO never rises above the true marginal.
