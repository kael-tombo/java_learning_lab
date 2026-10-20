# Self-Supervised Learning — Exercises

Based on the two snippets in CODE_DEEP_DIVE; `javac --release 21` everywhere; no
third-party libraries.

## 1. Temperature sweep tableau

Extend Snippet 1 to `tau in {0.05, 0.1, 0.2, 0.5, 1, 2, 10}`; print `p(pos)` and loss per
row. Report where `p(pos)` first falls below `0.5` and write the softmax limit argument
from MATH_FOUNDATION that predicts the `tau -> inf` row value within tolerance.

## 2. Full cosine table for the views

Print the whole 4x4 similarity matrix for Snippet 2's views. Verify three entries from
your own arithmetic: `c[1][2]`, `c[2][0]`, and `c[3][1]`, quoting the dot products used.
The diagonal should print exactly `1.0`; the masked-adjacency loop must skip it.

## 3. Hardest-negative experiment

Insert a new key close to the positive, `[0.5, 0.866]` (cosine to anchor `q` is exactly
`0.5`), and rerun all temperatures. Report `p(pos)` at `tau = 0.1`: it should drop
markedly because exponent gaps of 1.0 instead of 14 no longer saturate. Name the standard
concept: hard negatives sharpen the contrastive signal.

## 4. Gradient intuition (no autograd needed)

From the derivative sketch `(1 - p(+)) * d cos / d anchor`, compute the magnitude when
`p + = 0.997527` versus `0.734212`; confirm the direction of the claim "large p means tiny
gradient". One paragraph relating this to why low temperature slows early training when
the encoder is terrible.

## 5. View-strength ablation

Change `T`'s mix from `0.8*v + [0, 0.2]` to `0.1*v + [0, 0.2]` in Snippet 2 (weaker view),
rerun, and report the NT-Xent mean: weaker views should raise the mean loss because the
positive-pair similarity falls. Quote both means (observed `0.2562` for the original) and
the new positive cosines.

## Verification discipline

Any number reported above must appear in stdout you captured; where a claim depends on a
limit argument, cite which subsection of MATH_FOUNDATION it comes from.
