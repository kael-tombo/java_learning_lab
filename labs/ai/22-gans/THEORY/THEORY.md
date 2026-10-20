# Generative Adversarial Networks — Theory

A **generative adversarial network** is a two-player game between a generator `G`, which
maps noise `z` to synthetic samples, and a discriminator `D`, which scores inputs as real
or fake. $G$ tries to make samples that $D$ cannot distinguish from data; $D$ tries to keep
telling them apart. Training is the search for an equilibrium of this game, not for a
single global minimum.

## The game and its equilibrium

- Generator: transforms a low-dimensional latent vector into a candidate sample.
- Discriminator: a binary classifier without any generative component.
- Equilibrium: the theoretical result for a large, flexible $D$ is that the globally
  optimal discriminator for a fixed generator is the posterior ratio
  `p_data(x) / (p_data(x) + p_model(x))`.
- Another standard fact: at the true optimum, the generator has collapsed the model onto
  the real data distribution entirely, the discriminator outputs one-half everywhere... and
  — this is the classic parity result — neither side can improve further because fake and
  real are matched exactly.

## Training dynamics

In practice both networks are updated alternately:

1. Sample a real batch and a fake batch; ascend the discriminator objective on both.
2. Sample a fresh fake batch; ascend the generator's objective (with a so-called
   non-saturating surrogate so that early, hopeless-looking samples still carry gradient).
3. Alternate until samples look plausible or until dynamics become clearly unstable.

Known failure modes covered conceptually in this lab: oscillation, vanishing generator
gradient when the discriminator wins outright, and mode dropping (the generator covering
fewer data modes than the true distribution).

## Evaluation

There is no single likelihood-based score because the game is implicit — the model samples,
it does not expose densities. Evalua-tion in practice uses sample-level heuristics
(quality + diversity rankings, a trained classifier's confidence at fake samples) and
human review; treat all such metrics as proxies and say so in reports.

## Why Java learners should care

The alternating-updates pattern is a general tool: any system where two components' losses
fight (blind ranking, a policy and its critic, simulated opponents) follows the same
template. Our snippets reproduce the essential dynamic on one scalar with zero
dependencies, then show how step size destabilizes the game.
