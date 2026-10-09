# Why It Exists: Law of Large Numbers and CLT

## The problem it replaced
Before the limit theorems, "the average of many observations" had no guarantee at all. Three separate traditions needed the same missing piece:

1. **Games of chance** — Cardano (1564) and Pascal–Fermat (1654) could compute *one* round's odds but had no statement that a casino's nightly take stabilizes. Jacob Bernoulli's *Ars Conjectandi* (1713) supplies exactly that: the relative frequency converges to p, and he even bounded the deviation — though his bound, using only |X − p| ≤ 1, was so loose he needed 25 550 trials to make a wrong call worse than 1/1000.
2. **Astronomy and geodesy** — Laplace and Gauss averaged repeated measurements of the same quantity and *knew* the average was better than any single reading, but the justification was informal until Chebyshev (1867) put an inequality on P(|X̄ − μ| ≥ ε) ≤ σ²/(nε²).
3. **Social statistics** — Quetelet's "average man" (1835) treated a mean over thousands of citizens as a real quantity; Poisson (1837) coined "loi des grands nombres" while criticizing just that usage.

## What the two theorems fix
- **LLN** guarantees the *average* settles (sample mean → μ), which is what makes frequencies usable as estimates of probability in the first place.
- **CLT** (Lindeberg 1922; Lindeberg–Lévy case) says *how* the average fluctuates: X̄ ≈ N(μ, σ²/n) — the 1/√n scale that every confidence interval and standard error in labs 06–07 depends on.

## Why not just one
The LLN says nothing about *shape* or *speed*; convergence can be arbitrarily slow (Poisson's 1897 example of a distribution with mean 0 whose partial sums converge but at any prescribed rate). The CLT needs finite variance — a fact made vivid by the stable laws (Lévy 1925; Mandelbrot 1963 on cotton prices) where variance is infinite and averaging does not produce a bell curve.

## The alternative, and why it failed

**"Enough observations, and you can see the law directly."** Pre-1713 practice was exactly this: no theorem, just the intuition that frequencies stabilize. Jacob Bernoulli's own calculation exposed its cost — with only |X − p| ≤ 1 available, his bound needed 25 550 throws to guarantee staying within 1/1000 of p. The intuition was right and the *rate* was unknowable without the inequality machinery (Chebyshev 1867 needs σ², and immediately gives σ²/(nε²)).

**"Assume the errors are normal and proceed."** Astronomers used Gaussian errors from Bessel and Gauss (1810s–1820s) a full century before any proof that averages become Gaussian — Laplace had the result by 1812 but in non-rigorous form, and Lyapunov's characteristic-function proof did not arrive until 1901. The practice outran the theory for eighty years, which is survivable *only because* the limit turns out to be robust: Lyapunov (finite third moment) and Lindeberg (1922, no identical distribution needed) show how little has to be true for the Gaussian to appear.

**"Just simulate it and look."** Simulation without the theorems cannot distinguish slow convergence from non-convergence, or a valid mean with infinite variance from an unstable one — the St. Petersburg payoffs (1738) have a sample average that wanders forever with no defect in the code. The limit theorems are exactly what turns a wandering trace into a diagnosable statement: E|X| fails → no LLN expected; E|X| < ∞ but no settling → check dependence.

## Two questions worth re-answering after this lab

1. *What did the 1/√n rule ever do for me?* It converts a hardware budget into an accuracy claim: quadruple the samples or accept 2× wider intervals — no third option exists for i.i.d. data, and the Berry–Esseen inversion (HOW_IT_WORKS §7) prices skewness into the count before you buy.
2. *Why two theorems instead of one?* Because "converges" is two separate promises: *where* (LLN, needs E|X| < ∞, no rate) and *how fast/what shape* (CLT, needs finite variance, gives 1.96). Either alone is unusable in practice — the LLN gives no interval, the CLT with no LLN could center on the wrong value — which is why the lab never cites one without the other.

## The demand each theorem now answers

Before 1713 no honest answer existed for "how many observations until I can trust this frequency?" The LLN answers *whether* trust is eventually possible at all (finite mean), the CLT answers *how many* you must buy for a stated margin (via σ/√n), and Berry–Esseen (1945) answers *how wrong the Gaussian shortcut still is* at that n. Every sample-size formula in labs 06–07 is that three-part answer with the arithmetic done.
