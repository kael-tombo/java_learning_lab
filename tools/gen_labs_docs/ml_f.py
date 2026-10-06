# -*- coding: utf-8 -*-
"""Tailored specs for labs/ml/lab09 .. lab10."""

from ml_a import URLS_ML

SPECS = []

# ---------------------------------------------------------------- lab09
SPECS.append(dict(
    track="ml", lab="lab09", full_set=True, level="Advanced",
    title="Gradient Boosting", main_class="com.ml.lab09.Main",
    problem="A single shallow tree underfits. Sequentially adding many of them, "
            "each correcting the last, fits nearly as well as a deep model while "
            "keeping the pieces interpretable.",
    why_now="Boosting is the default for tabular prediction. Its two knobs \u2014 the "
             "learning rate and the number of rounds \u2014 are the bias-variance dial of "
             "practical machine learning.",
    objectives=[
        "Derive the gradient-boosting update from the negative gradient of a loss",
        "Implement regression and logistic boosting with shallow trees as weak learners",
        "Explain the difference between gradient boosting and AdaBoost",
        "Use the learning rate and n_estimators as a joint regularisation pair",
        "Diagnose overfitting with validation curves and early stopping",
        "Read feature importance and SHAP-style contributions from an additive model",
    ],
    concepts=[
        ("Stage-wise additive fitting",
         "F\u2098(x) = F\u2097\u208b\u2081(x) + \u03b7 h\u2098(x). Each new weak learner fits the negative "
         "gradient of the loss with respect to the current prediction, so the "
         "ensemble improves monotonically on the training objective. It is boosting "
         "in the functional-gradient sense, not a reweighting scheme."),
        ("The learning rate is the real hyperparameter",
         "\u03b7 scales every weak learner's contribution. Small \u03b7 with many rounds is a "
         "fine-grained, well-regularised fit; large \u03b7 with few rounds is coarse and "
         "fast. The pair (\u03b7, M) is one regularisation dial \u2014 tune it jointly, "
         "never separately, and always with early stopping as the backstop."),
        ("Gradient boosting versus AdaBoost",
         "AdaBoost reweights misclassified samples and fits a classifier on the "
         "reweighted set. Gradient boosting fits residuals or gradients directly, "
         "which generalises to any differentiable loss \u2014 squared error, absolute "
         "error, logistic \u2014 with no reweighting trick. XGBoost and LightGBM add "
         "regularisation and histogram binning to the same idea."),
        ("Early stopping and the eval set",
         "Boosting overfits monotonically on training loss while validation loss turns. "
         "The standard protocol reserves a validation split, tracks validation loss "
         "every round, and stops at the best round with a patience window. In "
         "production, ship the best-round count, not the last round."),
        ("Subsampling as stochastic regularisation",
         "Stochastic gradient boosting samples a fraction of rows per tree. This "
         "decorrelates the trees the same way feature randomness does in a random "
         "forest, which is where a good part of its robustness comes from."),
        ("Additivity makes it explainable",
         "Because the model is a sum of trees, a prediction decomposes exactly into "
         "per-feature contributions. This is the basis of treeSHAP and of the "
         "reason-code systems risk teams need \u2014 a property no other strong tabular "
         "model offers as cleanly."),
    ],
    formulas=[
        ("F\u2098(x) = F\u2097\u208b\u2081(x) + \u03b7 h\u2098(x)", "Boosting update", "add a weak learner, scaled"),
        ("r\u1d62 = y\u1d62 \u2212 F(x\u1d62)", "Residual (squared error)", "negative gradient for least squares"),
        ("g\u1d62 = p\u1d62 \u2212 y\u1d62 (log loss)", "Negative gradient (logistic)", "the analogue for classification"),
        ("\u03b7 \u2208 (0, 1]", "Learning rate", "shrinkage; small \u03b7 needs more rounds"),
        ("v(x) = \u03a3_{m} \u03b7 T\u2098(x)", "Ensemble value", "sum of tree outputs, exactly additive"),
        ("early stop at argmin_m val_loss(m)", "Early stopping", "the standard safeguard"),
        ("SHAP_i \u2248 \u03b3^T E[|S \u222a {i}|]", "TreeSHAP", "exact additive attribution for tree ensembles"),
    ],
    flow=[
        "Split into train/validation/test; the validation split drives early stopping and is not the test set.",
        "Initialise F\u2080 with a constant (mean target, or log-odds for logistic loss).",
        "For each round m: compute negative gradients, fit a shallow tree on them, update F \u2190 F + \u03b7 h\u2098.",
        "Track validation loss every round; keep the best round.",
        "Sweep \u03b7 and depth jointly, and pick the pair with the best validation loss at a comparable round count.",
        "Fit the final model with the chosen M, then extract SHAP values for explanations and importance.",
    ],
    assumptions=[
        "The loss is differentiable and the weak learner can fit its negative gradient",
        "Trees are deliberately shallow (depth 1\u20136); depth and boosting interact strongly",
        "Shrinkage is used; \u03b7 = 1 with many rounds overfits almost immediately",
        "Validation data is separate from training and from the final test set",
        "Features are handled the same way at train and serve time (no target leakage in splits)",
        "Early stopping is available; without it the model will train past its optimum",
    ],
    pitfalls=[
        ("Train loss keeps falling, validation loss turns at round 40", "training continued past the optimum", "early stop on validation loss and ship the best round"),
        ("The model is worse than a random forest", "depth too large and \u03b7 too small, or no subsampling", "try depth 2\u20133, \u03b7 0.05\u20130.1, subsample 0.8"),
        ("SHAP values sum to something other than the prediction", "missing the baseline expectation term", "use the tree_path_dependent method and verify the additivity identity"),
        ("Predictions change after deploy", "categorical encoding or scaling done outside the estimator", "version preprocessing inside the model artifact"),
        ("Training is slow on 5M rows", "exact splits on all features", "histogram binning: pre-bucket features into 64\u2013256 bins"),
        ("Boosting importance looks like importance", "correlated features split credit arbitrarily", "use SHAP values on held-out data, not gain-based importance"),
    ],
    java=[
        ("int[] binIndex per feature", "histogram binning turns split search into integer counting"),
        ("PriorityQueue<Double> leafValues", "SHAP value computation over tree paths"),
        ("Arrays.sort on per-feature histograms", "the classic boosting inner loop"),
        ("SplittableRandom", "per-tree row subsampling that stays reproducible"),
        ("double[][] featureImportance by gain", "cheap first pass before investing in SHAP"),
    ],
    links=[
        "**Lab 03** supplies the weak learner; here it is a shallow tree added sequentially.",
        "**Lab 01** supplies the residuals that squared-error boosting fits.",
        "**Lab 02** supplies the logistic loss whose gradient boosting also minimises.",
        "**Lab 10** gives the validation protocol that early stopping depends on.",
    ],
    checklist=[
        "I can derive the boosting update as functional gradient descent",
        "I tune learning rate and rounds jointly, with early stopping",
        "I know how boosting differs from AdaBoost and from random forests",
        "I can compute and verify SHAP additivity",
        "I use histogram binning when n is large",
        "I never report boost importance without saying what it measures",
    ],
    cards=[
        ("What is gradient boosting, formally?", "Stage-wise functional gradient descent: each new weak learner fits the negative gradient of the loss with respect to the current prediction."),
        ("How does it differ from AdaBoost?", "AdaBoost reweights samples; gradient boosting fits gradients directly, which works for any differentiable loss."),
        ("What does the learning rate do?", "Scales each weak learner's contribution. Small \u03b7 needs more rounds but generalises better."),
        ("Why shallow trees?", "Depth controls the interaction order per tree; boosting adds depth across rounds, so depth 1\u20133 is usually enough."),
        ("Why is early stopping essential?", "Training loss falls monotonically while validation loss turns; without stopping you ship the overfit tail."),
        ("What does stochastic gradient boosting sample?", "A fraction of rows per tree, decorrelating the trees like feature randomness does in forests."),
        ("Why is boosting explainable?", "The model is an exact sum of trees, so per-feature contributions add up to the prediction (treeSHAP)."),
        ("Why is exact split search too slow at scale?", "It sorts and considers every distinct value per feature per node; histogram binning reduces this to a few hundred bins."),
    ],
    extra_cards=[
        ("How do you choose the number of rounds?", "From validation loss with a patience window; ship the best round, not the last."),
        ("What is the initial prediction F\u2080?", "The value that minimises the loss with no features: the mean for squared error, the log-odds for logistic loss."),
        ("When does boosting beat a random forest?", "On medium-sized tabular data with strong signal in a few features, and when you need the additive explanations."),
        ("What causes a boosting model to underfit?", "Too few rounds, too small a learning rate, too shallow trees, or unscaled/unsuitable features."),
    ],
    math_why="Boosting turns learning into optimisation: the loss is the objective, "
             "the residual is the gradient, and the tree is the optimiser. Once "
             "that framing lands, the loss function becomes a plug-in choice and "
             "the only real questions are regularisation and early stopping.",
    math=[
        ("From residuals to functional gradients",
         "F_m(x) = F_{m-1}(x) + eta * h_m(x)\nr_i = y_i - F(x_i)                 (least squares)\nr_i = p_i - y_i               (logistic)\nF_m(x) = F_{m-1}(x) + eta * h_m(x),  h_m fits r",
         "The residual is the negative gradient of the squared loss with respect to "
         "F(x). Gradient boosting generalises this to any differentiable loss, which "
         "is why it fits classification as easily as regression.",
         "y = [1, 3, 5], F = [1, 1, 1]. Residuals = [0, 2, 4]; the next tree fits "
         "them and F becomes [1, 3, 5]. Squared loss drops from 20/3 to 0."),
        ("Shrinkage as regularisation",
         "gradient of regularised objective:\nG_M(x) = sum_m eta * h_m(x) + lambda * ||h_m||^2 / 2\napproximate bound: test loss <= train_loss + sum_m eta * V(h_m) + M lambda",
         "A small \u03b7 with many weak learners approximates the full gradient path "
         "more finely, which lowers variance at the cost of many rounds. Lambda adds "
         "explicit complexity control for leaf values.",
         "eta = 1.0 reaches train error 0 in 6 rounds but test error 0.24. eta = "
         "0.05 needs 120 rounds and reaches test error 0.11."),
        ("Early stopping as a bias-variance knob",
         "m* = argmin_m validation_loss(m)\nshrink the final model toward the mean by eta * m* / m_best",
         "Early stopping is choosing m, a hyperparameter, by validation loss. The "
         "optional extra shrinkage replaces the overfit tail rounds with a slightly "
         "more conservative model.",
         "Validation loss by round: 50 \u2192 0.21, 100 \u2192 0.14, 200 \u2192 0.13, 400 \u2192 "
         "0.18. Best round 200; without early stopping you ship round 400 at 0.18."),
        ("Histogram binning cost",
         "exact: O(n log n) sort + O(n * #distinct_values) per node\nbinned: O(n * #bins) per node, #bins ~ 64\u2013256\nspeedup on 5M x 50: roughly 10\u201350x",
         "Binning is a lossy but nearly free approximation: it trades a tiny amount "
         "of split precision for an order of magnitude in speed, and it is what "
         "makes GPU and histogram boosting practical.",
         "5M rows \u00d7 50 features: exact search visits ~250M candidate splits per "
         "level; histogram visits 5M \u00d7 256 = 1.28B per level but with contiguous "
         "memory and no sorting \u2014 net 10\u201350x faster in practice."),
        ("Additivity and TreeSHAP",
         "prediction = base_value + sum_i phi_i\nconsistency: swapping a feature's value\nchanges the prediction by exactly the sum of its SHAP values",
         "Because the model is a sum of trees, attributions can be computed exactly "
         "rather than approximated. The efficiency property means the sum of "
         "contributions equals the prediction gap, always.",
         "For a 20-feature tree ensemble, TreeSHAP is O(TLD\u00b2) versus sampling-based "
         "methods at ~200 evaluations; the additivity identity holds to 1e-9."),
        ("Stochastic gradient boosting",
         "each tree sees rows I with P(i in I) = rho, rho < 1\nrho \u2192 1: standard boosting (higher variance)\nrho ~ 0.8: decorrelated trees, better generalisation",
         "Subsampling rows per tree is the analogue of feature randomness in random "
         "forests. Averaging decorrelated trees reduces variance, which matters most "
         "exactly where boosting is weakest \u2014 shallow, high-bias trees.",
         "On a noisy tabular dataset, rho = 0.8 with depth 3 improves test error from "
         "0.17 to 0.14 while allowing eta = 0.1 (faster convergence than eta = 0.03)."),
    ],
    math_traps=[
        "Training to the last round instead of the best round.",
        "Computing the initial value as 0 rather than the loss-minimising constant.",
        "Summing SHAP values without the baseline expectation, breaking additivity.",
        "Using gain-based importance as if it were attribution.",
        "Tuning depth and eta separately, which lands on an expensive pair.",
    ],
    math_problems=[
        "Compute two rounds of squared-error boosting by hand on 4 points with depth-1 stumps.",
        "Compute the negative gradient for squared error, absolute error and logistic loss; state which is which.",
        "Plot validation loss by round from a synthetic run and pick m*.",
        "Verify TreeSHAP additivity numerically on a 3-tree ensemble.",
        "Measure the effect of subsampling rho in {1.0, 0.9, 0.8, 0.6} on held-out loss.",
    ],
    tree="""src/com/ml/lab09/
  Main.java               driver: synthetic classification, boosting vs baseline
  GradientBoosting.java   fit (rounds, eta, depth, subsample), predict, stagedPredict
  RegressionTreeRegressor.java  the weak learner: shallow, histogram-binned splits
  AdaBoost.java           sample-reweighting variant for comparison
  ShApValues.java         exact TreeSHAP attribution over ensemble paths
  EarlyStopping.java      validation-loss tracking, best-round retention""",
    tree_note="stagedPredict(m) returning the model truncated at round m is the "
              "single most useful method for debugging boosting: it turns a "
              "training curve into something you can plot against validation loss.",
    types=[
        ("GradientBoosting", "rounds, eta, depth, subsample; fit/predict/stagedPredict"),
        ("RegressionTreeRegressor", "shallow histogram-binned tree fitting a target vector"),
        ("EarlyStopping", "best-round tracking with a patience window"),
        ("ShApValues", "exact per-feature attributions with the additivity identity"),
    ],
    patterns=[
        ("One boosting round: gradient, weak learner, scaled update",
         "The whole algorithm in one method. Initialisation is the loss-minimising "
         "constant, which is why the first prediction is already sensible.",
         """public double[] fitOneRound(double[][] x, double[] target) {
    double[] residual = new double[x.length];        // negative gradient of the loss
    for (int i = 0; i < x.length; i++) residual[i] = target[i] - predictRaw(x[i]);
    RegressionTreeRegressor tree = new RegressionTreeRegressor(maxDepth, numBins);
    tree.fit(x, residual, subsample);                // weak learner fits the gradient
    double[][] contrib = new double[x.length][x[0].length];
    for (int i = 0; i < x.length; i++) {
        double step = eta * tree.predict(x[i]);
        for (int j = 0; j < x[0].length; j++) contrib[i][j] += step;  // accumulate deltas
    }
    addGlobal(contrib);                              // keep a bias term for the deltas
    return contrib;                                  // exact additivity for SHAP
}"""),
        ("Early stopping that keeps the best round, not the last",
         "Track validation loss every round, retain the best contribution matrix, "
         "and expose the chosen round count so it can be logged and shipped.",
         """public int fit(double[][] xtr, double[] ytr, double[][] xval, double[] yval) {
    double base = mean(ytr);                          // loss-minimising constant
    init(base);
    double bestLoss = Double.MAX_VALUE;
    double[][] best = null; int bestRound = 0, stale = 0;
    for (int m = 1; m <= maxRounds; m++) {
        double[][] d = fitOneRound(xtr, ytr);         // one boosting round
        applyDelta(d);
        double loss = squaredError(yval, rawPredict(xval));
        if (loss < bestLoss - 1e-6) {
            bestLoss = loss; best = snapshotDelta(); bestRound = m; stale = 0;
        } else if (++stale >= patience) {             // patience, not just bestRound
            break;
        }
    }
    restore(best);                                    // ship the best round, not the last
    return bestRound;
}"""),
    ],
    costs=[
        ("One round (exact splits)", "O(n \u00b7 f \u00b7 log n \u00b7 depth)", "impractical above ~10\u00b77 rows"),
        ("One round (histogram binning)", "O(n \u00b7 f \u00b7 bins \u00b7 depth)", "the practical production path"),
        ("Prediction over M trees", "O(M \u00b7 2^depth)", "trivially cheap compared to training"),
        ("TreeSHAP attribution", "O(T \u00b7 L \u00b7 D\u00b2)", "exact, and cheap for shallow trees"),
    ],
    numerics=[
        "Initialise to the loss-minimising constant, not to zero.",
        "Use histogram binning above ~100k rows or ~50 features.",
        "Keep contributions in a matrix so SHAP additivity is checkable, not reconstructed.",
        "Guard against empty leaves when subsampling small datasets.",
        "Assert SHAP contributions sum to prediction minus baseline within 1e-9.",
    ],
    tests=[
        "The initial prediction equals the mean target (squared error) or the log-odds (logistic).",
        "Shallow trees with tiny eta reduce training loss monotonically.",
        "Early stopping returns the best round, verified against a full stored history.",
        "SHAP values sum to prediction minus base value within 1e-9.",
        "The same seed produces the same forest; different seeds produce slightly different models.",
        "Predicting with 0 rounds equals the base value.",
    ],
    extensions=[
        "Implement lambda (L2 leaf shrinkage) and show it substitutes for a lower learning rate.",
        "Add feature subsampling per split and compare against row subsampling.",
        "Implement quantile or Huber loss and compare robustness on contaminated targets.",
    ],
    code_checklist=[
        "Initial value is the loss-minimising constant",
        "Learning rate, depth, subsample and rounds are constructor arguments",
        "Early stopping with patience, shipping the best round",
        "Contributions retained so explanations are exact",
        "Histogram binning used above the size where exact splits hurt",
        "Validation loss curve logged on every run",
    ],
    exercise_selfcheck=[
        "I can derive the boosting update from the loss gradient",
        "I tune eta and rounds jointly with early stopping",
        "My explanations are verified additive",
        "I ship the best round, not the last",
    ],
    exercises=[
        ("Boosting from scratch, squared error",
         "Implement the full loop by hand once.",
         ["Initialise to the mean target.",
          "Compute residuals, fit depth-1 stumps, update with eta.",
          "Track training loss by round; assert it decreases.",
          "Compare with a single depth-6 tree on the same data."],
         "A from-scratch implementation plus a training-loss curve."),
        ("Functional gradients for three losses",
         "Show the framework generalises.",
         ["Implement negative gradients for squared, absolute and logistic loss.",
          "Fit boosting under each.",
          "Compare test error and robustness to an outlier.",
          "Explain why the gradient differs per loss."],
         "Three boosting variants with a written comparison."),
        ("Tune eta and rounds jointly",
         "Refuse the one-knob-at-a-time trap.",
         ["Run a grid of eta in {0.3, 0.1, 0.03} x rounds in {50, 200, 800}.",
          "Plot validation loss against rounds per eta.",
          "Pick a pair from the surface and justify it.",
          "Report the cost in training time."],
         "A surface plot and a defended (eta, rounds) pair."),
        ("Early stopping, properly",
         "Ship the best round and prove it.",
         ["Implement early stopping with patience = 30.",
          "Store the full validation history.",
          "Compare the best round with the last round on the test set.",
          "Quantify what early stopping saved."],
         "A validation curve and a quantified saving."),
        ("AdaBoost versus gradient boosting",
         "Implement the reweighting variant and compare.",
         ["Implement AdaBoost with sample weights.",
          "Run both on the same data with the same weak learner.",
          "Compare training curves and test error.",
          "Explain the difference in one paragraph."],
         "Two curves and a written mechanism explanation."),
        ("Histogram binning",
         "Make it fast enough to matter.",
         ["Bin each feature into 128 quantile bins.",
          "Rewrite split search over bins instead of values.",
          "Benchmark against exact search on 200k rows.",
          "Measure the accuracy delta."],
         "A benchmark table and a measured accuracy cost."),
        ("SHAP explanations you can defend",
         "Make the additive model explainable.",
         ["Implement exact TreeSHAP or a path-dependent approximation.",
          "Verify contributions sum to prediction minus baseline.",
          "Compare explanations against permutation importance.",
          "Write up three example explanations in plain language."],
         "A verified attribution method and three readable explanations."),
        ("Shadow-mode challenger",
         "Practice how boosting actually ships.",
         ["Train a booster on 80% of the data; log predictions on the rest.",
          "Compare against the current champion model.",
          "Compute accuracy, ECE and latency for both.",
          "Write a promotion recommendation with thresholds."],
         "A shadow evaluation report with a promotion decision."),
    ],
    quiz=[
        ("What does gradient boosting fit at each round?", ["Sample weights", "The negative gradient of the loss", "The full gradient of the model parameters", "Residuals of the final model"], 1, "It fits the negative gradient with respect to the current prediction, which equals residuals for squared error."),
        ("How does gradient boosting differ from AdaBoost?", ["It uses different trees", "It fits gradients instead of reweighting samples", "It is faster", "It cannot classify"], 1, "AdaBoost reweights; gradient boosting fits gradients, which generalises to any loss."),
        ("The learning rate eta...", ["Controls tree depth", "Scales each weak learner's contribution", "Sets the number of bins", "Determines the loss function"], 1, "Eta is shrinkage on each round's update."),
        ("Why are trees shallow in boosting?", ["Memory", "Boosting adds interaction depth across rounds", "Shallow trees are more accurate alone", "Required by the library"], 1, "Each shallow tree adds one level of interaction; stacking rounds builds the complexity."),
        ("Early stopping is essentially...", ["Halting training when the gradient vanishes", "Choosing the number of rounds by validation loss", "Stopping when memory runs out", "Truncating trees"], 1, "The round count is a hyperparameter chosen on validation data."),
        ("Why does boosting need a validation split?", ["To compute training loss", "To choose the number of rounds without touching the test set", "For SHAP values", "To initialise F\u2080"], 1, "The round count must be selected on data not used for fitting."),
        ("What is stochastic gradient boosting?", ["Using a random learning rate", "Subsampling rows per tree", "Dropping features per tree", "Adding noise to the target"], 1, "Row subsampling decorrelates the trees and reduces variance."),
        ("TreeSHAP is attractive because it is...", ["Approximate", "Exact and additive", "Model-free", "Unsupervised"], 1, "Tree ensembles admit exact Shapley values via path enumeration, and the additivity identity holds exactly."),
        ("Gain-based importance is unreliable when...", ["The model is deep", "Features are correlated, so credit is split arbitrarily", "There are many bins", "The target is skewed"], 1, "Correlated features share credit unpredictably between them."),
        ("Histogram binning helps because it...", ["Improves accuracy", "Reduces candidate splits to a few hundred per feature", "Removes the need for early stopping", "Allows larger eta"], 1, "It trades a small precision loss for an order of magnitude in speed."),
        ("The initial prediction F\u2080 for squared error is...", ["Zero", "The mean of the targets", "The log-odds", "The first feature"], 1, "The constant minimising the loss with no features is the mean target."),
        ("Overfitting in boosting shows up as...", ["Rising training loss", "Training loss falling while validation loss rises", "Fewer trees", "Lower eta"], 1, "The classic signature is a monotonically falling train curve with a turning validation curve."),
        ("Which loss makes boosting robust to outliers?", ["Squared error", "Absolute error or Huber", "Log loss", "Any, equally"], 1, "Squared error is outlier-dominated; Huber or absolute error down-weights extremes."),
        ("Increasing rounds with eta fixed is equivalent to...", ["Increasing eta", "Decreasing eta (with more compute)", "Increasing depth", "Adding features"], 1, "Smaller eta with more rounds approximates the same total shrinkage more finely."),
        ("What does SHAP additivity let you do?", ["Retrain faster", "Verify that explanations account for the whole prediction", "Remove the baseline", "Avoid cross-validation"], 1, "If the contributions sum to prediction minus baseline, nothing is unexplained."),
    ],
    vision=dict(
        future="Boosting stays the accuracy leader on tabular data, while "
               "distribution shift pushes the field toward models that adapt: "
               "recursive feature machines, monotone constraints, and hybrid "
               "GNN-plus-boosting ensembles. The winning property is no longer raw "
               "score but explainability under drift.",
        good=[
            "Every model ships with the (eta, depth, rounds, best round) tuple in its card.",
            "Validation curves are published with the model, not just the final metric.",
            "Explanations are verified additive and expressed as feature contributions.",
            "Sub-sampling and lambda are used deliberately rather than left at defaults.",
        ],
        ladder=[
            ("L1", "Boost", "Implement boosting with shallow trees and early stopping."),
            ("L2", "Tune jointly", "Sweep eta and rounds together, plot validation curves."),
            ("L3", "Explain", "Compute exact TreeSHAP values and verify additivity."),
            ("L4", "Operate", "Shadow a challenger, monitor drift, and rehearse rollback."),
        ],
        behaviors="Treat the round count as a hyperparameter, not an implementation detail. "
                  "Explain every important prediction with contributions that sum to "
                  "the score. Tune regularization as a pair.",
        anti=[
            "A booster shipped at round 5,000 because the script had no early stop.",
            "eta and depth tuned one at a time, landing on an expensive pair.",
            "Gain-based importance presented as an explanation.",
            "No subsampling, no lambda, no validation curve \u2014 just defaults.",
        ],
        trends=[
            "Monotone and shape-constrained boosting for regulated credit and insurance decisions.",
            "Distributional robustness: online boosting variants that adapt under drift.",
            "Graph-plus-boosting hybrids where boosting handles tabular and GNNs handle relational structure.",
            "Explainability as a first-class deliverable rather than an add-on.",
        ],
        d30="Implement boosting from scratch with residuals, and plot training loss by round.",
        d60="Add functional gradients for logistic loss and tune (eta, rounds) on a surface.",
        d90="Ship exact TreeSHAP explanations plus a shadow-mode challenger with a documented promotion gate.",
        metrics=[
            "I can derive the update rule for any differentiable loss.",
            "My model ships the best round, not the last.",
            "My explanations add up to the prediction.",
            "I have a validation curve for every boosted model I have shipped.",
        ],
        closer="Boosting taught the industry that accuracy and interpretability "
               "are not opposites, provided you add the pieces rather than "
               "complicating a single model.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Boosted Classifier with Verified Explanations",
        brief="Build a gradient-boosting classifier, tune it with early stopping, "
              "and produce SHAP explanations you can check add up.",
        timebox="4 hours",
        why="Boosting without explanations is hard to approve in a real review. This "
            "project forces the pairing from the start.",
        requirements=[
            "Load a binary classification dataset (adult-income style) or synthesise one with nonlinearity.",
            "Implement boosting: squared-error or logistic gradient, depth 2\u20133 trees, subsampling.",
            "Tune (eta, depth, rounds) on a grid; pick from validation curves, not the last row.",
            "Compare against a single decision tree and a logistic regression baseline on identical folds.",
            "Implement exact or path-dependent TreeSHAP; assert contributions sum to prediction minus baseline.",
            "Write 5 explanations in plain language for 5 specific rows.",
            "Add a shadow-mode evaluation report comparing to a baseline model on held-out data.",
        ],
        steps=[
            ("1", "30m", "Load, encode, split stratified; assert no leakage", "A reproducible pipeline"),
            ("2", "45m", "Implement boosting with subsampling and a validation history", "Validation loss by round stored"),
            ("3", "40m", "Grid over eta x depth; plot curves; choose the pair", "A surface and a defended choice"),
            ("4", "20m", "Three-way comparison on identical folds", "A comparison table"),
            ("5", "45m", "Implement SHAP; verify additivity within 1e-9", "A passing additivity test"),
            ("6", "30m", "Write five plain-language explanations for chosen rows", "Five readable explanations"),
            ("7", "20m", "Model card with the full hyperparameter tuple and limitations", "A card a reviewer can approve"),
        ],
        diagram=""" dataset --> encode --> stratified folds
                         |
        per (eta, depth) grid: boosting with early stopping
                         |
            validation loss curves --> chosen (eta, depth, best round)
                         |
              +----------+-----------+------------+
              |                      |            |
        boosted model      single tree      logistic
              |                      |            |
              +----------+-----------+------------+
                         |
                 SHAP attribution + additivity check
                         |
            explanations -> model card -> shadow report""",
        notes=[
            "Depth 2-3 with eta 0.05-0.1 is a sane starting region; do not start at depth 6.",
            "Store the validation history per configuration or you cannot choose k honestly.",
            "Additivity failing usually means the baseline expectation is missing, not that SHAP is broken.",
            "Compare on identical folds; different splits make the comparison meaningless.",
        ],
        deliverables=[
            "One-command run producing the grid, curves and three-way comparison.",
            "SHAP implementation with a passing additivity test.",
            "Five plain-language explanations for named rows.",
            "Model card with (eta, depth, best round, subsample) and limitations.",
        ],
        grading=[
            ("Correctness", "30%", "Boosting verified against a hand-computed round; SHAP additive"),
            ("Tuning", "25%", "Grid, curves and a defended hyperparameter choice"),
            ("Comparison", "20%", "Baselines on identical folds with the same protocol"),
            ("Explanations", "15%", "Five readable explanations that match the numbers"),
            ("Communication", "10%", "Model card names a limitation"),
        ],
        stretch=[
            "Add L2 leaf shrinkage (lambda) and show it substitutes for a lower eta.",
            "Implement quantile loss and compare robustness under label contamination.",
            "Build a shadow challenger against a baseline and write the promotion gate.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Credit Default Boosting Service",
        scenario="A lender approves 40k credit applications a day with an 8 ms "
                 "scoring budget. Decisions are challenged by consumers and "
                 "reviewed by fair-lending counsel, so every score needs a "
                 "reason-code explanation that adds up.",
        scale=[
            ("Volume", "~40k applications/day, peak 60 applications/s"),
            ("Base rate", "3.2% default within 12 months"),
            ("Latency budget", "p99 < 8 ms per decision, including feature fetch"),
            ("Labels", "12-month delayed; backfilled weekly with a freshness SLA"),
            ("Compliance", "ECOA/FCRA reason codes required on every adverse action"),
        ],
        diagram=""" applications --> bureau + internal features (point-in-time correct)
                        |
                drift + distribution checks
                        |
     champion booster (depth 3, eta 0.08, best round from validation)
                        |                      \
                        |                       +--> challenger in shadow
                        |
              SHAP contributions -> reason codes (top 5, additive check)
                        |
        policy layer: cutoffs by product, state rules, override logic
                        |
   +----------+-----------+------------+
   |          |           |            |
 approve   refer    manual review   decline
 (67%)     (14%)       (9%)        (10%) + adverse action notice
                                        |
                                dispute / adverse action service""",
        components=[
            ("Feature and point-in-time discipline",
             ["Bureau features fetched with an as-of date so no post-decision data leaks",
              "Internal features versioned; a change requires a shadow window",
              "Missingness indicators are themselves features, not silent gaps",
              "Feature snapshot ID stored with every decision for replay and dispute evidence"]),
            ("Model and champion/challenger",
             ["Champion: depth-3 boosting, eta 0.08, rounds from weekly validation with early stopping",
              "Challenger scores 100% of applications in shadow; promotion needs matured-label parity",
              "Every model card records (eta, depth, best round, subsample, lambda) and its validation curve",
              "Rollback to the previous champion is one command and rehearsed quarterly"]),
            ("Reason codes and explainability",
             ["TreeSHAP contributions computed per decision; additivity asserted in production at low sample rate",
              "Top 5 contributions mapped to consumer-readable reason codes",
              "Reason-code catalogue versioned so historical decisions stay explainable",
              "Adverse action notices generated from the same contributions, not a separate narrative"]),
            ("Monitoring and fair-lending controls",
             ["Approval rate, mean score and reason-code mix monitored by product and protected-class proxy",
              "Calibration by approval band; drift PSI on features and scores",
              "Weekly matured-label accuracy with a 12-month lag, published rather than alerted",
              "Fair-lending review sign-off recorded before every promotion"]),
        ],
        timeline=[
            ("Week 1", "Ship a logistic baseline with full reason codes so every later model has a reference"),
            ("Week 2", "Champion booster in shadow with point-in-time feature discipline and replay tests"),
            ("Week 3", "Calibration pass, reason-code catalogue review with compliance, additivity checks in production"),
            ("Week 4", "Canary at 10% of decisions; verify adverse action notices end to end"),
            ("Week 6", "Full cutover with rollback to the logistic baseline as the documented safe state"),
        ],
        runbook=[
            "# Champion model and its frozen hyperparameters",
            "curl -s localhost:8080/admin/model | jq '{version,eta,depth,bestRound,ageHours}'",
            "",
            "# Reason codes and additivity check for one adverse decision",
            "curl -s 'localhost:8080/admin/explain?applicationId=a-884213' | jq '.reasonCodes,.sumCheck'",
            "",
            "# Approval rate and reason-code mix vs last week",
            "curl -s 'localhost:8080/admin/fairness?window=1w' | jq '.approvalRate,.byGroup,.delta'",
            "",
            "# Roll back to the logistic baseline (documented safe state)",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"credit-logreg-v6\"}'",
            "",
            "# Verify the decision log is complete for the dispute window",
            "psql -c \"select count(*) from decisions where created_at > now() - interval '1 day';\"",
        ],
        metrics=[
            "SLO: p99 decision latency < 8 ms; availability 99.95%; every decision has a stored reason code.",
            "Business: default rate at a fixed approval mix, versus the pre-model baseline.",
            "Model: matured-label AUC and calibration by approval band, published weekly.",
            "Compliance: 100% adverse action notices generated from the same SHAP contributions, sampled and audited.",
            "Fairness: approval rate and reason-code mix by group, reviewed before every promotion.",
        ],
        failures=[
            ("Default rate rises after a champion cutover", "Model drift or a mix change in applicant flow", "Roll back to the logistic baseline, compare matured labels, inspect drift PSI by product"),
            ("Adverse action notice missing reason codes", "SHAP path skipped or the catalogue version mismatched", "Fail closed: fall back to logistic reason codes and page; every notice must have codes"),
            ("SHAP additivity check fails", "Baseline expectation drift after a model swap", "Block promotion until additivity holds; treat as a correctness bug, not a tuning issue"),
            ("Approval rate diverges by group", "Proxy feature drift or a mix change", "Pause promotion, run the fair-lending review, document the finding before resuming"),
            ("Latency breaches 8 ms", "Feature fetch moved onto the request path", "Restore the cached point-in-time snapshot path; compression must not add per-request work"),
        ],
        backlog=[
            "Automate the 12-month label backfill with a freshness SLA per source.",
            "Shadow challenger promotion gate: parity on matured labels at equal approval mix.",
            "Reason-code stability monitoring so a model's explanations do not shift silently between versions.",
            "Scheduled rollback drill with measured detection-to-mitigation time, published to compliance.",
            "Counterfactual explanation tooling for consumer dispute responses.",
        ],
        urls=URLS_ML,
        closer="The deliverable is an 8 ms decision whose adverse action notice can "
               "be reconstructed from the stored contributions, with a rollback to "
               "a model compliance already signed off on.",
    ),
))

# ---------------------------------------------------------------- lab10
SPECS.append(dict(
    track="ml", lab="lab10", full_set=True, level="Intermediate",
    title="Model Evaluation", main_class="com.ml.lab10.Main",
    problem="You can always make a model look good on the data you trained it on. "
            "The whole craft is measuring performance on data the model has never "
            "seen, in the way the business will actually experience it.",
    why_now="Every algorithm in this track is worthless without an honest "
             "evaluation protocol. This is the lab that stops you shipping a model "
             "that is worse than the baseline.",
    objectives=[
        "Build a confusion matrix correctly and derive every metric from it",
        "Explain why accuracy fails under class imbalance and what to use instead",
        "Compute ROC-AUC and the PR curve, and know which to trust when",
        "Implement k-fold and grouped/time-series cross-validation correctly",
        "Estimate confidence intervals on your metric estimates",
        "Choose an evaluation protocol that matches deployment and defend it",
    ],
    concepts=[
        ("The confusion matrix is the source of truth",
         "TP, FP, FN, TN determine every classification metric. Precision asks 'of "
         "those I flagged, how many were right'; recall asks 'of those that were "
         "positive, how many did I catch'. They trade off against each other "
         "through the threshold, and neither is meaningful alone."),
        ("Why accuracy is a trap",
         "At a 1% fraud base rate, predicting 'never fraud' gives 99% accuracy and "
         "catches nothing. Accuracy is only informative when classes are balanced "
         "and error costs are symmetric. Report a confusion matrix before any "
         "aggregate."),
        ("ROC versus precision-recall",
         "ROC-AUC uses the false positive rate, which shrinks as the base rate "
         "falls, making ROC look optimistic on rare positives. PR curves focus on "
         "precision, which degrades honestly. For rare positives and imbalanced "
         "costs, PR-AUC is the metric to quote."),
        ("Cross-validation must match deployment",
         "k-fold assumes i.i.d. rows. Time series must respect time (forward "
         "chaining). Grouped data must split by group, or the same patient or user "
         "appears in train and test and you have leaked. Preprocessing must be fit "
         "inside each fold. This is where most published numbers quietly go wrong."),
        ("Variance of your estimate",
         "A metric on 200 samples has a wide confidence interval. Comparing two "
         "models by a 0.5% difference without an interval is not a comparison. Use "
         "repeated CV or bootstrap intervals, and prefer the model that wins "
         "consistently rather than the one that wins on average."),
        ("Calibration versus discrimination",
         "AUC measures ranking. Calibration measures whether a predicted 0.2 "
         "happens 20% of the time. Both matter: a ranking model that sends "
         "probabilities to a pricing engine needs calibration. Report both, and "
         "choose the threshold from the cost matrix rather than from the metric."),
    ],
    formulas=[
        ("Accuracy = (TP+TN)/N", "Accuracy", "misleading under imbalance"),
        ("Precision = TP/(TP+FP)", "Precision", "of flagged, how many were right"),
        ("Recall = TP/(TP+FN)", "Recall / TPR", "of true positives, how many were caught"),
        ("F1 = 2PR/(P+R)", "F1", "harmonic mean; ignores TN"),
        ("F\u03b2 = (1+\u03b2\u00b2)PR/(\u03b2\u00b2P + R)", "F-beta", "weights recall when \u03b2 > 1"),
        ("AUC = P(score_pos > score_neg)", "ROC AUC", "threshold-free ranking quality"),
        ("AP = \u03a3 (R_k \u2212 R_{k\u22121}) P_k", "Average precision", "PR summary; better than AUC when rare positives"),
        ("CI \u2248 metric \u00b1 1.96 \u00b7 SE", "Normal CI for a proportion", "rough interval on a metric estimate"),
    ],
    flow=[
        "Define the metric from the cost matrix before you look at any numbers.",
        "Split with a protocol matching deployment: stratified k-fold, grouped, or time-based.",
        "Fit every preprocessing step inside the training fold.",
        "Compute the confusion matrix, then all metrics from it; print all of them.",
        "Plot the ROC and PR curves, and choose a threshold from the cost matrix on validation folds.",
        "Report an interval, a baseline comparison, and the protocol you used \u2014 all three.",
    ],
    assumptions=[
        "The evaluation split is representative of production traffic",
        "Splits respect the data-generating structure: time, groups, entities",
        "Preprocessing is fitted inside the training fold only",
        "The metric chosen matches the business cost, not the convenience",
        "Labels are correct; label noise caps achievable metrics",
        "Enough evaluation samples for the interval to be narrow enough to decide",
    ],
    pitfalls=[
        ("Accuracy 99%, recall 0", "1% positive class and an untrained baseline", "always print the confusion matrix and compare with a trivial predictor"),
        ("Validation score better than the holdout score", "preprocessing or feature selection done before splitting", "move every fitted step inside the fold and assert it"),
        ("Time-series CV score far above reality", "shuffled folds let the model see the future", "use forward-chaining splits and a final future-only holdout"),
        ("Model A wins by 0.3% and you ship it", "no interval on the estimate", "use repeated CV or bootstrap intervals and require a consistent win"),
        ("ROC-AUC 0.95 on a rare-positive task, terrible precision", "FPR shrinks with the base rate", "quote PR-AUC and precision at the operating point instead"),
        ("Published result not reproducible", "no seed recorded for splits or model init", "record seeds, folds and version every artifact"),
    ],
    java=[
        ("int[] confusionMatrix(y, yHat)", "the single source of truth for every metric"),
        ("Arrays.sort on scored predictions", "rank-based ROC and PR computation"),
        ("SplittableRandom with a recorded seed", "reproducible folds"),
        ("record Fold(int[] train, int[] test)", "explicit, inspectable, serialisable folds"),
        ("Collectors.groupingBy for grouped splits", "group-aware partitioning by entity id"),
    ],
    links=[
        "**Every lab in this track** depends on this protocol; the metric decides which one wins.",
        "**Lab 02** shows why threshold choice comes from costs, not from 0.5.",
        "**Lab 07** shows why unsupervised structure needs external validation, not cross-validation.",
        "**mlops/lab10** applies this to a live A/B decision on production traffic.",
    ],
    checklist=[
        "I print the confusion matrix before any aggregate metric",
        "I quote PR-AUC when positives are rare, and explain why",
        "My splits match deployment: time, group, or stratified",
        "Every fitted preprocessing step lives inside the training fold",
        "I report an interval and a baseline, not just a point estimate",
        "My threshold comes from a cost matrix",
    ],
    cards=[
        ("Why is accuracy misleading on imbalanced data?", "Predicting the majority class gives high accuracy while catching none of the rare positives."),
        ("Precision and recall describe what?", "Precision: of those flagged, how many were right. Recall: of those positive, how many were caught."),
        ("When should you quote PR-AUC over ROC-AUC?", "When positives are rare, because the false positive rate shrinks as the base rate falls and flatters ROC."),
        ("What does k-fold cross-validation assume?", "Rows are i.i.d.; with time or groups you must split differently."),
        ("Why must preprocessing be fit inside the training fold?", "Otherwise the test fold's distribution leaks into the model and the score is optimistic."),
        ("What is average precision?", "The area under the PR curve computed from precision at each recall level; a better summary than AUC on rare positives."),
        ("How do you choose a classification threshold?", "From the cost of each error type, not from 0.5 and not from the metric you report."),
        ("Why report an interval on a metric?", "Because a 0.3% difference on 200 samples is usually noise; the interval tells you whether it is real."),
    ],
    extra_cards=[
        ("What is F-beta for?", "Weighing recall more heavily than precision (\u03b2 > 1) or the reverse (\u03b2 < 1) in a single number."),
        ("What is calibration and why does it differ from AUC?", "Predicted probabilities matching observed frequencies; AUC only measures ranking, so a model can be well-ranked and badly calibrated."),
        ("How do you validate a time series model?", "Forward-chaining splits plus a final holdout that is strictly later than anything used in training."),
        ("What is the most common evaluation leak?", "Fitting the scaler, imputer or feature selector on the full dataset before splitting."),
    ],
    math_why="Evaluation is where the mathematics of estimation meets the "
             "economics of error. The confusion matrix gives you the counts, the "
             "curves give you the trade-off, and the interval tells you whether "
             "your comparison is real.",
    math=[
        ("From counts to metrics",
         "TP, FP, FN, TN from the confusion matrix\nP = TP/(TP+FP),  R = TP/(TP+FN)\nF1 = 2PR/(P+R),  F_beta = (1+b^2)PR/(b^2 P + R)",
         "Every metric is a ratio of cells, so the confusion matrix is the only "
         "thing you need to compute. F1's harmonic mean means precision and recall "
         "must both be decent to score well.",
         "TP = 90, FP = 10, FN = 40: precision = 0.90, recall = 0.69, F1 = 0.78. "
         "Accuracy on a 1,000-row set with TN = 860 would read 0.95 while recall is "
         "below 0.7."),
        ("Accuracy versus imbalance",
         "accuracy of the trivial predictor = 1 - pi, where pi is the positive rate\nat pi = 0.01: accuracy = 0.99, recall = 0\nuseful metrics must be compared against this floor",
         "The trivial predictor sets the floor any real model must beat. At low "
         "prevalence, only recall-type metrics discriminate, which is why balanced "
         "accuracy and F-beta appear in class-imbalance work.",
         "1% positives, 10,000 rows: trivial accuracy 0.99. A model with recall 0.3 "
         "and precision 0.6 has accuracy 0.966 \u2014 worse than trivial, but far more "
         "useful. Accuracy hides that entirely."),
        ("ROC and PR curves",
         "ROC: sweep threshold, plot TPR = TP/(TP+FN) against FPR = FP/(FP+TN)\nPR:  sweep threshold, plot precision = TP/(TP+FP) against recall\nAUC_ROC = P(s_pos > s_neg)",
         "With rare positives, FPR has a tiny denominator, so it stays small even "
         "when many false positives are generated. Precision's denominator is the "
         "flagged set, so it degrades visibly.",
         "1,000 rows, 10 positives. At recall 0.8, ROC shows FPR = 0.001 (one FP) "
         "\u2014 excellent. PR shows precision = 0.62, which is the number a reviewer "
         "actually experiences."),
        ("Average precision",
         "AP = sum_k (R_k - R_{k-1}) P_k, over thresholds sorted by descending score\nAP approximates the PR area and is comparable across datasets",
         "AP is a step-wise summary of the PR curve that stays meaningful on small "
         "rare-positive sets, where trapezoidal integration over precision is noisy.",
         "10 positives in 1,000 rows: AP = 0.71 while AUC = 0.94. The gap is the "
         "story \u2014 the model ranks well but its top-of-list precision is mediocre."),
        ("Variance of a metric estimate",
         "SE(p_hat) = sqrt(p(1-p)/n) for a proportion\nmetric CI ~ estimate \u00b1 1.96 SE\ncompare models with paired tests on the same folds",
         "Sampling error is often larger than the difference you are chasing. "
         "Paired comparisons on identical folds remove the fold-to-fold variance, "
         "which is the dominant term.",
         "Precision 0.80 on n = 100: SE = 0.04, so the 95% interval is 0.72\u20130.88. A "
         "0.3% improvement over another model is far inside that noise."),
        ("Cross-validation variance",
         "variance of the k-fold estimate ~ sigma^2 / (k * n/k) = sigma^2 / n\nadding folds reduces variance from partition noise, not sampling noise\nrepeated CV reduces both but costs k * r fits",
         "More folds reduce the noise from how the data was partitioned. They do not "
         "add data. Going from 5-fold to 10-fold rarely changes the estimate much; "
         "repeating with different seeds does reduce variance.",
         "10-fold CV on 5,000 rows estimates accuracy within roughly \u00b11%. Ten-fold "
         "instead of five changes the mean by about 0.1\u20130.3%, but a repeated 5-fold "
         "with 5 seeds tightens the reported interval noticeably."),
    ],
    math_traps=[
        "Computing precision with a zero denominator (no predicted positives) without guarding.",
        "Reporting accuracy as a percentage when the task is binary and rare-positive.",
        "Integrating PR with the trapezoid rule on a small rare-positive set instead of using average precision.",
        "Comparing two models across different fold assignments rather than paired folds.",
        "Averaging precision across classes without stating whether it is macro or weighted.",
    ],
    math_problems=[
        "Compute precision, recall, F1, specificity and balanced accuracy from a given confusion matrix.",
        "Show that the trivial predictor's accuracy equals 1 - pi and compute it for pi = 0.001, 0.01, 0.1.",
        "Compute ROC-AUC by the rank formula and by trapezoidal integration on a scored dataset; assert equality.",
        "Compute average precision for a 10-positive dataset and compare with trapezoidal PR integration.",
        "Compute the 95% CI for precision 0.8 at n = 50, 100, 500 and 5,000; explain when the difference becomes decisive.",
    ],
    tree="""src/com/ml/lab10/
  Main.java               driver: several datasets, full metric report
  ConfusionMatrix.java    int[] confusionMatrix + all derived metrics
  RocCurve.java           TPR/FPR sweep by rank, trapezoidal AUC
  PrCurve.java            precision/recall sweep + average precision
  CrossValidator.java     stratified k-fold, grouped folds, forward-chaining folds
  ThresholdSelector.java  cost-matrix driven threshold choice on validation folds""",
    tree_note="CrossValidator returns explicit index arrays (record Fold) rather "
              "than running a callback. Being able to print a fold is how you "
              "catch leakage in grouped and time-ordered data.",
    types=[
        ("ConfusionMatrix", "counts plus every derived metric, and the trivial-baseline comparison"),
        ("RocCurve / PrCurve", "rank-based curves with AUC and average precision"),
        ("CrossValidator", "stratified, grouped and forward-chaining fold generation"),
        ("ThresholdSelector", "cost-matrix threshold selection on validation folds only"),
    ],
    patterns=[
        ("Confusion matrix as the single source of truth",
         "Every metric derives from the four counts. Returning them as a record "
         "makes it impossible to report accuracy without also reporting the matrix.",
         """public record Metrics(int tp, int fp, int fn, int tn,
                      double precision, double recall, double f1,
                      double specificity, double balancedAccuracy,
                      double accuracy, double trivialAccuracy) {

    public static Metrics of(int[] y, int[] yHat) {
        int tp = 0, fp = 0, fn = 0, tn = 0;
        for (int i = 0; i < y.length; i++) {
            if (y[i] == 1 && yHat[i] == 1) tp++;
            else if (y[i] == 0 && yHat[i] == 1) fp++;
            else if (y[i] == 1 && yHat[i] == 0) fn++;
            else tn++;
        }
        int n = y.length;
        int pos = tp + fn;
        double p = safe(tp, tp + fp);                 // guard zero denominators
        double r = safe(tp, pos);
        double spec = safe(tn, tn + fp);
        return new Metrics(tp, fp, fn, tn, p, r, harmonic(p, r), spec,
                0.5 * (r + spec), safe(tp + tn, n), safe(Math.max(tp + tn, fn + fp), n));
    }
    static double safe(double num, double den) { return den == 0 ? 0.0 : num / den; }
    static double harmonic(double a, double b) { return (a + b) == 0 ? 0 : 2 * a * b / (a + b); }
}"""),
        ("Splits that respect how the data was generated",
         "Three strategies behind one interface. Using the wrong one is the most "
         "common evaluation leak, so the type name says which is which.",
         """public interface Folding { List<Fold> folds(int n); }

record Fold(int[] train, int[] test) {}

static Folding stratified(int[] y, int k) {
    // shuffle within each class, then deal rows round-robin into k folds:
    // guarantees every fold keeps the class ratio
}

static Folding grouped(int[] groupId, int k) {
    // group ids are hashed to folds so no entity can appear in train and test
}

static Folding forwardChaining(int n, int k, int minTrain) {
    // test folds walk forward in time: [minTrain, minTrain+w), [minTrain+w, minTrain+2w), ...
    // no fold ever trains on data at or after its test window
}"""),
    ],
    costs=[
        ("Confusion matrix and metrics", "O(n)", "one pass"),
        ("ROC curve by rank sort", "O(n log n)", "sort once; AUC from ranks, no sweep loop needed"),
        ("PR curve and average precision", "O(n log n)", "same sort reused"),
        ("k-fold evaluation with a model fit", "O(k \u00b7 fit_cost)", "fits dominate; cache fold indices across runs"),
    ],
    numerics=[
        "Guard every metric's denominator; a model that predicts one class has no precision.",
        "Compute AUC from ranks (Mann-Whitney) rather than a trapezoid sweep; it is exact and faster.",
        "Cache fold indices so repeated runs compare like for like.",
        "Print the trivial baseline next to accuracy in every report.",
        "Round metrics consistently; mixed precision in a report reads as sloppiness.",
    ],
    tests=[
        "A perfect classifier yields tp = n, fp = fn = 0, precision = recall = 1.",
        "A trivial all-positive classifier yields recall 1.0, precision = pi, FPR 1.0.",
        "AUC by rank equals AUC by trapezoid within 1e-9.",
        "Stratified folds preserve the class ratio within one row.",
        "Grouped folds never place the same group id in both train and test.",
        "Forward-chaining folds always have max(train index) < min(test index).",
        "Two runs with the same seed produce identical folds.",
    ],
    extensions=[
        "Implement stratified k-fold with a documented fold count and cache the indices to disk.",
        "Add bootstrap confidence intervals on a metric and a paired test between two models.",
        "Implement cost-based threshold selection and report the cost curve alongside PR.",
    ],
    code_checklist=[
        "Every metric derives from one confusion matrix",
        "Trivial baseline printed with accuracy",
        "Fold type chosen to match data generation, and asserted",
        "Fold indices cached and reproducible from a seed",
        "Threshold selected on validation folds only",
        "Interval or repeated-fold spread reported for the headline metric",
    ],
    exercise_selfcheck=[
        "My report starts with the confusion matrix",
        "I can explain why I chose ROC or PR for this task",
        "My splits respect time and groups",
        "I compared against a trivial baseline",
    ],
    exercises=[
        ("Build the metric suite from scratch",
         "Every metric from the four counts, cross-checked by hand.",
         ["Implement confusionMatrix(y, yHat).",
          "Derive precision, recall, F1, specificity and balanced accuracy.",
          "Compute each by hand on a 10-row example.",
          "Add trivial-baseline accuracy next to accuracy."],
         "A verified metric suite and a hand-worked example."),
        ("ROC and PR, both curves",
         "See the difference a rare positive rate makes.",
         ["Compute ROC by threshold sweep and AUC by trapezoids.",
          "Compute AUC by the rank (Mann-Whitney) method; assert equality.",
          "Compute the PR curve and average precision.",
          "Compare AUC and AP on a 1% positive dataset."],
         "Two curves and a comparison showing why AP is the honest metric here."),
        ("k-fold done correctly",
         "The fold strategy is where numbers are won or lost.",
         ["Implement stratified k-fold with a recorded seed.",
          "Assert each fold's class ratio matches the whole set.",
          "Cache fold indices and reuse across two models.",
          "Compute the spread across folds."],
         "A fold generator with assertions and a two-model comparison on identical folds."),
        ("Grouped and time-based splits",
         "Handle the cases where i.i.d. is a lie.",
         ["Implement grouped splits by entity id.",
          "Implement forward-chaining splits for a time series.",
          "Show leakage: shuffle a time series and compare scores.",
          "Quantify the optimism the shuffled split introduces."],
         "Two split implementations plus a quantified leakage number."),
        ("Threshold selection from costs",
         "Turn business costs into an operating point.",
         ["Implement cost-based threshold selection on validation folds.",
          "Plot cost and precision/recall against threshold.",
          "Compare with the 0.5 threshold and with max-F1.",
          "Write the recommendation with numbers."],
         "A cost curve and a defended operating point."),
        ("Confidence intervals on a metric",
         "Know when your difference is real.",
         ["Bootstrap the evaluation set 1,000 times; compute the metric each time.",
          "Report the 2.5/50/97.5 percentiles.",
          "Compare two models with a paired bootstrap on identical samples.",
          "Conclude whether a 0.3% gap is meaningful."],
         "An interval and a paired comparison with a verdict."),
        ("Calibration versus discrimination",
         "Two properties, one model.",
         ["Compute AUC and reliability bins for a classifier.",
          "Report ECE before and after Platt scaling.",
          "Find a threshold where precision is usable and report the resulting recall.",
          "Explain the difference to a stakeholder."],
         "Two reports and a plain-language explanation."),
        ("Publish an evaluation report",
         "Package the protocol so it is reusable and reviewable.",
         ["Generate a markdown report: protocol, folds, metrics, curves, baseline.",
          "Include the exact seed, library versions and fold indices hash.",
          "Have a colleague reproduce the numbers from the repo.",
          "Write the recommendation and its confidence."],
         "A reproducible report and a second pair of eyes confirming the numbers."),
    ],
    quiz=[
        ("What does precision measure?", ["Of true positives, how many were caught", "Of those flagged, how many were correct", "Overall correctness", "The false positive rate"], 1, "Precision is TP/(TP+FP): the purity of the flagged set."),
        ("A model predicts the majority class always. Accuracy is 99%. Recall is?", ["0.99", "1.0", "0", "0.01"], 2, "If every positive is missed, recall is 0 no matter how good the accuracy looks."),
        ("Which metric summarises PR better on rare positives?", ["ROC-AUC", "Average precision", "Accuracy", "Log loss"], 1, "AP stays meaningful where ROC's false positive rate flatters small-denominator effects."),
        ("Why does ROC look optimistic on rare positives?", ["It uses log scale", "FPR's denominator stays large while precision's shrinks", "It ignores TN", "It smooths the curve"], 1, "FPR divides by the huge negative class, so many false positives barely move it."),
        ("What does k-fold cross-validation assume?", ["Time independence", "Rows are i.i.d. and exchangeable", "Normality", "Balanced classes"], 1, "Grouped or temporal data needs a different split, or you leak."),
        ("Why fit the scaler inside each fold?", ["Speed", "Otherwise test distribution information leaks into training", "Numerical stability", "It is required by k-fold"], 1, "Full-dataset scaling makes the CV score optimistic and does not match serving."),
        ("What does forward-chaining ensure?", ["Random folds", "Every fold trains only on data before its test window", "Equal fold sizes", "Balanced classes"], 1, "It respects time order, which is the only honest protocol for forecasting."),
        ("Precision 0.8 with recall 0.3 at n = 100. Is a rival at 0.81/0.31 better?", ["Yes, clearly", "No \u2014 the difference is inside the noise", "Yes, because precision is higher", "It depends on the threshold"], 1, "At n = 100 the standard error on precision is about 0.04, so 0.01 is meaningless."),
        ("Why compare models on identical folds?", ["It is faster", "It removes fold-to-fold variance from the comparison", "It guarantees equal accuracy", "It allows paired tests"], 1, "Paired comparison cancels the dominant variance term."),
        ("What is balanced accuracy?", ["Accuracy divided by classes", "Mean of sensitivity and specificity", "The average of precision and recall", "Accuracy on a balanced sample"], 1, "It weights both classes equally, which resists imbalance."),
        ("F1 ignores which quantity?", ["False positives", "False negatives", "True negatives", "Thresholds"], 2, "F1 uses precision and recall only, so true negatives never affect it."),
        ("Calibration means...", ["High AUC", "Predicted probabilities match observed frequencies", "Low variance", "High recall"], 1, "Calibration is about probability accuracy; AUC is about ranking."),
        ("Which threshold should you ship?", ["0.5", "The one minimising expected cost from your cost matrix", "The one maximising accuracy", "The median score"], 1, "The cost matrix, evaluated on validation folds, is the decision."),
        ("What does a widening gap between training and CV error suggest?", ["Underfitting", "High variance/overfitting", "Data leakage", "A better model"], 1, "The gap is the classic variance signal; leakage shows up as the opposite pattern."),
        ("Why report a baseline?", ["To fill space", "So readers can judge whether the model's gain exceeds trivial predictors", "Because metrics are meaningless alone", "It is required by law"], 1, "Against a trivial baseline you know how much of the performance is real."),
    ],
    vision=dict(
        future="Evaluation moves toward protocol-as-code: versioned evaluation "
               "suites that run in CI, offline metrics tracked against online "
               "outcomes, and continuous evaluation on shadow traffic. The metric "
               "ceases to be a report and becomes a deployment gate.",
        good=[
            "Every reported number ships with its interval, baseline, protocol and seed.",
            "Fold strategy is asserted, not assumed: groups split by group, time by time.",
            "Rare-positive tasks quote PR-AUC and precision at the operating point.",
            "Thresholds come from cost matrices stored next to the model.",
        ],
        ladder=[
            ("L1", "Measure", "Compute a confusion matrix and accuracy honestly."),
            ("L2", "Be careful", "Stratified folds, in-fold preprocessing, PR-AUC for rare classes."),
            ("L3", "Be rigorous", "Intervals, paired model comparison, repeated CV."),
            ("L4", "Gate", "Run the protocol in CI and block promotion on regression."),
        ],
        behaviors="Print the confusion matrix first. Choose the protocol that matches "
                  "how the data was generated. Treat a difference smaller than your "
                  "interval as no difference.",
        anti=[
            "Accuracy on a 1% positive class as a headline.",
            "Shuffled cross-validation on time series.",
            "Preprocessing fit before splitting.",
            "A/B-testing a model on a difference well inside the noise band.",
        ],
        trends=[
            "Continuous evaluation on shadow traffic with offline/online metric correlation tracking.",
            "Evaluation suites as code, gated in CI, with leakage assertions.",
            "Slice-based evaluation: performance per segment, not only in aggregate.",
            "Statistically rigorous experiment design (sequential testing, CUPED variance reduction).",
        ],
        d30="Build the metric suite from the confusion matrix and cross-check by hand.",
        d60="Implement stratified, grouped and forward-chaining folds with leakage assertions.",
        d90="Add bootstrap intervals, a paired comparison between two models, and a reproducible report someone else can rerun.",
        metrics=[
            "I always print the confusion matrix and the trivial baseline.",
            "My splits match how the data was generated.",
            "I quote an interval with every headline number.",
            "I can justify ROC versus PR for my task.",
        ],
        closer="An evaluation protocol is the only thing standing between you and "
               "a model that is confidently worse than doing nothing.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Evaluation Suite for an Imbalanced Classifier",
        brief="Build a complete evaluation suite: correct folds, all metrics, "
              "curves, intervals, and a cost-based operating point.",
        timebox="3\u20134 hours",
        why="This is the lab you will reuse for every model you ever ship. Doing it "
            "once, properly, is worth more than any new algorithm.",
        requirements=[
            "Load a rare-positive binary dataset (fraud, churn or credit) with at least 1,000 positives.",
            "Implement stratified k-fold, and additionally grouped and forward-chaining folds where relevant.",
            "Move all preprocessing inside the fold; add an assertion that would fail if you leaked.",
            "Report the confusion matrix, accuracy with trivial baseline, precision, recall, F1, F2, balanced accuracy, ROC-AUC and average precision.",
            "Plot ROC and PR; compute AUC two independent ways and assert they agree.",
            "Bootstrap a 95% interval on the headline metric and compare two models with a paired test.",
            "Choose the threshold from a cost matrix and report expected cost per 10,000 cases.",
        ],
        steps=[
            ("1", "25m", "Load data; assert class ratio and positivity count", "A documented base rate"),
            ("2", "30m", "Stratified folds with assertions; cache fold indices", "Reusable, inspectable folds"),
            ("3", "30m", "In-fold preprocessing pipeline; leakage assertion that fails on the naive version", "A passing leakage test"),
            ("4", "25m", "Full metric suite plus both curves", "A metrics table and two curves"),
            ("5", "30m", "Bootstrap interval and paired comparison between two models", "Intervals and a verdict"),
            ("6", "20m", "Cost-matrix threshold sweep; expected cost per 10,000", "A cost curve with a chosen point"),
            ("7", "25m", "Publish a markdown report: protocol, folds hash, seed, metrics, recommendation", "A reproducible report"),
        ],
        diagram=""" dataset (rare positives)
        |
  stratified folds (cached, asserted)      forward-chaining folds
        |                                       |
   in-fold preprocessing (scaler/imputer)      |
        |                                       |
   model A / model B  --> same folds, paired comparison
        |
   confusion matrix -> all metrics (with trivial baseline)
        |
   ROC (two methods, assert equal) | PR | average precision
        |
   bootstrap 95% CI  +  cost-matrix threshold  --> expected cost / 10k
        |
   markdown report (seed, folds hash, versions, recommendation)""",
        notes=[
            "The leakage assertion is the highest-value line in the project: it must fail on the naive pipeline.",
            "PR curves at 1% positives look nothing like ROC curves; show both to whoever reads the report.",
            "Paired comparisons on identical folds remove the dominant variance term.",
            "Cache fold indices to disk so a colleague's rerun is truly identical.",
        ],
        deliverables=[
            "One-command run producing the full report.",
            "Two curves (ROC, PR) with AUC computed two ways and an equality assertion.",
            "Bootstrap intervals plus a paired comparison verdict between two models.",
            "Cost curve with the chosen operating point and expected cost per 10,000.",
        ],
        grading=[
            ("Protocol correctness", "30%", "Correct folds, in-fold preprocessing, leakage assertion present"),
            ("Metric completeness", "20%", "Confusion matrix, all metrics, trivial baseline, both curves"),
            ("Statistical rigor", "25%", "Intervals and a paired comparison with a stated verdict"),
            ("Decision", "15%", "Cost-based threshold with expected cost per 10,000"),
            ("Reproducibility", "10%", "Seed, fold hash and versions in the report"),
        ],
        stretch=[
            "Add slice-based evaluation: metrics per segment, and report the worst slice.",
            "Implement a sequential-testing guard for peeking at results during an A/B test.",
            "Correlate an offline metric with a simulated online outcome to justify the choice.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Online Evaluation Loop for a Ranking Model",
        scenario="A marketplace search-and-rank model serves 40M queries a day. "
                 "Offline metrics looked excellent, click-through is flat, and "
                 "nobody can say which offline metric predicted anything. You build "
                 "the evaluation loop that makes the answer knowable.",
        scale=[
            ("Query volume", "~40M queries/day, peak 12k QPS"),
            ("Candidate set", "2M items, ranking 200 per query at p99 < 150 ms"),
            ("Labels", "clicks and orders arrive within minutes; long-term value in 14 days"),
            ("Offline/online gap", "NDCG@10 rose 4% over 6 weeks while CTR moved 0.1%"),
            ("Release cadence", "challenger scores 100% of traffic in shadow, twice weekly"),
        ],
        diagram=""" query + candidates --> feature service (point-in-time)
                        |
        +---------------+----------------+
        |               |                |
  champion (live)   challenger        log store (impressions + features + scores)
        |            (shadow)                 |
        |                                    |
        +----------------+--------------------+
                         |
              offline evaluation suite (CI, versioned)
                         |
              outcome join (clicks, orders, 14d value)
                         |
        correlation dashboard: offline metric vs online delta
                         |
        promotion gate + automatic rollback""",
        components=[
            ("Impression logging",
             ["Log query id, candidate ids, features, scores, model version and position for every impression",
              "Sampling is documented; unsampled impressions must be reproducible from the log",
              "Log retention aligned to the longest label horizon (14 days for value)",
              "Log volume and drop rate themselves monitored \u2014 a silent gap biases every metric"]),
            ("Offline evaluation suite",
             ["Versioned suite in CI: NDCG@k, MAP, MRR, calibration, and slice metrics per query intent",
              "Runs on a fixed query sample so scores are comparable week to week",
              "Leakage assertions: no post-click feature, no post-outcome feature",
              "Publishes the report as an artifact attached to the candidate model"]),
            ("Outcome joining and correlation",
             ["Join outcomes to impressions with a documented attribution window",
              "Track offline/online correlation per metric over time, not once",
              "Segment by query intent, device and new/returning user",
              "Report the correlation with an interval; treat a weak correlation as a finding"]),
            ("Promotion and rollback",
             ["Shadow evaluation with a fixed traffic slice and a minimum duration before promotion",
              "Promotion gate: offline metrics improve AND the online guardrails hold",
              "Automatic rollback on a guardrail breach (CTR, revenue per session, latency)",
              "Every promotion records the report artifact, the approver and the date"]),
        ],
        timeline=[
            ("Week 1", "Instrument impression logging; verify no gaps by sampling joins"),
            ("Week 2", "Versioned offline suite in CI with leakage assertions and fixed query samples"),
            ("Week 3", "Outcome join and the offline/online correlation dashboard"),
            ("Week 4", "Promotion gate and automated rollback wired to guardrails"),
            ("Week 6", "First two challenger cycles run end to end; document what the loop caught"),
        ],
        runbook=[
            "# Champion and challenger versions in flight",
            "curl -s localhost:8080/admin/models | jq '{champion,challenger,shadowPct}'",
            "",
            "# Impression log completeness for the last hour",
            "curl -s 'localhost:8080/admin/loghealth?window=1h' | jq '.logged,.expected,.dropRate'",
            "",
            "# Offline report for the challenger (CI artifact summary)",
            "curl -s 'localhost:8080/admin/offline?version=ranker-v42' | jq '.ndcg10,.map,.calibrationEce'",
            "",
            "# Offline/online correlation by metric, with intervals",
            "curl -s 'localhost:8080/admin/correlation?window=28d' | jq '.ndcg,.ctr,.ci'",
            "",
            "# Roll back to the champion (automatic on guardrail breach, manual here)",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"ranker-v41\"}'",
        ],
        metrics=[
            "Business: revenue per session and CTR per query intent, with intervals, weekly.",
            "Reliability: impression log completeness > 99.9% and drop rate < 0.1%.",
            "Offline: NDCG@10 and MAP on a fixed query sample, versioned and comparable.",
            "Validity: offline/online correlation per metric with a confidence interval, tracked as a time series.",
            "Guardrails: p99 latency, result diversity, and zero-result rate per candidate set.",
        ],
        failures=[
            ("Offline metric improves, online metric flat", "offline/online correlation is weak or the query sample drifted", "Compare on intent slices, check log completeness, and treat the metric as unvalidated until correlated"),
            ("Impression log gap during peak", "Sampling or writer backpressure", "Fall back to sampling-with-provenance, alert on drop rate, backfill from the query log"),
            ("Candidate passes offline, breaches latency in shadow", "feature fetch cost higher on live traffic", "Promotion gate blocks; feature path optimised before retry"),
            ("Zero-result rate spikes after a rollout", "Candidate generation regression", "Automatic rollback on the zero-result guardrail; investigate retrieval, not ranking"),
            ("Ranking becomes homogeneous across users", "Diversity guardrail absent", "Add per-user result diversity as a hard guardrail and roll back"),
        ],
        backlog=[
            "Long-term value labels (14-day) joined automatically into the correlation dashboard.",
            "Per-intent metric slices with minimum sample sizes declared in the suite.",
            "Counterfactual logging of position bias correction so NDCG comparisons are honest.",
            "Automatic regression test that fails a candidate whose offline report is missing.",
            "Documented rollback drill with measured time-to-safe, published quarterly.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a loop that says which offline metric earned "
               "the right to influence a decision \u2014 and rolls back automatically "
               "when one starts lying.",
    ),
))
