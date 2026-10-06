# -*- coding: utf-8 -*-
"""Tailored specs for labs/ml/lab02 .. lab05."""

from ml_a import URLS_ML

SPECS = []

# ---------------------------------------------------------------- lab02
SPECS.append(dict(
    track="ml", lab="lab02", full_set=False, level="Foundational",
    title="Logistic Regression", main_class="com.ml.lab02.Main",
    problem="Your target is a class, not a number, but you still want a linear "
            "decision boundary you can defend to a regulator.",
    why_now="It is the calibration reference for every classifier in the track, and "
             "the fastest way to learn how a loss function differs from a metric.",
    objectives=[
        "Derive cross-entropy from maximum likelihood under Bernoulli outcomes",
        "Implement the sigmoid stably and know where it saturates",
        "Fit by gradient descent with feature scaling and a learning-rate schedule",
        "Read a confusion matrix and derive precision, recall, F1, accuracy",
        "Explain why the 0.5 threshold is a business decision, not a statistical one",
        "Diagnose complete separation and fix it with regularisation",
    ],
    concepts=[
        ("The sigmoid as a link function",
         "s(z) = 1/(1+e\u207b\u1d63) maps any real score to a probability. Its log-odds are "
         "linear: log(p/(1\u2212p)) = z = \u03b2\u2080 + \u03b2\u1d40x. That is the actual model; the "
         "probability is just how we report it. Anything linear-in-log-odds is a "
         "logistic regression."),
        ("Cross-entropy as negative log-likelihood",
         "J(\u03b2) = \u2212(1/m)\u03a3[y\u1d62 log p\u1d62 + (1\u2212y\u1d62) log(1\u2212p\u1d62)]. Because it is the "
         "log of a Bernoulli likelihood, minimising it is maximum likelihood \u2014 no "
         "assumed error distribution, unlike squared loss on 0/1 labels."),
        ("Numerical stability",
         "Never call log(sigmoid(\u22121000)): the sigmoid returns 0.0 and log(0) is "
         "\u2212\u221e. Use the piecewise form or `log1p(exp(\u2211z))`, and clip probabilities "
         "before taking logs. This one detail separates a working implementation "
         "from a NaN at iteration 3."),
        ("The decision threshold",
         "Predict 1 when p > 0.5 by default, but the threshold is a cost decision. A "
         "missed fraud (recall cost) is not the same as a false alarm. Sweep the "
         "threshold against your cost matrix and put the chosen value in the config."),
        ("Separation and regularisation",
         "If a feature perfectly separates the classes, \u03b2 diverges: log-loss keeps "
         "falling while accuracy is already 1. The fix is a small L2 penalty (or "
         "bounded iterations). Perfect accuracy plus enormous coefficients is the "
         "signature, and it will fail the moment the boundary moves."),
        ("Calibration vs discrimination",
         "Discrimination is ranking positives above negatives (AUC); calibration is "
         "predicted probability matching observed frequency. Logistic regression is "
         "naturally calibrated; boosted trees and KNN often are not. If you report "
         "a probability to a risk team, check calibration, not just AUC."),
    ],
    formulas=[
        ("p = \u03c3(z) = 1/(1+e\u207b\u1d63)", "Sigmoid", "score \u2192 probability"),
        ("z = \u03b2\u2080 + \u03b2\u1d40x", "Log-odds (logit)", "the linear part of the model"),
        ("J(\u03b2) = \u2212(1/m)\u03a3[y log p + (1\u2212y)log(1\u2212p)]", "Cross-entropy", "mean negative log-likelihood"),
        ("\u2202J/\u2202\u03b2\u2c7c = (1/m)(p\u1d62 \u2212 y\u1d62)x\u1d62", "Gradient", "convex, so descent converges"),
        ("Precision = TP/(TP+FP)", "Precision", "of flagged cases, how many were right"),
        ("Recall = TP/(TP+FN)", "Recall / TPR", "of true cases, how many we caught"),
        ("F1 = 2PR/(P+R)", "F1", "harmonic mean; punishes imbalance"),
        ("AUC = P(score(X\u2081) > score(X\u2080))", "ROC AUC", "ranking quality, threshold-free"),
    ],
    flow=[
        "Encode labels as 0/1 and split with stratification so both folds keep the class ratio.",
        "Scale features (logistic regression has no scale invariance because of the penalty).",
        "Initialise \u03b2 = 0, so the initial loss is log 2 \u2248 0.693 \u2014 a useful sanity check.",
        "Iterate \u03b2 \u2190 \u03b2 \u2212 \u03b1\u00b7X\u1d40(p \u2212 y)/m until the loss change is below tolerance.",
        "Compute the decision threshold from your cost matrix rather than accepting 0.5.",
        "Report the confusion matrix, the PR curve and calibration \u2014 AUC alone hides threshold failures.",
    ],
    assumptions=[
        "Correct model form: log-odds are linear in the features",
        "Observations are conditionally independent given the features",
        "No perfect separation, or a penalty is applied",
        "Features are measured without error (measurement error attenuates \u03b2)",
        "Sample is representative of the population you will score",
        "If regularising, features were standardised so the penalty is uniform",
    ],
    pitfalls=[
        ("log(0) or NaN during the first iterations", "computing log(sigmoid(z)) naively for large negative z", "use the piecewise stable form or log1p(exp(z))"),
        ("Accuracy 100%, coefficients in the thousands", "complete separation, no penalty", "add L2 regularisation and report bounded coefficients"),
        ("A great AUC and a useless model in practice", "threshold set to 0.5 on an uncalibrated score", "choose the threshold from the cost matrix; check calibration"),
        ("Test F1 collapses while accuracy looks fine", "class imbalance makes accuracy meaningless", "always read the confusion matrix; optimise the metric that is priced"),
        ("Predictions flip after deploy", "scaler refit outside the estimator", "ship the fitted scaler with \u03b2"),
        ("Training loss decreases but probabilities are absurd", "loss computed with unnormalised scores", "verify the loss is averaged over samples, not summed inconsistently"),
    ],
    java=[
        ("Math.exp / Math.log1p", "stable sigmoid and log-loss without overflowing"),
        ("DoubleSummaryStatistics", "streaming class counts and score statistics"),
        ("Arrays.stream(...).parallel()", "the X\u1d40(p\u2212y) accumulation parallelises cleanly over rows"),
        ("record BinaryRow(double[] x, int y)", "keeps the label alongside features so folds cannot drift apart"),
        ("SplittableRandom", "reproducible stratified shuffling for splits"),
        ("Math.min / Math.max clamping", "guard p into [\u03b5, 1\u2212\u03b5] before taking logs"),
    ],
    links=[
        "**Lab 10** turns the confusion matrix into cross-validation and PR/ROC analysis.",
        "**Lab 03** trades the smooth boundary for axis-aligned splits and gains nonlinearity.",
        "**Lab 09** shows how boosting fixes logistic regression's linearity by adding weak trees.",
        "**mlops/lab10** applies these metrics to a real A/B decision on production traffic.",
    ],
    checklist=[
        "I can derive cross-entropy from a Bernoulli likelihood in four lines",
        "I never call log(sigmoid(z)) without a stability guard",
        "I choose the threshold from costs, and can defend the choice",
        "I can spot separation from the coefficient magnitudes",
        "I can explain the PR curve's advantage over ROC under imbalance",
        "I know what calibration means and how to test it",
    ],
    cards=[
        ("Why is cross-entropy the right loss for 0/1 labels?", "It is the negative log-likelihood of a Bernoulli model, so minimising it is maximum likelihood under a well-specified link."),
        ("What is the initial cross-entropy at \u03b2 = 0 and why does it matter?", "log 2 \u2248 0.693, because p = 0.5 for every row. A different starting value means a bug in initialisation."),
        ("What is complete separation?", "A feature or combination that perfectly predicts the label, sending \u03b2 to infinity while loss keeps falling."),
        ("Why scale features for logistic regression?", "Gradient descent converges far faster, and any L2 penalty would otherwise be applied unevenly across units."),
        ("Why does logistic regression need no scaling for correctness, only for speed?", "The model form is unaffected; the optimisation path and penalty are not."),
        ("What does ROC AUC measure that accuracy does not?", "Ranking quality across all thresholds, independent of class balance and of any single operating point."),
        ("When is accuracy the wrong metric?", "Whenever the positive class is under ~10%: always correct by predicting the majority class, so it carries almost no information."),
        ("How do you pick a classification threshold?", "From the cost of each error type: pick the threshold where marginal benefit crosses marginal cost."),
        ("What is the F1 score's blind spot?", "It ignores true negatives, so a model that over-predicts positives can score well on F1 while flooding reviewers."),
        ("What is calibration?", "Predicted probabilities matching observed frequencies: of everything scored 0.2, about 20% actually occurs."),
    ],
    extra_cards=[
        ("Discretise predicted probabilities and compare to observed rate. What are you testing?", "Calibration. Well-calibrated bins hug the diagonal on a reliability diagram."),
        ("Why can logistic regression be overconfident?", "Maximum likelihood pushes probabilities toward 0 and 1 for separable or extreme data; temperature scaling or Platt scaling fixes it."),
        ("What is the odds ratio here?", "exp(\u03b2\u2c7c): the change in odds per unit change in feature j, holding others fixed."),
        ("Regularised logistic loss adds what term?", "\u03bb/2 ||\u03b2||\u00b2, which bounds the coefficients and makes separation impossible."),
    ],
    math_why="Everything in this lab falls out of one decision: model the outcome as "
             "Bernoulli and pick the link. The cost of that choice is a linear "
             "boundary; the benefit is a calibrated probability you can threshold "
             "on business grounds.",
    math=[
        ("Sigmoid and its derivatives",
         "sigma(z) = 1/(1+e^-z)\nd sigma/dz = sigma(z) * (1 - sigma(z))\nmax derivative = 0.25 at z = 0",
         "The derivative's maximum of 1/4 means gradients vanish for extreme scores \u2014 "
         "the vanishing-gradient problem in its mildest form, and the reason we "
         "standardise and use a sensible learning rate.",
         "z = \u221220: p = 2.06e-10, p\u00b7(1\u2212p) \u2248 2e-10. The gradient contribution is "
         "effectively zero, so that row stops learning even if it is misclassified."),
        ("Cross-entropy from maximum likelihood",
         "P(y) = prod_i p_i^y_i (1-p_i)^(1-y_i)\nlog P(y) = sum_i [y_i log p_i + (1-y_i) log(1-p_i)]\nJ = -log P(y)/m",
         "The likelihood of a set of Bernoulli labels factorises exactly because "
         "observations are conditionally independent. Taking logs turns products into "
         "sums, which is what makes the optimisation tractable.",
         "Two rows, one y=1 with p=0.9 and one y=0 with p=0.1: log-likelihood = "
         "log 0.9 + log 0.9 = -0.21, so J = 0.105. Confident and correct is cheap."),
        ("Stable log-loss",
         "log(1 - sigma(z)) for z >= 0:  = log(1 + e^-z) = log1p(e^-z)\nlog(sigma(z)) for z < 0:   = -z + log1p(e^z)\nloss = -[y*logp + (1-y)*log1p_mp]",
         "The two branches avoid evaluating e^(+large), which overflows a double at "
         "about 709. This is the difference between a fit that converges and one that "
         "returns NaN on row 50.",
         "z = \u22121000, y = 1: naive code computes log(0.0) = -Infinity, J becomes "
         "NaN and the loop dies. Stable form gives -y\u00b7z + log1p(e^z) = 0.0 exactly."),
        ("Gradient and convexity",
         "dJ/d beta_j = (1/m) sum_i (p_i - y_i) x_ij\nJ is convex in beta => gradient descent reaches the global optimum",
         "Cross-entropy is convex, so there is a single global minimum and no "
         "restarts or learning-rate drama beyond step size. Regularisation keeps it "
         "strictly convex and makes the solution unique.",
         "On separable data the minimum is at infinity, so J decreases monotonically "
         "and \u03b2 grows without bound \u2014 convexity, not convergence, is the issue."),
        ("Threshold and expected cost",
         "Cost(t) = FP(t) * cFP + FN(t) * cFN\noptimal t* = argmin_t Cost(t)\nfor calibrated p: classify 1 iff p > cFP/(cFP+cFN)",
         "The optimal threshold is a function of the cost ratio, not of the data. A "
         "missed case costing 10x a false alarm moves the threshold to about 0.09.",
         "cFP = 5, cFN = 50: threshold \u2248 0.09. At that point recall rises sharply "
         "and precision falls \u2014 the right trade when a missed case is a missed "
         "fraud."),
        ("Gradient descent step size",
         "Hessian of J = (1/m) X^T W X, W = diag(p(1-p))\nalpha < 2 / lambda_max(H)",
         "Because W \u2208 (0, 0.25], the curvature is bounded, which gives a principled "
         "step-size ceiling. Too large and the iterates oscillate; too small and 1000 "
         "iterations is not enough.",
         "With standardised features and n=1000, p=10, lambda_max \u2248 2.5, so "
         "alpha = 0.1 is safely stable; alpha = 0.9 diverges and the loss becomes NaN."),
    ],
    math_traps=[
        "log(0), log(1) and overflow in e^z \u2014 use the two-branch stable form.",
        "Averaging the loss over rows while leaving the gradient un-normalised \u2014 inconsistent by a factor of m.",
        "Comparing AUC across datasets with different base rates; AUC is base-rate invariant but the operating point is not.",
        "Reporting accuracy on a 1% positive class and concluding the model works.",
    ],
    math_problems=[
        "Derive dJ/d\u03b2\u2c7c from the likelihood and verify against finite differences on a 4-row example.",
        "Compute the loss for p = [0.9, 0.1] with y = [1, 0] and again with y = [0, 1]; explain the difference in three sentences.",
        "Show that log(sigmoid(-800)) is NaN in double precision but the stable form returns a finite number.",
        "For cFP = 5 and cFN = 50, compute the cost-optimal threshold and the resulting precision/recall on a small labelled set.",
        "Plot the loss surface for two collinear features and show the long valley that scaling fixes.",
    ],
    tree="""src/com/ml/lab02/
  Main.java                 driver: synthetic binary data, fit, report
  LogisticRegression.java   fit(), predictProba(), predict(threshold), coefficients()
  Metrics.java              confusion matrix, precision, recall, F1, AUC, PR curve
  ThresholdSweeper.java     cost-matrix driven threshold selection
  Calibration.java          reliability bins and expected calibration error""",
    tree_note="The stable log-loss lives in one place (`logLoss`) and is used by "
              "both the trainer and the reporter \u2014 two implementations of log-loss "
              "will eventually disagree, and that bug is invisible.",
    types=[
        ("LogisticRegression", "owns \u03b2, the fitted scaler, and the prediction threshold"),
        ("Metrics", "confusionMatrix(), precision(), recall(), f1(), rocAuc(), prCurve()"),
        ("ThresholdSweeper", "given a cost matrix, returns the threshold minimising expected cost"),
        ("Calibration", "reliabilityBins() and expectedCalibrationError() over predicted scores"),
    ],
    patterns=[
        ("Numerically stable loss and sigmoid",
         "One place for both, with the two-branch structure documented so nobody "
         "later 'simplifies' it back into the overflow bug.",
         """static double logLoss(double z, int y) {
    // max(z,0) form avoids evaluating exp(+huge); log1p keeps precision near 0
    if (y == 1) {
        return z >= 0 ? Math.log1p(Math.exp(-z)) : -z + Math.log1p(Math.exp(z));
    }
    return z >= 0 ? Math.log1p(Math.exp(-z)) - z : Math.log1p(Math.exp(z));
}

static double sigmoid(double z) {
    if (z >= 0) return 1.0 / (1.0 + Math.exp(-z));
    double e = Math.exp(z);            // e in (0,1], no overflow
    return e / (1.0 + e);
}"""),
        ("Training loop with L2 and a convergence guard",
         "Learning rate, penalty strength and max iterations are constructor "
         "arguments, not constants. Convergence is on relative loss change, which is "
         "scale-free.",
         """public void fit(double[][] x, int[] y, double lr, double lambda, int maxIter) {
    int n = x.length, p = x[0].length;
    beta = new double[p];
    double prev = Double.POSITIVE_INFINITY;
    for (int it = 0; it < maxIter; it++) {
        double loss = 0;
        double[] grad = new double[p];
        for (int i = 0; i < n; i++) {           // accumulate loss and gradient
            double z = 0;
            for (int j = 0; j < p; j++) z += beta[j] * xs[i][j];
            double pi = sigmoid(z);
            loss += y[i] == 1 ? -Math.log(Math.max(pi, 1e-15))
                              : -Math.log(Math.max(1 - pi, 1e-15));
            double g = pi - y[i];
            for (int j = 0; j < p; j++) grad[j] += g * xs[i][j];
        }
        loss = loss / n + lambda * sumSquares(beta) / 2;
        for (int j = 0; j < p; j++) beta[j] -= lr * (grad[j] / n + lambda * beta[j]);
        if (Math.abs(prev - loss) < 1e-9 * Math.max(1.0, Math.abs(loss))) break;
        prev = loss;
    }
}"""),
        ("Cost-matrix threshold selection",
         "Sweep every distinct score, compute the realised cost at each candidate "
         "threshold, and return the argmin. This is the piece reviewers ask about, "
         "so it is explicit rather than buried in a config file.",
         """public static double optimalThreshold(double[] scores, int[] y,
                                         double costFp, double costFn) {
    double[] uniq = Arrays.stream(scores).distinct().sorted().toArray();
    double bestT = 0.5, bestCost = Double.MAX_VALUE;
    for (double t : uniq) {                      // predict 1 iff score >= t
        long fp = 0, fn = 0;
        for (int i = 0; i < scores.length; i++) {
            boolean pred = scores[i] >= t;
            if (pred && y[i] == 0) fp++;
            if (!pred && y[i] == 1) fn++;
        }
        double cost = fp * costFp + fn * costFn;
        if (cost < bestCost) { bestCost = cost; bestT = t; }
    }
    return bestT;
}"""),
    ],
    costs=[
        ("One full gradient pass", "O(np)", "row-parallel; accumulate grad into a per-thread buffer then reduce"),
        ("Training for k iterations", "O(k n p)", "k typically 200\u20132000 with a good learning rate"),
        ("predictProba(row)", "O(p)", "one dot product plus a sigmoid"),
        ("Full metric suite incl. AUC", "O(n log n)", "sort once for ROC and reuse ranks for PR"),
    ],
    numerics=[
        "Never call log(sigmoid(z)) without the two-branch guard.",
        "Initialise \u03b2 = 0 and assert the first loss is within 1e-9 of log 2.",
        "Standardise features; the Hessian condition number scales with feature scale.",
        "Use L2 by default \u2014 it prevents separation blowups and stabilises \u03b2.",
        "Sweep the threshold on a validation split, never on the test set.",
    ],
    tests=[
        "Sanity: at \u03b2 = 0 all probabilities equal 0.5 and loss equals log 2.",
        "Separation: perfectly separable data with \u03bb > 0 keeps every |coefficient| below 1/sqrt(\u03bb).",
        "Stability: no NaN for z in [\u22121000, 10000] across both label values.",
        "Monotonicity: increasing a positive coefficient increases p for x\u2c7c > 0.",
        "AUC sanity: a perfect ranking gives 1.0, random scores give \u2248 0.5, inverted gives 0.0.",
        "Calibration: on synthetic data from the model itself, mean predicted \u2248 observed rate within 2%.",
    ],
    extensions=[
        "Implement class weighting and show it moves the threshold's optimal position.",
        "Add Platt scaling / temperature scaling as a post-hoc calibration stage and re-measure ECE.",
        "Implement multiclass (one-vs-rest and softmax) and compare against the binary path.",
        "Report the decision curve analysis in addition to ROC so cost-sensitive readers get their curve.",
    ],
    code_checklist=[
        "Stable log-loss in exactly one place",
        "Learning rate, penalty and threshold are constructor/config values",
        "Threshold chosen on validation data with the cost matrix in the repo",
        "Tests cover the extreme-z and separation cases",
        "Confusion matrix printed in every example run",
        "Model artifact contains \u03b2, scaler stats and threshold together",
    ],
    exercise_selfcheck=[
        "I can state my threshold and the cost ratio behind it",
        "My coefficients are bounded and my loss converged",
        "I reported a confusion matrix, not just accuracy",
        "I checked calibration, not only AUC",
    ],
    exercises=[
        ("Derive and implement stable log-loss",
         "Write the loss so it never overflows, then prove it against the naive form.",
         ["Implement naive and stable versions side by side.",
          "Test z from -1000 to 1000 for both label values.",
          "Assert |naive_stable| < 1e-9 wherever the naive version is finite.",
          "Print the first z at which the naive version returns NaN."],
         "A test that fails on the naive version and passes on yours, with the failing z reported."),
        ("Gradient descent from first principles",
         "Derive the gradient, code the loop, and show convergence on separable and non-separable data.",
         ["Implement dJ/db as (p - y).mean().",
          "Run with alpha in {0.01, 0.1, 0.5, 2.0}; record divergence.",
          "Plot loss vs iteration as text.",
          "Show separable loss keeps dropping while ||beta|| grows."],
         "Four convergence traces and a written explanation of the two failure regimes."),
        ("Full confusion matrix and metric suite",
         "Compute TP/FP/FN/TN and every derived metric from scratch and cross-check by hand.",
         ["Write confusionMatrix(int[] y, int[] yHat).",
          "Derive precision, recall, specificity, F1, accuracy from the four cells.",
          "Compute ROC AUC by the rank method and by the trapezoid method; assert equality.",
          "Build a PR curve and integrate it."],
         "A metrics class with two independent AUC implementations agreeing to 1e-9."),
        ("Threshold sweep with a cost matrix",
         "Turn business costs into an operating point.",
         ["Implement optimalThreshold with costs cFP and cFN.",
          "Sweep cost ratio from 1:1 to 1:100 and plot the threshold.",
          "Report precision/recall/cost at each setting.",
          "Write the recommendation for a fraud team."],
         "A cost curve plus a one-paragraph operating-point recommendation."),
        ("Calibration diagnostics",
         "Test whether predicted probabilities mean what they say.",
         ["Bin predictions into deciles and compare to observed rates.",
          "Compute expected calibration error.",
          "Fit on biased data and show miscalibration.",
          "Add temperature scaling and show ECE drop."],
         "A reliability diagram before and after scaling."),
        ("Regularisation sweep and separation",
         "Use lambda to control coefficient growth on separable data.",
         ["Create separable data (y = x > 0).",
          "Sweep lambda over 7 decades with and without the penalty.",
          "Plot max|beta| and validation loss vs lambda.",
          "Pick lambda from the curve and justify it."],
         "Two plots and a lambda choice justified by held-out loss."),
        ("Class weighting for imbalanced fraud",
         "Handle imbalance without letting precision collapse.",
         ["Add per-class weights w1 and w0 to the loss.",
          "Sweep the weight ratio and report precision/recall at 0.5.",
          "Compare with threshold tuning at weight 1.",
          "Explain which one a reviewer would prefer."],
         "A comparison table of weighting vs thresholding with a stated recommendation."),
        ("Ship a scoring endpoint",
         "Expose the model over HTTP and prove parity with the batch path.",
         ["Serialise beta, scaler and threshold to a properties file.",
          "Serve POST /score returning p and the label at the configured threshold.",
          "Assert served p equals offline predictProba to 1e-9.",
          "Log model version, threshold and p for every call."],
         "A running endpoint, a parity test and a curl transcript."),
    ],
    quiz=[
        ("Logistic regression's decision boundary is...", ["Arbitrary", "A hyperplane defined by log-odds = 0", "A set of axis-aligned splits", "Defined by the nearest neighbours"], 1, "Only the log-odds are linear; any invertible monotone transformation of them also yields a linear boundary."),
        ("Cross-entropy equals...", ["Mean squared error", "Negative log-likelihood of Bernoulli outcomes", "Hinge loss", "Regularisation penalty"], 1, "It is exactly -log P(y|X), so minimising it is maximum likelihood."),
        ("The initial loss at beta = 0 is...", ["0", "log 2 \u2248 0.693", "1", "-log 2"], 1, "All probabilities are 0.5, so each row contributes -log 0.5 = log 2."),
        ("Complete separation causes...", ["Underfitting", "Coefficients diverging while loss keeps falling", "Vanishing features", "Higher accuracy always"], 1, "The infimum of the loss is approached at infinite weights; regularisation restores a finite optimum."),
        ("Why scale features for logistic regression?", ["It is required for correctness", "Better conditioning for gradient descent and uniform penalties", "It removes the intercept", "It makes p linear"], 1, "Correctness is unaffected; optimisation speed and penalty fairness are."),
        ("F1 ignores which quantity?", ["False positives", "False negatives", "True negatives", "Threshold value"], 2, "F1 uses precision and recall only, so a flood of true negatives never hurts the score."),
        ("ROC AUC is best described as...", ["Accuracy at 0.5", "P(score positive > score negative)", "Expected calibration error", "The area under the loss curve"], 1, "AUC is the probability a random positive outranks a random negative \u2014 threshold-free ranking quality."),
        ("For a calibrated model, the cost-optimal threshold is...", ["0.5 always", "cFP / (cFP + cFN)", "The median score", "1 - precision"], 1, "Expected cost is minimised by flipping the decision when p exceeds the cost ratio."),
        ("PSI-style drift aside, how do you detect concept drift?", ["Retrain more often blindly", "Compare live metrics against expected performance", "Increase the learning rate", "Add more features"], 1, "Concept drift shows up as degrading live quality; data drift is detected on feature distributions."),
        ("A model with AUC 0.92 and precision 0.3 at 10% recall...", ["Should ship", "May be useless depending on the cost of a miss", "Is broken", "Needs more features only"], 1, "AUC says nothing about the operating point; price the errors before deciding."),
        ("log(sigmoid(z)) for z = -500 evaluates to...", ["0", "-Infinity then NaN when logged", "500", "-500"], 1, "sigmoid underflows to 0.0, and log(0.0) is -Infinity, which poisons the mean."),
        ("Vanishing gradients in logistic regression come from...", ["The sigmoid derivative peaking at 0.25", "Too many features", "A large learning rate", "Class imbalance"], 0, "Extreme scores saturate the sigmoid, so dJ/db shrinks towards zero for those rows."),
        ("Which statement about calibration is true?", ["High AUC implies calibration", "Calibration is about probability accuracy, AUC about ranking", "They are the same metric", "Only tree models can be calibrated"], 1, "A model can rank perfectly while its probabilities are badly off; Platt or temperature scaling fixes the latter."),
        ("Why stratify the train/test split?", ["To speed up training", "To keep the class ratio identical across folds", "To reduce dimensionality", "To prevent overfitting"], 1, "Stratification preserves the base rate so a rare positive class is not lost in a fold."),
        ("Your model predicts 0 for everything and accuracy is 97%. Why?", ["The learning rate is too small", "Imbalance makes the majority-only baseline strong", "The sigmoid is broken", "Features were scaled"], 1, "Always print the confusion matrix; a trivial predictor should never be reported without one."),
    ],
    vision=dict(
        future="Logistic regression becomes the transparent scoring layer under "
               "constrained regimes: credit, insurance, clinical risk, and any "
               "decision a regulator must be able to interrogate. The frontier is "
               "not more expressive fits but probabilities that stay honest under "
               "shift, with calibration monitored as a first-class metric and "
               "monotonic constraints where business rules exist.",
        good=[
            "Every score is served with its model version, threshold and calibration curve.",
            "Thresholds live in config with the cost matrix next to them in the repo.",
            "Calibration is monitored per segment, not just globally.",
            "A constant baseline (always-negative) is on the same dashboard as the model.",
        ],
        ladder=[
            ("L1", "Fit and score", "Train, threshold at 0.5, report a confusion matrix."),
            ("L2", "Tune the operating point", "Derive the threshold from a cost matrix and justify it in writing."),
            ("L3", "Harden the fit", "Handle separation, weight imbalance, and verify calibration on held-out data."),
            ("L4", "Own it in production", "Monitor calibration and segment performance per week; trigger retraining on drift."),
        ],
        behaviors="Reach for the simplest score that satisfies the decision. Treat "
                  "probability as a claim about the world and check it. Prefer "
                  "monotonic constraints over post-hoc explanation hacks.",
        anti=[
            "A 0.97 accuracy on a 3% positive rate, presented without a confusion matrix.",
            "Tuning the threshold on the test set until the number looks good.",
            "Shipping unbounded coefficients because separation was never checked.",
            "Treating an uncalibrated score as a risk probability in a pricing decision.",
        ],
        trends=[
            "Monotonic and shape-constrained models (GAMs) giving both accuracy and auditability.",
            "Always-on calibration monitoring with automatic Platt/temperature refits.",
            "Conformal prediction for binary outcomes, giving finite-sample coverage guarantees.",
            "Scorecards and feature stores standardising scoring inputs across teams.",
        ],
        d30="Implement log-loss with the two-branch stable form and a unit test that fails on the naive version.",
        d60="Build the cost-matrix threshold sweep and produce a cost curve for a realistic error ratio.",
        d90="Ship a scoring endpoint that logs model version, threshold and probability, plus a per-segment calibration report.",
        metrics=[
            "I can quote my operating point's cost, not just its F1.",
            "I know whether my probabilities are calibrated and by how much.",
            "I can detect separation in a fitted model within seconds of looking at the coefficients.",
            "My threshold is reproducible from a config file and a cost matrix.",
        ],
        closer="A probability you can defend beats a probability you cannot.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Fraud Triage Scorer",
        brief="Score transactions as fraud, choose a cost-driven threshold, and "
              "prove the model beats 'flag nothing' and 'flag everything'.",
        timebox="3 hours",
        why="Fraud is the canonical imbalanced, asymmetric-cost problem. If your "
            "threshold logic survives here, it survives most risk queues.",
        requirements=[
            "Synthesise 200k transactions with ~2% fraud, including class-conditional features (amount z-score, velocity, hour).",
            "Implement logistic regression with L2 and a stable log-loss.",
            "Derive the cost-optimal threshold from a stated cost matrix (false positive = 1, false negative = 60).",
            "Report the confusion matrix, PR curve, AUC, and expected cost per 10k transactions.",
            "Check calibration by decile and report ECE.",
            "Write a 10-line model card including the known attack it will miss.",
        ],
        steps=[
            ("1", "20m", "Generate data with class-conditional signals and inject 10% label noise", "A CSV where a naive majority classifier scores 98%"),
            ("2", "25m", "Implement LogisticRegression with L2 and stable loss", "Converged fit with bounded coefficients"),
            ("3", "25m", "Implement the full metric suite plus PR curve", "PR curve printed, AUC cross-checked two ways"),
            ("4", "20m", "Run the threshold sweep with the 1:60 cost matrix", "Cost curve with a minimum clearly visible"),
            ("5", "20m", "Calibration deciles and ECE", "Reliability table plus one ECE number"),
            ("6", "20m", "Compare against always-flag and never-flag baselines on cost", "Three-row cost table"),
            ("7", "15m", "Model card with limitations and a retrain trigger", "A card a risk manager can read in 2 minutes"),
        ],
        diagram="""transactions.csv --> FeatureBuilder (velocity, amount z-score, hour)
                        |
                  stratified split
                        |
            +-----------+-----------+
            |                       |
      LogisticRegression      Baselines (never / always flag)
      (L2, stable loss)               |
            |                       |
     threshold sweep (cost 1:60) <----+
            |
   confusion matrix | PR curve | calibration | cost per 10k""",
        notes=[
            "Inject label noise deliberately; a perfectly separable synthetic fraud set teaches you nothing about thresholding.",
            "Report cost per 10k transactions, not percentages \u2014 percentages hide the asymmetry.",
            "Keep the scaler inside the estimator so the artifact is self-contained.",
            "Plot the PR curve, not just ROC; at 2% prevalence the two curves say very different things.",
        ],
        deliverables=[
            "Runnable project with one command producing the metrics table.",
            "Cost-vs-threshold curve and the chosen operating point marked.",
            "Calibration decile table with ECE.",
            "Model card: data, features, metrics, limitations, retrain trigger.",
        ],
        grading=[
            ("Correctness", "30%", "Loss is stable, coefficients bounded, metrics verified against hand calculations"),
            ("Operating point", "25%", "Threshold derived from the cost matrix and defended"),
            ("Evaluation honesty", "20%", "Baselines reported; test set used once; imbalance respected"),
            ("Communication", "15%", "Model card names a real limitation"),
            ("Insight", "10%", "One quantified finding about which fraud types are detectable"),
        ],
        stretch=[
            "Add a velocity-window feature and show the PR-AUC gain it produces.",
            "Implement cost-sensitive thresholding at prediction time and show the effect on the review queue size.",
            "Add a score-distribution drift check that flags when incoming traffic stops matching training.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Transaction Fraud Triage Service",
        scenario="A payments processor reviews ~2M transactions/day. Manual review "
                 "costs $12 and catches 60% of true fraud. You own the model that "
                 "decides what a human looks at, and the audit trail that regulators "
                 "and card networks will read.",
        scale=[
            ("Daily volume", "~2M transactions/day, ~65k transactions/minute at peak"),
            ("Positive rate", "1.5\u20132.5% confirmed fraud, drifting seasonally"),
            ("Review capacity", "1,200 analysts \u00d7 60 reviews/hour \u2248 72k reviews/day"),
            ("Serving SLO", "p99 < 60 ms, availability 99.95%"),
            ("Success metric", "Fraud dollars recovered per analyst-hour; cost per decision"),
        ],
        diagram=""" Authorisation events --> Stream (Kafka) --> Feature service (velocity windows)
                                        |
                              +---------+---------+
                              |                   |
                    Scoring service            Score log (90d)
                    (Java, model in memory)         |
                              |                   |
                    threshold + reason codes        |
                              |                   |
                   +----------+---------+         |
                   |                    |         |
           Auto-decline (95%)     Review queue      |
           low score, low risk    ranked by $      |
                                        |         |
                                  Analyst UI <-----+
                                        |
                              labels fed back (delayed confirmations)
                                        |
                          drift + calibration monitor""",
        components=[
            ("Feature service",
             ["Velocity features from a streaming state store (count per card/IP/device in 1h, 24h)",
              "Amount features as z-score against a 30-day per-merchant baseline",
              "Feature values computed once and reused by scoring and by analyst UI",
              "Feature contract versioned; a schema change requires a dual-write window"]),
            ("Scoring service",
             ["Model loaded from the registry at startup, hot-reloadable without dropping traffic",
              "Returns score, calibrated probability, and top-3 reason codes",
              "p99 under 60 ms with a precomputed feature lookup (no synchronous joins)",
              "Degrades to the previous model version if the registry is unreachable"]),
            ("Decisioning and review queue",
             ["Threshold per risk tier, stored in config with an approver in the change log",
              "Auto-decline only when score, velocity and merchant risk all agree",
              "Review queue ranked by expected dollar loss, not raw score",
              "Every decision emits score, threshold version and feature values for audit"]),
            ("Delayed-label feedback and monitoring",
             ["Chargeback labels arrive 30\u2013120 days late; backfill them into training windows",
              "Weekly calibration report by tier and by acquirer",
              "Drift alert on score distribution and velocity features",
              "Champion/challenger: the challenger scores live traffic in shadow mode"]),
        ],
        timeline=[
            ("Week 1", "Ship rule-based triage with reason codes; publish the review-queue and cost dashboards"),
            ("Week 2", "Model v1 in shadow mode only; compare against rules on live traffic, ship nothing"),
            ("Week 3", "Calibration pass, threshold approval with the fraud team and risk committee"),
            ("Week 4", "Canary at 5% of traffic with an instant revert switch; verify cost per review"),
            ("Week 6", "Ramp to 50%, then 100%; retire the rule set; publish the model card and runbook"),
        ],
        runbook=[
            "# Is the scorer healthy and which version is live?",
            "curl -s localhost:8080/health | jq '{version,modelAgeHours,thresholdSet}'",
            "",
            "# Score distribution today vs last week",
            "curl -s 'localhost:8080/admin/score-dist?window=24h' | jq '.p50,.p99,.mean'",
            "",
            "# Freeze decisions (traffic to manual) during an incident",
            "curl -XPOST localhost:8080/admin/mode -d '{\"mode\":\"MANUAL_ONLY\"}'",
            "",
            "# Roll back to the previous model version",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"fraud-2026-09-21\"}'",
            "",
            "# Confirm the decision log is complete for the audit window",
            "psql -c \"select count(*) from decision_log where created_at > now() - interval '1 hour';\"",
        ],
        metrics=[
            "SLO: 99.95% availability, p99 scoring < 60 ms, decision log completeness 100%.",
            "Business: fraud dollars recovered per analyst-hour; dollars per 1k declined.",
            "Model: recall at the top 1% of scores; calibration error by tier.",
            "Drift: PSI on score distribution and velocity features, alert at 0.2.",
            "Guardrails: false-positive rate on trusted merchants (auto-decline must stay rare).",
        ],
        failures=[
            ("Score distribution collapses to near-constant", "feature service returning stale velocity values", "Fail to MANUAL_ONLY, alert on feature freshness, roll back model version"),
            ("Recall at top 1% drops 20% week over week", "new fraud pattern or an acquirer change", "Compare label-lag windows, inspect drift PSI, retrain on the freshest labels"),
            ("Review queue exceeds analyst capacity", "threshold too loose after a config push", "Auto-widen the threshold with an audited config change and page the ops lead"),
            ("p99 breaches 60 ms", "synchronous feature lookups during peak", "Switch to the precomputed path; cap concurrency on the enrichment client"),
            ("Regulator asks why a customer was declined", "reason codes missing from the decision log", "Every decision already carries score, threshold version and features \u2014 this is why that log exists"),
        ],
        backlog=[
            "Chargeback label backfill job with an explicit freshness SLA per acquirer.",
            "Shadow-mode challenger scoring with automatic promotion when recall improves at equal review volume.",
            "Per-merchant segment calibration so trusted merchants are not over-flagged.",
            "Chaos drill: feature store outage, registry outage and rule-engine outage, each with a documented fallback.",
            "Documented rollback drill every quarter, timed, with the result published.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a decision system with an audit trail: every "
               "decline can be explained with the score, the threshold version and "
               "the feature values that produced it.",
    ),
))
