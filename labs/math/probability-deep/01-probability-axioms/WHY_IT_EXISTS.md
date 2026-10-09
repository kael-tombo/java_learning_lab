# Why It Exists: Probability Axioms

## The problem it replaced
Before 1933 "the probability of X" meant three incompatible things:

1. **Classical (Laplace):** favorable cases / all cases — requires knowing which cases are equally likely, and fails on Bertrand's random-chord paradox (1889), where three natural "uniform" choices give 1/3, 1/4 and 1/2 for the same verbal question.
2. **Frequentist (von Mises):** the long-run limit of relative frequencies — undefined for one-off events like "probability the dam fails this decade."
3. **Personal (de Finetti):** a degree of belief — with no rules for what a coherent belief must satisfy, any number is defensible.

Each camp got different answers to the same problem, and none could say which operations on probabilities were legal.

## What the axioms buy
Kolmogorov's three requirements (1933) are interpretation-free: they constrain the *calculus* while leaving the *modeling* open. All three interpretations then satisfy the same axioms, so:

- The addition and product rules become theorems, not extra assumptions.
- Conditional probability is defined by division — including the regular conditional distribution for continuous spaces, where P(X = x) = 0.
- Expectation, variance and independence are definable from the measure alone, which is what lets the law of large numbers even be *stated* (lab 05).
- Frequentist estimators (lab 06) and Bayesian posteriors (lab 08) can be compared on common ground instead of arguing over what probability *is*.

## What it deliberately does not do
The axioms do not tell you the measure. P(die face) = 1/6 is a modeling commitment; P(disease) = 0.01 comes from data; P(team wins) comes from a market. The axioms only guarantee that whatever you choose, the rest of probability — conditioning, Bayes, expectation — stays consistent and never returns a value outside [0, 1].

## What breaks without the axioms

- **Contradictory answers.** Bertrand's chord problem returns 1/3, 1/4 and 1/2 from three natural "uniform" constructions. The axioms do not pick a winner; they force you to state the measure — which is where the real disagreement lives.
- **Order-dependent totals.** Without countable additivity, infinite sums of probabilities can be rearranged to different limits (Riemann), so "the probability of the even-numbered outcomes" would depend on summation order.
- **Undefined conditioning.** P(A|B) requires dividing by P(B); a framework admitting zero-probability events without limits cannot define the single operation every application performs.
- **No shared calculus.** Frequency (von Mises), logical (Cox) and personal (Savage/de Finetti) readings would each need separate rules; the axioms are thin enough that all three satisfy them — lab 08 depends on this exactly.
- **No guardrail on modeling error.** With axioms, at least *arithmetic* mistakes (a table summing to 1.4) are detectable; without them, nothing distinguishes a modeling choice from a contradiction.

## Why formal axioms arrived when they did

The 1900 Hilbert problems and the parallel rigor movement in analysis exposed a gap: probability arguments in physics and actuarial work used "length of the favorable set / length of all sets" without a definition of length that survived arbitrary limits. Keyles' 1936 frequency-based proposal and von Mises' collective-based approach both failed to define a *probability measure* usable on uncountable spaces. Kolmogorov's 1933 choice — take measure theory's σ-additivity as the single axiom — solved three concrete problems at once: it made conditional probability on null events definable (via regular conditional distributions), it gave a limit theorem framework (convergence of measures), and it unified the discrete (counting) and continuous (Lebesgue) cases under one definition of expectation.
