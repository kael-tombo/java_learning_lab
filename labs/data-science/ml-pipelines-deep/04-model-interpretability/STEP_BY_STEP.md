# Model Interpretability — Step by Step

## Step 1. Run the permutation demo
Compile and run PermutationImportance. Confirm baseline_acc=1.0,
permuted_x1_acc=0.6666666666666666, importance_x1=0.33333333333333337.
Recompute by hand: rule x1+0.2x2>0.5 is perfect on the 6 rows; the
reversed-x1 predictions miss rows 2 and 5, so 4/6 = 0.6667.

## Step 2. Split the Shapley game by hand
v({})=0, v({1})=4, v({2})=3, v({1,2})=10. Orders: (1,2) gives margins
4 then 6; (2,1) gives 3 then 7. Average per player: phi1=(4+7)/2=5.5,
phi2=(3+6)/2=4.5. Run ShapleyTiny and confirm, including
efficiency_holds=true.

## Step 3. Fit the local surrogate
Run LimeSurrogate at x0=2 for f(x)=x^2. Confirm slope
3.9999999999999982 (true gradient 4), intercept 4.057135543484657,
slope_close_to_4=true. Change kernel width 0.3 to 0.6, predict the
slope moves slightly, run, and record both.

## Step 4. Shuffle the other feature
Extend the permutation demo to shuffle x2 instead of x1. Predict a
smaller drop (x2 has weight 0.2 in the rule), run, and compare ranks.
This is the correlated/weighted-features lesson in miniature.

## Step 5. Break efficiency on purpose
In ShapleyTiny, change v({1,2}) to 9 without changing singles.
Predict sum 10.0 != 9.0 and efficiency_holds=false. Run, confirm, and
state why the efficiency gate catches inconsistent value functions.

## Step 6. Sketch a PDP by hand
For the demo rule over x1 in {0.0,...,1.0} with x2 averaged over its 6
values, compute the positive rate per grid point. Plot and read the
threshold shape. Mark grid regions with no nearby rows.

## Step 7. Write the explanation report
One page per method: question, model/dataset versions, settings, raw
numbers, stability rerun spread, and the non-causal disclaimer.
