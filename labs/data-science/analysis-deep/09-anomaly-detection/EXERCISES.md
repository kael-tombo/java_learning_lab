# Exercises - Anomaly Detection

## 1. Masking demo (runnable)

Copy AnomBase, add a second 30.0 (12 points). Show both extremes now
score |z| < 3 while IQR still flags them. Write the two-sentence lesson
(robust spread resists; sd does not).

## 2. MAD variant (runnable)

Replace mean/sd with median/MAD (MAD = median |x - median|, robust
z = 0.6745*(x-median)/MAD). Flag robust-|z| > 3.5 on the 12-point set
from Exercise 1 and compare flags with both classic rules.

## 3. Full P/R curve (runnable)

Extend PrCurve to thresholds 0.05..0.95 in steps of 0.05. Print the
table, find the max-F1 threshold, and state its P/R. Explain why max-F1
is a default, not a decision (costs decide).

## 4. Your volumes, your PPV (runnable)

Copy BaseRate with your system's prevalence and daily volume. Print PPV
plus expected true/false alerts per day. If false pages exceed on-call
tolerance, compute the fpr needed for PPV = 0.5 at fixed sens = 0.99.

## 5. Joint anomaly hunt (paper)

Two features, each healthy in [9, 11], but valid points always satisfy
x + y in [19, 21] (they move in opposition). Give a pair both margins
accept yet the sum rejects (example: (10.9, 10.9) sums to 21.8), and
name the method family (isolation/multivariate) that catches it while
univariate fences stay silent.

## 6. Tier design (paper)

PPV 0.09, 1000 flags/day, one on-call engineer. Design three tiers with
volumes each, response times, and the outcome log fields. Show the math
that keeps pages under ~5/night.

## 7. Threshold from costs (runnable)

Miss cost $500, false-page cost $5. Extend PrCurve to compute expected
cost per decision at each 0.05 threshold and print the minimizing one.
State its P/R and explain why it differs from the max-F1 threshold.

## 8. Drift response drill (paper)

Flag rate triples overnight with no known incident; precision-at-20
halves. Write the five-line response: freeze, compare center/spread,
identify the shifted input, re-fit Window, re-sweep thresholds.
