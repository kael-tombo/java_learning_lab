# Multi-Task Learning — Exercises

Each builds on the snippets in CODE_DEEP_DIVE; compile with `javac --release 21`.

## 1. Predict the weight flip

Before running anything, compute by hand the combined first coefficient for
weights `(1, 10)` on `(gA, gB)` given `gA = [-6, -3.5]` and `gB = [0.183104, 0.274317]`.
Which single weight makes the derivative's first component exactly zero? Arithmetic gives
`w = 6 / 0.183104 ≈ 32.77` — confirm numerically, then explain in one sentence what
happens near that balance (the step becomes a pure second-component move).

## 2. Interference profiling across initializations

Run Snippet 1's pair of heads from `(w1, w2) in {(0.5, 0.5), (2, 1), (1, 2)}` (edit the
constants). For each, print the two losses and the cosine of the two gradients. Report
whether sign agreement or magnitude dominance changes first as `(w1, w2)` moves; write a
one-line verdict: interference depends on BOTH initialization and task scaling.

## 3. Projection harms whom?

Using Snippet 2 with an artificially stronger conflict, `gB = [6.0, -2.0]` (antisymmetric
toward `gA`), compute the projected `gB'` norm over `|gB|` before and after. Where losses
stay the same, quantify how much second-task strength is sacrificed by the projection
rule at this conflict level; compare against what an equal-weighted sum would do to the
first task's descent direction.

## 4. Rebuild the balancing scheme

Replace `sigma_t = sqrt(L_t)` in Snippet 1 with `sigma_t` fixed at `(1.0, 0.25)` — the
uncertainty-heuristic proper — and print `(w_A, w_B)` and the combined gradient.
Expected: task A de-emphasized far more because `1/(2 * 1) = 0.5` against `1/(2*0.0625) = 8`,
ratio 16; verify exactly that and note it in your capture log.

## 5. Report card

Write a `DecisionTable` to stdout: for each of the four strategies from the snippets
(uniform, 20x upweight, sqrt-balanced, projected-orthogonal), the two per-task losses and
the multi-config direction sign after one step of `lr = 0.01` from `(0.5, 0.5)`.
Conclude which strategy and which task's loss agrees best with your expectations from
THEORY, citing run lines — and where a strategy surprised you, flag that line.

## Collection rule

Your submission is a log file plus one Java file; every claim maps to a printed row.
