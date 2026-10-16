# Model Interpretability — Exercises

## 1. Hand-score the permutation
Cover the output. With rule x1+0.2x2>0.5, labels {0,1,1,0,1,0}, and
reversed x1, predict each of the 6 permuted predictions and the
accuracy 4/6 before running. Uncover and compare with 0.6666666666666666.

## 2. Shuffle x2 instead
Copy the snippet, permute x2 with the same reversal, predict a smaller
drop (x2 weight is only 0.2), run, and rank x1 vs x2. Write why the
rank follows the rule weights on this data.

## 3. Shapley by hand first
With v({})=0, v({1})=4, v({2})=3, v({1,2})=10, compute both orders'
margins on paper: (1,2)->4,6 and (2,1)->3,7, then phi1=5.5, phi2=4.5.
Run ShapleyTiny and confirm plus efficiency_holds=true.

## 4. Dummy player drill
Add a third player with v(S union {3}) = v(S) for all S. State its
Shapley value (0, by the dummy axiom) without code, then extend the
snippet to 6 orders and verify numerically.

## 5. Kernel-width sensitivity
In LimeSurrogate, change width 0.3 to 1.0. Predict the slope still
near 4 but slightly different, run, record both slopes. Write the
stability sentence: coefficients are functions of (model, x0, width,
sample), not of the model alone.

## 6. PDP sketch
For the permutation demo's rule, grid x1 over {0.0,0.2,...,1.0},
average over the 6 observed x2 values at each point, and plot the
positive rate. Mark where the curve jumps and where data is thin.
