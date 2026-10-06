# -*- coding: utf-8 -*-
"""Tailored specs for labs/ml/lab01 .. lab05."""

ML = "ML Academy"
URLS_ML = [
    ("scikit-learn \u2014 Linear Models user guide",
     "https://scikit-learn.org/stable/modules/linear_model.html",
     "Canonical OLS/ridge/lasso derivation and the least-squares objective; the "
     "reference for what a closed-form solution actually guarantees."),
    ("NumPy \u2014 linalg module reference",
     "https://numpy.org/doc/stable/reference/routines.linalg.html",
     "`linalg.solve`, `lstsq`, `pinv`, SVD \u2014 how practitioners avoid forming "
     "X\u1d40X explicitly and what conditioning means in practice."),
]

SPECS = []

# ---------------------------------------------------------------- lab01
SPECS.append(dict(
    track="ml", lab="lab01", full_set=False, level="Foundational",
    title="Linear Regression", main_class="com.ml.lab01.Main",
    problem="You have a labelled numeric target and you want the simplest honest "
            "description of how features move it. Linear regression is that "
            "description: a hyperplane through your data whose coefficients are "
            "estimated, not guessed.",
    why_now="Every other algorithm in this track is judged against it. If you cannot "
             "say what residual a tree is correcting, boosting is just incantation.",
    objectives=[
        "Derive and implement the normal-equation solution for OLS",
        "Implement batch gradient descent and explain why closed form usually wins",
        "Compute MSE, MAE, RMSE and R\u00b2 and know which one to quote",
        "Diagnose violated Gauss-Markov assumptions from residual plots",
        "Recognise when multicollinearity makes coefficients uninterpretable",
        "Explain what ridge and lasso actually change about the estimator",
    ],
    concepts=[
        ("The OLS estimator",
         "Ordinary least squares picks the coefficient vector \u03b2 that minimises the "
         "sum of squared residuals, SSR(\u03b2) = \u03a3(y\u1d62 \u2212 x\u1d62\u1d40\u03b2)\u00b2. Because the "
         "objective is a convex quadratic in \u03b2, the optimum is unique when the "
         "design matrix has full column rank. 'Ordinary' just means unweighted "
         "squared loss \u2014 nothing exotic."),
        ("Normal equation versus gradient descent",
         "Setting \u2207SSR(\u03b2) = 0 gives X\u1d40(X\u03b2 \u2212 y) = 0, hence "
         "\u03b2\u0302 = (X\u1d40X)\u207b\u00b9X\u1d40y. That is one solve. Gradient descent "
         "iterates \u03b2 \u2190 \u03b2 \u2212 \u03b1(2/m)X\u1d40(X\u03b2 \u2212 y) instead. Use the "
         "closed form for small p, gradient descent for large p or for the many "
         "variants (ridge, elastic net) that have no closed form."),
        ("Conditioning and why you rarely invert",
         "Forming X\u1d40X squares the condition number: cond(X\u1d40X) \u2248 cond(X)\u00b2. "
         "The stable route is to solve X\u1d40X\u03b2 = X\u1d40y directly (QR, Cholesky) "
         "or use SVD. Invert only for didactic clarity \u2014 and only on well-scaled data."),
        ("Residual analysis",
         "Residual e\u1d62 = y\u1d62 \u2212 \u0177\u1d62 carries the model's complaints. Plot e vs "
         "fitted (curvature means you are missing structure), Q-Q of e (tails mean "
         "fat-tailed noise and invalid standard errors), and e vs each feature "
         "(a random scatter means you exploited the signal)."),
        ("R\u00b2 and its limits",
         "R\u00b2 = 1 \u2212 SSR/SST is a *training* in-sample ratio and can be pushed to 1 "
         "by adding features. Adjusted R\u00b2 penalises parameter count. Quoting "
         "adjusted R\u00b2 as if it were out-of-sample performance is a classic interview "
         "trap and a classic production mistake."),
        ("Regularisation as a bias-variance dial",
         "Ridge minimises SSR + \u03bb||\u03b2||\u00b2: it shrinks coefficients smoothly and "
         "keeps all of them. Lasso uses \u03bb||\u03b2||\u2081 and zeroes small ones, giving "
         "sparse models. Both add bias and reduce variance, and both require scaling "
         "features first or the penalty is applied arbitrarily."),
    ],
    formulas=[
        ("\u03b2\u0302 = (X\u1d40X)\u207b\u00b9X\u1d40y", "Normal equation", "closed-form OLS coefficients (requires invertibility)"),
        ("SSR(\u03b2) = \u03a3(y\u1d62 \u2212 x\u1d62\u1d40\u03b2)\u00b2", "Residual sum of squares", "the quantity OLS minimises"),
        ("\u03b2 \u2190 \u03b2 \u2212 \u03b1(2/m)X\u1d40(X\u03b2 \u2212 y)", "Gradient step", "batch descent on SSR/m"),
        ("MSE = (1/n)\u03a3(y\u1d62 \u2212 \u0177\u1d62)\u00b2", "Mean squared error", "average squared prediction error"),
        ("R\u00b2 = 1 \u2212 SSR/SST", "Coefficient of determination", "in-sample variance explained"),
        ("R\u00b2_adj = 1 \u2212 (1\u2212R\u00b2)(n\u22121)/(n\u2212p\u22121)", "Adjusted R\u00b2", "parameter-count-penalised fit"),
        ("\u03b2\u0302_ridge = (X\u1d40X + \u03bbI)\u207b\u00b9X\u1d40y", "Ridge solution", "shrinkage added to the normal equation"),
        ("\u03bb_i = \u03c3\u00b2/\u03c3_x\u00b2", "OLS standard error", "uncertainty in the variance of a coefficient"),
    ],
    flow=[
        "Load the data and split **before** touching it: 70/15/15 with a fixed seed, stratified if the target is categorical.",
        "Fit preprocessing (impute, scale) on the *training fold only* and apply it forward \u2014 this is where leakage enters if you skip it.",
        "Solve for \u03b2\u0302 with a QR or SVD-based least-squares routine; keep the singular values to diagnose rank deficiency.",
        "Compute predictions and the full error suite: MSE, MAE, RMSE, R\u00b2, adjusted R\u00b2.",
        "Plot residuals against fitted values and each feature; hunt curvature, fans, and outliers.",
        "Check the coefficient table: expected sign, plausible magnitude, and VIF for collinearity.",
        "Re-run on the held-out split and compare train vs test error \u2014 the gap is your variance estimate.",
    ],
    assumptions=[
        "Linearity in the parameters (not in the features \u2014 you may add terms)",
        "E[\u03b5 | X] = 0: no omitted variable correlated with a feature",
        "Homoscedasticity: Var(\u03b5 | X) = \u03c3\u00b2 (otherwise use HC robust errors)",
        "No perfect multicollinearity between features (X\u1d40X invertible)",
        "Independent observations; for time series, no autocorrelation in \u03b5",
        "Exogenous sampling \u2014 features are not themselves functions of the error",
    ],
    pitfalls=[
        ("Coefficients flip sign on tiny data changes", "multicollinearity inflating the variance of \u03b2", "standardise, drop redundant columns, or report the model not the coefficients"),
        ("R\u00b2 = 0.99, production error is terrible", "in-sample fit quoted as generalisation", "always report held-out or cross-validated error next to R\u00b2"),
        ("Test score better than train score", "you fitted the scaler or imputer on the full dataset", "fit preprocessing inside the training fold only"),
        ("MSE explodes when one row has a big label", "squared loss is outlier-dominated", "report MAE alongside; consider Huber loss for heavy-tailed labels"),
        ("NaN coefficients or LinAlgException", "rank-deficient design matrix (constant column, duplicate feature)", "drop constant columns, assert rank, regularise"),
        ("Prediction drifts after a feature rescale upstream", "model learned on a different unit than production feeds", "version the preprocessing into the model artifact"),
    ],
    java=[
        ("java.util.Arrays / streams", "sorting, mean, and in-place normalisation without extra dependencies"),
        ("Apache Commons Math (RealMatrix)", "a dependable Gaussian-elimination and LU solve for the didactic normal equation"),
        ("DoubleSummaryStatistics", "streaming mean/variance/count without keeping the whole array"),
        ("java.util.random.Random / SplittableRandom", "reproducible splits and bootstrap resampling"),
        ("record FeatureRow(double[] x, double y)", "an immutable row type keeps train/test code honest"),
        ("Math.log1p / Math.expm1", "numerically stable log and exp when you move to log-link variants"),
    ],
    links=[
        "**Lab 02** replaces the linear output with a probability so you can classify.",
        "**Lab 05** shows how badly scaling and correlated features hurt distance-based methods.",
        "**Lab 08 (PCA)** is the regularised answer to 'too many correlated features'.",
        "**Lab 09 (Gradient Boosting)** repeatedly fits shallow trees to the residuals this lab leaves behind.",
        "**Lab 10** supplies the honest evaluation protocol this lab deliberately avoids.",
    ],
    checklist=[
        "I can derive \u03b2\u0302 from \u2207SSR = 0 without notes",
        "I can explain why forming X\u1d40X is numerically worse than solving directly",
        "I can read a residual plot and name what is wrong",
        "I can state the five Gauss-Markov conditions and what each buys me",
        "I can justify MAE over MSE for a heavy-tailed target",
        "I can explain what ridge changes and why scaling must come first",
    ],
    cards=[
        ("What does 'ordinary' mean in ordinary least squares?", "Unweighted squared-error loss: every residual contributes equally regardless of sign or size."),
        ("What is BLUE?", "Best Linear Unbiased Estimator. OLS is BLUE under the Gauss-Markov assumptions."),
        ("Why avoid forming X\u1d40X explicitly?", "It squares the condition number; QR, Cholesky or SVD is numerically safer and never needs an inverse."),
        ("What breaks the exogeneity assumption E[\u03b5|X]=0 in practice?", "An omitted variable that both affects y and is correlated with a feature \u2014 classic example is wage regressions on education."),
        ("MSE or MAE for a target with extreme outliers?", "MAE. MSE grows quadratically with the outlier and effectively hands the fit to one point."),
        ("What is the Gauss-Markov theorem's actual claim?", "Under those five assumptions no other linear unbiased estimator has lower variance than OLS."),
        ("Is a high R\u00b2 evidence of a good model?", "No. R\u00b2 is in-sample; with enough features it approaches 1 for a worthless model."),
        ("What does a residual fan shape (heteroscedasticity) break?", "The constant-variance assumption, so the textbook standard errors and t-statistics become unreliable."),
        ("How does ridge differ from lasso?", "Ridge shrinks all coefficients smoothly (L2); lasso can drive coefficients exactly to zero (L1), yielding sparsity."),
        ("Why scale features before ridge?", "The penalty applies to coefficient magnitude; unscaled features make it penalise units rather than information."),
    ],
    extra_cards=[
        ("What is VIF and why compute it?", "Variance inflation factor per feature: VIF_j = 1/(1-R\u00b2_j) regressed on the other columns. Above ~10 the coefficient is not interpretable."),
        ("Homoscedasticity violated \u2014 what now?", "Use heteroscedasticity-robust (HC3) standard errors; the coefficients stay valid, only the inference changes."),
        ("Why is gradient descent preferred over the normal equation at scale?", "X\u1d40X is p\u00d7p, so cost and memory grow quadratically in feature count, and ridge has no closed form anyway."),
        ("Adjusted R\u00b2 penalises what exactly?", "Parameter count, via (n-1)/(n-p-1). It is still an in-sample statistic \u2014 not a generalisation estimate."),
    ],
    math_why="Linear regression is the cleanest place to see three ideas that recur "
             "for the rest of the track: a convex objective with a unique optimum, "
             "the geometry of least squares as projection, and the variance of an "
             "estimator growing with feature collinearity.",
    math=[
        ("Least-squares normal equation",
         "grad_beta SSR = 2 X^T (X beta - y) = 0\n  =>  X^T X beta = X^T y\n  =>  beta_hat = (X^T X)^-1 X^T y",
         "The gradient vanishes at the optimum because SSR is convex. If X^T X is "
         "singular the objective is flat along some direction and \u03b2\u0302 is not unique.",
         "Two features, x1 = [1,2,3,4], x2 = 2*x1. X^T X is singular; RSSO(8) "
         "throws LinAlgException. Fix: drop x2 or use ridge (\u03bb>0 makes X^T X + \u03bbI PD)."),
        ("Projection geometry",
         "SSR_min = ||y||^2 - y^T P_X y,   P_X = X (X^T X)^-1 X^T\nR^2 = 1 - SSR/SST = y^T P_X y / y^T y",
         "OLS is the orthogonal projection of y onto the column space of X. R\u00b2 is "
         "literally the squared cosine between y and its projection \u2014 that is why it "
         "is bounded by 1 and why it cannot go negative once an intercept is present.",
         "y perfectly predicted: R\u00b2 = 1. Adding p useless features to n points with "
         "an intercept still gives R\u00b2 \u2248 1 in sample, and a negative value out of sample."),
        ("Gauss-Markov and the variance of beta",
         "Var(beta_hat | X) = sigma^2 (X^T X)^-1\nVar(beta_j) = sigma^2 / (SST_xj (1 - R_j^2))",
         "The diagonal of (X^T X)\u207b\u00b9 is the variance of each coefficient. As R\u00b2_j "
         "\u2192 1 (collinearity) the denominator vanishes and the variance explodes. This "
         "is the mechanism behind sign-flipping coefficients.",
         "Add a feature that is 0.99-correlated with an existing one: R\u00b2_j = 0.98, "
         "so (1-R\u00b2_j) = 0.02 and the standard error grows about 7\u00d7 versus an "
         "uncorrelated feature."),
        ("Gradient descent convergence",
         "f(beta_k) - f(beta*) <= 2 L ||beta_0 - beta*||^2 / (2^k alpha L)",
         "For L-smooth convex f, the gap shrinks geometrically. The condition number "
         "\u03ba = L/\u03bc sets the stable range alpha \u2208 (0, 2/L): too small and you crawl, "
         "too large and you diverge or ring around the optimum.",
         "L = 2X\u1d40X's largest eigenvalue, say 12. alpha = 0.05 (stable); alpha = 0.5 "
         "diverges. With \u03ba = 500, ridge's \u03bb and the shape of X should be standardised."),
        ("Ridge as Bayesian MAP",
         "beta_hat(lam) = (X^T X + lam I)^-1 X^T y\n equivalent to: beta ~ N(0, sigma^2/lam I), noise ~ N(0, sigma^2 I)",
         "Ridge is the MAP estimate under a zero-mean Gaussian prior on the weights. "
         "That is a real modelling statement, not just a numerical hack \u2014 it says "
         "large weights need more evidence.",
         "With lam = 1 and a feature whose OLS coefficient was 12.0, the ridge "
         "coefficient lands near 1.1: shrunk hard, still ordered, never exactly zero."),
        ("Evaluation arithmetic and units",
         "RMSE = sqrt(MSE);  MAE = mean|e|\nRMSE/MAE ratio: 1 for Gaussian noise, >1 for heavy tails\nMAPE is undefined when any y = 0",
         "RMSE and MAE live in the target's units, which makes them quotable in a "
         "SLO. Their ratio is a cheap tail diagnostic; MAPE explodes near zero and "
         "should be replaced with sMAPE or WAPE.",
         "Residuals: 100 points at 1, one at 100. MAE = 1.9, RMSE = 10.0, ratio 5.3 "
         "\u2014 the metric you shipped must match the business loss function."),
    ],
    math_traps=[
        "Dividing by n instead of n\u22121 for sample variance \u2014 silently biased low.",
        "Computing R\u00b2 without an intercept: it can go negative and means something different.",
        "Standardising the target and then quoting RMSE in standardised units to stakeholders.",
        "Using a Gauss-Jordan inverse instead of a solve: same answer for a 4\u00d74 matrix, different answer for a 400\u00d7400.",
        "Rounding coefficients before deployment \u2014 0.1% coefficient error can move a decision threshold.",
    ],
    math_problems=[
        "For x = [1,2,3,4,5] and y = [2,4,5,4,5], compute \u03b2\u0302, MSE and R\u00b2 by hand and verify with code.",
        "Show that adding a constant column to X makes X\u1d40X singular, then explain why an intercept column is safe only with \u03b2\u2080 excluded.",
        "Derive the gradient of SSR/m and confirm it equals (2/m)X\u1d40X\u03b2 \u2212 (2/m)X\u1d40y by finite differences.",
        "Given \u03c3 = 2 and SST_x = 10 for a feature, compute the standard error of its coefficient when R\u00b2_x = 0 and again at R\u00b2_x = 0.9.",
        "For ridge with p = 3, compute \u03b2\u0302 at \u03bb = 0, 0.1, 1, 10 and plot coefficient magnitude against \u03bb.",
    ],
    tree="""src/com/ml/lab01/
  Main.java                 driver: loads data, fits, reports metrics
  LinearRegression.java     the estimator: fit(), predict(), coefficients()
  Matrix.java               minimal double[][] helpers (solve, transpose, identity)
  Metrics.java              mse, mae, rmse, r2, adjustedR2
  ResidualDiagnostics.java  residual stats, VIF, autocorrelation at lag k""",
    tree_note="Deliberately dependency-free so every operation is visible. Swap "
              "`Matrix.solve` for a QR or SVD implementation and watch the "
              "conditioning section of THEORY.md stop being academic.",
    types=[
        ("LinearRegression", "holds \u03b2, the fitted mean, and a fit()/predict() pair; stateless w.r.t. data"),
        ("Matrix", "static double[][] utilities: transpose, identity, matMul, solve (Gaussian elimination)"),
        ("Metrics", "static double[] errorMetrics(y, yHat) returning MSE, MAE, RMSE, R\u00b2, adjR\u00b2"),
        ("ResidualDiagnostics", "residual(), vif(), durbinWatson() \u2014 the assumption checkers"),
    ],
    patterns=[
        ("Fitting by QR-free Gaussian elimination (the didactic path)",
         "Build the normal equations once, then solve. Never invert in production code; "
         "this method is here because it makes the derivation checkable by hand.",
         """public static double[] solve(double[][] a, double[] b) {
    int n = b.length;
    double[][] m = new double[n][n + 1];           // augmented
    for (int i = 0; i < n; i++) {
        System.arraycopy(a[i], 0, m[i], 0, n);
        m[i][n] = b[i];
    }
    for (int col = 0; col < n; col++) {             // forward elimination
        int piv = col;
        for (int r = col + 1; r < n; r++) {
            if (Math.abs(m[r][col]) > Math.abs(m[piv][col])) piv = r;
        }
        if (Math.abs(m[piv][col]) < 1e-12) {
            throw new IllegalStateException("singular matrix at column " + col);
        }
        double[] tmp = m[col]; m[col] = m[piv]; m[piv] = tmp;
        for (int r = col + 1; r < n; r++) {
            double f = m[r][col] / m[col][col];
            for (int c = col; c <= n; c++) m[r][c] -= f * m[col][c];
        }
    }
    double[] x = new double[n];                     // back substitution
    for (int r = n - 1; r >= 0; r--) {
        double s = m[r][n];
        for (int c = r + 1; c < n; c++) s -= m[r][c] * x[c];
        x[r] = s / m[r][r];
    }
    return x;
}"""),
        ("The estimator with a feature-scaling step baked in",
         "Scaling lives inside the estimator so it cannot be forgotten at prediction "
         "time. `fit` records the scaler; `predict` reuses it. This is the single "
         "biggest defence against train/serve skew.",
         """public final class LinearRegression {
    private double[] beta;                 // scaled-space coefficients
    private double[] featureMean, featureScale;
    private double yMean;

    public void fit(double[][] x, double[] y) {
        int n = x.length, p = x[0].length;
        featureMean = colMeans(x);  featureScale = colScales(x);
        double[][] xs = standardize(x, featureMean, featureScale);
        double[][] xtx = new double[p][p];
        double[]  xty = new double[p];
        for (int i = 0; i < n; i++)                 // accumulate X^T X and X^T y
            for (int a = 0; a < p; a++) {
                xty[a] += xs[i][a] * y[i];
                for (int b = 0; b < p; b++) xtx[a][b] += xs[i][a] * xs[i][b];
            }
        for (int a = 0; a < p; a++) xtx[a][a] += 1e-8;  // tiny ridge for stability
        beta = Matrix.solve(xtx, xty);
        yMean = Arrays.stream(y).average().orElseThrow();
    }

    public double predict(double[] row) {
        double s = 0;
        for (int j = 0; j < beta.length; j++)
            s += beta[j] * (row[j] - featureMean[j]) / featureScale[j];
        return s + yMean;                          // un-standardise y
    }
}"""),
        ("Streaming metrics that do not need the whole array",
         "Welford's algorithm gives variance in one pass with excellent numerical "
         "behaviour. Use it in the training loop and in any streaming production "
         "metric where retaining rows is not an option.",
         """public static double[] streamingMetrics(DoubleStream ys,
                                           ToDoubleFunction<Double> predict) {
    // Welford: numerically stable mean/M2 in a single pass
    class Acc {
        double n, mean, m2;
        void add(double x) {
            n++;
            double d = x - mean;
            mean += d / n;
            m2 += d * (x - mean);
        }
    }
    Acc truth = new Acc(), err = new Acc();
    ys.forEach(y -> { truth.add(y); err.add(predict.applyAsDouble(y)); });
    double mse = err.m2 / err.n;
    double sst = truth.m2;
    return new double[] { mse, Math.sqrt(mse), Math.abs(err.mean), 1 - err.m2 / sst };
}"""),
    ],
    costs=[
        ("Build X\u1d40X", "O(n p\u00b2)", "dominant cost; parallelise over rows if p is large"),
        ("Gaussian elimination on p\u00d7p", "O(p\u00b3)", "fine to p \u2248 1000; switch to iterative above that"),
        ("One prediction", "O(p)", "pure dot product with the coefficient vector"),
        ("Full metric suite", "O(n p)", "two passes, memory O(1) with Welford"),
    ],
    numerics=[
        "Standardise features before solving; scaling is a preconditioner for the normal equations.",
        "Add a token ridge (1e-8) only to make the solve total, and say so in a comment \u2014 do not hide real collinearity.",
        "Compare against a one-feature baseline; if the full model cannot beat it, the extra features are noise.",
        "Use `Math.fma` where available to avoid cancellation in long dot products.",
        "Report coefficient uncertainty (\u03c3\u00b2(X\u1d40X)\u207b\u00b9 diagonal) alongside point estimates \u2014 a coefficient with a t-statistic of 0.1 is not a finding.",
    ],
    tests=[
        "Perfect-fit test: y = 3 + 2x synthetically \u21d2 \u03b2 = (2, 3) within 1e-9 and R\u00b2 = 1.",
        "Invariance test: scaling a feature by 1000 must not change R\u00b2 and must scale \u03b2 by 0.001.",
        "Singularity test: duplicate a column and assert the explicit failure, not a silent garbage answer.",
        "Symmetry test: adding a constant to every y must shift the intercept by exactly that constant.",
        "Property test: for random X with full rank, OLS residuals must be orthogonal to every column of X (X\u1d40e \u2248 0).",
        "Golden test: a fixed tiny dataset with hand-computed coefficients locked in as expected values.",
    ],
    extensions=[
        "Swap `Matrix.solve` for QR and add an assertion that both agree to 1e-10 on well-conditioned data.",
        "Implement ridge by augmenting X\u1d40X with \u03bbI and sweep \u03bb; plot train/test error to pick it honestly.",
        "Add iteratively reweighted least squares (IRLS) for a target whose variance grows with its mean.",
        "Report bootstrap confidence intervals on each coefficient using `SplittableRandom` for determinism.",
    ],
    code_checklist=[
        "Preprocessing lives inside the estimator, not the caller",
        "Singular matrices fail loudly with a message naming the column",
        "Seeds and splits are constants, not ambient randomness",
        "Metrics are computed on held-out data and both are reported",
        "No `double` accumulation without considering Kahan or Welford",
        "Every numeric constant has a comment explaining why that value",
    ],
    exercise_selfcheck=[
        "My held-out MSE is worse than a mean-only baseline",
        "I checked residual plots and can name one residual structure",
        "I can reproduce my coefficient vector by hand on a 3-point dataset",
        "I refactored so the test split is provably untouched by preprocessing",
    ],
    exercises=[
        ("Implement the normal equation from scratch",
         "Build X\u1d40X and X\u1d40y by hand in nested loops, then solve with Gaussian elimination including partial pivoting.",
         ["Generate n=200 rows from y = 2 + 1.5\u00b7x1 \u2212 0.5\u00b7x2 + noise.",
          "Construct X with an intercept column of 1.0s.",
          "Accumulate xtx and xty; assert xtx is symmetric to 1e-12.",
          "Solve and compare \u03b2 against a least-squares result you compute by gradient descent instead."],
         "A `solve()` that recovers (2.0, 1.5, -0.5) to within 1e-6, plus a test that throws on a singular matrix."),
        ("Implement batch gradient descent and compare",
         "Derive the gradient of SSR/m, code plain gradient descent, then add momentum and compare convergence curves.",
         ["Implement the loss as a `ToDoubleFunction<double[]>`.",
          "Track the loss every iteration and stop when the relative change < 1e-8.",
          "Plot (text-based) loss vs iteration for \u03b1 in {1e-4, 1e-3, 1e-2, 1e-1}.",
          "Report iterations to reach 1e-6 loss for each \u03b1."],
         "A table of iterations-to-converge per learning rate and one sentence on why the largest \u03b1 diverges."),
        ("Build the metric suite and check units",
         "Implement MSE, RMSE, MAE, R\u00b2, adjusted R\u00b2 and MAPE, then reason about when each one lies.",
         ["Compute all metrics on a train split and a test split.",
          "Construct a deliberately outlier-contaminated set and compare RMSE to MAE.",
          "Include a y = 0 case and show MAPE's failure mode.",
          "Replace MAPE with sMAPE and WAPE and report all three."],
         "A metric table plus a 5-line note on which metric maps to which business loss."),
        ("Residual diagnostics toolkit",
         "Write a Residuals class producing the numbers you would check before trusting a fit.",
         ["Plot residual vs fitted as an ASCII scatter.",
          "Compute Q-Q correlation: regress standardised residuals on theoretical normal quantiles.",
          "Implement Durbin-Watson for lag-1 autocorrelation.",
          "Flag any residual with |standardised residual| > 3."],
         "A diagnostics report that flags linearity violation, heavy tails, or serial correlation with evidence for each."),
        ("Variance inflation and collinearity surgery",
         "Add a near-duplicate feature, watch VIF explode, then fix it.",
         ["Implement VIF per feature via auxiliary regressions.",
          "Add x3 = x1 + 0.01\u00b7noise and report VIF before and after.",
          "Drop one of the pair and show R\u00b2 barely moves while coefficient stability improves.",
          "Repeat with 5 correlated features to show VIF compounding."],
         "A before/after table of VIF, coefficient standard errors, and R\u00b2."),
        ("Ridge from \u03bb = 0 to \u03bb = 100",
         "Implement ridge by augmenting the normal equations and use it to see shrinkage happen.",
         ["Solve (\u03bb) over a logarithmic grid of 20 values.",
          "Plot each coefficient magnitude against \u03bb.",
          "Hold out 20% and plot test MSE against \u03bb.",
          "Argue for the \u03bb you would ship, using the curve rather than taste."],
         "Two ASCII plots and a written \u03bb choice defended by the test-error curve."),
        ("Streaming Welford over a 10M-row synthetic stream",
         "Compute mean, variance, MSE and R\u00b2 in one pass without retaining rows.",
         ["Generate rows lazily from a supplier so memory stays O(1).",
          "Assert streaming variance matches a two-pass computation on 100k rows.",
          "Report throughput in rows/sec.",
          "Repeat with a data set that has an extreme outlier to show the numerical advantage."],
         "A benchmark showing agreement with two-pass results and a throughput number."),
        ("Honest evaluation harness",
         "Write k-fold cross-validation and stop yourself from fooling yourself.",
         ["Implement stratified k-fold with a fixed seed.",
          "Fit the scaler inside each fold, not outside.",
          "Report mean \u00b1 std of MSE and R\u00b2 across folds.",
          "Deliberately leak the scaler and show the optimistic bias it introduces."],
         "A comparison table of honest vs leaked CV, with the size of the optimism quantified."),
        ("Coefficient uncertainty and bootstrap intervals",
         "Answer 'is this coefficient real?' with resampling instead of assertion.",
         ["Compute OLS standard errors from \u03c3\u00b2(X\u1d40X)\u207b\u00b9.",
          "Bootstrap rows with replacement, B = 500, refitting each time.",
          "Report the 2.5/50/97.5 percentiles per coefficient.",
          "Compare the analytic and bootstrap intervals and explain any gap."],
         "A table of analytic vs bootstrap intervals, flagging any coefficient whose interval spans zero."),
        ("Ship it: a tiny prediction service",
         "Package the model plus its scaler behind `com.sun.net.httpserver` and prove the served prediction matches the batch one.",
         ["Serialise \u03b2, featureMean and featureScale to a properties file.",
          "Expose POST /predict accepting JSON-ish key=value input.",
          "Assert served output equals offline `predict()` to 1e-9.",
          "Log the coefficient vector and model version in the response."],
         "A running server, a golden-file test, and a curl transcript proving parity."),
    ],
    quiz=[
        ("What is the objective minimised by ordinary least squares?", ["Sum of absolute residuals", "Sum of squared residuals", "Maximum likelihood over any distribution", "Sum of residual signs"], 1, "OLS minimises \u03a3(y\u1d62 \u2212 \u0177\u1d62)\u00b2. Absolute loss gives LAD regression, a different estimator."),
        ("When does the normal equation fail?", ["When n < p", "When X\u1d40X is singular", "When y is skewed", "When p = 2"], 1, "The closed form needs X\u1d40X invertible. n < p implies singularity; skewness is irrelevant to the solve."),
        ("What does R\u00b2 = 1 \u2212 SSR/SST actually measure?", ["Out-of-sample accuracy", "In-sample proportion of variance explained", "Correlation between two features", "Statistical significance"], 1, "It is an in-sample ratio. A model with 500 useless features on 100 points scores near 1."),
        ("Which assumption covers unequal error spread across the range of a feature?", ["Linearity", "Homoscedasticity", "Independence", "Normality"], 1, "Constant Var(\u03b5|X) = \u03c3\u00b2 is homoscedasticity. Its violation needs robust errors or a variance model."),
        ("Why does multicollinearity inflate standard errors?", ["It adds variance to y", "It shrinks the diagonal of (X\u1d40X)\u207b\u00b9 toward zero", "It reduces n", "It biases the intercept"], 1, "As R\u00b2_j \u2192 1 the factor 1/(1\u2212R\u00b2_j) in Var(\u03b2_j) diverges, so tiny data changes move \u03b2_j a lot."),
        ("Which penalty does lasso apply?", ["L\u2082 only", "L\u2081 only", "L\u2081 and L\u2082", "Neither"], 1, "Lasso uses L\u2081, whose subgradient includes zero \u2014 that is exactly why coefficients can be exactly 0."),
        ("You scale a feature by 1000 and refit without penalty. What changes?", ["R\u00b2 changes", "That feature's coefficient scales by 1/1000", "The intercept becomes biased", "MSE improves"], 1, "Standardisation rescales \u03b2 by the reciprocal and leaves fitted values, hence R\u00b2 and MSE, untouched."),
        ("MSE = 400 and MAE = 12 on the same test set. What does that suggest?", ["Residuals are symmetric and light-tailed", "Residuals have heavy tails or outliers", "The model is unbiased", "The labels are integers"], 1, "RMSE/MAE \u2248 5.3 indicates a few large errors dominate; report MAE for the business loss."),
        ("What is the practical benefit of ridge over OLS?", ["It is always more accurate", "It shrinks coefficients and stabilises estimates under collinearity", "It removes the intercept", "It guarantees sparsity"], 1, "Ridge adds bias to cut variance; it never gives exact sparsity."),
        ("What does Durbin-Watson near 2 indicate?", ["Positive autocorrelation", "No first-order autocorrelation", "Heteroscedasticity", "Non-normality"], 1, "DW \u2248 2 means residuals are not serially correlated; values well below 2 mean positive autocorrelation."),
        ("Why must cross-validation folds each refit the scaler?", ["It is a convention with no effect", "Otherwise the test fold's statistics leak into training", "It speeds up convergence", "It reduces dimensionality"], 1, "Fitting the scaler on all data leaks test distribution information and inflates CV scores."),
        ("A ridge penalty is added without standardising features. What breaks?", ["Nothing, it is scale-invariant", "The penalty penalises whichever features have the largest units", "The intercept is removed", "R\u00b2 becomes undefined"], 1, "The penalty acts on coefficient magnitude, so an unstandardised millimetre feature is punished more than a standardised one."),
        ("Which statement about adjusted R\u00b2 is correct?", ["It is out-of-sample performance", "It penalises parameter count but remains in-sample", "It replaces cross-validation", "It can exceed 1"], 1, "It corrects for p via (n\u22121)/(n\u2212p\u22121) and still describes the training fit."),
        ("Computing SSE via \u03a3y\u00b2 \u2212 \u03a3y\u0177 + \u03a3\u0177\u00b2 is numerically...", ["Always preferable", "Unstable for large-magnitude y because of cancellation", "Equivalent to computing residuals directly", "Only valid with an intercept"], 1, "Summing squares of large numbers then subtracting loses precision; summing residuals directly is stable."),
        ("Two models, same test set, R\u00b2 0.80 vs 0.78. Which do you ship?", ["The higher R\u00b2, always", "The one with better held-out MAE and a defensible cost per error", "The simpler one, always", "Neither \u2014 R\u00b2 is meaningless"], 1, "Decision must come from the metric that matches the loss and from a statistically honest comparison, not from a single number."),
    ],
    vision=dict(
        future="Linear regression survives as the transparent baseline every ML system "
               "is measured against, and as the interpretable tier inside regulated "
               "decisions. The direction of travel is not fancier \u03b2 \u2014 it is \u03b2 that "
               "carries its own uncertainty, updates when the data drifts, and can be "
               "explained to a regulator in one sentence.",
        good=[
            "Every service ships a mean/baseline predictor next to the real model, and its test error is on the same dashboard.",
            "Coefficients are published with confidence intervals and a direction sanity check, not as bare numbers.",
            "Preprocessing lives inside the model artifact so train/serve skew is structurally impossible.",
            "Regularisation strength (\u03bb, or the feature scaling contract) is a versioned config value, not a hard-coded constant.",
        ],
        ladder=[
            ("L1", "Fit and explain", "Read a residual plot and name the assumption you violated."),
            ("L2", "Debug the fit", "Trace a coefficient change back to collinearity, scaling or leakage."),
            ("L3", "Engineer the estimator", "Add ridge/lasso, pick \u03bb from a held-out curve, justify it in writing."),
            ("L4", "Own it in production", "Alert on feature drift, retrain on a schedule, publish intervals with every prediction batch."),
        ],
        behaviors="Write the residual plot before the metric. State assumptions out "
                  "loud and test them. Prefer the model you can explain to a "
                  "non-technical stakeholder unless you have measured evidence that "
                  "a complex one beats it in a way that matters.",
        anti=[
            "Quoting training R\u00b2 in a slide deck as 'accuracy'.",
            "Throwing features at a model until the metric improves, with no held-out set to catch it.",
            "Hand-editing coefficients in a spreadsheet because the fit 'looked wrong'.",
            "Scaling outside the estimator, then wondering why production predictions drift.",
        ],
        trends=[
            "Interpretable-by-default models (GAMs, monotonic constraints, sparse scoring) as a regulated baseline tier.",
            "Uncertainty-aware reporting: prediction intervals and heteroscedastic noise models on every forecast.",
            "Streaming/online variants of linear models that track distribution shift without full retraining.",
            "Conformal prediction wrapping any regressor to guarantee marginal coverage.",
        ],
        d30="Implement OLS via QR, add the metric suite, and reproduce a coefficient vector by hand on a small dataset.",
        d60="Build the k-fold harness with in-fold preprocessing and quantify the optimism a leaked scaler introduces.",
        d90="Ship a prediction endpoint with a baked-in scaler, a baseline comparison on the same dashboard, and a drift alert on feature means.",
        metrics=[
            "I can state my model's test MAE and the baseline's, side by side, without looking anything up.",
            "Given a residual plot I can name the violated assumption in under 30 seconds.",
            "I can justify a regularisation strength from a curve rather than a preference.",
            "A colleague can reproduce my exact test score from the repo with one command.",
        ],
        closer="Regression literacy is not a stepping stone to something better \u2014 it "
               "is the part that tells you whether anything you built is real.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Demand Forecaster with an Honest Evaluation Harness",
        brief="Build a small regression service that predicts daily demand per store "
              "and SKU, with the preprocessing, the baseline, and the evaluation "
              "protocol all inside the same artifact.",
        timebox="3\u20134 hours",
        why="The interesting part of a forecasting model is not the fit \u2014 it is the "
            "baseline it must beat, the split that respects time, and the fact that "
            "the scaler must ship with the coefficients. This project forces all three.",
        requirements=[
            "Load a CSV of date, store_id, sku, promo_flag, price, units_sold (synthesise 2 years of data if you have none).",
            "Engineer features: day-of-week one-hot, month, rolling 7-day mean of *past* units only, and a promo interaction.",
            "Implement OLS (closed form) plus a ridge variant with a \u03bb you select from a held-out curve.",
            "Ship a mean-of-last-28-days baseline and beat it, or explain why you cannot.",
            "Split by time (train on the past, test on the last 30 days), never randomly.",
            "Report MSE, MAE, R\u00b2 and a per-SKU breakdown; write a 10-line model card.",
        ],
        steps=[
            ("1", "20m", "Synthesise or load the dataset; assert no future leakage in feature construction", "A CSV plus a leakage checklist you can defend"),
            ("2", "25m", "Implement `features(row, asOfDate)` so a row's features only use history", "Refusing any feature that would need future data"),
            ("3", "30m", "Implement OLS and ridge with in-estimator scaling", "Coefficients reproduce to 1e-8 and ridge shrinks them"),
            ("4", "25m", "Build the time-based split and the 28-day-mean baseline", "Baseline MAE computed and printed first"),
            ("5", "30m", "Sweep \u03bb on the validation window, plot test error, choose \u03bb", "A defensible \u03bb plus the curve that justifies it"),
            ("6", "25m", "Per-SKU error breakdown and a residual diagnostic pass", "Worst 5 SKUs explained in one line each"),
            ("7", "20m", "Write the model card and a README with the exact run command", "A stranger reproduces your numbers in one command"),
        ],
        diagram="""CSV rows --> FeatureBuilder (uses history only)
                    |
                    v
             [time split: train / valid / test-30d]
                    |
        +-----------+-----------+
        |                       |
   Standardizer            Baseline (28-day mean)
   (inside estimator)             |
        |                       |
     OLS / ridge                 |
        |                       |
        +-----------+-----------+
                    v
        Metrics + per-SKU report + model card""",
        notes=[
            "Rolling means must use `shift(1)` semantics: today's feature cannot include today's sales.",
            "Promo interactions are where ridge earns its keep \u2014 promo and price are strongly correlated.",
            "Store a `featureVersion` string with the artifact so a schema change is detectable.",
            "Print the baseline metric before your model metric; it disciplines every claim that follows.",
        ],
        deliverables=[
            "Runnable Maven/Gradle project with one command to reproduce the reported numbers.",
            "Metrics table: baseline vs OLS vs ridge\u03bb*, train/valid/test, MAE and MSE.",
            "ASCII plots of validation error vs \u03bb and of residuals vs fitted.",
            "10-line model card: data, features, metrics, known limitations, retrain trigger.",
        ],
        grading=[
            ("Correctness", "30%", "Coefficients verified by hand; no leakage; time-based split respected"),
            ("Evaluation honesty", "25%", "Baseline reported, \u03bb chosen from a curve, test set touched once"),
            ("Engineering", "20%", "Estimator owns its preprocessing; artifacts are versioned; tests pass"),
            ("Communication", "15%", "Model card explains limitations and a retrain trigger"),
            ("Insight", "10%", "At least one non-obvious finding about the data, quantified"),
        ],
        stretch=[
            "Add a seasonal naive baseline (same weekday, previous week) and show which model wins where.",
            "Compute prediction intervals with residual quantiles and report coverage.",
            "Add a drift check that alerts when live rolling-mean features diverge from training.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Store-Level Demand Forecast Service",
        scenario="A 400-store retail chain forecasts next-day units per SKU to drive "
                 "replenishment. Today a vendor spreadsheet is emailed each morning; "
                 "it is stale, unversioned, and nobody can say how good it is. You "
                 "replace it with a service, and you are on call when it breaks.",
        scale=[
            ("Rows per training run", "~180M (400 stores \u00d7 ~1.2k active SKUs \u00d7 365 days)"),
            ("Prediction SLA", "Full next-day board in < 20 min, p95 board freshness < 30 min"),
            ("Train frequency", "Nightly at 02:00 local, plus on-demand retrain"),
            ("Consumers", "Replenishment planner UI, auto-order service, finance forecast report"),
            ("Accuracy bar", "Must beat the seasonal-naive baseline by \u2265 5% MAE to promote"),
        ],
        diagram="""  CSV dumps / POS events --> Ingest (validate schema + row counts)
                                        |
                        +---------------+---------------+
                        |                               |
                 Offline store (Parquet)         Validation gate (fail -> page)
                        |                          |
                 Nightly train job (02:00)            |
                        |                          |
                 Model registry (versioned) <--------+
                        |
                 Serving tier: /predict (per-SKU), /board (per-store)
                        |
       +----------------+----------------+
       |                                 |
  Planner UI                     Auto-order service
  (board view)                   (p99 < 120 ms)

  Side channels: metrics -> Prometheus, structured logs, prediction log -> drift monitor""",
        components=[
            ("Ingest and validation",
             ["Read partitioned Parquet by date; reject files with unexpected partitions",
              "Row-count and null-ratio assertions per partition before anything else runs",
              "Idempotent re-runs keyed by (date, store, sku) so a retry cannot double-count",
              "Emit ingestion metrics: rows, reject rate, latency"]),
            ("Feature pipeline",
             ["Calendar features (dow, month, holiday flags) are pure functions of time",
              "Rolling means computed with strict lookback windows, never future values",
              "Price and promo features sourced from the merchandising table with a freshness SLA",
              "Feature definitions versioned in git; the version travels with the model"]),
            ("Training job",
             ["Nightly Docker run on a spot pool with a hard timeout and checkpointing",
              "Sweep \u03bb over a small grid, select on a rolling validation window",
              "Gate: reject any candidate that does not beat seasonal-naive by the agreed margin",
              "Register the model with coefficient vector, scaler, feature version and metrics"]),
            ("Serving tier",
             ["`/predict` single SKU, `/board` whole store; both return the model version",
              "Batch predictions cached per (store, date) because boards are requested repeatedly",
              "P99 under 120 ms; a mean-baseline fallback returns 200 rather than failing the planner",
              "Prediction log retained 90 days for drift analysis and dispute resolution"]),
            ("Monitoring and governance",
             ["Dashboards: MAE by store decile, error by SKU velocity, feature drift PSI",
              "Alert when 7-day rolling MAE degrades > 15% against the model's training error",
              "Weekly retrain trigger when drift PSI exceeds 0.2 on any feature",
              "Model card and approval record attached to every registry entry"]),
        ],
        timeline=[
            ("Week 1", "Ship the baseline: seasonal naive + honest metrics + dashboard, so every later claim has a reference"),
            ("Week 2", "Time-safe feature pipeline with unit tests asserting no future reads"),
            ("Week 3", "Train job, \u03bb sweep, registry entry, and the promotion gate wired to fail closed"),
            ("Week 4", "Shadow serving beside the spreadsheet, then 10% of stores on real decisions"),
            ("Week 5", "100% cutover, spreadsheet retired, runbook published, on-call rotation handed over"),
        ],
        runbook=[
            "# Is tonight's board fresh?",
            "curl -s localhost:8080/health | jq '.boardFreshnessSeconds'",
            "",
            "# Did the nightly train fail?",
            "curl -s localhost:8080/admin/last-run | jq '{status,modelVersion,mae}'",
            "docker logs --since 6h forecast-trainer | grep -i 'gate\\|reject\\|converg'",
            "",
            "# Feature drift on the top features",
            "curl -s 'localhost:8080/admin/drift?feature=rolling7' | jq '.psi,.threshold'",
            "",
            "# Safe mitigation: pin the last known-good model",
            "curl -XPOST localhost:8080/admin/pin -d '{\"version\":\"forecast-2026-09-28\"}'",
            "",
            "# Confirm the board matches the pinned version",
            "curl -s localhost:8080/board?store=0417 | jq '.modelVersion'",
        ],
        metrics=[
            "SLO: 99% of boards served within 30 min of the 02:00 train finishing.",
            "Accuracy: MAE vs seasonal-naive, tracked per store decile and per SKU velocity band.",
            "Freshness: `boardFreshnessSeconds` p95 and max \u2014 the single number the planner team watches.",
            "Promotion gate: no model reaches production without a \u2265 5% MAE improvement over baseline.",
            "Business: stock-out rate and over-order value in the 30 days after cutover, compared to the spreadsheet period.",
        ],
        failures=[
            ("Ingest rejects half the partition after a source schema change", "schema assertion fires", "Fail closed, keep serving yesterday's board, page the data owner"),
            ("Overnight MAE spikes 30%", "stock-out event or a bad promo file", "Pin previous model version, diff the feature distributions, re-run on the affected stores"),
            ("Planner reports stale board", "train job overran its window", "Serve the cached board with an explicit `stale=true` flag rather than blocking the UI"),
            ("P99 predict latency breaches 120 ms", "cache miss storm after a config change", "Warm the batch cache, shed per-SKU calls to the baseline fallback"),
            ("Coefficients flip between nightly runs", "collinear price/promo features", "Standardise features, report the \u03bb chosen, alert on coefficient sign changes > 20%"),
        ],
        backlog=[
            "Add prediction intervals to the board so planners can see uncertainty, not just point estimates.",
            "Backfill 24 months of POS history so the seasonal-naive baseline is competitive from day one.",
            "Automate \u03bb selection with a Bayesian search once nightly retrains exceed 20 minutes.",
            "Add a shadow evaluation job that scores every candidate against the last 7 days of actuals.",
            "Publish per-store fairness and accuracy audits for the board as an accessibility requirement, not an afterthought.",
        ],
        urls=URLS_ML,
        closer="The deliverable is not the model. It is a forecast service with a "
               "baseline, a gate, a rollback command and a number the planner can "
               "verify in ten seconds.",
    ),
))
