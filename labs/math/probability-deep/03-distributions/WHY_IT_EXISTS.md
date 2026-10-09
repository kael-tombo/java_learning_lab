# Why It Exists: Probability Distributions

## The problem: chance has shapes, and shapes repeat
Before named families, every new random phenomenon demanded a fresh combinatorial derivation. What emerged historically was that *the same shapes keep recurring* because the same mechanisms do:

- **Independent binary trials** always produce the binomial (Bernoulli, 1713) — coin flips, defectives in a batch, click/no-click.
- **Rare events in a fixed exposure** always produce the Poisson (Bortkiewicz, 1898: cavalry deaths per corps-year; Erlang, 1917: calls arriving at an exchange).
- **Sums of many small influences** always produce the normal (de Moivre 1718, Laplace 1812) — measurement error, biological variation, portfolio components.
- **Multiplicative accumulation** always produces the lognormal (Gibrat, 1931, for firm sizes; later income, file sizes).
- **Minimum-of-many** always produces the extreme-value laws (Fisher & Tippett, 1928) — flood peaks, material strength, maximum daily load.

A distribution is therefore a *compressed description of a mechanism*. Naming it once means every future instance shares one implementation, one set of tables, one body of limit theory.

## What the catalog buys
1. **Closed forms where none would otherwise exist**: convolution of Poissons is Poisson; a normal's sum is normal — no numerical integration.
2. **Limits as approximations with bounds**: Berry (1941) and Esseen (1942) quantified the normal approximation error (∝ 1/√n), so you know when the shortcut fails.
3. **A parameter space for estimation**: once the family is chosen, labs 06 (MLE) and 07 (tests) reduce to estimating 1–3 numbers instead of an arbitrary function.
4. **Conjugacy for Bayesian updating** (lab 08): Beta × Binomial, Gamma × Poisson, Normal × Normal close algebraically.

## The honest caveat
The catalog is open-ended: Poisson (1837) protested that his own "law of large numbers" was over-applied to data that were not rare-event counts. Family selection is a *modeling* act requiring goodness-of-fit evidence (lab 07's χ²/KS tools), not a naming convenience — hence `fit/` and `GoFTest` living beside the distributions in ARCHITECTURE.md.

## Why a catalog of named distributions exists

Frequentist and computational work both need to *reuse* a distribution: an estimator's sampling distribution must be derived once and applied everywhere, a simulation must sample millions of draws fast, and two scientists must be able to say "we both used a gamma(2, scale=3)" without ambiguity. The named families are the vocabulary that makes this reuse possible — they are exactly the distributions that are (a) closed under the operations that occur in practice (sums, conditioning, superposition), (b) estimable from a few sufficient statistics, and (c) tabulatable.

## What fails without them

- **Inference becomes per-dataset numerics.** Gosset's t-ratio only became usable because the t family was tabulated once (1908) and printed; without a named family, every experiment would need its own Monte Carlo calibration.
- **Sampling loses speed.** Specialized algorithms (BTPE for binomial, Marsaglia–Tsang for gamma) exist only because the families are fixed; a "general" sampler for an arbitrary density costs orders of magnitude more per draw.
- **Communication becomes imprecise.** "Overdispersed counts" says actionable things to a statistician; "the histogram looks a bit bumpy" does not.

## The design principle

A distribution earns its name by *composability*: Poisson counts stay Poisson under superposition, gamma waiting times stay gamma under addition, normal errors stay normal under linear maps. Families that lack such closure still exist (they are described by their CDF or likelihood instead), but they never become standard vocabulary.
