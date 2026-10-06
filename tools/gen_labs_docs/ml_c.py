# -*- coding: utf-8 -*-
"""Tailored specs for labs/ml/lab03 .. lab04."""

from ml_a import URLS_ML

SPECS = []

# ---------------------------------------------------------------- lab03
SPECS.append(dict(
    track="ml", lab="lab03", full_set=False, level="Intermediate",
    title="Decision Trees & Random Forests", main_class="com.ml.lab03.Main",
    problem="Linear models assume the world is smooth. Trees let you carve the "
            "feature space with axis-aligned boxes and capture thresholds, "
            "interactions and non-monotone effects with no transformation.",
    why_now="Trees are the weak learner inside boosting (Lab 09) and the "
             "interpretable model of choice wherever an auditor asks 'why'.",
    objectives=[
        "Compute entropy and Gini impurity and pick the split that maximises impurity reduction",
        "Implement CART regression and classification trees with a stopping rule",
        "Explain bagging: bootstrap resampling plus decorrelated feature subsets",
        "Read feature-importance numbers critically, including their bias",
        "Control overfitting with depth, min-samples and min-impurity thresholds",
        "Quantify the bias-variance trade-off as forest size grows",
    ],
    concepts=[
        ("Impurity and information gain",
         "A leaf is pure when all labels match; impurity measures the opposite. "
         "Information gain IG(S,A) = impurity(S) \u2212 \u03a3_v (|S_v|/|S|)impurity(S_v). "
         "Entropy uses base-2 logs and is measured in bits; Gini is cheaper and "
         "usually picks the same splits, differing mainly on tiny datasets."),
        ("Greedy recursive partitioning",
         "Trees are built top-down, greedily taking the best split at each node. "
         "This is not globally optimal \u2014 a split that looks terrible now may enable "
         "an excellent split later. It is fast and, in practice, good enough; nobody "
         "solves the optimal-decision-tree problem in production."),
        ("Overfitting and the stopping rule",
         "An unrestricted tree memorises the training set: 100% train accuracy and "
         "a worse test score than a stump. Stop on max_depth, min_samples_split, "
         "min_samples_leaf or min_impurity_decrease. Validation curves, not intuition, "
         "should pick these."),
        ("Bagging and why it works",
         "Each tree sees a bootstrap sample (n draws with replacement), so trees are "
         "diverse but individually high-variance. Averaging predictions cancels "
         "uncorrelated variance: variance of a mean of B independent trees with "
         "variance \u03c3\u00b2 is \u03c3\u00b2/B. You cannot parallelise bagging without that "
         "independence."),
        ("Random forests and feature randomness",
         "At each split, forests consider only a random subset of m features "
         "(typically \u221ad). Without it, the strongest feature would be chosen at "
         "every node and all trees would be near-identical \u2014 low diversity, no "
         "variance reduction. This single change is why forests beat plain bagging."),
        ("Feature importance, honestly",
         "Impurity-based importance (total impurity decrease, weighted by node size) "
         "biasedly favours high-cardinality features. Permutation importance on "
         "held-out data is the defensible default. Report permutation importance "
         "with error bars, or do not report importance at all."),
    ],
    formulas=[
        ("H(S) = \u2212\u03a3 p(c) log\u2082 p(c)", "Entropy", "uncertainty of the label distribution (bits)"),
        ("Gini(S) = 1 \u2212 \u03a3 p(c)\u00b2", "Gini impurity", "cheaper alternative, same split choices"),
        ("IG = impurity(S) \u2212 \u03a3 (n_v/n) impurity(S_v)", "Information gain", "drop in impurity from a split"),
        ("P(\u03b2) = 1/n \u03a3 1[y\u1d62 in bootstrap]", "Bootstrap sample", "n draws with replacement from n rows"),
        ("Var(mean of B) = \u03c3\u00b2/B", "Variance reduction", "why averaging helps, only if trees differ"),
        ("OOB error", "Out-of-bag estimate", "each row's error from trees that never saw it \u2014 free cross-validation"),
    ],
    flow=[
        "Encode categoricals as ordinal splits or one-hot; decide explicitly, because a tree will exploit the encoding.",
        "At each node, evaluate every candidate threshold on a random feature subset and take the best.",
        "Split while depth/size/impurity rules allow; a pure node becomes a leaf.",
        "Leaf value: mean target (regression) or majority class / class proportions (classification).",
        "Grow B trees on bootstrap samples; average or majority-vote the predictions.",
        "Read permutation importance on held-out data, then prune or re-fit if importance is diffuse.",
    ],
    assumptions=[
        "Features are comparable or explicitly one-hot encoded; ordinal encoding of nominals invents order",
        "Splits are axis-aligned \u2014 rotation-sensitive, so scaling does not matter but geometry does",
        "Bootstrap diversity holds; correlated trees (highly collinear features) reduce the benefit",
        "Enough samples per leaf; otherwise leaves memorise noise",
        "Features are available at prediction time (a tree cannot invent a feature)",
        "Extrapolation is impossible: trees never predict outside the training range",
    ],
    pitfalls=[
        ("Train accuracy 100%, test accuracy poor", "no stopping rule, pure leaves", "cap depth, require min_samples_leaf, validate"),
        ("Importance ranks a high-cardinality ID column first", "impurity-based bias toward many distinct values", "use permutation importance, or drop identifiers entirely"),
        ("Adding 200 trees does not help", "correlated trees limit the variance reduction", "check pairwise tree correlation and try more feature randomness"),
        ("Trees perform worse than the linear baseline", "features are rotatable (PCA-style) and trees are axis-aligned", "rotate/project features, or use an ensemble that is rotation-oblivious"),
        ("Predicting outside the training range", "trees cannot extrapolate", "clip predictions, or model the extremes separately"),
        ("Same result across runs after 'randomising'", "bootstrap built from a shared Random seed", "seed per tree, and assert run-to-run variance"),
    ],
    java=[
        ("Arrays.sort on candidate thresholds", "sorting thresholds once per feature avoids O(n\u00b2) scans"),
        ("SplittableRandom", "per-tree bootstrap seeds make forests reproducible"),
        ("double[] / int[] parallel arrays", "zero-boxing feature access inside the hot split loop"),
        ("TreeMap<Integer, Double>", "weighted counts for class proportions at a leaf"),
        ("record Split(int feature, double threshold, double gain)", "an immutable, inspectable split record"),
    ],
    links=[
        "**Lab 04** (SVM) trades the axis-aligned boundary for a smooth maximum-margin one.",
        "**Lab 06** (Naive Bayes) is the generative counterpoint: model P(x|y) instead of splitting on x.",
        "**Lab 08** (PCA) is the standard answer to the rotation-sensitivity problem.",
        "**Lab 09** (Gradient Boosting) reuses trees as weak learners added sequentially.",
    ],
    checklist=[
        "I can compute entropy and Gini by hand and show they pick the same split",
        "I can explain why feature-subset randomness is needed, not optional",
        "I can read OOB error and know it is nearly free cross-validation",
        "I can say why permutation importance beats impurity importance",
        "I know that trees cannot extrapolate",
        "I can pick depth/min-leaf from a validation curve",
    ],
    cards=[
        ("Why are random forests more robust than plain bagging?", "Feature-subset randomness decorrelates the trees; without it every tree picks the same dominant feature and averaging cancels nothing."),
        ("What does OOB error measure?", "The error of each row using only the trees whose bootstrap sample excluded it \u2014 a free, slightly pessimistic cross-validation estimate."),
        ("Entropy vs Gini: which do you use?", "Gini for speed, entropy for the information-theoretic framing; empirically they pick near-identical splits."),
        ("Why does a deeper tree not mean a better model?", "Past the point where the leaves are pure, extra depth only memorises noise; validation error turns upward."),
        ("What makes impurity-based importance biased?", "It rewards features with many candidate split points and large node counts, which high-cardinality features have by construction."),
        ("Can a decision tree extrapolate beyond the training range?", "No. A leaf returns an average or majority of its training rows, so predictions are bounded by the observed range."),
        ("Why is bagging variance \u03c3\u00b2/B?", "Only if the B estimators are independent; correlated trees keep a residual variance that more trees cannot remove."),
        ("What is mtry in a random forest?", "The number of features considered per split, usually \u221ad \u2014 the bias-variance dial of the forest."),
    ],
    extra_cards=[
        ("How do you stop a tree from overfitting?", "max_depth, min_samples_split, min_samples_leaf, min_impurity_decrease, max_features, and early stopping on validation error."),
        ("Trees are invariant to feature scaling. Why does that matter here?", "Because it isolates the real weakness \u2014 axis-aligned splits \u2014 from the linear models' sensitivity to units."),
        ("How do you handle a nominal feature with 500 categories?", "One-hot (or ordinal with an explicit category ordering only if one exists); never feed a raw ID to a tree."),
        ("When is a single deep tree actually the right choice?", "When interpretability rules out ensembles, the data is small, and the interactions are axis-aligned."),
    ],
    math_why="Trees are greedy set partitions. Once you see a split as a "
             "conditional-probability lookup \u2014 P(y|x\u2208leaf) \u2014 the impurity "
             "criteria, the pruning rules and the importance scores all fall out of "
             "the same argument.",
    math=[
        ("Entropy, Gini and information gain",
         "H(S) = -sum_c p_c log2 p_c        Gini(S) = 1 - sum_c p_c^2\nIG(A) = impurity(S) - sum_v (n_v/n) impurity(S_v)",
         "Impurity is 0 for a pure leaf and maximised for a uniform label "
         "distribution. Information gain is the expected impurity of the children "
         "subtracted from the parent, weighted by child size.",
         "S = {0,0,0,1}: H = 0.811 bits. Split x>2.5 gives leaves {0,0} and {0,1}: "
         "weighted child entropy = 0.25\u00b70 + 0.75\u00b70.918 = 0.689, so IG = 0.122 bits."),
        ("Bootstrap variance reduction",
         "Var(mean of B iid trees) = sigma^2 / B\nwith correlation rho: Var = sigma^2 (1 + (B-1)rho) / B",
         "Perfect independence gives the 1/B law. Any correlation rho > 0 leaves an "
         "irreducible floor, which is why feature randomness matters more than raw "
         "tree count.",
         "sigma\u00b2 = 0.25, B = 100. rho = 0 gives 0.0025; rho = 0.1 gives 0.0228 "
         "\u2014 nearly ten times the variance despite the same number of trees."),
        ("Leaf value estimators",
         "regression leaf: yhat = mean(y in leaf)\nclassification leaf: argmax_c p_c, p_c = n_c / n",
         "A leaf is a conditional mean or mode under the fitted model. That is why "
         "trees are poor at extrapolation and why leaf variance tracks local noise.",
         "Leaf with targets [10, 12, 14]: prediction 12, local variance 4/3, local "
         "standard error 0.82 \u2014 a usable uncertainty estimate for free."),
        ("Bias-variance as trees grow",
         "train error decreases monotonically with depth\ntest error ~ bias(depth) + variance(depth) + sigma^2",
         "Deep trees drive bias to near zero and variance up. The optimal depth is "
         "where validation loss turns up, and it usually sits far shallower than "
         "people expect.",
         "With n = 5,000, optimal max_depth is typically 4\u20136 and leaf size 20\u201340. "
         "Depth 20 fits the noise and doubles test error."),
        ("OOB error as cross-validation",
         "row i is in-bag for ~63.2% of trees (1 - (1 - 1/n)^n)\nOOB_i = error of row i over trees where it is out-of-bag",
         "Each row is naturally held out by the bootstrap, so one training run "
         "yields an out-of-sample estimate for every row at no extra compute. It is "
         "slightly pessimistic compared to k-fold.",
         "n = 1,000: expected in-bag trees \u2248 632, out-of-bag \u2248 368. OOB over "
         "1,000 rows \u00d7 368 trees is a tight estimate, unlike 10-fold's 100 rows per fold."),
    ],
    math_traps=[
        "log(0) when a class is absent from a node \u2014 guard the log term.",
        "Using impurity decrease for importance instead of permutation, and reporting the biased number.",
        "Fixing the bootstrap seed across trees, which silently correlates them.",
        "Comparing a tree's OOB error to a linear model's test error without noting OOB is pessimistic.",
    ],
    math_problems=[
        "Compute entropy and Gini for [0,0,0,1] and for [0,1], and say which one information gain prefers.",
        "Find the threshold on a 10-point one-feature dataset that maximises IG; show it by hand.",
        "Given sigma\u00b2 = 0.25, B = 50, compute variance reduction for rho in {0, 0.05, 0.2, 0.5}.",
        "Estimate the expected out-of-bag tree count for n = 10,000 and explain why OOB is pessimistic.",
        "Show that with an ordinal encoding of {small, medium, large} as 0,1,2 the tree can only cut between groups, never within.",
    ],
    tree="""src/com/ml/lab03/
  Main.java                driver on the play-tennis style dataset
  Tree.java                node structure, recursive build, predict
  SplitFinder.java         impurity, candidate thresholds, best split
  RandomForest.java        bootstrap, feature subsets, aggregate, OOB error
  FeatureImportance.java   impurity and permutation importance""",
    tree_note="Split search is the only hot loop. Thresholds are precomputed once "
              "per node from sorted feature values so the inner scan is a linear "
              "scan with running left/right sums, not a sort per candidate.",
    types=[
        ("Tree / Node", "feature, threshold, left, right, prediction, depth \u2014 a plain record tree"),
        ("SplitFinder", "bestSplit(rows, features) returning a Split with gain"),
        ("RandomForest", "fit/predict/predictProba, plus oobError() and treeCorrelation()"),
        ("FeatureImportance", "permutationImportance(model, X, y, repeats)"),
    ],
    patterns=[
        ("Best-threshold search with running sums",
         "Sort once per (node, feature), then scan candidate splits maintaining "
         "left/right class counts. O(n log n) per feature per node instead of "
         "O(n\u00b2).",
         """static Split bestSplit(int[][] x, int[] y, int[] candidates) {
    int n = y.length;
    double bestGain = 0; int bestF = -1; double bestT = 0;
    for (int f : candidates) {
        Integer[] idx = new Integer[n];                 // one sort per feature
        for (int i = 0; i < n; i++) idx[i] = i;
        java.util.Arrays.sort(idx, (a, b) -> Double.compare(x[a][f], x[b][f]));
        int totalPos = 0;
        for (int i = 0; i < n; i++) totalPos += y[i];
        int leftPos = 0, leftN = 0;                      // running counts
        for (int k = 0; k < n - 1; k++) {
            int i = idx[k];
            leftPos += y[i]; leftN++;
            if (x[i][f] == x[idx[k + 1]][f]) continue;   // keep distinct thresholds
            double t = (x[i][f] + x[idx[k + 1]][f]) / 2.0;
            int rightN = n - leftN, rightPos = totalPos - leftPos;
            double gain = giniImpurity(leftPos, leftN) * (leftN / (double) n)
                        + giniImpurity(rightPos, rightN) * (rightN / (double) n);
            gain = 1 - gain;                             // impurity drop, not increase
            if (gain > bestGain) { bestGain = gain; bestF = f; bestT = t; }
        }
    }
    return bestF < 0 ? null : new Split(bestF, bestT, bestGain);
}"""),
        ("Bagging with deterministic per-tree seeds and OOB scoring",
         "One seed per tree keeps the forest reproducible while guaranteeing "
         "independent bootstrap samples. OOB errors are accumulated during the same "
         "pass, so validation costs nothing extra.",
         """public void fit(int[][] x, int[] y, int nTrees) {
    int n = y.length, p = x[0].length, mtry = (int) Math.round(Math.sqrt(p));
    long baseSeed = 0x9E3779B97F4A7C15L;               // golden ratio, arbitrary but fixed
    for (int t = 0; t < nTrees; t++) {
        SplittableRandom rnd = new SplittableRandom(baseSeed + t);  // independent per tree
        int[] bag = new int[n];
        boolean[] inBag = new boolean[n];
        for (int i = 0; i < n; i++) { bag[i] = rnd.nextInt(n); inBag[bag[i]] = true; }
        trees.add(growTree(x, y, bag, mtry, rnd));
        for (int i = 0; i < n; i++)                       // out-of-bag accumulation
            if (!inBag[i]) oobCorrect[i] += trees.get(t).predict(x[i]) == y[i] ? 1 : 0;
        oobCounts[i0(n)]++;                                // per-row OOB tree count
    }
}

public double oobError() {
    double err = 0; int seen = 0;
    for (int i = 0; i < oobCounts.length; i++)
        if (oobCounts[i] > 0) { err += 1.0 - oobCorrect[i] / (double) oobCounts[i]; seen++; }
    return err / seen;
}"""),
    ],
    costs=[
        ("One split search over all features", "O(np log n)", "sorting dominates; restrict to mtry features in a forest"),
        ("Building one tree", "O(n log n \u00b7 features \u00b7 depth)", "shallow trees dominate with max_depth 4\u20138"),
        ("Prediction", "O(depth)", "no matrix multiply, no scaling needed"),
        ("Full forest prediction", "O(B \u00b7 depth)", "parallelise across trees; it is embarrassingly parallel"),
    ],
    numerics=[
        "Guard log(0) in entropy when a node has no positive examples.",
        "Compare gains with a small epsilon so ties do not produce split thrash.",
        "Use `Math.sqrt(p)` for mtry and expose it; it is a real hyperparameter.",
        "Compare tree importances only after permutation importance, with repeats >= 30 for error bars.",
    ],
    tests=[
        "Pure-label node returns a single-class leaf and no split is proposed.",
        "Permutation importance is ~0 for a random noise feature.",
        "A forest with nTrees = 1 equals a single tree's prediction exactly.",
        "OOB tree counts average to about 0.368 \u00b7 nTrees per row for large n.",
        "Trees are invariant to feature scaling (assert identical predictions after scaling).",
        "Run twice with the same seed and assert identical predictions.",
    ],
    extensions=[
        "Implement Extra-Trees (random thresholds as well as random features) and measure the speed/accuracy trade.",
        "Add cost-complexity pruning with a validation-set alpha and plot the pruning curve.",
        "Compute pairwise tree correlation and show it falls as mtry grows.",
    ],
    code_checklist=[
        "Per-tree seeds, not one shared Random",
        "Thresholds precomputed once per node",
        "Depth, leaf size and mtry are constructor arguments",
        "Importance reported by permutation, with repeats",
        "OOB error printed in every example run",
        "Categorical encodings documented in the class JavaDoc",
    ],
    exercise_selfcheck=[
        "I can show a forest's gain over a single tree on the same split",
        "I can explain what happens to variance as nTrees grows with and without feature randomness",
        "My importance ranking survives a permutation test",
        "My forest is reproducible run to run",
    ],
    exercises=[
        ("Implement CART from scratch",
         "Build a classification tree with entropy and a real stopping rule.",
         ["Sort candidate thresholds per node; find the max-IG split.",
          "Add maxDepth, minSamplesLeaf and minImpurityDecrease stopping rules.",
          "Verify on the play-tennis style dataset by hand for the root split.",
          "Assert every leaf is pure or satisfies a stopping rule."],
         "A tree you can print level by level, plus a hand-verified root split."),
        ("Impurity metrics compared",
         "Show empirically that entropy and Gini agree.",
         ["Implement both impurity functions.",
          "Find the best split under each on three datasets.",
          "Report whether the chosen thresholds ever differ.",
          "Explain the tie-breaking difference."],
         "A table of chosen thresholds per dataset with a written explanation."),
        ("Depth versus test error",
         "Find the overfitting knee empirically.",
         ["Train depths 1..12 on a synthetic XOR-plus-noise dataset.",
          "Plot train and test accuracy per depth as text.",
          "Mark the minimum test-error depth.",
          "Explain the train/test divergence in two sentences."],
         "Two ASCII curves and the depth you would ship."),
        ("Bagging without feature randomness",
         "Measure the correlation floor.",
         ["Train 50 plain bagged trees and 50 forest trees.",
          "Compute pairwise prediction disagreement for both.",
          "Report OOB error for both.",
          "Quantify how much variance randomness recovered."],
         "A disagreement matrix summary and a variance-reduction calculation."),
        ("Permutation importance",
         "Replace the biased measure with a defensible one.",
         ["Implement impurity importance.",
          "Implement permutation importance with 30 repeats.",
          "Compare rankings on a dataset with an ID column.",
          "Show impurity ranks the ID first and permutation does not."],
         "Both rankings side by side with the standard error on the permutation numbers."),
        ("OOB as free cross-validation",
         "Validate OOB against explicit k-fold on the same data.",
         ["Implement 5-fold CV with a fixed seed.",
          "Compute OOB error from the forest.",
          "Compare the two numbers and explain the gap.",
          "Show OOB cost is essentially free."],
         "A two-row comparison with a written explanation of the optimism/pessimism."),
        ("Classification with class weighting",
         "Handle imbalance inside the tree.",
         ["Weight class contributions in the impurity calculation.",
          "Train on a 2% positive synthetic set.",
          "Compare accuracy, F1 and PR-AUC weighted vs unweighted.",
          "Pick the operating point and justify it."],
         "A metrics table and a stated recommendation."),
        ("Ship an explainable model",
         "Expose a prediction plus its decision path over HTTP.",
         ["Serialise the tree to a nested text format; reload on start.",
          "Serve POST /predict returning label, probability and the rule path.",
          "Assert the path is non-empty and ends at a pure leaf.",
          "Log model version and tree count."],
         "A running endpoint, a parity test and a sample rule path."),
    ],
    quiz=[
        ("Which impurity measure is measured in bits?", ["Gini", "Entropy", "Both", "Neither"], 1, "Entropy with base-2 logs is in bits; Gini is a probability-like scale."),
        ("What does a random forest randomise beyond bootstrap sampling?", ["The labels", "The feature subset considered at each split", "The learning rate", "The loss function"], 1, "mtry features per split is what decorrelates the trees."),
        ("OOB error is an estimate of...", ["Training error", "Out-of-sample error using trees that never saw the row", "Bias alone", "Variance alone"], 1, "Out-of-bag rows give a held-out prediction for nearly every row at no extra cost."),
        ("Impurity-based importance is biased toward...", ["Low-cardinality features", "High-cardinality features", "Categorical features only", "The first feature"], 1, "More distinct values means more candidate thresholds and larger impurity drops."),
        ("What happens to test error as a single tree deepens?", ["It always falls", "It falls then rises", "It is constant", "It is undefined"], 1, "Bias falls, variance rises; the minimum is well before full depth."),
        ("A pure leaf on training data implies...", ["The model generalises", "No more splits are possible and overfitting risk is high", "The feature is important", "The labels are noise"], 1, "Purity on training data is memorisation, not learning."),
        ("Bagging reduces variance by roughly...", ["1/B", "1/sqrt(B)", "1/log B", "B"], 0, "Averaging B independent estimators gives variance sigma\u00b2/B."),
        ("Trees cannot extrapolate because...", ["They use a linear model at the leaf", "Leaf predictions are averages of observed targets", "They clip at the training mean", "They use sigmoid leaves"], 1, "A leaf returns a mean of its training rows, so it cannot leave the observed range."),
        ("mtry = sqrt(p) is a compromise between...", ["Speed and accuracy", "Bias and variance", "Memory and disk", "Training and inference"], 1, "Too few features per split raises bias; too many correlates the trees."),
        ("The main cost in split search is...", ["Evaluating the prediction", "Sorting candidate thresholds", "Allocating nodes", "Copying the data"], 1, "Sorting dominates, which is why thresholds are cached per node."),
        ("Permutation importance measures...", ["How much the model uses a feature at fit time", "How much accuracy drops when that feature is shuffled at test time", "The feature's variance", "The split's information gain"], 1, "It is a post-hoc, out-of-sample measure and is the one to report."),
        ("Which statement about correlated trees is true?", ["They average fine anyway", "Variance reduction is capped by their correlation", "They overfit less", "They must be pruned"], 1, "The 1/B law assumes independence; correlation leaves an irreducible floor."),
        ("Gini and entropy differ most when...", ["The dataset is huge", "The label distribution is nearly uniform", "There are no features", "All labels are equal"], 1, "Near-uniform distributions make the two curves differ most in shape."),
        ("Why hold out data for a tree's stopping rule?", ["To train faster", "To choose depth/leaf size without biasing the training fit", "To reduce memory", "To fix class imbalance"], 1, "The stopping rule is a hyperparameter and must be selected on data the tree never grew on."),
        ("Adding trees to a forest monotonically improves test error until...", ["The file size limit", "Diversity saturates and the curve flattens", "The seed changes", "Depth is reduced"], 1, "Variance reduction saturates; extra trees cost latency and memory for nothing."),
    ],
    vision=dict(
        future="Trees remain the workhorse for tabular data and the default "
               "interpretable model. The direction is not bigger forests but "
               "diagnostic ones: honest importance, out-of-distribution detection, "
               "and monotonic or shape constraints so the model cannot encode a rule "
               "the business forbids.",
        good=[
            "Every forest reports OOB or held-out error next to its training error.",
            "Importance is permutation-based with error bars, or omitted entirely.",
            "Depth and leaf size come from a validation curve and are recorded in the model card.",
            "Categorical encoding is decided once, documented, and enforced in tests.",
        ],
        ladder=[
            ("L1", "Grow a tree", "Split on information gain, stop on depth, report accuracy."),
            ("L2", "Tune the stopping rule", "Find the depth/leaf-size knee on a validation curve."),
            ("L3", "Ensemble properly", "Add bagging and feature randomness; quantify diversity and OOB error."),
            ("L4", "Make it trustworthy", "Permutation importance, OOD detection, constrained splits, documented in a model card."),
        ],
        behaviors="Print the tree before the accuracy. Prefer honest held-out "
                  "numbers over flattering training curves. Treat an identifier "
                  "column as a bug until proven otherwise.",
        anti=[
            "Reporting impurity importance as if it were a business explanation.",
            "A 20-deep tree shipped because 'more depth means better'.",
            "500 trees when 100 made no difference, doubling latency for nothing.",
            "Feeding raw IDs and then removing the feature that mattered most.",
        ],
        trends=[
            "Gradient-boosted trees taking over most tabular workloads, with forests as the robust baseline.",
            "Explainable Boosting Machines: monotone and shape constraints on inputs and interactions.",
            "Quantile forests for uncertainty bands instead of point predictions.",
            "Tree-based OOD detection (isolation forests, Mahalanobis in leaf space).",
        ],
        d30="Implement CART with entropy and a stopping rule; verify the root split by hand.",
        d60="Build the forest with per-tree seeds, mtry and OOB error; compare against plain bagging.",
        d90="Add permutation importance with repeats and publish a model card stating the depth you chose and why.",
        metrics=[
            "I can quote OOB or held-out error, never training accuracy alone.",
            "I can explain why my forest is better than a single tree in one sentence involving variance.",
            "My importance ranking survives a permutation test.",
            "My forests reproduce exactly across runs.",
        ],
        closer="A forest you can interrogate is worth more than a slightly higher score you cannot explain.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Customer Churn Classifier",
        brief="Predict churn from a tabular dataset with a forest, calibrate the "
              "operating point against the cost of a retention call, and report "
              "importance honestly.",
        timebox="3 hours",
        why="Churn is imbalanced, priced, and full of traps: a tenure feature that "
             "leaks the label, an account ID that looks important, and a business "
             "that cannot afford false alarms.",
        requirements=[
            "Load or synthesise 30k customers with tenure, plan, monthly spend, support tickets, region, churn.",
            "Split stratified; keep customer_id out of the feature set and add a test asserting it.",
            "Train a single tuned tree, then a 200-tree forest with mtry = sqrt(p).",
            "Report OOB error, held-out accuracy, PR-AUC and a confusion matrix at a cost-justified threshold.",
            "Compute permutation importance with 30 repeats; explain the top three features.",
            "Ship the forest as a serialised artifact with a score endpoint that returns the rule path.",
        ],
        steps=[
            ("1", "20m", "Assemble the feature matrix; assert no identifier or post-outcome field is present", "A feature list a reviewer can read"),
            ("2", "20m", "Tune a single tree's depth on validation data", "A depth curve and a chosen depth"),
            ("3", "25m", "Train the 200-tree forest; log OOB and held-out metrics per tree count", "Two curves showing where extra trees stop helping"),
            ("4", "20m", "Threshold sweep with retention-call cost vs lost-customer cost", "A cost curve with a marked optimum"),
            ("5", "25m", "Permutation importance with repeats and standard errors", "A ranked table you would defend in a review"),
            ("6", "20m", "Serialise the forest; serve /predict with the rule path", "Reload from disk and assert identical predictions"),
            ("7", "15m", "Model card: metrics, threshold, cost, limitations, retrain trigger", "A card the retention team can act on"),
        ],
        diagram="""customers.csv --> FeatureBuilder (drops id, adds tenure buckets)
                        |
             stratified split (train / valid / test)
                        |
     +------------------+------------------+
     |                  |                  |
 single tree (tuned)  forest (200)    baseline (predict churn=1)
     |                  |                  |
     +------------------+------------------+
                        |
      OOB + held-out metrics | threshold sweep | permutation importance
                        |
           serialise forest --> /predict (score + rule path)""",
        notes=[
            "A customer_id column will dominate impurity importance; that is the lesson, not a nuisance.",
            "Churn labels drift with the calendar; keep the test split in the future relative to training.",
            "Trees cannot extrapolate, so a rare high-spend segment will be under-predicted \u2014 flag it in the card.",
            "Log tree count vs OOB error so the 200-tree choice is justified rather than assumed.",
        ],
        deliverables=[
            "One-command reproduction script producing the metrics table.",
            "Depth curve, OOB-vs-tree-count curve, and the cost-vs-threshold curve.",
            "Permutation importance table with error bars and a written interpretation.",
            "Model card plus a serialised forest artifact.",
        ],
        grading=[
            ("Correctness", "30%", "Tree implementation verified; identifier excluded; serialisation round-trips"),
            ("Evaluation honesty", "25%", "OOB and held-out both reported; baseline compared; one test set"),
            ("Tuning justification", "20%", "Depth and threshold each chosen from a plotted curve"),
            ("Interpretation", "15%", "Importance defended with repeats and error bars"),
            ("Communication", "10%", "Model card names a real limitation"),
        ],
        stretch=[
            "Add a monotone constraint (higher tenure must not increase churn) and measure the accuracy cost.",
            "Quantile forest for calibrated intervals on the churn probability.",
            "Isolation-forest detector for OOD customers and a report on what it flags.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Churn Scoring for a Subscription Business",
        scenario="A 900k-subscriber SaaS business loses 3.4% of subscribers monthly to "
                 "churn. A retention team of 40 can make about 9,000 save calls a "
                 "week. You own the model that decides who gets called, and the "
                 "contractual and regulatory constraints on profiling.",
        scale=[
            ("Population", "900k active subscribers, ~30k events/day in the product stream"),
            ("Label definition", "cancellation within 30 days of scoring (delayed by up to 30 days)"),
            ("Base rate", "3.4% monthly churn, rising to 5.1% in the first 30 days after signup"),
            ("Action capacity", "~9,000 retention calls/week; the model must rank, not classify"),
            ("SLO", "Nightly score for all subscribers in < 30 min; p99 lookup < 100 ms"),
        ],
        diagram=""" Product events --> Warehouse (events + billing + support)
                        |
                 Nightly feature job (30d lookback)
                        |
            +-----------+-----------+
            |                       |
     Feature snapshot          Labels (30-day delayed)
     (versioned table)               |
            |                       |
      Model training --> Registry --> Scoring service (lookup p99<100ms)
            |                       |
     validation gates        +----+----+
     (beat baseline,        |         |
      calibration)      Retention    Marketing
                       worklist     (win-back flow)
                            |         |
                    Save outcome --> labels (closing the loop)

   Side: drift + calibration monitors, weekly fairness report by plan tier""",
        components=[
            ("Feature pipeline",
             ["30-day lookback windows: logins, feature usage, tickets, invoices, plan changes",
              "Snapshot written to a versioned table so any score can be replayed exactly",
              "Feature definitions owned by a named team; changes require a version bump and shadow run",
              "Late-arriving events reconciled before scoring, never after"]),
            ("Training and promotion gates",
             ["Champion/challenger; the challenger scores live traffic in shadow for 7 days",
              "Gate 1: must beat the rules baseline by 15% recall at equal contact volume",
              "Gate 2: calibration error within tolerance across plan tiers",
              "Gate 3: a human approval record with the reviewer, the numbers and the date"]),
            ("Scoring and worklist",
             ["Nightly batch scores 900k subscribers; a lookup service serves the worklist UI",
              "Ranked worklist of 9,000, not a binary list; capacity is a first-class input",
              "Every worklist row carries the top reason codes for the call script",
              "Contact outcomes (saved / not saved / no answer) written back with the score version"]),
            ("Monitoring and fairness",
             ["Weekly calibration by plan tier, region and tenure band",
              "Drift PSI on features and on the score distribution",
              "Accuracy tracked on matured labels with a 30-day lag, published not alerted",
              "No protected attributes in features; a documented proxy review before each release"]),
        ],
        timeline=[
            ("Week 1", "Rules baseline plus a live worklist so every later model has a reference"),
            ("Week 2", "Feature snapshot pipeline with replay tests; label backfill verified against known cancellations"),
            ("Week 3", "Model v1 in shadow for 7 days; compare recall at equal volume and inspect the mis-ranked accounts"),
            ("Week 4", "Calibration pass, fairness review, human approval; canary at 10% of worklist capacity"),
            ("Week 5", "Full cutover with the rules baseline kept as the rollback target; runbook and on-call handover"),
        ],
        runbook=[
            "# Did tonight's scoring run finish, and which model?",
            "curl -s localhost:8080/admin/last-run | jq '{status,modelVersion,rowsScored,minutes}'",
            "",
            "# Calibration on matured labels",
            "curl -s 'localhost:8080/admin/calibration?window=28d' | jq '.ece,.byTier'",
            "",
            "# Freeze the worklist and fall back to rules (safe manual mode)",
            "curl -XPOST localhost:8080/admin/mode -d '{\"mode\":\"RULES_FALLBACK\"}'",
            "",
            "# Roll back to the previous champion",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"churn-2026-09-14\"}'",
            "",
            "# Verify every worklist row carries a score version",
            "psql -c \"select count(*) from worklist where score_version is null;\"",
        ],
        metrics=[
            "Business: saves per 1,000 calls, and monthly logo churn versus the pre-model baseline.",
            "Model: recall at the top 9,000 of 900k (the capacity-limited operating point).",
            "Calibration: ECE overall and per plan tier; report, do not hide.",
            "Operations: nightly run completes before 05:00; worklist available before the call shift starts.",
            "Guardrail: no tier's recall falls more than 10% relative to the overall rate without an explicit review.",
        ],
        failures=[
            ("Nightly run misses the 05:00 deadline", "feature job slowed by a new join", "Serve yesterday's snapshot with a staleness banner; page the data owner"),
            ("Recall at capacity collapses 25%", "behaviour change or a billing migration", "Roll back to the champion, inspect drift PSI, retrain on post-migration labels"),
            ("Calibration drifts by tier", "a plan mix shift over time", "Retrain with recent windows; add tier-aware recalibration; document in the card"),
            ("Worklist rows missing reason codes", "feature snapshot version mismatch", "Fail the run loudly rather than serving half-populated call scripts"),
            ("A regulator asks about profiling", "no approval record for the live model", "Every promotion stores reviewer, metrics and date \u2014 that record is the answer"),
        ],
        backlog=[
            "Automated label backfill with a freshness SLA per cancellation reason code.",
            "Shadow-mode challenger with automatic promotion on recall gain at equal volume.",
            "Per-tenant override: a human-specified flag must be visible in the worklist and in the audit log.",
            "Documented rollback drill each quarter, timed, result published.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a ranked worklist a 40-person team can act on, "
               "with every score replayable from a versioned feature snapshot and "
               "every promotion carrying an approval record.",
    ),
))

# ---------------------------------------------------------------- lab04
SPECS.append(dict(
    track="ml", lab="lab04", full_set=True, level="Advanced",
    title="Support Vector Machines", main_class="com.ml.lab04.Main",
    problem="You want the most confident separator you can draw between two "
            "classes, and you want it to generalise from the support vectors "
            "alone rather than from every point.",
    why_now="SVMs are the geometric view of classification. Even when you never "
             "ship one, the margin, the kernel trick and the dual form show up in "
             "every modern kernel method.",
    objectives=[
        "State the primal and dual formulations of the hard- and soft-margin problems",
        "Explain the geometric meaning of the margin and why support vectors alone determine the boundary",
        "Implement the kernel trick for linear, polynomial and RBF kernels",
        "Implement a simplified SMO-style coordinate ascent optimiser",
        "Choose C and gamma from validation data and explain what each controls",
        "Recognise when an SVM is the wrong tool: large n, high cardinality, uncalibrated scores",
    ],
    concepts=[
        ("Maximum margin",
         "The decision boundary sits midway between the two closest convex hulls; "
         "the margin width is 2/||w||. Maximising it minimises ||w||, which is what "
         "the primal objective 0.5||w||\u00b2 does. Points strictly outside the margin "
         "never influence the solution."),
        ("Soft margin and the C trade-off",
         "Adding slack \u03be\u1d62 with penalty C \u00b7 \u03a3\u03be\u1d62 allows violations. Large C means "
         "almost no violations (risk overfitting); small C tolerates a wide margin "
         "(underfitting). C is the misclassification budget priced per unit of margin."),
        ("The dual form and support vectors",
         "Training solves max over \u03b1 of \u03a3\u03b1\u1d62 \u2212 0.5||\u03a3\u03b1\u1d62y\u1d62 K(x\u1d62,x\u2c7c)||\u00b2 subject to "
         "0 \u2264 \u03b1\u1d62 \u2264 C and \u03a3\u03b1\u1d62y\u1d62 = 0. The solution is w = \u03a3\u03b1\u1d62y\u1d62x\u1d62, so only points "
         "with \u03b1\u1d62 > 0 matter. Prediction is f(x) = \u03a3\u03b1\u1d62y\u1d62K(x\u1d62,x) + b."),
        ("The kernel trick",
         "Replace x\u1d40x\u02e2 with K(x\u02e2). RBF, exp(\u2212\u03b3||x\u2212x\u02e2||\u00b2), implies an infinite "
         "dimensional feature map; polynomial, (x\u1d40x\u02e2 + r)^d, gives a finite one. "
         "SVMs become the natural model for string, graph and protein similarity \u2014 "
         "anywhere the similarity is already known."),
        ("Feature scaling is mandatory",
         "RBF and polynomial kernels use squared distances. Unstandardised features "
         "with different units make one dimension dominate the distance and the "
         "kernel degenerates. Standardise, and verify with a test that scaling one "
         "feature by 1000 changes results."),
        ("SMO and why it is hard",
         "SMO optimises two \u03b1 values at a time so each subproblem has a closed form. "
         "Complexity is O(n\u00b2\u2013\u00b3) per pass in memory for the kernel matrix, which is "
         "the practical ceiling: SVMs are for n in the thousands, not millions."),
    ],
    formulas=[
        ("min 0.5||w||\u00b2 s.t. y\u1d62(w\u1d40x\u1d62 + b) \u2265 1", "Hard-margin primal", "maximum-margin separator"),
        ("min 0.5||w||\u00b2 + C\u03a3\u03be\u1d62 s.t. y\u1d62f(x\u1d62) \u2265 1 \u2212 \u03be\u1d62", "Soft-margin primal", "slack variables priced by C"),
        ("f(x) = \u03a3 \u03b1\u1d62y\u1d62K(x\u1d62,x) + b", "Decision function", "prediction depends only on support vectors"),
        ("K(x,z) = exp(\u2212\u03b3||x\u2212z||\u00b2)", "RBF kernel", "infinite-dimensional feature map"),
        ("margin width = 2/||w||", "Geometric margin", "objective minimises ||w|| to widen it"),
        ("\u03b1\u1d62 \u2208 [0, C], \u03a3\u03b1\u1d62y\u1d62 = 0", "Dual constraints", "0 < \u03b1 identifies support vectors"),
        ("K(x,z) = (x\u1d40z + r)^d", "Polynomial kernel", "finite-degree expansion"),
        ("gamma = 1/(2\u03c3\u00b2)", "RBF bandwidth", "set from feature variance when not tuned"),
    ],
    flow=[
        "Standardise features, then encode categoricals \u2014 kernels see raw distances.",
        "Choose a kernel: linear for text/high-dim, RBF for compact numeric data, polynomial for interaction counts.",
        "Run SMO-style coordinate ascent over \u03b1 with a shrinking learning rate and a tolerance on KKT violation.",
        "Recover b from the support vectors in the margin band and clip \u03b1 into [0, C] each sweep.",
        "Tune C and gamma on a validation grid; plot the surface, do not eyeball a single point.",
        "Inspect the support vectors: they are the rows your model is made of, and often a data-quality story.",
    ],
    assumptions=[
        "Features are scaled; otherwise the kernel measures the wrong distance",
        "Classes are separable in the induced feature space, or soft margin C is chosen deliberately",
        "n is small enough that an O(n\u00b2) kernel matrix fits comfortably",
        "The similarity function K is a valid positive semi-definite kernel",
        "Independent samples; SVMs have no notion of order or time",
        "Class balance handled by class weights or C, since the margin ignores counts",
    ],
    pitfalls=[
        ("Accuracy collapses after standardisation of one feature", "features were left unscaled so one unit dominated", "standardise everything, and add a scaling-invariance test"),
        ("gamma = 100 blows up training time", "RBF bandwidth far too small, nearly every point becomes a support vector", "use gamma = 1/(p\u00b7Var) as a starting point and validate"),
        ("C = 1e6 memorises the training set", "hard-margin behaviour by construction", "sweep C down; check the support-vector fraction"),
        ("Scores look like probabilities but are not", "SVM outputs are margins, not calibrated probabilities", "wrap in Platt scaling if a probability is needed"),
        ("Kernel matrix OutOfMemoryError", "n\u00b2 doubles exceeds heap at n \u2248 40k", "switch to linear kernel, approximate kernels, or a different algorithm"),
        ("Results change between identical runs", "SMO initialisation uses an unseeded Random", "seed the initialisation and assert reproducibility"),
    ],
    java=[
        ("FunctionalInterface for kernels", "K(x,z) becomes a lambda you can swap and unit-test in isolation"),
        ("PriorityQueue<Double> for SMO selection", "worst-violating \u03b1 chosen first, the standard heuristic"),
        ("double[][] kernelMatrix", "precomputed K for small n; the dominant memory cost"),
        ("Arrays.fill + clipping in the \u03b1 update", "enforcing 0 \u2264 \u03b1 \u2264 C and the equality constraint"),
        ("SplittableRandom", "deterministic \u03b1 initialisation for reproducible training"),
    ],
    links=[
        "**Lab 03** gives the axis-aligned alternative; compare their boundaries on the same data.",
        "**Lab 06** offers the generative shortcut when the class-conditional densities are easy.",
        "**Lab 10** supplies ROC/AUC, which is the right way to compare a margin score across C and gamma.",
        "**Lab 14 in MLOps** shows how a hyperparameter sweep like C\u00d7gamma gets orchestrated.",
    ],
    checklist=[
        "I can state the primal, the dual and the kernel form from memory",
        "I can explain what support vectors are without looking at the formula",
        "I know why standardisation is not optional for RBF",
        "I can tune C and gamma from a validation surface",
        "I know the score is a margin, not a probability",
        "I can state the n at which SVM stops being practical",
    ],
    cards=[
        ("What determines an SVM's decision boundary?", "Only the support vectors, weighted by their dual coefficients \u03b1\u1d62."),
        ("Why standardise features for an RBF kernel?", "The kernel uses squared Euclidean distance, so unscaled units let one dimension dominate and effectively shrink \u03b3 for the rest."),
        ("What does C control?", "The price of each unit of margin violation: large C fits the training data, small C tolerates a wider, smoother margin."),
        ("What is a support vector?", "Any training point with \u03b1\u1d62 > 0 \u2014 a point on or inside the margin. Removing them changes the boundary."),
        ("Is the SVM output a probability?", "No, it is a signed distance-like margin. Wrap it in Platt scaling if a probability is required."),
        ("What does the kernel trick avoid?", "Explicitly computing the feature map, which is what makes infinite-dimensional maps usable."),
        ("Why is SMO used?", "Optimising all \u03b1 jointly has no closed form; updating two at a time makes each subproblem solvable analytically."),
        ("When does an SVM beat a random forest?", "Compact datasets with few features, clear margins, and a need for a smooth boundary without normalisation assumptions."),
    ],
    extra_cards=[
        ("What is the practical memory ceiling for kernel SVMs?", "The O(n\u00b2) kernel matrix: 40,000 rows \u00d7 8 bytes \u2248 12.8 GB, so real limits are in the low tens of thousands."),
        ("gamma in the RBF kernel, intuitively?", "A length scale. Small gamma = distant influence and a smooth boundary; large gamma = local influence and wiggly boundaries."),
        ("Why do polynomial kernels make sense for text?", "String kernels define a similarity over n-gram counts, which is exactly the x\u1d40z term raised to a degree."),
        ("How do you handle imbalance in an SVM?", "Per-class C weights, or adjust the decision threshold on the margin \u2014 never by resampling at prediction time."),
    ],
    math_why="The SVM is where optimisation theory becomes geometry. The dual "
             "derivation shows why only a few points matter, and the kernel trick "
             "shows that a model in an infinite space can still be trained and "
             "evaluated with only pairwise inner products.",
    math=[
        ("Primal to dual",
         "min 0.5||w||^2 + C sum xi   s.t. y_i(w.x_i + b) >= 1 - xi, xi >= 0\ndual: max sum a_i - 0.5 || sum a_i y_i x_i ||^2  s.t. 0 <= a_i <= C, sum a_i y_i = 0",
         "Lagrangian duality is exact for this convex problem: the dual optimum "
         "equals the primal optimum. That is why training can be expressed purely "
         "in terms of pairwise similarities.",
         "For a 3-point linearly separable set, the dual has a unique solution with "
         "two non-zero \u03b1 (the support vectors); the third point's \u03b1 is exactly 0 and it "
         "can be deleted without moving the boundary."),
        ("The margin and its geometric meaning",
         "distance from a point to the boundary = |w.x + b| / ||w||\ncorrect side requires >= 1/||w||, so margin width = 2/||w||\nminimising 0.5||w||^2 maximises the margin",
         "This is why hard-margin SVMs are robust: a point deep inside a class "
         "region has zero influence. Robustness to noise comes from the *loss on "
         "the margin*, not from counting points.",
         "||w|| = 2 gives a margin of 1.0; ||w|| = 10 gives 0.2. A support vector "
         "moved 0.01 along the normal cannot change ||w|| much, but a point that "
         "leaves the margin band enters as a new \u03b1 and can."),
        ("Kernel expansion",
         "linear:   K(x,z) = x.z\npolynomial: K(x,z) = (x.z + r)^d\nRBF:      K(x,z) = exp(-gamma ||x-z||^2)\n||x-z||^2 = ||x||^2 - 2x.z + ||z||^2",
         "Every training and prediction step only ever needs K(x\u1d62,x\u2c7c). Expanding "
         "the polynomial as a feature map gives degree-d terms with binomial "
         "coefficients; the RBF expansion is an infinite sum over the feature map.",
         "Polynomial with d=3, r=1, x.z=2: K = 27, and the expansion is 8x\u2081\u00b3 + "
         "12x\u2081\u00b2x\u2082 + 6x\u2081x\u2082\u00b2 + x\u2082\u00b3 + 6x\u2081\u00b2 + 12x\u2081x\u2082 + 6x\u2082 + 3x\u2081 + 3x\u2082 + 1."),
        ("KKT conditions and SMO convergence",
         "stationarity: w = sum a_i y_i x_i\ncomplementary slackness: a_i (margin violation) = 0\n0 <= a_i <= C, sum a_i y_i = 0\nviolation = |y_i f(x_i) - 1| when 0 < a_i < C",
         "A point with a strictly interior \u03b1 must sit exactly on the margin; a point "
         "at \u03b1 = 0 must be correctly classified outside it; a point at \u03b1 = C is inside "
         "the margin. SMO sweeps \u03b1 until no interior point is violated.",
         "Two interior points violating by 0.01 and -0.02: SMO picks both, solves "
         "the 2x2 quadratic exactly, and the total KKT violation drops by ~0.03 in a "
         "single update."),
        ("Soft margin C and the classification error trade-off",
         "training error ~ C (large C)\ngeneralisation gap = train err - test err grows with C\nfor separable data, large C drives ||w|| -> infinity",
         "There is no closed-form error curve; the only honest way to pick C is a "
         "validation sweep. Separable data plus large C is numerically the worst "
         "case, not the best.",
         "Separable data with C = 1e6: train error 0, support-vector fraction 0.98, "
         "test error 0.19. Dropping C to 0.1 gives 0.94 support vectors and test "
         "error 0.04."),
        ("Scalability, and the practical ceiling",
         "kernel matrix: n^2 doubles = 8n^2 bytes\ntime per SMO pass: O(n^2)\nheuristic bound in use: n < 5 x 10^4",
         "Memory, not time, is the binding constraint. Above that, use a linear "
         "kernel (sparse representation), an approximate kernel, or switch "
         "algorithms entirely.",
         "n = 10,000 needs 800 MB for the matrix; n = 40,000 needs 12.8 GB and "
         "likely OOMs on a 16 GB pod. n = 1,000,000 is unthinkable for a kernel "
         "SVM."),
    ],
    math_traps=[
        "Using RBF without standardising \u2014 gamma then describes a different geometry than you think.",
        "Assuming ||w|| from the dual equals the primal objective; they differ by the slack contribution.",
        "Reading the decision value as a probability and calibrating a threshold on it.",
        "Precomputing a kernel matrix for n above the memory budget instead of switching to a linear kernel.",
        "Sweeping C on the test set; the optimal margin is chosen, not measured.",
    ],
    math_problems=[
        "For two points x=(-1,-1) and z=(1,1) with labels -1 and +1, find the hard-margin solution by hand.",
        "Expand (x\u1d40z + 1)\u00b2 and identify every monomial term with its coefficient.",
        "Show that the RBF kernel matrix for n points is always positive semi-definite by construction.",
        "Compute the kernel matrix for three 2D points under linear, polynomial(d=2) and RBF(gamma=0.5).",
        "Given a trained SVM with \u03b1 = [0.4, 0.0, 0.7] and y = [1, -1, 1], state which points are support vectors and why.",
    ],
    tree="""src/com/ml/lab04/
  Main.java                 driver: 2D separable + noisy datasets
  Svm.java                  primal view: fit via dual, predict, supportVectors()
  Kernel.java               @FunctionalInterface: double of(double[] a, double[] b)
  Kernels.java              linear, polynomial, rbf implementations
  Smo.java                  two-variable coordinate ascent on alpha
  SvmC.java                 C and gamma sweep over a validation grid""",
    tree_note="Kernel evaluation dominates runtime, so Kernels is the only place "
              "that knows about distance. Caching the kernel matrix is correct "
              "only while the data is fixed \u2014 the moment you add rows, the cache "
              "is a correctness bug.",
    types=[
        ("Svm", "alpha[], b, supportVectorIndices; fit/predict/decisionFunction"),
        ("Kernel", "a functional interface so kernels are swappable and unit-testable"),
        ("Smo", "coordinate ascent: pick two alphas, solve the 2x2 subproblem in closed form"),
        ("SvmC", "grid sweep over C and gamma, returning validation curves"),
    ],
    patterns=[
        ("Kernel functions and the squared-distance shortcut",
         "Kernels are lambdas. The RBF expands the squared distance so the inner "
         "product never has to be recomputed per pair.",
         """@FunctionalInterface
public interface Kernel {
    double of(double[] a, double[] b);
    default String name() { return "custom"; }
}

public final class Kernels {
    public static Kernel linear() {
        return (a, b) -> {                       // K(x,z) = x.z
            double s = 0;
            for (int i = 0; i < a.length; i++) s += a[i] * b[i];
            return s;
        };
    }
    public static Kernel rbf(double gamma) {
        return new Kernel() {
            @Override public String name() { return "rbf(" + gamma + ")"; }
            @Override public double of(double[] a, double[] b) {
                double d2 = 0;                   // ||a-b||^2 without cancellation
                for (int i = 0; i < a.length; i++) {
                    double d = a[i] - b[i];
                    d2 += d * d;
                }
                return Math.exp(-gamma * d2);
            }
        };
    }
    public static Kernel poly(double r, int degree) {
        return (a, b) -> {
            double dot = 0;
            for (int i = 0; i < a.length; i++) dot += a[i] * b[i];
            return Math.pow(dot + r, degree);
        };
    }
}"""),
        ("SMO update for two alphas with clipping",
         "The 2x2 subproblem has a closed form; the eta = K11 + K22 - 2K12 guard "
         "catches the degenerate case where the two points are identical.",
         """static void updatePair(int i, int j, double[] a, int[] y, double[][] K,
                         double C, double b) {
    if (a[i] < EPS || a[j] < EPS || a[i] >= C - EPS || a[j] >= C - EPS) return;
    double eta = K[i][i] + K[j][j] - 2 * K[i][j];            // >= 0 for a PSD kernel
    if (eta < 1e-12) return;                                   // identical points
    double oldI = a[i], oldJ = a[j];
    double ei = decision(i, a, y, K, b) - y[i];
    double ej = decision(j, a, y, K, b) - y[j];
    a[j] = clamp(a[j] - y[j] * (ei - ej) / eta, 0, C);         // equality constraint
    double lo = Math.max(0, a[j] - a[i]);
    double hi = Math.min(C, C + C - a[j] - a[i]);
    a[j] = Math.min(hi, Math.max(lo, a[j]));
    a[i] = clamp(a[i] + y[i] * y[j] * (oldJ - a[j]), 0, C);    // keep sum a_i y_i fixed
}

static double decision(int k, double[] a, int[] y, double[][] K, double b) {
    double f = b;
    for (int m = 0; m < a.length; m++) if (a[m] > EPS) f += a[m] * y[m] * K[m][k];
    return f;
}"""),
    ],
    costs=[
        ("Kernel matrix construction", "O(n\u00b2p)", "memory 8n\u00b2 bytes is usually the binding limit"),
        ("One SMO sweep over all pairs", "O(n\u00b2)", "in practice far fewer pairs thanks to the violation heuristic"),
        ("Training to tolerance", "O(pass \u00b7 n\u00b2)", "typically 5\u201330 passes with a shrinking eta"),
        ("Prediction per point", "O(s \u00b7 d)", "s = number of support vectors, d = kernel dimension"),
    ],
    numerics=[
        "Standardise before computing any kernel; add a test that fails without it.",
        "Use an epsilon when deciding whether an alpha is at a bound.",
        "Recompute b as the mean over support vectors strictly inside the margin.",
        "Track the KKT violation and stop on it, not on a fixed iteration count.",
        "Report the support-vector fraction; above ~0.8 the model is memorising.",
    ],
    tests=[
        "SVC on two well-separated points recovers w with ||w|| within 5% of the analytic value.",
        "Scaling one feature by 1000 changes predictions \u2014 proving scaling is active, not decorative.",
        "A linear kernel on linearly separable data yields zero training error.",
        "The linear kernel on a linear model reproduces a plain logistic/perceptron solution up to the loss used.",
        "SMO's final KKT violation is below 1e-4 for every interior alpha.",
        "Two identical rows produce eta <= 0 and are skipped without NaN.",
    ],
    extensions=[
        "Add Platt scaling and show the sigmoid probabilities are calibrated on held-out data.",
        "Implement a linear kernel with sparse data so n can exceed 10^6.",
        "Report a learning curve against n to show where the margin stops helping.",
    ],
    code_checklist=[
        "Kernel is a swappable functional interface, not a boolean flag",
        "Scaling happens before the kernel, in the estimator",
        "Alpha bounds and the equality constraint are enforced on every update",
        "Training stops on KKT violation with a tolerance",
        "gamma and C are parameters with a sweep, not constants",
        "Support-vector fraction is logged every run",
    ],
    exercise_selfcheck=[
        "I can write the dual objective from memory",
        "I can explain why only alpha > 0 points matter",
        "My best gamma came from a validation surface",
        "I can state the memory ceiling in rows of data",
    ],
    exercises=[
        ("Hard-margin SVM by hand, then in code",
         "Solve the small case analytically and reproduce it with SMO.",
         ["Take 4 separable points; find the optimal w and b analytically.",
          "Compute the margin and identify the support vectors.",
          "Run your SMO and compare w, b and margin to the analytic answer.",
          "Assert agreement to 1e-3."],
         "Hand derivation plus a passing test that reproduces it in code."),
        ("Implement the kernel trick",
         "Add polynomial and RBF kernels and confirm they change the boundary.",
         ["Implement Kernels.linear, poly(r,d), rbf(gamma).",
          "Verify the PSD property numerically on a 5-point Gram matrix.",
          "Show RBF with a huge gamma fitting the training set exactly.",
          "Show that with a small gamma the boundary stays nearly linear."],
         "A Gram-matrix PSD check and two boundary comparisons."),
        ("Tune C and gamma properly",
         "Replace eyeballing with a validation surface.",
         ["Run a 5\u00d75 grid of (C, gamma) on 5-fold CV.",
          "Print the validation accuracy surface as text.",
          "Identify the plateau, not the single peak.",
          "Report held-out accuracy at the chosen point."],
         "A 5\u00d75 surface table, a chosen (C, gamma) and a one-paragraph justification."),
        ("Support-vector forensics",
         "Understand which rows the model actually uses.",
         ["Report the support-vector fraction for a grid of C.",
          "Plot support-vector fraction vs C.",
          "Inspect which training rows are support vectors and look for data smells.",
          "Remove them and refit; report the change."],
         "A fraction-vs-C curve and a short note on what the support vectors have in common."),
        ("Margin as a calibrated input",
         "Wrap the SVM in Platt scaling and measure the gain.",
         ["Collect margins and labels on a validation split.",
          "Fit a 1-D logistic regression on the margin.",
          "Compute ECE before and after.",
          "Sweep the decision threshold on the calibrated probability."],
         "Two reliability numbers and a threshold chosen on calibrated output."),
        ("Compare SVM against the rest of the track",
         "Benchmark the boundary shapes head to head.",
         ["Train logistic regression, a single tree, and an SVM on the same data.",
          "Report held-out accuracy for each.",
          "Plot the three boundaries on one ASCII grid.",
          "Explain which assumptions each model is making about the data."],
         "A comparison table plus an ASCII overlay of three boundaries."),
        ("Scalability cliff",
         "Find where the kernel matrix stops fitting.",
         ["Precompute the kernel matrix for n = 1k, 2k, 4k, 8k.",
          "Record heap usage and training time for each.",
          "Switch to a linear kernel above the cliff and compare accuracy.",
          "Write the rule you would put in a config."],
         "A memory/time table and a documented n threshold."),
        ("Ship a margin service",
         "Serve predictions with their margins and support-vector counts.",
         ["Serialise alphas, support vectors and the scaler stats.",
          "Serve POST /classify returning label, margin and s = #support vectors.",
          "Assert offline and served margins agree to 1e-9.",
          "Log gamma, C and the training date in the response."],
         "A running endpoint, a parity test and a sample response body."),
    ],
    quiz=[
        ("The SVM decision boundary depends only on...", ["All training points equally", "The support vectors", "The class priors", "The feature scaling"], 1, "w = \u03a3\u03b1\u1d62y\u1d62x\u1d62, and points with \u03b1\u1d62 = 0 contribute nothing."),
        ("Maximising the margin is equivalent to...", ["Minimising the number of misclassifications", "Minimising 0.5||w||\u00b2", "Maximising C", "Maximising the number of support vectors"], 1, "Margin width is 2/||w||, so a small ||w|| is a wide margin."),
        ("In the soft-margin formulation, C controls...", ["The kernel bandwidth", "The penalty on margin violations", "The class prior", "The feature dimension"], 1, "Larger C buys fewer violations at the cost of a narrower margin."),
        ("What is gamma in an RBF kernel?", ["The regularisation strength", "A length scale in the squared distance", "The class weight", "The convergence tolerance"], 1, "exp(\u2212\u03b3||x\u2212z||\u00b2) \u2014 large gamma means local influence only."),
        ("Why must features be standardised for RBF?", ["It improves accuracy", "Otherwise one feature's units dominate the distance", "It is required by the dual", "It reduces the number of features"], 1, "Squared distance mixes units unless they are comparable."),
        ("The kernel trick's benefit is...", ["Faster training", "Using a feature map without computing it", "Guaranteed better accuracy", "Removing the need for labels"], 1, "Only pairwise inner products are ever needed, so the map can be infinite-dimensional."),
        ("Which point is a support vector?", ["Any misclassified point", "Any point with \u03b1\u1d62 > 0", "Any point with the smallest norm", "The class centroid"], 1, "Positive dual coefficients define the boundary; the rest are irrelevant."),
        ("A very high support-vector fraction suggests...", ["A well-regularised model", "Memorisation and likely overfitting", "A large margin", "Perfect calibration"], 1, "When nearly every point is on the margin, the fit is following noise."),
        ("SVM decision values are...", ["Probabilities", "Signed margins needing calibration", "Class priors", "Distances in input space"], 1, "They are signed hyperplane values; Platt scaling is the standard wrapper."),
        ("The binding practical limit on kernel SVM size is...", ["Training time", "Memory for the O(n\u00b2) kernel matrix", "Feature count", "Class count"], 1, "8n\u00b2 bytes of doubles is what runs out first."),
        ("Complementary slackness implies that a point with 0 < \u03b1 < C is...", ["Inside the margin", "Exactly on the margin", "Correctly classified outside the margin", "Removed from the dataset"], 1, "Interior alphas must satisfy y\u1d62f(x\u1d62) = 1 exactly."),
        ("A polynomial kernel (x\u1d40z + r)^d corresponds to...", ["A linear model with d features", "A d-degree polynomial expansion", "An RBF approximation", "A random projection"], 1, "The expansion is exactly the monomials of degree up to d with binomial weights."),
        ("Why does SMO update two alphas at a time?", ["To parallelise", "Because the two-variable subproblem has a closed-form solution", "To reduce memory", "To enforce the sign of w"], 1, "With one variable the constraint couples it to all the others; with two it is quadratic."),
        ("Which is true of the hard-margin problem on separable data?", ["It has a unique solution with a unique margin", "It has no solution if points overlap", "C must be infinite", "The kernel must be linear"], 0, "Separability guarantees feasibility and convexity gives a unique optimum."),
        ("Choosing gamma by leaving it at its default is...", ["Always fine for small data", "Risky, because the default is arbitrary relative to your feature scale", "Optimal", "Equivalent to linear regression"], 1, "Set gamma from the feature variance or sweep it; the default knows nothing about your units."),
    ],
    vision=dict(
        future="The SVM survives as the conceptual bridge between convex optimisation, "
               "kernels and modern representation learning \u2014 its influence is in "
               "kernel methods, Gaussian processes and the intuition behind large-"
               "margin losses, not in new deployments of libsvm.",
        good=[
            "C and gamma come from a validation surface, with the plateau documented.",
            "Support-vector fraction is logged as a health signal.",
            "Scores are Platt-calibrated before any probability is published.",
            "The n at which we switch algorithms is written down in the model card.",
        ],
        ladder=[
            ("L1", "Fit a linear SVM", "Separate two classes, report the margin and support vectors."),
            ("L2", "Go non-linear", "Add the RBF kernel, tune gamma, understand the length scale."),
            ("L3", "Tune honestly", "Sweep C\u00d7gamma with CV, calibrate the margin, watch the support-vector fraction."),
            ("L4", "Know when to stop", "Recognise the scalability cliff and switch to a linear kernel or a tree ensemble."),
        ],
        behaviors="Prefer the linear kernel until you have evidence otherwise. "
                  "Scale before you fit. Treat the validation surface as a plateau, "
                  "not a peak.",
        anti=[
            "libsvm defaults shipped without ever looking at gamma.",
            "A margin quoted as a 0.87 'probability'.",
            "500k rows of kernel SVM because nobody checked the memory math.",
            "The best single point on a noisy grid chosen as 'the' hyperparameter.",
        ],
        trends=[
            "Kernel approximations and Nystr\u00f6m features extending SVMs to larger data.",
            "Large-margin losses inside neural objectives, where the SVM view informs design.",
            "Gaussian processes for calibrated uncertainty on small datasets, same kernel machinery.",
            "Differentiable SVM heads inside end-to-end and adversarial-robustness work.",
        ],
        d30="Implement linear and RBF kernels; verify a Gram matrix is positive semi-definite numerically.",
        d60="Implement SMO with KKT stopping and reproduce a hand-solved two-point case.",
        d90="Run a C\u00d7gamma sweep with cross-validation, Platt-calibrate the output, and document the memory cliff.",
        metrics=[
            "I can write the dual objective from memory.",
            "I can say what each alpha is doing without hesitating.",
            "My hyperparameters came from a surface I can show.",
            "I can state where this algorithm stops being practical and why.",
        ],
        closer="Understanding the margin is worth more than adding one more classifier to your toolkit.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Spam Classifier with a Defensible Margin",
        brief="Classify spam with an SVM, tune C and gamma from a validation "
              "surface, calibrate the margin, and explain the boundary.",
        timebox="3\u20134 hours",
        why="Spam is small enough for a kernel SVM and asymmetric enough that the "
            "threshold matters. It also forces the habit of tuning on a surface "
            "instead of a lucky point.",
        requirements=[
            "Load a labelled spam corpus (or synthesise one with class-conditional n-gram counts).",
            "Standardise features; log TF-IDF or binary counts and keep the vocabulary fixed.",
            "Train a linear SVM, then an RBF SVM; sweep C \u00d7 gamma over at least 25 combinations with 5-fold CV.",
            "Plot the validation surface and pick a point in the plateau, explaining why.",
            "Platt-calibrate the decision margin and report ECE before and after.",
            "Write a model card: expected precision at the chosen operating point, known spam classes it misses, and a retrain trigger.",
        ],
        steps=[
            ("1", "20m", "Build the feature matrix with a frozen vocabulary; assert no empty documents", "A reproducible matrix loader"),
            ("2", "20m", "Fit a linear SVM; report margin, support vectors and training error", "A baseline margin number"),
            ("3", "35m", "Run the 5\u00d75 C\u00d7gamma sweep with 5-fold CV", "A surface table, not a single number"),
            ("4", "20m", "Choose a plateau point and refit on all training data", "A documented hyperparameter choice"),
            ("5", "25m", "Platt calibration on a validation split; compute ECE before and after", "Two reliability numbers"),
            ("6", "20m", "Error analysis on 30 misclassified messages", "Three named failure patterns"),
            ("7", "20m", "Model card and a serialised artifact with the calibrator", "A reloadable model plus a readable card"),
        ],
        diagram="""messages --> Tokeniser --> vocabulary (frozen) --> TF-IDF matrix
                                                        |
                                              stratified 5-fold CV
                                                        |
                                    +-------------------+-------------------+
                                    |                                       |
                          linear SVM (baseline)                  C x gamma sweep (RBF)
                                    |                                       |
                                    +---------------+-----------------------+
                                                    |
                                        best plateau point (documented)
                                                    |
                                        refit on full training set
                                                    |
                                 Platt calibrator --> /classify (label + calibrated p)""",
        notes=[
            "Binary counts often beat TF-IDF for short text; try both and report the difference.",
            "A validation surface is a plateau; the peak is usually noise.",
            "Support-vector fraction above ~0.8 means the kernel is too wiggly for this data.",
            "Keep the vocabulary frozen in the artifact \u2014 a refitted vocabulary silently changes every score.",
        ],
        deliverables=[
            "One-command run producing the surface table and the metrics.",
            "ASCII validation surface with the chosen point marked.",
            "Calibration before/after with ECE.",
            "Model card, serialised model and calibrator.",
        ],
        grading=[
            ("Correctness", "30%", "Dual/margin implementation verified; CV protocol clean; vocabulary frozen"),
            ("Tuning", "25%", "Surface swept, plateau point chosen and justified"),
            ("Calibration", "20%", "Margins converted to probabilities with evidence of improvement"),
            ("Analysis", "15%", "Named failure patterns from real misclassifications"),
            ("Communication", "10%", "Model card states precision at the operating point"),
        ],
        stretch=[
            "Add a linear kernel with hashed features and push n past 100k.",
            "Compare against a bag-of-words logistic regression on cost, not just accuracy.",
            "Use the support vectors to build a nearest-neighbour explanation endpoint.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Inbound Email Threat Triage",
        scenario="An enterprise mail provider must decide, per message, whether to "
                 "deliver, quarantine or route to a security analyst. The scoring "
                 "budget is 12 ms per message, the analyst queue is fixed at 400 "
                 "per hour, and a false negative means a phishing click in a "
                 "customer's inbox.",
        scale=[
            ("Daily volume", "~40M inbound messages/day, peak 900 msg/s"),
            ("Positive rate", "0.4% malicious, rising during incident windows"),
            ("Analyst capacity", "400 messages/hour = 9,600/day"),
            ("Latency budget", "p99 < 12 ms, including envelope and body features"),
            ("Hard constraint", "quarantine decisions must be explainable to the customer on request"),
        ],
        diagram=""" MTA --> Header/URL/reputation features (cached, precomputed)
            |
      Streaming classifier (SVM or gradient-boosted alternative)
            |            \
            |             +--> shadow score (challenger) --> offline comparison
            |
   Policy engine (rules + threshold + customer overrides)
            |
   +--------+----------+-----------+
   |        |          |           |
 deliver  quarantine  analyst   customer
 (99%)    (0.35%)    queue      override
                                     |
                          appeal/explanation service <-- decision log

   Feedback: analyst verdicts (minutes) + user reports (hours) --> labels""",
        components=[
            ("Feature service",
             ["Envelope and authentication results (SPF/DKIM/DMARC) precomputed by the MTA",
              "Reputation lookups for sender IP, sending domain and URL host with local caching",
              "Attachment and link features computed in a streaming stage under 3 ms",
              "Feature contract versioned; a schema change triggers a shadow period before enforcement"]),
            ("Model tier",
             ["Linear SVM first: at 900 msg/s a kernel model is unnecessary and unprovable at scale",
              "RBF kernel retained only for the low-volume analyst-facing re-scoring path",
              "Model and calibrator loaded from the registry with hot reload and rollback",
              "Shadow challenger scores 100% of traffic and is compared weekly on matured labels"]),
            ("Policy engine",
             ["Threshold per customer tenant, with the highest-sensitivity tenants receiving the lowest threshold",
              "Overrides: allowlists, brand impersonation rules and known-safe senders",
              "Every decision writes score, threshold version, feature snapshot id and rule hits",
              "Fail-safe default: on model or feature outage, escalate to a stricter static rule set"]),
            ("Feedback and monitoring",
             ["Analyst verdicts arrive in minutes; user reports in hours \u2014 both become labels",
              "Daily precision/recall at the analyst cut, reported by tenant tier",
              "Drift on reputation features (a new sending domain can shift everything)",
              "Weekly red-team corpus scored as a fixed regression check before promotion"]),
        ],
        timeline=[
            ("Week 1", "Ship the static rule set with explanations and full decision logging"),
            ("Week 2", "Linear SVM in shadow; compare against rules for 7 days on live traffic"),
            ("Week 3", "Calibration and per-tenant thresholds; security review of false-negative paths"),
            ("Week 4", "Canary at 5% of traffic with a one-command revert; verify analyst queue depth"),
            ("Week 5", "Ramp to 50%, then 100% of scoring decisions; keep the rule set as the documented fallback"),
        ],
        runbook=[
            "# Which model and threshold are live?",
            "curl -s localhost:8080/admin/model | jq '{version,thresholdSet,ageHours}'",
            "",
            "# Quarantine rate vs the 7-day baseline",
            "curl -s 'localhost:8080/admin/rates?window=1h' | jq '{quarantine,baseline,delta}'",
            "",
            "# Force the stricter static rule set (safe mode)",
            "curl -XPOST localhost:8080/admin/mode -d '{\"mode\":\"RULES_SAFE\"}'",
            "",
            "# Roll back the model, keep the policy engine",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"threat-svm-2026-09-18\"}'",
            "",
            "# Explain one decision for a customer appeal",
            "curl -s 'localhost:8080/admin/explain?messageId=m-9931' | jq '.score,.rules,.features'",
        ],
        metrics=[
            "SLO: p99 scoring < 12 ms; availability 99.99% (a scoring outage quarantines or escalates, never silently delivers).",
            "Security: false-negative rate on the analyst-reviewed set; true-positive rate on the red-team corpus.",
            "Operations: analyst queue depth vs capacity, and median time-to-verdict.",
            "Customer: false-quarantine rate per 10k messages, and appeal overturn rate.",
            "Model: calibration by tenant tier; shadow challenger delta on matured labels.",
        ],
        failures=[
            ("Reputation cache misses flood the feature path", "cache eviction storm after a config change", "Serve the stale-but-bounded cache, degrade to authentication-only features, page on p99"),
            ("Quarantine rate doubles overnight", "a new sending domain is being scored as malicious", "Roll back the model, inspect the top changed features, keep the static rules"),
            ("Latency breaches the 12 ms budget", "synchronous DNS or reputation lookups on the hot path", "Enforce cached-only lookups with a hard timeout and fail closed to a neutral feature value"),
            ("Customer appeal cannot be answered", "decision log missing the feature snapshot id", "Every decision stores the snapshot id; without it the appeal stalls"),
            ("Analyst queue exceeds 400/hour", "threshold loosened by a config push", "Restore the last approved threshold set and page the security duty manager"),
        ],
        backlog=[
            "Red-team corpus as a scheduled regression job gating every promotion.",
            "Per-tenant threshold model with an approval workflow instead of direct config edits.",
            "Shadow-to-promotion automation with a two-week minimum shadow period.",
            "Explainability endpoint for appeals with a customer-readable reason list.",
            "Quarterly rollback drill measuring detection-to-mitigation time.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a 12 ms decision plus an explanation a customer "
               "can be shown, backed by a static fallback that keeps the system safe "
               "when the model is unavailable.",
    ),
))
