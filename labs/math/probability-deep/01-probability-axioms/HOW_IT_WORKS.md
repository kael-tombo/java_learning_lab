# How It Works: Probability Axioms

## 1. Building the joint from marginals and conditionals
Start with P(D) = 0.01 and the two conditionals. Each of the four partition cells is one multiplication. The constraint that the four cells sum to 1 is not an extra assumption — it follows from total probability:
0.0099 + 0.0001 + 0.0495 + 0.9405 = 1. This is exactly why the conditional probabilities must sum to 1 over each row: 0.99 + 0.01 = 1 and 0.05 + 0.95 = 1.

## 2. Marginalization: adding a row or a column
P(+) is the column sum 0.0099 + 0.0495 = 0.0594. Marginalization is how you *leave* a conditioning variable behind; you never need the full joint to answer a question about one variable — you sum the rest out.

## 3. Conditioning: one division, at the end
P(D|+) = 0.0099/0.0594. The numerator is a joint, the denominator is the marginal of the observed event. Doing the division first (e.g. dividing each cell by 0.01 as you go) introduces rounding into every cell and then propagates it; the axioms only require the ratio to be right.

## 4. Independence: a factorization test
Two events are independent iff the joint equals the product of marginals. Test: 0.0099 vs P(D)·P(+) = 0.01 × 0.0594 = 0.000594. They differ by 16.7×, so disease and a positive test are strongly dependent — which is the whole point of the test. Independence is a numerical property you can check, not a feeling about whether two things are "related."

## 5. Countable additivity in practice
Flipping a fair coin until the first head: P(first head at position k) = (1/2)^k. Summing the geometric series Σ_{k≥1} (1/2)^k = 1 — only countable additivity licenses exchanging the infinite sum with the probability, and it is what guarantees a stopping time almost surely exists.

## 6. Why the axioms hold up
Non-negativity, normalization and countable additivity are preserved by marginals (sum rows), conditioning (divide by a positive constant) and limits (continuity from below). So derived quantities inherit validity; no operation in the pipeline can smuggle in a probability outside [0, 1].

## Micro-example: conditioning on a partial observation

Roll two dice and learn only that the maximum is 5. Of the 36 cells, exactly 9 survive: the pairs where max = 5, each still equally likely *inside the conditioning event*. So P(sum ≥ 10 | max = 5) = {(4,5), (5,4), (5,5)} = 3/9 = 1/3, versus the unconditional P(sum ≥ 10) = 6/36 = 1/6. Conditioning doubled the probability because the surviving cells are biased toward large sums — the mechanism behind every Bayesian and screening update later in this course.

## Where each operation belongs in code

- Product rule: one multiply per joint cell — no division yet, so no rounding hot spot.
- Marginalization: sum over the variable you are *not* keeping — this is where a variable leaves the model.
- Conditioning: exactly one division, by the observed event's marginal, performed once at the end of the pass.
- Normalization check: after the division the surviving cells must total 1; assert it and you catch table bugs immediately.
