# Self-Supervised Learning — Mathematical Foundation

## InfoNCE, the contrastive log loss (exact statement)

Given an anchor embedding `q`, a positive key `k+`, and negatives `k-1..k-M`, and cosine
similarities `s_i = cos(q, k_i)`:

```
InfoNCE(q, k+, {k_i}) = -log [ exp(s+ / tau) / sum_i exp(s_i / tau) ]
```

with `tau` the temperature, usually a small positive constant. The quantity inside the log
is exactly the softmax probability of the positive; hence `0 < loss < log(M + 1)`, and
loss #0 is a from-scratch ceiling while a perfectly aligned anchor reaches toward zero.

## Softmax limits to be able to quote

- As `tau -> 0+`: the argmax candidate takes probability -> 1, so the loss tends to
  `0` if the positive has the largest similarity, and blows toward `M+1... = log(M+1)`
  style ceiling magnitudes when it does not.
- As `tau -> infinity`: all `s_i / tau -> 0`, probabilities equalize to `1/(M+1)`, and the
  loss ceiling approaches `log(M + 1)` — no discrimination at all.

## NT-Xent, the two-view softmax variant (SimCLR-style form)

For a batch of two samples and their two views {a1, a2, b1, b2} with positives
`(a1, a2)`, `(b1, b2)`:

```
l(i, j) = -log exp(s_ij / tau) / sum_{k != i} exp(s_ik / tau)
L = ( l(1->2) + l(2->1) + l(3->4) + l(4->3) ) / 4
```

i.e., each ordered anchored term excludes the self-similarity (masked diagonal) and
averages both directions per positive pair — the standard SimCLR statement retained here
in its 4-sample form.

## Why cosine and temperature, not raw dot products

Cosine bounds `s in [-1, 1]`, which keeps exponent arguments modest for moderate `tau`;
dot products scale with embedding norm and would force per-model learning-rate games.
`tau` inside the exponent acts like a gain knob: `exp(s / tau)` magnifies small
similarity differences quadratically-ish in effect (compare the observed rows for
`tau = 0.1` vs `1.0` in CODE_DEEP_DIVE).

## Aggregation intuition worth deriving once

Derivative of the loss wrt the anchor pulls `q` toward the positive only in proportion to
`spot error = 1 - p(+)`; with a dominant positive (tau small, p near 1) gradients are tiny,
with hard negatives they are large. Standard analysis, no exotic assumptions needed.
