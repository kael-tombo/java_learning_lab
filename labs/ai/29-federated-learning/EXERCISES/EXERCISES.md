# Federated Learning — Exercises

Start from the two snippets in CODE_DEEP_DIVE; `javac --release 21` on JDK 21+.

## 1. Re-derive both aggregates before running

With `g = ([0.2, -0.1], [0.4, 0.2], [-0.3, 0.5])` and `n = (1, 2, 3)`, compute uniform and
weighted means on paper, then confirm the console rows `[0.1, 0.2]` and
`[0.016667, 0.3]`. Show the ratio arithmetic in comments.

## 2. Invert the weights

Set `n = (3, 2, 1)` and rerun Snippet 1. Predict the weighted gradient's components by
hand first — `(3*0.2 + 2*0.4 - 0.3)/6 = 0.183333` and
`(3*(-0.1) + 2*0.2 + 0.5)/6 = 0.100000`; the third-round weighted position must then be
`[-0.055, -0.030]`. Verify both predictions against the printed rows and note any
corrections next to them in your log.

## 3. Drift distance versus number of local steps

Modify Snippet 2 to loop local step count `k over {1, 3, 10, 30}` and print, for each,
the norm of `(client-average end - theta_0)` minus `norm of one aggregated step`. Write
one sentence quantifying the growth linearity claim (`~k` behavior) and where it breaks
(the 30-step row will exceed the initial distance scale — number-quote it).

## 4. Client dropout mid-round

Simulate selection: client 2 drops out of round 2 (skip its vector for that round only,
keep it in rounds 1 and 3). Report the four-round trajectory with the missing line
marked. Explain in your log why aggregation with the *previous* round's vector for the
no-show is usually refused (stale-update hazard, said in THEORY).

## 5. Norm screen

Add a guard function `maxNormAllowed = 0.6`: any client whose submitted gradient norm
exceeds it gets scaled down to that bound before aggregation (a crude but standard
anomaly screen). Rerun Snippet 1 with a fifth client `g_5 = [3.0, -2.0]` (`n = 4`) and
report round-3 weighted coordinates with and without the screen; both sets of numbers
go to your log.

## Reporting rule

Numbers must come from your own captured runs; predictions-by-hand get written BEFORE the
run, then confirmed or corrected with a one-line note.
