# Generative Adversarial Networks — Exercises

Run on JDK 21+; every task compiles with `javac --release 21 -encoding UTF-8`.

## 1. Extend the toy to two data modes

Change the data to two points, `-1.0` and `+1.0`, and evaluate the discrim function on
both when updating (`L_D = log D(-1) + log D(1) + log(1-D(g))`). Verify with your own run
that the generator's single point cannot sit on both modes at once; report where it ends
after 20 alternations. This is mode dropping in miniature.

## 2. Non-saturating switch

Replace the generator step (`drift`, `ascent`) with the *saturating* rule
`dg = -D(g) * w` derived from ascending `log(1 - D(g))`... i.e., compare gradients out of
both surrogates at `D(g) = 0.02`. State in writing which surrogate keeps its magnitude and
why the community calls one of them saturating.

## 3. Track the value function

In Snippet 1 print `V = log D(1.0) + log(1 - D(g))` every 5 iterations. Confirm that it
does NOT shrink monotonically: the alternating updates change `V` in both directions,
which is the signature of a game rather than a minimization.

## 4. Equilibrium distance metric

Instrument both snippets to print `|D(1.0) - D(g)|` at the end. The theory section states
that at a global saddle this quantity is `0.0` with `D = 0.5` everywhere; measure how far
each learning-rate variant lands from that and put the three numbers in a table.

## 5. Second generated point

Give the generator two points `g1, g2` starting at `-0.5` and `+0.5`, updating both with
the non-saturating rule. Brief written answer: does the pair drift toward the data point
symmetrically or asymmetrically? Justify from the logit function's monotonicity, then
check numerically.

## Rules of engagement

Every number you report must come from a run you executed; quote the compile command and
paste the tail of stdout. Hand-deriving gradient formulas in comments is encouraged and
eliminates copying risk.
