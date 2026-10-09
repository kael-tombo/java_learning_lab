# Architecture: Probability Axioms Implementation

## Module layering
```
com.mathlab.probaaxioms
├── space/      SampleSpace, Outcome, BitSetEvent   (structure only)
├── measure/    ProbabilityMeasure, WeightTable     (assigns mass to outcomes)
├── rules/      ProductRule, InclusionExclusion, Bayes
├── exact/      Rational, BigIntFraction            (oracle for doubles)
├── montecarlo/ UniformSampler, Estimator           (approximate answers)
└── check/      NormalizationInvariant, SumAssertion
```
Dependencies point strictly downward: `rules` never touches `space` internals, `montecarlo` reads the measure but cannot mutate it.

## Why the measure is a separate object
Events describe *what* can happen; the measure says *how much* mass each outcome gets. Keeping them apart lets one sample space carry several measures (uniform dice vs. loaded dice) — the Bertrand-paradox mistake is then a model choice you make explicitly rather than buried inside event construction.

## Invariants enforced at construction
1. Weights are ≥ 0 (negative mass throws immediately).
2. Weights sum to 1 within 1e-12, or the constructor normalizes and records that it did.
3. The universe mask covers every defined outcome, so complements are closed.
4. Conditioning requires P(B) > 0; a zero-probability conditioning event is a typed error, not NaN.

## Patterns used
- **Strategy**: exact-rational and double evaluators implement one `ProbabilityEvaluator` interface; tests run both and compare within 1e-12.
- **Immutable measure**: conditioning returns a *new* measure (posterior), never mutates the prior — required so a prior can be reused across many independent observations.
- **Composite events**: unions/intersections build an expression tree evaluated lazily; the tree can be printed as the probability tree shown in VISUAL_GUIDE.md.

## Test topology
Unit tests per rule (product, marginalization, conditioning), property tests asserting `Σp = 1` after every operation, and one analytic oracle test: the two-dice table, the Monty Hall switch rate 2/3, and the medical-test posterior 1/6 — all computed by hand to full precision.
