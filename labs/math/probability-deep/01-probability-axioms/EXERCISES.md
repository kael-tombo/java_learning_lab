# Exercises — Probability Axioms

Each solution cites a number that was computed (the exercises reuse the
arithmetic environment of CODE_DEEP_DIVE.md; snippet statements appear
once there and are not repeated here).

## Problem 1. Three Events, One Union
Roll one fair die. Let A = even faces, B = faces at most 3, C = {2, 3}.
Compute P(A ∪ B ∪ C) two ways.

**Solution**: Exact pieces: P(A) = 1/2, P(B) = 1/2, P(C) = 1/3;
pairwise intersections P(A∩B) = P(A∩C) = P({2}) = 1/6, P(B∩C) = 1/3;
triple overlap P(A∩B∩C) = 1/6. Inclusion–exclusion:
1/2 + 1/2 + 1/3 − 1/6 − 1/6 − 1/3 + 1/6 = 5/6.
Direct way: the union is {1,2,3,4,6} (6 and 5 are the only exclusions),
which has 5 of 6 faces, so 5/6. Both routes agree exactly.

## Problem 2. Evidence Kept in Fraction Form
With the worked medical scenario (prior 1/100, sensitivity 99/100, FPR
1/50), suppose a second, independent test comes back positive too.
Compute the posterior.

**Solution**: After the first positive the machine showed P(D | +) = 1/3.
Treat that as the new prior. Given disease status, the second test is
independent, so the likelihood ratio repeats:
numerator (1/3)(99/100) = 33/100; denominator 33/100 +
(2/3)(1/50) = 33/100 + 1/75 = 103/300. Posterior =
(33/100)/(103/300) = 99/103 ≈ 0.9612 (executed: 99/103). One flip
raised credibility from 1/3 to about 96%; that is the squaring effect
of repeat evidence on odds.

## Problem 3. Track a Posterior by Hand-Check Fractions
Use the partition C1 = {1,2,3}, C2 = {4,5,6} on a fair die with the
event A of even faces. Verify the law of total probability and then give
P(C2 | A).

**Solution**: Exact conditionals from the run: P(A | C1) = 1/3 and
P(A | C2) = 2/3. Then P(A) = (1/2)(1/3) + (1/2)(2/3) = 1/2, equal to the
direct value — the bookkeeping closes. Bayes:
P(C2 | A) = (1/2 · 2/3)/(1/2) = 2/3, complementing the second problem's
direction and matching the run's P(C1 | A) = 1/3.

## Problem 4. Programming Exercise
Write a function `posterior(prior, sens, fpr)` using `fractions.Fraction`
that returns P(D | +) as an exact fraction, then run it for the Problem 2
chain twice (1/100 then 1/3) and confirm the two outputs are 1/3 and
99/103. Guard: raise on prior outside (0, 1).

**Solution skeleton**:

```python
from fractions import Fraction as F

def posterior(prior, sens, fpr):
    if not (0 < prior < 1):
        raise ValueError("prior must lie strictly between 0 and 1")
    pos = prior * sens + (1 - prior) * fpr
    return prior * sens / pos

print(posterior(F(1, 100), F(99, 100), F(1, 50)))
print(posterior(F(1, 3), F(99, 100), F(1, 50)))
```

The executed pair of outputs is 1/3 and 99/103, matching the analytic
values above; the guard fires on an all-or-nothing prior, where the
formula would divide by a zero-mass conditioning.

## Problem 5. Which Conditioning Violates Which Identity
For the die events of Problem 1, evaluate P(C | A) + P(C | B).

**Solution**: Exact from the run: P(C ∩ A) = P({2}) = 1/6 gives
P(C | A) = (1/6)/(1/2) = 1/3, and P(C | B) = P({2,3})/P(B) =
(1/3)/(1/2) = 2/3. Their mixed sum 1/3 + 2/3 = 1 is a coincidence of
this die, not an identity; always-valid is the within-one-conditioning
form — P(C | B) + P(C^c | B) = 1, since C^c ∩ B = {1} contributes
1/3 on the same model.
