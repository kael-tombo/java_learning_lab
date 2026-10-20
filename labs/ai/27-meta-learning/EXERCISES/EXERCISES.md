# Meta-Learning — Exercises

Built on the two snippets in CODE_DEEP_DIVE; `javac --release 21` throughout.

## 1. Derive the inner contract closed form

For task A at `lr = 0.05`, prove by induction `a_k = 0.5 * (1 - 0.6^k)` and check it
against the printed `0.46112` at `k = 5`. Do the same for task B:
`b_k = -0.5 + 0.5 * (-0.6)^k`. Both derivations belong in your source comment block.

## 2. Inner-loop divergence demo

Rerun Snippet 2's task B inner loop with `lr = 0.1` for 8 steps WITHOUT the Reptile
interpolation. Report the 8 values; the update factor becomes `-2.2` and magnitudes blow
up (11.2128 by step 4). State the stability bound in one line: a scalar Newton-like step
on curvature `c` needs `lr < 2/c`, and `2/32 = 0.0625` here.

## 3. Meta-step sweep

Modify Snippet 1 to loop `inner alpha` over `{0.02, 0.05, 0.1, 0.25}` for task A and
report the query loss at `theta1` each time. At the largest alpha, does the query loss
beat the no-adaptation initial loss of `2.25`? Explain overshoot in one sentence using
the fixed point 0.5.

## 4. Three-task generalization

Add task C: `y = 0.25x`, support `(4, 1)`, query `(6, 1.5)`. Predict on paper the FOMAML
gradient sign at `theta0 = 0`, then confirm; after computing all three tasks' meta-steps
with `beta = 0.1`, state which task dominates the averaged meta-point and by what ratio
(gradient-magnitude comparison, one number).

## 5. Reptile with epsilon schedule

Change Snippet 2 to use `epsilon_k = 0.5 / sqrt(k)` across 20 meta-rounds, keeping inner
k = 5 fixed, and print theta after each round. Expected qualitative shape: an initial fast
walk toward the between-task mean, then tiny corrections; report the theta values at
rounds 1, 5, 20 and the total displacement from 0.0.

## Output authenticity

Quote each claimed number from stdout you captured after an actual run; any formula cited
above must appear verbatim in a comment of the modified source.
