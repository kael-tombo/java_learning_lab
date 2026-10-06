# -*- coding: utf-8 -*-
"""Tailored specs for labs/ml/lab05 .. lab06."""

from ml_a import URLS_ML

SPECS = []

# ---------------------------------------------------------------- lab05
SPECS.append(dict(
    track="ml", lab="lab05", full_set=True, level="Intermediate",
    title="K-Nearest Neighbors", main_class="com.ml.lab05.Main",
    problem="You have no model to train and no distributional assumption you trust. "
            "All you can say is that similar things have similar outcomes.",
    why_now="KNN is the cheapest credible baseline and the clearest demonstration of "
             "the curse of dimensionality \u2014 it is the algorithm that makes scaling "
             "and feature selection non-optional.",
    objectives=[
        "Implement Euclidean, Manhattan and Minkowski distances and know when each is appropriate",
        "Find the k nearest neighbours with a sorted full scan and with a bounded max-heap",
        "Aggregate by majority vote and by distance weighting, and explain the difference",
        "Select k by cross-validation and explain the bias-variance direction of the trade-off",
        "Demonstrate the curse of dimensionality quantitatively",
        "Decide when KNN is inappropriate and say what to use instead",
    ],
    concepts=[
        ("Instance-based learning",
         "KNN keeps the whole training set and defers all work to prediction time. "
         "There is no training phase to speak of \u2014 only an indexing one. That is its "
         "attraction (trivial to get right, no assumptions) and its production cost "
         "(latency grows with n and with the query rate)."),
        ("Distance metrics",
         "Euclidean favours large single-axis differences; Manhattan accumulates small "
         "ones along many axes and suits sparse high-dimensional text. Minkowski "
         "interpolates via p: p=1 Manhattan, p=2 Euclidean, p\u2192\u221e Chebyshev. In high "
         "dimensions all distances concentrate \u2014 see below."),
        ("Choosing k and the bias-variance trade",
         "k = 1 gives a jagged, high-variance boundary that memorises noise; k = n "
         "gives a constant predictor. Cross-validation picks k, and the useful range "
         "is usually surprisingly narrow. With noisy labels, small k is actively "
         "harmful because a mislabelled neighbour votes."),
        ("Distance weighting",
         "Instead of counting votes, weight each by 1/d (or 1/d\u00b2). This makes the "
         "nearest neighbour dominant, effectively interpolating. It also makes "
         "predictions sensitive to a single outlier point, which is a real risk."),
        ("The curse of dimensionality",
         "In high dimensions the ratio max(d)/min(d) of distances concentrates near 1. "
         "For d = 100 uniformly random points, the 1st and 100th neighbour distances "
         "differ by only tens of percent \u2014 'nearest' stops being informative. "
         "Dimension reduction or feature selection is mandatory, not optional."),
        ("Scaling, missing values and duplicates",
         "KNN is a geometric method, so units are part of the model: a salary in cents "
         "outweighs every other feature. Missing values need an explicit imputation "
         "strategy *and* a distance that ignores the imputed dimension, or you are "
         "rewarding rows for being incomplete."),
    ],
    formulas=[
        ("d_p(x,z) = (\u03a3|x\u1d62 \u2212 z\u1d62|\u1d56)^(1/p)", "Minkowski distance", "p=1 Manhattan, p=2 Euclidean"),
        ("d(x,z) = \u221a\u03a3(x\u1d62\u2212z\u1d62)\u00b2", "Euclidean distance", "default; penalises large single-axis gaps"),
        ("w\u1d62 = 1/d(x\u1d62,x)", "Inverse-distance weight", "nearer neighbours dominate the vote"),
        ("\u0177(x) = argmax_c \u03a3_{i in kNN} w\u1d62 \u00b7 1[y\u1d62 = c]", "KNN prediction", "weighted class vote"),
        ("d_bias \u221d 1/k", "Bias decreases with k", "smoother boundary as k grows"),
        ("Var \u221d 1/k\u00b2 (naively)", "Variance decreases with k", "the opposite force, hence a U-shaped curve"),
    ],
    flow=[
        "Split, then scale using statistics from the training fold only.",
        "Choose a distance metric and justify it for the data's shape and sparsity.",
        "Reduce dimension or select features if p > ~20; record the decision.",
        "Sweep k and the weighting scheme on validation folds \u2014 plot the whole curve, not the argmax.",
        "At prediction time, find the k neighbours, vote, and return the winning class plus the vote fraction.",
        "Set a latency budget: if the query rate is high, add an index (KD-tree, ball tree) and measure the effect.",
    ],
    assumptions=[
        "Features are scaled and of comparable units, or the metric is dominated by one axis",
        "Locally constant density: nearby points share a label",
        "No informative signal was lost by removing features",
        "Independent, non-adversarial data \u2014 poison points can flip predictions",
        "The query rate allows O(n\u00b7d) search, or an index is in place",
        "Labels are locally consistent; otherwise small k amplifies label noise",
    ],
    pitfalls=[
        ("Accuracy craters when one feature changes units", "unscaled features dominate every distance", "standardise inside the estimator and test scaling invariance"),
        ("Predictions flip when a duplicate row is added", "1/d weighting with d = 0", "guard zero distance and define the tie rule explicitly"),
        ("k = 1 chosen because it validated best by 0.2%", "validation noise at a single fold", "use repeated CV and prefer the plateau, not the peak"),
        ("Performance collapses above p = 50", "curse of dimensionality, distances concentrate", "apply PCA or supervised feature selection first"),
        ("Prediction takes 400 ms", "full scan per query with no index", "cache, batch, or index with a KD-tree/ball tree and measure"),
        ("Bad predictions on rows with nulls", "imputed zeros make incomplete rows look similar", "impute with a real strategy and mask the dimension in the distance"),
    ],
    java=[
        ("PriorityQueue<Neighbour>", "a bounded max-heap keeps the k nearest in O(n log k) instead of sorting n"),
        ("Arrays.sort on primitive distances", "the simple reference path, useful as a correctness oracle"),
        ("IntStream / double[] for squared distance", "avoids allocation in the hot inner loop"),
        ("SplittableRandom", "reproducible bootstrap-style sampling for k-fold"),
        ("record Neighbour(int index, double distance)", "immutable pair that sorts and heapifies cleanly"),
    ],
    links=[
        "**Lab 08** (PCA) is the standard answer to the curse of dimensionality.",
        "**Lab 04** (SVM) shares the margin intuition but trains a parametric model instead of memorising.",
        "**Lab 10** supplies the cross-validation protocol you need to choose k honestly.",
        "**Lab 07** (K-Means) is the unsupervised relative: neighbours for labels, centroids for structure.",
    ],
    checklist=[
        "I can explain why scaling is not optional here",
        "I can show distance concentration numerically in high dimensions",
        "I choose k from a curve, not a single number",
        "I know when distance weighting helps and when it adds fragility",
        "I can state the prediction-time cost and how to reduce it",
        "I can name three cases where KNN is the wrong tool",
    ],
    cards=[
        ("Why does KNN require feature scaling?", "Distance is geometric: a feature in cents contributes a squared term orders of magnitude larger than one in dollars."),
        ("What does k control?", "Smoothness. Small k is jagged and high-variance; large k is smooth and high-bias. The validation curve is U-shaped."),
        ("What is the curse of dimensionality, concretely?", "As dimensions grow, all pairwise distances converge to similar values, so 'nearest' stops discriminating."),
        ("Euclidean or Manhattan for text?", "Usually Manhattan (p=1): it accumulates small per-token differences instead of squaring them into one large gap."),
        ("How does inverse-distance weighting change the result?", "The nearest neighbour dominates; predictions approach a local interpolation and become sensitive to outliers."),
        ("What is KNN's main production disadvantage?", "No training, all cost at prediction: latency grows linearly with n and the query rate."),
        ("Why is k = 1 risky with noisy labels?", "A single mislabelled neighbour becomes the entire prediction for that region."),
        ("Does KNN need a training phase?", "Only an indexing one. Everything expensive happens at query time."),
    ],
    extra_cards=[
        ("How do you pick k in practice?", "Repeated k-fold over a range, plot the mean curve, pick inside the plateau, and report the variance of that choice."),
        ("What is a KD-tree and when does it fail?", "A spatial index that prunes search; it degrades sharply once p exceeds about 10\u201320 dimensions."),
        ("How do you handle ties in a distance?", "Define it explicitly \u2014 nearest-first with a stable index tiebreak \u2014 otherwise results depend on array order."),
        ("Why does KNN not extrapolate?", "Predictions are votes or weighted averages of observed labels, so they stay inside the label set of nearby rows."),
    ],
    math_why="KNN is the lab where geometry becomes a complexity question. The same "
             "distance function that makes the method intuitive also creates the "
             "curse of dimensionality and the O(n) query cost \u2014 both are "
             "consequences of having no model at all.",
    math=[
        ("Distance metrics and their geometry",
         "L1: d1 = sum |xi - zi|\nL2: d2 = sqrt(sum (xi - zi)^2)\nLp: dp = (sum |xi - zi|^p)^(1/p)",
         "L2 squares before summing, so one large axis difference dominates. L1 sums "
         "before powering, so many small differences add up. That single choice "
         "decides whether high-dimensional sparse data looks close or far.",
         "x = (1, 0), z = (0, 10): d2 = sqrt(1+100) = 10.05 (one axis dominates); "
         "d1 = 1 + 10 = 11. For 20 features each differing by 1: d2 = sqrt(20) = 4.47, "
         "d1 = 20 (many small gaps accumulate)."),
        ("Weighted vote versus counting",
         "majority:  yhat = argmax_c #{i in kNN : yi = c}\nweighted: yhat = argmax_c sum_i (1/d_i) 1[yi = c]",
         "Counting treats a neighbour at d=1 the same as one at d=1000. Weighting "
         "restores locality, at the cost of one outlier dominating a region.",
         "k = 3: labels A(0.9), B(1.1), B(1.2). Majority gives B. Weighted gives "
         "A with 1.111 vs B's 0.909 + 0.833 = 1.742, so B still wins \u2014 but if A is "
         "at d = 0.1, A wins 10 to 1.74."),
        ("Distance concentration",
         "for uniform points in [0,1]^d: E[d] ~ d/2, Var[d] ~ (1/12) d(d+2)\nrelative std dev ~ sqrt(12/(d+2)) / sqrt(d)\nc1 = (dmax - dmin)/dmean -> 1 as d grows",
         "Absolute distances grow with d while their spread shrinks proportionally. "
         "The ratio between the nearest and farthest neighbour stops depending on the "
         "point, which is exactly what kills k-NN in high dimensions.",
         "d = 10: relative spread ~ 30%; d = 100: ~9%; d = 1000: ~3%. Neighbour "
         "ratios move from meaningful to indistinguishable as dimension climbs."),
        ("Cost of the search",
         "brute force: O(n d) per query, O(n d) to sort, or O(n log k) with a heap\nprecompute distance matrix: O(n^2 d) once, O(n) per query\nKD-tree: ~O(log n) average, degrades to O(n) as d grows",
         "The full-scan cost is per query, so total cost is O(q n d) for q queries. "
         "Precomputing the matrix moves work to a one-off O(n\u00b2d) and is only worth "
         "it for small n with many repeated queries.",
         "n = 10,000, d = 20, q = 1,000: brute force = 200M operations per query "
         "batch. With a precomputed matrix, each query is a 10,000-element partial "
         "sort \u2014 three orders of magnitude cheaper."),
        ("Bias-variance in k",
         "prediction variance ~ roughly 1/k near the neighbourhood\nbias ~ grows like the local curvature, roughly as k grows\ntotal loss = bias + variance has a U-shape in k",
         "Neither extreme is right: k = 1 memorises, k = n predicts the majority "
         "class. The optimum is where the two curves cross, which is why sweeping k "
         "is mandatory rather than optional.",
         "On 2D Gaussian blobs with 5% label noise: k = 1 gives 88% (high variance), "
         "k = 15 gives 93%, k = 200 gives 82% (swamped). The plateau is broad: k from "
         "10 to 30 all score 93%."),
        ("Scaling and the effective condition number",
         "after scaling each feature to unit variance, the average squared distance\nE||x-z||^2 = sum_j Var_j (unscaled) vs 2p (scaled)\nratio unscaled/scaled = (sum_j Var_j) / (2p)",
         "If one feature has variance 100\u00d7 the rest, it contributes 100\u00d7 more to "
         "every distance, so neighbour selection is effectively decided by that "
         "feature alone.",
         "p = 5, one feature with variance 100 and four with variance 1: the "
         "dominant feature is 100/104 = 96% of the squared distance. Neighbours are "
         "chosen almost entirely by it."),
    ],
    math_traps=[
        "Comparing distances without checking for zero (duplicate rows) before taking 1/d.",
        "Using squared distance with distance weighting \u2014 consistent, but note that k(x) is then weighted by 1/d\u00b2, not 1/d.",
        "Interpreting a k-fold argmax of one decimal place of accuracy as a real difference.",
        "Assuming a KD-tree keeps its logarithmic behaviour in 30 dimensions \u2014 it does not.",
        "Reporting accuracy for a nearest-neighbour method that has no generalisation story without a held-out set.",
    ],
    math_problems=[
        "Compute d1, d2 and d\u221e for the pairs (1,0)/(0,10) and (1,1,1)/(2,2,2).",
        "For neighbours at distances 0.5, 1, 2 and 4, compare majority vote and 1/d weighting.",
        "Generate uniform random points and measure the nearest-to-farthest distance ratio for d = 2, 10, 100, 1000.",
        "Show that with p features of unit variance, E||x-z||\u00b2 = 2p; derive it from the variance sum.",
        "Time brute-force KNN for n = 10\u2074 and n = 10\u2075 and explain what changes when you add an index.",
    ],
    tree="""src/com/ml/lab05/
  Main.java             driver: synthetic 2D blobs, k sweep, boundary plot
  KnnClassifier.java    fit (store + scale), predict via heap, k and weighting config
  Distance.java         @FunctionalInterface + euclidean/manhattan/minkowski
  NeighbourIndex.java   bounded PriorityQueue keep-k helper
  KSweep.java           cross-validated k curve and weighting comparison""",
    tree_note="The bounded heap is the only interesting code. Everything else is "
              "bookkeeping, and getting the heap wrong silently returns the k "
              "farthest points \u2014 so KSweep cross-checks it against a full sort.",
    types=[
        ("KnnClassifier", "stores the scaled training matrix plus labels; predict() does the work"),
        ("Distance", "a functional interface so metrics are swappable and testable"),
        ("NeighbourIndex", "bounded max-heap keeping the k smallest distances seen"),
        ("KSweep", "cross-validated accuracy curve over k and weighting scheme"),
    ],
    patterns=[
        ("Keeping the k nearest with a bounded max-heap",
         "A max-heap of size k lets you discard anything worse than the current "
         "worst kept neighbour in O(1). Heapify once at the end to order them.",
         """static int[] kNearest(double[] q, double[][] xs, int k, Distance d) {
    // max-heap keyed on distance: the root is the *worst* kept neighbour
    PriorityQueue<Neighbour> heap =
        new PriorityQueue<>(k, Comparator.comparingDouble(Neighbour::distance));
    for (int i = 0; i < xs.length; i++) {
        double dist = d.of(q, xs[i]);
        if (heap.size() < k) {
            heap.add(new Neighbour(i, dist));
        } else if (dist < heap.peek().distance()) {
            heap.poll();                       // evict the farthest kept
            heap.add(new Neighbour(i, dist));
        }
    }
    Neighbour[] kept = heap.toArray(new Neighbour[0]);
    Arrays.sort(kept, Comparator.comparingDouble(Neighbour::distance));
    int[] out = new int[kept.length];          // nearest first
    for (int i = 0; i < kept.length; i++) out[i] = kept[i].index();
    return out;
}"""),
        ("Prediction with voting, weights and a zero-distance guard",
         "Both aggregation modes live here. The zero-distance case is handled first "
         "and explicitly, because it is the one that produces NaN in the weighted "
         "path.",
         """public int predict(double[] raw, int k, boolean weighted) {
    double[] q = scaler.transform(raw);           // scaling lives in the estimator
    int[] idx = NeighbourIndex.kNearest(q, xs, k, distance);
    Map<Integer, Double> votes = new HashMap<>();
    for (int i : idx) {
        double d = distance.of(q, xs[i]);
        if (d < 1e-12) return labels[i];          // exact duplicate: no vote needed
        double w = weighted ? 1.0 / d : 1.0;
        votes.merge(labels[i], w, Double::sum);
    }
    return votes.entrySet().stream()
        .max(Map.Entry.comparingByValue())
        .orElseThrow()
        .getKey();
}"""),
    ],
    costs=[
        ("Brute-force neighbour search per query", "O(n d)", "the dominant per-request cost"),
        ("Keeping the k nearest with a heap", "O(n log k)", "beats sorting when k << n"),
        ("Sorting the training set once by each dimension", "O(n log n \u00b7 d)", "enables partial-sort tricks and grid indexes"),
        ("Prediction memory", "O(k)", "only neighbours are retained; the model is the dataset"),
    ],
    numerics=[
        "Standardise inside the estimator; add a test that asserts identical predictions after rescaling.",
        "Guard d = 0 before taking 1/d, and define the duplicate rule explicitly.",
        "Tie-break by index so identical distances give deterministic predictions.",
        "Use squared distance consistently for ranking and 1/d for weighting only if you have thought it through.",
        "Report k, the metric and the weighting scheme next to every accuracy number.",
    ],
    tests=[
        "A hand-computed 4-point dataset returns the expected neighbour indices for k = 2.",
        "The heap implementation agrees with a full sort on 1,000 random points.",
        "Scaling a feature by 1000 leaves predictions unchanged.",
        "Adding a duplicate of a training row does not change the prediction or produce NaN.",
        "k = n predicts the majority class exactly.",
        "Prediction is deterministic across runs and across JVM invocations.",
    ],
    extensions=[
        "Implement a KD-tree index and measure where it stops beating brute force in p.",
        "Add a local outlier factor pre-filter and report the latency/metric trade.",
        "Use PCA to k dimensions and show the accuracy recovered on a high-p dataset.",
    ],
    code_checklist=[
        "Scaling, metric, k and weighting are all estimator state, not caller choices",
        "Zero distance handled before any division",
        "Tie-breaking is deterministic",
        "k chosen from a plotted curve and recorded",
        "A test cross-checks the heap against a reference sort",
        "Prediction latency measured and reported with the accuracy",
    ],
    exercise_selfcheck=[
        "I can state why scaling is required, with a failing test that proves it",
        "I picked k from a curve rather than an argmax",
        "I measured the curse of dimensionality on my own data",
        "I know my prediction latency budget and how I would enforce it",
    ],
    exercises=[
        ("Implement the three distance metrics",
         "Get the geometry right, including the p parameterisation.",
         ["Implement euclidean, manhattan and minkowski(p).",
          "Verify triangle inequality numerically on random points.",
          "Show minkowski(p=1) equals manhattan and p=2 equals euclidean.",
          "Plot the difference on a 2D grid of pairs."],
         "A metrics class plus a numerical identity test."),
        ("Full scan and heap must agree",
         "Two implementations, one answer.",
         ["Implement a full-sort neighbour finder.",
          "Implement the bounded heap version.",
          "Assert index equality on 1,000 random queries.",
          "Benchmark both."],
         "A passing equivalence test and a benchmark table."),
        ("Majority versus weighted voting",
         "See exactly what weighting changes.",
         ["Implement both aggregations.",
          "Test on hand-built 3-neighbour cases.",
          "Measure the effect on a noisy synthetic dataset.",
          "Plot accuracy vs k for both."],
         "Two curves and a written rule for when weighting helps."),
        ("The k sweep, done honestly",
         "Repeated cross-validation, not one split.",
         ["Run 5-fold CV for k in {1,3,5,7,9,15,21,31,51}.",
          "Repeat 5 times with different seeds.",
          "Plot mean \u00b1 std accuracy versus log k.",
          "Pick k inside the plateau and report the uncertainty."],
         "A plateau plot with error bars and a justified k."),
        ("Demonstrate the curse of dimensionality",
         "Make the problem visible with your own numbers.",
         ["Generate isotropic Gaussian blobs at p = 2, 5, 10, 20, 50, 100.",
          "Hold n fixed; measure 1-NN accuracy at each p.",
          "Measure the nearest-to-farthest distance ratio.",
          "Add PCA to 2 dimensions and re-measure."],
         "A table of accuracy versus p, with and without PCA."),
        ("Scaling invariance test",
         "Prove the estimator handles units.",
         ["Fit on standardised features.",
          "Predict on raw features.",
          "Assert predictions agree to 1e-9.",
          "Show what happens when you fit on raw features (the failure case)."],
         "A test that fails on the raw-fit version and passes on the correct one."),
        ("Missing values and duplicates",
         "Handle the messy cases explicitly.",
         ["Introduce 10% missing values with an imputer and a distance mask.",
          "Add duplicate rows and assert deterministic predictions.",
          "Compare accuracy with and without the mask.",
          "Document the tie rule."],
         "A decision table of the four cases and their outcomes."),
        ("Latency budget for a lookup service",
         "Make prediction fast enough to serve.",
         ["Batch 1,000 queries and time brute force.",
          "Implement a simple grid index and re-time.",
          "Report accuracy lost by the index.",
          "Set an explicit latency SLO and a fallback."],
         "A latency/accuracy table and a stated SLO."),
    ],
    quiz=[
        ("Why does KNN require feature scaling?", ["It is faster with scaled data", "Distances are dominated by features with large units", "Scaling improves AUC", "It is only needed for Manhattan"], 1, "Squared distance weights each feature by its variance, so unscaled units decide the neighbourhood."),
        ("Increasing k does what?", ["Increases variance, decreases bias", "Decreases variance, increases bias", "Increases both", "Changes nothing"], 1, "Averaging over more neighbours smooths the boundary: less variance, more bias."),
        ("The 1/d weighting mainly...", ["Reduces memory use", "Lets the nearest neighbour dominate", "Guarantees accuracy", "Removes the need for scaling"], 1, "Weighting restores locality, approaching a local interpolation."),
        ("Curse of dimensionality means...", ["KNN is slower in high dimensions", "All distances become similar, so 'nearest' loses meaning", "KNN needs more data", "Scaling stops working"], 1, "Distance concentration makes neighbour selection uninformative as d grows."),
        ("A KD-tree's advantage disappears when...", ["k is large", "Dimension exceeds roughly 10\u201320", "Data is sparse", "Labels are noisy"], 1, "Axis-aligned pruning relies on distances being spread out, which concentration destroys."),
        ("With k = 1, prediction latency is...", ["Independent of n", "O(n \u00b7 d)", "O(log n)", "O(1)"], 1, "Every query scans or indexes the whole training set; there is no trained model to amortise."),
        ("Which metric suits sparse text features?", ["Euclidean", "Manhattan (p = 1)", "Cosine similarity", "Chebyshev"], 1, "Manhattan accumulates small per-feature gaps instead of squaring them, which suits sparse vectors."),
        ("Ties in distance should be resolved by...", ["Random choice", "A deterministic rule such as nearest index", "Ignoring them", "Returning the majority class"], 1, "Without a rule, predictions depend on array order and become irreproducible."),
        ("Distance weighting increases sensitivity to...", ["Training set size", "Outlier points near the query", "Feature count", "The learning rate"], 1, "One very close neighbour can dominate the weighted vote."),
        ("Why is a local imputation strategy needed?", ["To reduce file size", "Global means make incomplete rows look artificially similar", "To speed up search", "It is optional"], 1, "Imputed global values create false similarity between rows that share the same missing pattern."),
        ("KNN's 'training' time is essentially...", ["Zero, all work at query time", "The same as a neural net", "Dominant", "Half the query time"], 0, "Only indexing happens up front; the expensive part is prediction."),
        ("The best k is usually found by...", ["Taking the largest k that still fits in memory", "Cross-validating and choosing inside the plateau", "Defaulting to 5", "Using the training accuracy"], 1, "Validation curves are U-shaped and noisy; the plateau is the answer, not the peak."),
        ("Compared to logistic regression, KNN...", ["Is parametric and fast", "Is non-parametric and slower at prediction", "Requires labels for training", "Cannot handle categorical features"], 1, "KNN stores the data and predicts by lookup."),
        ("A duplicate row at distance 0 causes problems with...", ["Euclidean only", "Inverse-distance weighting (1/0)", "Manhattan only", "Neither"], 1, "1/0 is infinite; the fix is an explicit duplicate rule, not a numeric epsilon hack."),
        ("Where does KNN fit in a production stack?", ["As the final model for most tabular problems", "As a strong baseline and for small, low-dimensional, latency-tolerant lookups", "Never, it is obsolete", "Only for images"], 1, "It is a valuable baseline and a sanity check that a harder model actually beats memorisation."),
    ],
    vision=dict(
        future="KNN survives as the baseline that exposes whether a fancy model is "
               "actually learning. Approximate nearest-neighbour indexes (HNSW, IVF) "
               "and learned metric learning extend it to embeddings and retrieval, "
               "which is where most production KNN now lives.",
        good=[
            "Every KNN score is reported with k, the metric, the weighting and the scaling in the same table.",
            "Distance concentration is measured, not assumed, when p is large.",
            "Prediction latency has a budget and an index behind it.",
            "A parametric baseline sits next to it so 'KNN won' means something.",
        ],
        ladder=[
            ("L1", "Classify", "Implement euclidean KNN, pick k = 5, report accuracy."),
            ("L2", "Tune honestly", "Cross-validate k and the metric, plot the curve, defend the choice."),
            ("L3", "Make it fast", "Add a bounded heap and an index; measure latency versus accuracy."),
            ("L4", "Know when to stop", "Measure distance concentration and switch to a parametric or embedding-based method."),
        ],
        behaviors="Baseline first, complexity second. Measure the query cost as "
                  "carefully as the metric. When the neighbourhood stops meaning "
                  "anything, say so with numbers.",
        anti=[
            "Reporting KNN accuracy without the k or the metric it used.",
            "Leaving unscaled features in a distance-based model.",
            "Assuming a KD-tree is fast regardless of dimension.",
            "Choosing k from a single train/validation split.",
        ],
        trends=[
            "Approximate nearest-neighbour indexes (HNSW, IVF-PQ) enabling vector search at billions of scale.",
            "Learned metric and embedding spaces making distance meaningful where raw features are not.",
            "Graph-based ANN systems powering retrieval-augmented generation.",
            "Hybrid sparse-dense retrieval that blends lexical and vector scores.",
        ],
        d30="Implement the three metrics and a full-sort neighbour finder, verified against hand calculations.",
        d60="Add the bounded heap and prove it matches the sort; benchmark both.",
        d90="Run a repeated k sweep, measure distance concentration on a high-p dataset, and publish the trade-off table.",
        metrics=[
            "I can state k, metric, weighting and scaling in one sentence for any KNN number I quote.",
            "I can measure rather than guess the dimensionality cliff for a dataset.",
            "I can put a latency number next to an accuracy number.",
            "I know when not to use KNN and can name the replacement.",
        ],
        closer="KNN is the model that teaches you what the other models are buying: "
               "assumptions in exchange for speed and structure.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Movie Recommendation by Nearest Neighbours",
        brief="Recommend films from user ratings with KNN over users and over items, "
              "and report precision@k with a latency budget.",
        timebox="3\u20134 hours",
        why="Recommenders expose every KNN failure mode at once: sparsity, scaling, "
            "k choice, cold start, and query cost.",
        requirements=[
            "Load MovieLens-style ratings (ratings.csv + movies.csv) or synthesise a sparse rating matrix.",
            "Implement item-based KNN: find similar films by co-rating similarity, then score unseen films for a user.",
            "Standardise (or mean-centre per user, which handles rating-scale bias better).",
            "Sweep k and measure precision@10 and recall@10 with a leave-one-out evaluation.",
            "Report a latency benchmark for 1,000 recommendations and state a per-request budget.",
            "Write a model card covering cold start, popularity bias and what the similarity metric misses.",
        ],
        steps=[
            ("1", "25m", "Load data; assert sparsity level and build the item-user matrix", "A documented sparsity number"),
            ("2", "30m", "Implement item-item similarity (cosine and adjusted cosine) with a min-support filter", "Similarities for 100 items, reproducible"),
            ("3", "25m", "Implement neighbour-based scoring for a user; exclude already-seen items", "A ranked list per user"),
            ("4", "30m", "Leave-one-out evaluation; sweep k and the similarity metric", "Precision@10 and recall@10 curves"),
            ("5", "20m", "Benchmark 1,000 recommendations and record p50/p95 latency", "A latency table with a stated budget"),
            ("6", "20m", "Analyse cold start and popularity bias; compare against a popularity baseline", "A named failure mode with numbers"),
            ("7", "20m", "Model card plus a serving endpoint for /recommend?user=", "A readable card and a working endpoint"),
        ],
        diagram="""ratings.csv --> item-user matrix (sparse)
                        |
        +---------------+----------------+
        |                                |
  item-item similarity            popularity baseline
  (cosine / adj-cosine)                  |
        |                                |
   top-k neighbours per item             |
        |                                |
  score = weighted mean of user's ratings |
        |                                |
   exclude seen, rank top-10  ---------->+
                        |
      leave-one-out precision@10 / recall@10""",
        notes=[
            "Mean-centring per user removes individual rating harshness; it usually beats raw cosine.",
            "A min-support threshold stops one co-rater from defining a film's similarity.",
            "Report recall@10 and NDCG too; precision@10 alone flatters popular catalogues.",
            "The popularity baseline is the number that makes your recommender look good or bad.",
        ],
        deliverables=[
            "One-command run producing the k sweep and metric table.",
            "Latency benchmark with a stated per-request budget.",
            "Cold-start and popularity-bias analysis with numbers.",
            "Model card plus a /recommend endpoint.",
        ],
        grading=[
            ("Correctness", "30%", "Similarity and scoring verified on a hand-worked example; seen items excluded"),
            ("Evaluation", "25%", "Leave-one-out protocol, k sweep, baseline reported"),
            ("Performance", "20%", "Latency measured against a stated budget"),
            ("Analysis", "15%", "Cold start and popularity bias quantified"),
            ("Communication", "10%", "Model card names what the metric misses"),
        ],
        stretch=[
            "Add user-based KNN and compare: which wins, and on what kind of user?",
            "Blend with the popularity baseline and show the gain at the head of the list.",
            "Index the similarity search with an approximate NN structure and measure the accuracy cost.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Similar-Item Recommendations for a Retail Catalogue",
        scenario="A grocery retailer with 400k SKUs needs 'customers who bought this "
                 "also bought' inside 120 ms for a page render, for 12M sessions a "
                 "day. The catalogue changes hourly and cold items have no history.",
        scale=[
            ("Catalogue", "~400k active SKUs, ~1.8M orders/day, ~55M order lines/day"),
            ("Traffic", "12M sessions/day, peak 4,500 rec slots/s across all placements"),
            ("Latency budget", "p99 < 120 ms per slot, including retrieval and ranking"),
            ("Freshness", "similarity lists refreshed hourly; new SKUs served within 1 hour"),
            ("Business metric", "incremental units per session, measured by a holdout"),
        ],
        diagram=""" order stream --> line-item store (Kafka) --> hourly similarity job
                                                        |
                                          item-item ANN index (in-memory + warm cache)
                                                        |
  page render --> rec service --> slot budget / dedupe / exclusion lists --> page
        |                                                     |
        |                                            impression + order events
        |                                                     |
        +------------------> holdout measurement <-----------+
                                    |
                          hourly index rebuild + drift checks""",
        components=[
            ("Similarity computation",
             ["Co-purchase counts in fixed time windows with a decay factor",
              "Normalised item-item similarity (cosine-style) with a minimum-support filter",
              "Top-N neighbours stored per item; the full matrix is never materialised",
              "Warm-start from the previous index so partial rebuilds stay available"]),
            ("Index and serving",
             ["In-memory ANN index over item embeddings plus an exact-lookup fallback for hot items",
              "L1 cache of the top 10k most-requested items' neighbour lists",
              "Slot budgets, seen-item exclusion and category diversity applied per placement",
              "p99 under 120 ms enforced by a timeout with a popularity fallback"]),
            ("Freshness and cold start",
             ["Incremental hourly updates rather than full nightly rebuilds",
              "Brand-new SKUs served from attribute-only similarity until co-purchase data accrues",
              "Zero-result detection routed to category popularity, logged as a quality signal",
              "Index version pinned in every response so a stale slot is identifiable"]),
        ],
        timeline=[
            ("Week 1", "Ship a co-purchase baseline with popularity fallback and full impression logging"),
            ("Week 2", "Hourly similarity job with warm start; verify a rebuild never serves an empty index"),
            ("Week 3", "ANN index plus cache; measure p99 and the accuracy/cost trade-off"),
            ("Week 4", "Cold-start path for new SKUs; holdout measurement framework running"),
            ("Week 5", "Diversity and slot-budget rules tuned against the holdout; runbook published"),
        ],
        runbook=[
            "# Index health and freshness",
            "curl -s localhost:8080/admin/index | jq '{version,builtAt,items,zeroResultRate}'",
            "",
            "# Latency by placement",
            "curl -s 'localhost:8080/admin/latency?window=15m' | jq '.p50,.p95,.p99'",
            "",
            "# Fall back to category popularity for every slot",
            "curl -XPOST localhost:8080/admin/mode -d '{\"mode\":\"POPULARITY_ONLY\"}'",
            "",
            "# Force a partial index rebuild (top 10k hot items only)",
            "curl -XPOST localhost:8080/admin/rebuild -d '{\"scope\":\"hot\"}'",
            "",
            "# Verify a known SKU returns neighbours (regression check)",
            "curl -s 'localhost:8080/similar?sku=SKU-0048212' | jq '.neighbours|length'",
        ],
        metrics=[
            "SLO: p99 slot latency < 120 ms; index freshness < 70 min; availability 99.95%.",
            "Business: incremental units per session against a 5% holdout, reported with confidence intervals.",
            "Quality: click-through on recommendations, and zero-result rate by category.",
            "Freshness: share of SKUs served from cold-start similarity, and its CTR delta.",
            "Cost: memory per index version and rebuild duration, tracked against the hourly budget.",
        ],
        failures=[
            ("Index rebuild fails and the hot set goes stale", "OOM during the full similarity job", "Keep the previous version live, rebuild the hot subset, page; never delete the last good index"),
            ("p99 slot latency breaches 120 ms", "cache miss storm after a catalogue drop", "Serve popularity fallback for overflow slots and log the substitution"),
            ("Zero-result rate spikes on new categories", "attribute-only similarity is too coarse", "Route to category popularity, alert the merchandising owner"),
            ("Recommendation CTR drops 20%", "seasonal demand shift not in the index", "Trigger an out-of-band rebuild, verify the holdout before concluding the model failed"),
            ("Two slots on a page return the same SKU", "dedupe logic lost in a config change", "Slot-level dedupe is enforced in code and covered by a test, not configuration"),
        ],
        backlog=[
            "Incremental similarity updates per partition instead of full hourly rebuilds.",
            "Embedding-based co-visitation so long-tail items get neighbours before co-purchase data exists.",
            "Holdout-based incremental evaluation wired into the rebuild job's exit criteria.",
            "Documented index rollback to the previous version, timed drill each quarter.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a 120 ms slot with a fallback, a versioned index "
               "and a holdout measurement \u2014 a recommender nobody can hold to a "
               "number is just a random assortment.",
    ),
))

# ---------------------------------------------------------------- lab06
SPECS.append(dict(
    track="ml", lab="lab06", full_set=True, level="Intermediate",
    title="Naive Bayes Classifier", main_class="com.ml.lab06.Main",
    problem="You have few labelled examples, many features, and you suspect the "
            "features are roughly independent given the class.",
    why_now="Naive Bayes is the text-classification workhorse it has always been, "
             "and the cleanest place to see what conditional independence buys and "
             "what it costs.",
    objectives=[
        "State the three Naive Bayes variants and what each assumes about feature type",
        "Derive Gaussian, multinomial and Bernoulli likelihoods",
        "Explain why the naive step is a modelling choice, not an implementation shortcut",
        "Implement Laplace (add-\u03b1) smoothing and see why unsmoothed estimates break",
        "Use log-space arithmetic so products of small probabilities do not underflow",
        "Know where NB beats logistic regression (small data, text) and where it loses",
    ],
    concepts=[
        ("The generative shortcut",
         "Bayes' theorem flips the problem: instead of modelling P(y|x) directly, "
         "model the class-conditional densities P(x|y) and the prior P(y). With a "
         "naive assumption over features, each density factorises, and classification "
         "becomes counting."),
        ("Three variants, three data types",
         "Gaussian NB assumes each feature is normal within a class (continuous data). "
         "Multinomial NB models feature *counts* (bag-of-words). Bernoulli NB models "
         "presence/absence (a document is a set of indicators). Using multinomial NB "
         "on binary flags, or Bernoulli on raw counts, quietly changes the model."),
        ("What 'naive' actually assumes",
         "Conditional independence: P(x\u1d62 | y) = \u220f\u1d62 P(x\u1d62 | y). This is almost never "
         "true \u2014 'bank' and 'loan' co-occur. It still works because the discriminative "
         "ranking survives small errors in the likelihood. Treat it as a bias that "
         "costs calibration and some accuracy, not as a fatal flaw."),
        ("Laplace smoothing",
         "P(x\u1d62 = v | y = c) = (count(c,v) + \u03b1) / (N_c + \u03b1|V|) with \u03b1 = 1. Without it, an unseen "
         "value in a class gives probability 0 and that class is excluded forever. "
         "Smoothing is what makes the classifier handle new vocabulary at all."),
        ("Log-space arithmetic",
         "Multiplying 5,000 probabilities of 0.01 underflows a double long before you "
         "reach the last row. Summing log probabilities is exactly equivalent and "
         "never overflows. If you see p = 0.0 or NaN, this is why."),
        ("NB gives a posterior, but a poorly calibrated one",
         "The posterior is nominal, so users expect it to be a probability. It is not: "
         "NB posteriors are famously overconfident, especially with correlated "
         "features and small training sets. Platt scaling on the NB log-odds fixes "
         "most of it for a few lines."),
    ],
    formulas=[
        ("P(y=c | x) \u221d P(y=c) \u00b7 P(x | y=c)", "Bayes' rule (proportional)", "drop the evidence constant for argmax"),
        ("P(x | y=c) = \u220f P(x\u1d62 | y=c)", "Naive independence", "the assumption that costs accuracy"),
        ("P(x\u1d62 | y=c) = exp(\u2212(x\u1d62\u2212\u03bc_c\u1d62)\u00b2/2\u03c3_c\u1d62\u00b2)/(\u03c3\u1d62c\u221a2\u03c0)", "Gaussian likelihood", "continuous features"),
        ("P(x | y=c) \u221d \u220f\u1d62 count(c, x\u1d62)", "Multinomial likelihood", "term counts per class"),
        ("P(x\u1d62 | y=c) = (count + \u03b1)/(N_c + \u03b1|V|)", "Laplace smoothing", "keeps unseen values possible"),
        ("log P(c) + \u03a3\u1d62 log P(x\u1d62 | c)", "Log-posterior score", "argmax is identical, numerically safe"),
        ("confusion matrix metrics", "precision / recall / F1", "text classification is imbalanced in practice"),
    ],
    flow=[
        "Vectorise the input to counts (multinomial) or indicators (Bernoulli); the choice is the model.",
        "Split stratified; keep the vocabulary fitted on the training fold only.",
        "Compute per-class priors and feature likelihoods with smoothing.",
        "Score in log space: log prior + \u03a3 log P(feature | class), pick the argmax.",
        "Evaluate with precision/recall/F1 and a PR curve; report per class, not just accuracy.",
        "If probabilities matter, Platt-calibrate the log-odds score on a validation split.",
    ],
    assumptions=[
        "Features are conditionally independent given the class",
        "The chosen variant matches the feature type (counts vs indicators vs continuous)",
        "The training set is representative of the deployment distribution",
        "Class priors in training reflect deployment; re-estimate them if they drift",
        "Enough examples per class for the likelihood estimates to be stable",
        "Smoothing is applied \u2014 unsmoothed NB is undefined on unseen values",
    ],
    pitfalls=[
        ("All posteriors print as 1.0 or 0.0", "multiplying many probabilities underflows a double", "compute in log space from the start"),
        ("The class with an unseen word is never predicted", "unsmoothed zero likelihood", "apply Laplace smoothing with \u03b1 = 1"),
        ("Accuracy collapses after preprocessing", "scaler or TF-IDF refit on the full dataset", "fit the vectoriser inside the training fold"),
        ("NB underperforms badly on small numeric data", "correlated continuous features break the independence assumption", "use logistic regression or a tree ensemble instead"),
        ("Probabilities are wildly overconfident", "NB posteriors are not calibrated", "Platt-scale the log-odds; or only use the argmax"),
        ("Multiclass numbers look implausible", "using multinomial NB on binary indicators", "use Bernoulli for presence/absence features"),
    ],
    java=[
        ("HashMap<Integer, Double>", "per-class token log-probability maps in sparse form"),
        ("Math.log / Math.log1p", "log-space likelihood accumulation"),
        ("double[] classPriors", "the log-prior vector, one entry per class"),
        ("record Example(double[] numeric, int[] tokens, int label)", "carries all three feature views so variants stay comparable"),
        ("PriorityQueue for top-k terms", "explain a document by its highest-weight tokens"),
    ],
    links=[
        "**Lab 02** is the discriminative counterpart \u2014 compare them on the same small dataset.",
        "**Lab 09** applies the same log-odds idea with a much stronger learner underneath.",
        "**Lab 04** replaces the generative model with a margin, buying accuracy at the cost of data efficiency.",
        "**Lab 10** gives the F1 and PR-curve protocol that text classification actually needs.",
    ],
    checklist=[
        "I can state which independence assumption each variant makes",
        "I never compute a posterior in probability space",
        "I always smooth, and can explain what \u03b1 does",
        "I choose multinomial vs Bernoulli from the feature representation",
        "I know NB posteriors are uncalibrated",
        "I report per-class F1, not just accuracy",
    ],
    cards=[
        ("Why is it called naive?", "It assumes features are conditionally independent given the class, which is almost never true but is a useful bias."),
        ("Which NB variant fits TF counts?", "Multinomial NB, which models the counts of terms per class."),
        ("Which variant fits document presence/absence?", "Bernoulli NB, which models each term as an indicator and also uses document length."),
        ("Why compute in log space?", "Multiplying thousands of small probabilities underflows to zero; summing logs is mathematically identical and numerically safe."),
        ("What does Laplace smoothing prevent?", "A zero likelihood for an unseen value, which would permanently exclude that class."),
        ("Why is NB posteriors overconfident?", "The independence assumption makes the likelihood product too sharp, so the posterior piles up near 0 and 1."),
        ("When does NB beat logistic regression?", "Small training sets, high-dimensional text, and a need for a fast, stable, cheap baseline."),
        ("What is the evidence term P(x) and why is it dropped?", "It is constant across classes for a given x, so it cannot change the argmax."),
    ],
    extra_cards=[
        ("How do you get a calibrated probability from NB?", "Platt-scale the log-odds score: fit a 1-D logistic regression on (log-odds, label) from a validation split."),
        ("Why does NB training cost nothing per feature?", "Sufficient statistics: per-class totals and per-class feature counts. New data means incrementing counts."),
        ("What breaks if you mix up Gaussian and Multinomial NB?", "Continuous values passed to a count model produce nonsense likelihoods; the model is silently wrong, not loudly."),
        ("How do you explain a NB decision?", "Show the highest and lowest log-likelihood contributions per feature \u2014 the tokens that pushed the score each way."),
    ],
    math_why="Naive Bayes is a complete generative model built on one approximation. "
             "That makes every term \u2014 prior, likelihood, smoothing, posterior \u2014 "
             "individually inspectable, which is why it remains a teaching vehicle "
             "long after better classifiers took over.",
    math=[
        ("Bayes' theorem and dropping the evidence",
         "P(y|x) = P(x|y) P(y) / P(x)\nargmax_c P(y=c|x) = argmax_c [ P(y=c) P(x|y=c) ]\nP(x) = sum_c P(x|y=c) P(y=c) is constant in c",
         "For classification the normaliser does not affect the argmax, so we never "
         "compute it. That also means the score is not a probability \u2014 it is a "
         "relative likelihood until you divide by the evidence.",
         "Two classes with prior-weighted likelihoods of 3.0 and 1.2: the argmax is "
         "class A. The actual posterior needs P(x) = 4.2, giving 0.714 \u2014 which is "
         "the only number you may publish."),
        ("Conditional independence",
         "P(x|y=c) = P(x_1|y=c) ... P(x_p|y=c)\ntrue:      P(x_1, x_2|y=c) generally != product\nlog form: sum_i log P(x_i|y=c)",
         "The independence assumption lets each feature's contribution be computed "
         "and cached separately, which is what makes training O(n \u00b7 p) with tiny "
         "state and prediction O(support) rather than O(n \u00b2).",
         "In spam data, P('free' and 'money' | spam) \u2248 0.08, while the independent "
         "product gives 0.10. A 25% relative error per pair compounds across tokens, "
         "which is why NB overconfident."),
        ("Gaussian NB parameters",
         "mu_cj = (1/N_c) sum_{i in c} x_ij\nsigma^2_cj = (1/N_c) sum_{i in c} (x_ij - mu_cj)^2\nlog P(x_j|y=c) = -0.5 log(2 pi sigma^2_cj) - (x_j-mu_cj)^2 / (2 sigma^2_cj)",
         "Each class gets a mean and a variance per feature. The quadratic term is a "
         "Mahalanobis-style distance, so Gaussian NB is effectively a diagonal "
         "Gaussian discriminant analysis.",
         "Class with x = 5, mu = 3, sigma = 2: -0.5 log(2 pi \u00b7 4) - 4/8 = "
         "-1.2655 - 0.5 = -1.7655. Class with sigma = 0.5: the same x becomes a much "
         "worse fit, which is why variance matters."),
        ("Multinomial NB with smoothing",
         "theta_cj = (count(c, token j) + alpha) / (sum_j' count(c, j') + alpha V)\nlog P(token|c) = log theta_cj",
         "Smoothing keeps every token possible in every class. alpha interpolates "
         "between the MLE (alpha = 0) and a uniform prior (alpha \u2192 \u221e); alpha = 1 is "
         "the classic Laplace choice.",
         "Class with 100 tokens and vocabulary 50,000: an unseen token has "
         "theta = 1/50100 with alpha = 1, not 0. Without smoothing the class loses "
         "forever."),
        ("Underflow and log-space scoring",
         "log score(c) = log P(y=c) + sum_j log P(token j | c)\nlog P(token|c) values around -9.5; 500 tokens\nsum = -4750 -> P = e^-4750 = 0 in double",
         "Double precision underflows around 1e-308, i.e. log p \u2248 -709. Text "
         "documents exceed that within roughly 75 tokens at typical log-probabilities, "
         "so the failure is guaranteed, not possible.",
         "A 500-token document: probability-space product returns 0.0 for all "
         "classes. Log-space returns -4702.3 vs -4801.1 \u2014 a clear, correct "
         "difference."),
        ("Calibration error",
         "ECE = sum_b (n_b/N) | acc(b) - conf(b)|\nfor NB with correlated features the log-odds slope\nshrinks far from 1, so |acc - conf| grows",
         "NB is overconfident because independence makes the likelihood ratio too "
         "extreme. A one-parameter recalibration (Platt scaling) recovers most of it, "
         "which is usually cheaper than switching models.",
         "Bins with confidence 0.95 average accuracy 0.80: ECE \u2248 0.15. After "
         "Platt scaling the same bins sit near the diagonal with ECE \u2248 0.02."),
    ],
    math_traps=[
        "Computing P(c|x) as if it were P(x|c) \u2014 a classic and very quiet inversion.",
        "Dropping the evidence term and then publishing the score as a probability.",
        "Estimating variances with n\u22121 when the class is a population, which is standard for NB.",
        "Zero variance in a class making the Gaussian likelihood infinite \u2014 smooth the variance.",
        "Using counts for a Bernoulli model or indicators for a multinomial one.",
    ],
    math_problems=[
        "For one document of 4 tokens, compute the multinomial NB score for two classes in probability space, then in log space; show the underflow.",
        "Show that dropping P(x) does not change the argmax over any number of classes.",
        "Compute Gaussian NB parameters for a 2-feature class and score a new point.",
        "With alpha = 1, compute the smoothed probability of a token seen 0 times in a class with 100 tokens and |V| = 50,000.",
        "Compute ECE for 3 bins with (n, conf, acc) = (500, 0.9, 0.95), (400, 0.6, 0.55), (100, 0.3, 0.2).",
    ],
    tree="""src/com/ml/lab06/
  Main.java               driver: Iris-style continuous + small text corpus
  GaussianNB.java         per-class mean/variance, log-likelihood scoring
  MultinomialNB.java      token count maps, Laplace smoothing, log-space scores
  BernoulliNB.java        indicator model with document-length term
  TextVectorizer.java     vocabulary + counts fitted on the training split only
  Calibrator.java         Platt scaling on the log-odds score""",
    tree_note="All three variants share one scoring shape: build a per-class log "
              "likelihood, add the log prior, argmax. Keeping that skeleton "
              "identical is what makes the variants comparable in a benchmark.",
    types=[
        ("GaussianNB", "fit/predict/predictLogProb; per-class mu and sigma^2 arrays"),
        ("MultinomialNB", "per-class token->count maps plus smoothed log probabilities"),
        ("BernoulliNB", "per-class presence probabilities plus a document-length term"),
        ("TextVectorizer", "vocabulary, counts/indicators, fitted once on the training split"),
    ],
    patterns=[
        ("Log-space scoring and the argmax that never underflows",
         "Accumulate log likelihoods instead of products. The evidence term is "
         "dropped deliberately, with a comment saying so.",
         """public int predict(int[] tokenIds) {
    double[] score = new double[numClasses];
    for (int c = 0; c < numClasses; c++) score[c] = logPrior[c];
    for (int t : tokenIds) {                     // log space: sum, never product
        for (int c = 0; c < numClasses; c++) {
            Double lp = logProb[c].get(t);          // smoothed, so never null
            score[c] += (lp == null ? logUnseen : lp);
        }
    }
    int best = 0;                                  // argmax_c P(y=c)P(x|c); P(x) dropped
    for (int c = 1; c < numClasses; c++) if (score[c] > score[best]) best = c;
    return best;
}"""),
        ("Smoothing that keeps unseen tokens possible",
         "Build the smoothed log-probability map once per class, including a "
         "single fallback value for tokens never seen in training.",
         """static Map<Integer, Double> smoothedLogProbs(Map<Integer, Integer> counts,
                                                   int totalTokens, int vocabSize,
                                                   double alpha) {
    Map<Integer, Double> out = new HashMap<>(counts.size() * 2);
    double denom = totalTokens + alpha * vocabSize;   // Laplace: (count + a)/(N + aV)
    for (Map.Entry<Integer, Integer> e : counts.entrySet())
        out.put(e.getKey(), Math.log((e.getValue() + alpha) / denom));
    return out;
}"""),
    ],
    costs=[
        ("Training, multinomial", "O(n\u00b7tokens)", "incrementally updatable as counts grow"),
        ("Prediction, multinomial", "O(L\u00b7C)", "L = document length in tokens, C = classes"),
        ("Gaussian NB prediction", "O(p\u00b7C)", "one quadratic term per feature per class"),
        ("Training memory", "O(C\u00b7|V|)", "sparse maps; only observed tokens are stored"),
    ],
    numerics=[
        "Always accumulate log-likelihoods; never multiply probabilities.",
        "Smooth with alpha = 1 and keep an explicit logUnseen fallback for unseen tokens.",
        "Guard zero variance in Gaussian NB (add a floor) or the likelihood explodes.",
        "Use n, not n\u22121, for per-class variance: the class is the population.",
        "Fit the vectoriser inside the training fold; a refitted vocabulary changes every score.",
    ],
    tests=[
        "Predicting on training data returns the majority class at worst and perfect accuracy only if separable.",
        "A document containing a token absent from all training data still classifies without NaN.",
        "Log-space and probability-space scoring agree on a 3-token document to 1e-12.",
        "Vocabulary size is unchanged after refitting on a smaller corpus (no leakage).",
        "Predicting a 5,000-token document returns finite scores, not zeros.",
        "Bernoulli and multinomial variants produce different predictions on the same binary-flagged input.",
    ],
    extensions=[
        "Add complement NB (which inverts the document order and often helps on imbalanced text).",
        "Implement NB-SVM: fit a logistic regression on the NB log-count ratio features.",
        "Add Platt calibration and report the ECE change.",
    ],
    code_checklist=[
        "Scoring happens in log space only",
        "Smoothing applied with a documented alpha and an unseen-value fallback",
        "Variant chosen explicitly, with the feature representation that requires",
        "Vectoriser fitted inside the training fold and versioned",
        "Per-class metrics reported, not only accuracy",
        "Posterior published only after calibration, or not at all",
    ],
    exercise_selfcheck=[
        "I can explain which independence assumption my variant makes",
        "My scoring never multiplies probabilities",
        "I can state why NB posteriors need calibration before publication",
        "I report per-class F1 on imbalanced data",
    ],
    exercises=[
        ("Derive the multinomial NB score",
         "Get from Bayes to the log-space scoring formula by hand.",
         ["Write out Bayes' theorem and drop the evidence.",
          "Substitute the multinomial likelihood and take logs.",
          "Show the order of terms does not matter after taking logs.",
          "Implement it and compare against a probability-space version on short docs."],
         "A hand derivation and a test that agrees to 1e-12."),
        ("Prove the underflow",
         "Show why probability-space scoring fails on real documents.",
         ["Score a 100, 1,000 and 5,000-token document in probability space.",
          "Record where the product hits 0.0.",
          "Score the same documents in log space.",
          "Confirm identical argmax wherever probability space still works."],
         "A table of underflow thresholds and a passing equivalence test below them."),
        ("Laplace smoothing end to end",
         "See exactly what unsmoothed NB does with an unseen word.",
         ["Train without smoothing; score a document with an unseen token.",
          "Observe the class being eliminated permanently.",
          "Add alpha = 1 and re-score.",
          "Sweep alpha over 0, 0.1, 1, 10 and report validation F1."],
         "A before/after table and an alpha choice from a curve."),
        ("Implement all three variants",
         "Compare them on data that suits each.",
         ["Implement Gaussian, Multinomial and Bernoulli NB.",
          "Run all three on a small continuous set and a binary text set.",
          "Report which variant wins where.",
          "Explain the mismatch cases in two sentences each."],
         "A comparison table with a written explanation of each result."),
        ("Calibration for NB probabilities",
         "Make the posterior publishable.",
         ["Collect log-odds scores on a validation split.",
          "Bin into deciles and compute ECE.",
          "Fit Platt scaling (1-D logistic) on the log-odds.",
          "Report ECE before and after."],
         "Two ECE numbers and a reliability table."),
        ("Class imbalance and complements",
         "Handle the case where the minority class matters.",
         ["Train on a 2% positive corpus and report accuracy plus macro-F1.",
          "Add class priors weighted by inverse frequency.",
          "Implement complement NB.",
          "Compare all three on macro-F1."],
         "A metrics table and a recommendation."),
        ("Explainability endpoint",
         "Serve the per-token contributions that drove a decision.",
         ["Expose per-token log-likelihood differences between the top two classes.",
          "Serve POST /classify returning label and the top contributing tokens.",
          "Verify contributions sum to the score difference.",
          "Check the explanations against 20 hand-read documents."],
         "A running endpoint and 20 spot-checked explanations."),
        ("Streaming NB training",
         "Update counts incrementally instead of retraining.",
         ["Implement fit() and observe() with count updates.",
          "Stream 100k labelled documents.",
          "Show predictions update without a full retrain.",
          "Measure the wall-clock cost of the update path."],
         "A streaming demo with a throughput number and identical final counts."),
    ],
    quiz=[
        ("The 'naive' assumption is...", ["Classes are equally likely", "Features are conditionally independent given the class", "Features are normally distributed", "Labels are binary"], 1, "Conditional independence is the assumption; class balance is a prior, not the assumption."),
        ("Which variant fits binary term indicators?", ["Gaussian", "Multinomial", "Bernoulli", "Any of them"], 2, "Bernoulli models each term's presence or absence, plus a document-length term."),
        ("Laplace smoothing prevents...", ["Slow training", "Zero probabilities for unseen values", "Class imbalance", "Overfitting to the majority class"], 1, "Add-alpha keeps every token possible in every class."),
        ("Why is probability-space scoring unsafe for text?", ["It is slower", "Products of many small probabilities underflow to zero", "It cannot handle multi-byte characters", "It ignores the prior"], 1, "Log space is mathematically identical and numerically safe."),
        ("What happens to the argmax when P(x) is dropped?", ["Nothing", "The argmax changes because P(x) is class dependent", "It becomes random", "It becomes the prior"], 0, "P(x) is a constant across classes for a fixed x, so it cannot reorder them."),
        ("Why are NB posteriors overconfident?", ["The prior is wrong", "The independence assumption makes the likelihood ratio too extreme", "Smoothing adds mass to unseen tokens", "The variance estimate is biased"], 1, "Multiplying over many features compounds independence error into a sharper ratio."),
        ("Gaussian NB estimates per class...", ["A single variance", "A mean and a variance per feature", "A covariance matrix", "A density estimate via KDE"], 1, "Per-class per-feature mean and variance gives a diagonal-covariance discriminant."),
        ("When does NB beat logistic regression?", ["Very large datasets", "Small datasets with many features, especially text", "Continuous data only", "When labels are continuous"], 1, "Low variance from few parameters makes it strong in low-data regimes."),
        ("NB training is best described as...", ["Iterative optimisation", "Counting sufficient statistics", "Gradient descent", "Cross-validation"], 1, "Per-class totals and feature counts are all that is needed, so updates are incremental."),
        ("Which is NOT true of multinomial NB?", ["It uses term counts", "It applies smoothing", "It can handle binary features", "It ignores document length entirely"], 2, "Multinomial uses counts and is insensitive to length; that is a known weakness versus Bernoulli."),
        ("P(x|y) is the...", ["Posterior", "Likelihood", "Prior", "Evidence"], 1, "Likelihood is the conditional density of the data given the class; the posterior is the reverse."),
        ("How do you get calibrated probabilities from NB?", ["Clip the posterior", "Platt-scale the log-odds score", "Raise to a power", "Average with the prior"], 1, "A one-dimensional logistic fit on the log-odds recovers most of the calibration error."),
        ("Adding alpha to smoothing counts...", ["Speeds up training", "Interpolates between the MLE and a uniform prior", "Removes the prior term", "Reduces class imbalance"], 1, "alpha = 0 is the MLE; alpha tending to infinity approaches uniform over the vocabulary."),
        ("Why fit the vectoriser inside the training fold?", ["Speed", "Otherwise the vocabulary sees test-fold text and leaks it", "Memory", "It changes the smoothing"], 1, "Vocabulary leakage is a real source of optimistic accuracy on text tasks."),
    ],
    vision=dict(
        future="Naive Bayes survives where the count model is genuinely the right "
               "shape: text, spam, document routing and any high-dimensional sparse "
               "problem with limited labels. The frontier is not the base classifier "
               "but its hybrids \u2014 NB-SVM, complement NB and calibration wrappers "
               "\u2014 which inherit its speed while borrowing discriminative strength.",
        good=[
            "The variant is chosen explicitly and justified by the feature representation.",
            "Scoring is log-space everywhere and smoothing is on by default with a documented alpha.",
            "Per-class precision/recall/F1 is reported because text is imbalanced.",
            "Any published probability has been calibrated, or the score is labelled a score.",
        ],
        ladder=[
            ("L1", "Classify", "Implement multinomial NB with smoothing and report accuracy."),
            ("L2", "Be rigorous", "Log space, in-fold vectoriser, per-class metrics, alpha swept."),
            ("L3", "Calibrate", "Platt-scale the log-odds and report the ECE change."),
            ("L4", "Extend", "Complement NB, NB-SVM, and a streaming incremental fit."),
        ],
        behaviors="Match the variant to the data representation. Treat the naive "
                  "assumption as a documented bias. Never publish an uncalibrated "
                  "posterior.",
        anti=[
            "Inverting the conditional by accident: P(x|y) treated as P(y|x).",
            "Smoothing switched off 'to keep it pure'.",
            "Accuracy quoted on a corpus with 2% positives.",
            "A vocabulary refit on the full corpus inside a CV loop.",
        ],
        trends=[
            "NB-SVM and log-count ratio features blending generative priors with discriminative training.",
            "Complement and one-vs-rest NB variants for imbalanced text.",
            "FastText-style linear models with subword features as the practical successor for text classification.",
            "Calibration as a standard pipeline stage rather than an afterthought.",
        ],
        d30="Implement multinomial NB in log space and prove the underflow it avoids.",
        d60="Implement all three variants and compare them on data suited to each.",
        d90="Add Platt calibration, a streaming fit, and an explainability endpoint showing per-token contributions.",
        metrics=[
            "I can state which independence assumption each variant makes.",
            "My scores are computed in log space and I can prove it.",
            "I can measure my calibration error before and after.",
            "I report macro-F1, not just accuracy.",
        ],
        closer="A count model you understand completely is worth more than a "
               "complex model whose assumptions you cannot state.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Email Spam Filter with Calibrated Probabilities",
        brief="Build a spam filter with Naive Bayes, calibrate the posteriors, and "
              "make the threshold a cost decision.",
        timebox="3 hours",
        why="Spam is the canonical NB problem: sparse counts, imbalance, and an "
            "asymmetric cost that makes the threshold the interesting part.",
        requirements=[
            "Load a labelled spam corpus (Enron-Spam is public) or synthesise one with class-conditional token counts.",
            "Implement multinomial and Bernoulli NB; report both on the same split.",
            "Sweep alpha over 7 values and plot macro-F1 and calibration error.",
            "Platt-calibrate the log-odds; report ECE before and after.",
            "Choose a threshold from a cost matrix (false positive = 1, false negative = 20) and report cost per 1,000 messages.",
            "Expose per-token contributions that justify each classification, and audit 20 of them by hand.",
        ],
        steps=[
            ("1", "20m", "Load corpus, build the in-fold vectoriser, assert no empty documents", "A reproducible corpus loader"),
            ("2", "25m", "Implement multinomial NB with log-space scoring and smoothing", "A fitted model with finite scores on long documents"),
            ("3", "20m", "Implement Bernoulli NB and compare", "A variant comparison table"),
            ("4", "25m", "Sweep alpha; plot macro-F1 and ECE against alpha", "Two curves and a chosen alpha"),
            ("5", "25m", "Platt calibration on a validation split; recompute ECE", "Before/after calibration numbers"),
            ("6", "20m", "Cost-matrix threshold sweep; report cost per 1,000 messages", "A cost curve with a marked optimum"),
            ("7", "25m", "Per-token contribution endpoint; hand-audit 20 messages", "An audited explanation sample"),
        ],
        diagram="""messages --> Tokeniser --> in-fold vocabulary --> counts | indicators
                                          |
                     +--------------------+--------------------+
                     |                                         |
              Multinomial NB                             Bernoulli NB
                     |                                         |
                     +--------------------+--------------------+
                                          |
                        log-odds score --> calibration curve
                                          |
                    cost-based threshold --> /classify
                    (label, p, top tokens)""",
        notes=[
            "Stopwords help little for NB; the model handles them but they add noise to explanations.",
            "Report macro-F1: accuracy on a 10% spam corpus is mostly measuring the absence of spam.",
            "The audit step is the point of the project \u2014 explanations you have not read are not explanations.",
            "Keep the calibration split separate from both training and threshold tuning.",
        ],
        deliverables=[
            "One-command run producing the variant table, alpha sweep and cost curve.",
            "Calibration report before and after Platt scaling.",
            "20 hand-audited explanations with your verdict on each.",
            "Model card covering limitations, cost assumptions and a retrain trigger.",
        ],
        grading=[
            ("Correctness", "30%", "Log-space scoring, in-fold vectoriser, smoothing proven"),
            ("Calibration", "25%", "ECE measured and improved with evidence"),
            ("Operating point", "20%", "Threshold from the cost matrix, cost per 1,000 reported"),
            ("Analysis", "15%", "Variant comparison and 20 audited explanations"),
            ("Communication", "10%", "Model card states what the filter will miss"),
        ],
        stretch=[
            "Add complement NB and show where it helps on the imbalanced class.",
            "Implement NB-SVM (log-count ratio features plus logistic regression) and compare.",
            "Add a streaming incremental fit and demonstrate adaptation to a campaign.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Inbound Spam and Phishing Filter",
        scenario="A mid-size business mail provider filters 6M messages a day. A "
                 "legitimate message lost to the spam folder costs a customer; a "
                 "phishing message delivered costs far more. You own the filter, "
                 "its false-negative budget and the explanation shown to an end user "
                 "who disputes a decision.",
        scale=[
            ("Daily volume", "~6M messages/day, peak 1,400 msg/s"),
            ("Positive rate", "4\u20138% spam, 0.2\u20130.5% phishing, both rising during campaigns"),
            ("Latency budget", "p99 < 25 ms per message, including reputation lookups"),
            ("Contractual constraint", "false positives must be under 0.05% with a one-click restore"),
            ("Success metric", "phishing delivery rate and per-message compute cost"),
        ],
        diagram=""" MTA --> auth results (SPF/DKIM/DMARC) + reputation (cached)
            |
        NB scorer (multinomial over headers/body/URL tokens)
            |                     \
            |                      +--> per-token contribution log (explanations)
            v
        NB-SVM / boosted challenger (shadow)
            |
   Policy layer: bayes + reputation + campaign rules + tenant overrides
            |
  +--------+---------+------------+-----------+
  |        |         |            |           |
deliver  spam folder  quarantine  restore    appeal
 (95%)     (4.2%)     (0.5%)    request     service
                                     |
                        explain endpoint + one-click allowlist""",
        components=[
            ("Feature and scoring tier",
             ["Three token views: headers, visible body text, and URL host/path tokens",
              "Separate weights per view, tuned on a held-out split rather than assumed",
              "NB scores every message; the score plus top tokens are stored for 30 days for appeals",
              "Challenger model scores 100% of traffic in shadow; weekly comparison on matured labels"]),
            ("Policy layer",
             ["Bayes threshold per tenant, with an approval workflow for changes",
              "Reputation and authentication results act as overrides in both directions",
              "Campaign rules (known phishing infrastructure) bypass the model entirely",
              "Every decision records score, threshold version, token contributions and rule hits"]),
            ("Feedback and reputation",
             ["User restore requests are the strongest available label and arrive within minutes",
              "Phishing confirmations arrive in hours; blocklist propagation in minutes",
              "Restore requests beyond a per-tenant budget trigger an automatic review",
              "Confirmed phish propagate to the blocklist before the next retry attempt"]),
            ("Operations and compliance",
             ["p99 latency budget enforced with a timeout that falls back to header-only scoring",
              "Per-tenant false-positive tracking against the contractual 0.05% ceiling",
              "Appeal service exposing the top contributing tokens in plain language",
              "Full decision log retained 12 months for contractual and regulatory requests"]),
        ],
        timeline=[
            ("Week 1", "Ship header-only Bayes with logging and the restore request flow"),
            ("Week 2", "Add body and URL views with tuned weights; watch the FP rate against the ceiling"),
            ("Week 3", "Platt calibration and per-tenant thresholds with approval workflow"),
            ("Week 4", "Challenger in shadow; confirm no regression on confirmed phish"),
            ("Week 5", "Appeal explanations live; postmortem drill with a simulated campaign"),
        ],
        runbook=[
            "# Filter health, threshold set, model version",
            "curl -s localhost:8080/admin/filter | jq '{version,thresholdSet,ageHours}'",
            "",
            "# Spam and quarantine rates vs the 7-day baseline",
            "curl -s 'localhost:8080/admin/rates?window=1h' | jq '{spam,quarantine,baseline}'",
            "",
            "# Temporary safe mode: header-only scoring, stricter threshold",
            "curl -XPOST localhost:8080/admin/mode -d '{\"mode\":\"HEADER_ONLY_STRICT\"}'",
            "",
            "# Tenant override (allow a sender/domain) with audit logging",
            "curl -XPOST localhost:8080/admin/tenant-override -d '{\"tenant\":\"acme\",\"allow\":\"acme-mail.example\"}'",
            "",
            "# Explain one quarantined message for an appeal",
            "curl -s 'localhost:8080/admin/explain?messageId=m-4471' | jq '.score,.topTokens,.rules'",
        ],
        metrics=[
            "SLO: p99 < 25 ms; availability 99.95%; a scoring outage degrades to header-only, never to deliver-all.",
            "Security: phishing delivery rate, measured against confirmed phish per 100k messages.",
            "Contract: false-positive rate per tenant, hard ceiling 0.05%.",
            "Model: macro-F1 on matured labels; calibration error by tenant tier.",
            "Business: restores per 1,000 messages (a proxy for user trust) trending down.",
        ],
        failures=[
            ("A phishing campaign gets through at volume", "Novel infrastructure unseen in training", "Emergency blocklist propagation from confirms; add campaign rules; retrain on the confirmed set"),
            ("Spam folder complaints spike", "Threshold push or a tenant-specific vocabulary problem", "Restore to the last approved threshold set, inspect per-tenant scores, add tenant tokens"),
            ("p99 breaches 25 ms", "Synchronous reputation lookup added to the hot path", "Enforce cached-only lookups with a hard timeout; degrade to header-only scoring"),
            ("A legitimate bulk sender is filtered", "New sending domain with unfamiliar tokens", "Add a tenant override with audit logging; retrain with the sender's vocabulary"),
            ("Calibration drifts after a large retrain", "New class mix in the training window", "Re-fit the calibrator on a fresh validation split before promotion"),
        ],
        backlog=[
            "NB-SVM challenger promoted once it beats Bayes on matured labels at equal FP rate.",
            "Per-view weight tuning automated as part of the retrain job.",
            "Appeal explanation service translated into user-facing language with a quality review.",
            "Campaign-response drill: a simulated phishing wave timed end to end each quarter.",
            "Contractual FP ceiling enforced as an automated release gate, not a dashboard.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a filter that loses phishing, explains every "
               "quarantine, keeps its contractual false-positive ceiling, and can "
               "degrade safely when a dependency is down.",
    ),
))
