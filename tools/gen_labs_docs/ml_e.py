# -*- coding: utf-8 -*-
"""Tailored specs for labs/ml/lab07 .. lab08."""

from ml_a import URLS_ML

SPECS = []

# ---------------------------------------------------------------- lab07
SPECS.append(dict(
    track="ml", lab="lab07", full_set=True, level="Intermediate",
    title="K-Means & Hierarchical Clustering", main_class="com.ml.lab07.Main",
    problem="Nobody labelled your data, but you still need structure: segments, "
            "outliers, or a lower-dimensional view of the space.",
    why_now="Clustering is unsupervised, so every conclusion is a hypothesis rather "
             "than a measurement. That constraint shapes how you evaluate, and "
             "lab10's habits do not transfer for free.",
    objectives=[
        "Implement k-means++ initialisation and Lloyd iterations to convergence",
        "Explain inertia, the elbow method and the silhouette score, and their limits",
        "Implement agglomerative clustering with single, average, complete and Ward linkage",
        "Read a dendrogram and decide where to cut it",
        "Explain why k-means assumes spherical, similarly sized clusters",
        "Detect outliers from cluster distance and decide what to do about them",
    ],
    concepts=[
        ("Lloyd's algorithm",
         "Alternate assignment (each point to its nearest centroid) and update "
         "(centroid = mean of its members). This is EM with equal-variance spherical "
         "Gaussians and hard assignments. It monotonically decreases inertia, so it "
         "converges \u2014 but only to a local optimum, which is why initialisation matters."),
        ("k-means++ initialisation",
         "Pick the first centroid uniformly, then pick each subsequent centroid with "
         "probability proportional to its squared distance from the nearest existing "
         "centroid. This makes bad local optima exponentially less likely and costs "
         "nothing extra."),
        ("Inertia and the elbow",
         "Inertia (within-cluster sum of squares) always falls as k grows, so it "
         "cannot choose k on its own. Plot inertia against k and look for the elbow \u2014 "
         "the knee past which each extra cluster buys almost nothing. It is a visual "
         "judgement, and you should say so rather than pretending it is a test."),
        ("Silhouette and its limitations",
         "For each point, s = (b \u2212 a)/max(a, b) where a is mean intra-cluster distance "
         "and b the mean distance to the nearest other cluster. It ranges \u22121..1 and is "
         "scale-free, but it assumes roughly spherical, similarly sized clusters \u2014 "
         "exactly what k-means assumes. It cannot tell you k is wrong; it can only "
         "say the shape assumption failed."),
        ("Agglomerative clustering and linkage",
         "Start with n singleton clusters and repeatedly merge the closest pair. "
         "Linkage defines 'closest': single (chaining), complete (compact), average "
         "(compromise), Ward (minimises variance increase). Ward is the one that "
         "behaves like k-means and is the usual default."),
        ("Dendrograms and the cut",
         "The dendrogram records merge order and merge height. Choosing k means cutting "
         "at a height. Ward's height is interpretable as the within-cluster variance "
         "added by that merge, which makes the cut a variance budget decision rather "
         "than a guess."),
    ],
    formulas=[
        ("Inertia = \u03a3_{c} \u03a3_{i in c} ||x\u1d62 \u2212 \u03bc_c||\u00b2", "Within-cluster sum of squares", "the quantity k-means minimises"),
        ("argmin_c ||x\u1d62 \u2212 \u03bc_c||\u00b2", "Assignment step", "hard assignment, nearest centroid"),
        ("\u03bc_c = (1/|c|)\u03a3_{i in c} x\u1d62", "Update step", "centroid as cluster mean"),
        ("s(i) = (b(i) \u2212 a(i)) / max(a(i), b(i))", "Silhouette coefficient", "\u22121..1, higher is better"),
        ("d(A,B) = min_{a in A,b in B} d(a,b)", "Single linkage", "prone to chaining"),
        ("d(A,B) = \u03a3|a||b|d(a,b)/(|A||B|)", "Average linkage", "compromise between single and complete"),
        ("\u0394W(A\u222aB) = |A||B|/(|A|+|B|) ||\u03bc_A \u2212 \u03bc_B||\u00b2", "Ward merge cost", "variance added by a merge"),
    ],
    flow=[
        "Scale features. Clustering is geometric, and an unscaled axis will define the clusters for you.",
        "Decide whether you want k-means (fast, spherical) or agglomerative (interpretable, small n).",
        "Run k-means with k-means++ initialisation and multiple restarts; keep the lowest inertia.",
        "Plot inertia vs k for the elbow, and compute the mean silhouette for the same range.",
        "Inspect the actual clusters \u2014 size distribution, feature profiles and outliers \u2014 never just the score.",
        "Validate the segmentation against a business outcome; unlabelled structure is a hypothesis until something external confirms it.",
    ],
    assumptions=[
        "Features are scaled, or the highest-variance axis dominates the geometry",
        "k-means: clusters are spherical and of similar size",
        "K is chosen with domain input, not only by an internal metric",
        "The data is not better served by density-based methods (DBSCAN) if shapes are irregular",
        "n is small enough for agglomerative's O(n\u00b2) cost and O(n\u00b2) memory, or you use Ward with n < ~10k",
        "Cluster identity is stable enough to name; a cluster you cannot describe is not actionable",
    ],
    pitfalls=[
        ("One huge cluster plus k-1 tiny ones", "initialisation or feature scale dominated by outliers", "standardise, use k-means++, try multiple restarts"),
        ("Same input, different clusters each run", "single random initialisation, unseeded", "seed k-means++ and report the best-of-r inertia"),
        ("Silhouette says 0.7 and the segments are useless", "the metric scored the shape assumption, not business usefulness", "validate segments against an external outcome"),
        ("Curved clusters are shredded", "k-means assumes spherical clusters", "use DBSCAN or spectral clustering, or apply PCA/whitening first"),
        ("Agglomerative runs out of memory", "O(n\u00b2) distance matrix at n = 50k", "cap n, use Ward with a priority queue, or use k-means"),
        ("A cluster is a data-quality artefact", "duplicates or a missing-value sentinel in one group", "audit cluster membership before acting on the segment"),
    ],
    java=[
        ("PriorityQueue for Ward merges", "the heap makes agglomerative O(n\u00b2 log n) instead of a full pairwise re-scan"),
        ("Arrays.sort / partial selection for top-k", "finding the k nearest centroid per point"),
        ("SplittableRandom", "seeded k-means++ so runs are reproducible"),
        ("record Cluster(int id, double[] centroid, List<Integer> members)", "an inspectable cluster object"),
        ("double[][] centroidDistances cache", "recomputed once per iteration, reused in the assignment loop"),
    ],
    links=[
        "**Lab 08** (PCA) is often the right preprocessing step before clustering.",
        "**Lab 10**'s cross-validation does not transfer \u2014 unsupervised structure needs external validation.",
        "**Lab 05** (KNN) is the supervised cousin of the same distance geometry.",
        "**mlops/lab08** is where cluster drift becomes an operational alert.",
    ],
    checklist=[
        "I can explain inertia and why it cannot choose k alone",
        "I use k-means++ and report the best of several restarts",
        "I know when the silhouette score is lying to me",
        "I can state the spherical-cluster assumption and when it fails",
        "I choose the dendrogram cut as a variance budget, not a vibe",
        "I validate clusters against something outside the data",
    ],
    cards=[
        ("Why does inertia always decrease with k?", "More clusters means more freedom to fit; with k = n every point is its own cluster and inertia is zero."),
        ("What does k-means++ fix?", "Bad initialisation. Sampling centroids with probability proportional to squared distance avoids collapsing several centroids together."),
        ("What does the silhouette score assume?", "Spherical, similarly sized clusters \u2014 the same assumption k-means makes, so it cannot diagnose that failure."),
        ("Single linkage's characteristic flaw?", "Chaining: distant points get linked through a chain of close neighbours."),
        ("Why prefer Ward linkage?", "Each merge minimises the increase in within-cluster variance, so the dendrogram height is a variance budget."),
        ("Can k-means find non-convex clusters?", "No. Voronoi cells are convex, so a ring or a crescent cannot be recovered."),
        ("Why scale before clustering?", "Distance is dominated by the largest-variance axis, so unscaled data lets one feature define the segments."),
        ("How do you validate clusters without labels?", "Stability under resampling and initialisation, size distribution, feature profiles, and correlation with an external business outcome."),
    ],
    extra_cards=[
        ("What is a stopping criterion for k-means?", "Inertia change below a tolerance, or centroids moving less than eps. It always terminates because inertia is non-increasing."),
        ("Why is agglomerative O(n\u00b2) memory?", "It needs pairwise distances between every pair of points (or every pair of clusters), unlike k-means."),
        ("When should you prefer DBSCAN to k-means?", "Irregular cluster shapes, unknown k, and a genuine interest in noise points as outliers."),
        ("What does a very uneven cluster size distribution suggest?", "Either real heterogeneity, or a scaling/init problem worth checking before naming segments."),
    ],
    math_why="k-means is EM for equal-covariance spherical Gaussians with hard "
             "responsibilities. Once you see that, the monotonic decrease of "
             "inertia, the local-optimum problem and the spherical assumption all "
             "become one argument instead of three facts.",
    math=[
        ("Lloyd's algorithm as hard EM",
         "E-step: z_ic = 1[argmin_k ||x_i - mu_k||^2]\nM-step: mu_k = (1/n_k) sum_i z_ic x_i\nJ = sum_i ||x_i - z_i||^2 decreases monotonically",
         "Each iteration assigns points to their nearest centroid, then recomputes "
         "centroids. Because hard assignment means no responsibility smoothing, the "
         "objective can only fall, so termination is guaranteed \u2014 to a local "
         "optimum.",
         "Two blobs at (0,0) and (10,0) with k=2 always converge to a sensible split. "
         "The same data with k=3 splits the second blob, because inertia is lower "
         "\u2014 which is why you need more than inertia to choose k."),
        ("k-means++ seeding",
         "pick c1 uniformly\nP(ci) proportional to min_j ||x - c_j||^2\nE[clusters covered] rises, bad optima become exponentially unlikely",
         "The guarantee is on the quality of the objective achieved in one run, "
         "compared with the O(log k) restarts k-means++ makes unnecessary in "
         "practice.",
         "With 3 well-separated blobs and k=3: uniform seeding fails to cover all "
         "three about 22% of the time; k-means++ essentially never fails."),
        ("Inertia as a function of k",
         "Inertia(k) is non-increasing; Inertia(n) = 0\nknee heuristic: argmax_k [Inertia(k) - Inertia(k+1)] / (k+1)\nor the 'elbow' by visual curvature",
         "There is no statistical test here \u2014 the elbow is a judgement. Report "
         "the curve, name the chosen k, and give the business reason.",
         "Inertia 5200, 2400, 1500, 1200, 1080 for k = 1..5: the drop from 2 to 3 is "
         "large, from 4 to 5 is small. k = 3 is defensible; k = 5 is not."),
        ("Silhouette coefficient",
         "a(i) = mean distance from i to others in its cluster\nb(i) = min over other clusters c of mean distance to c\ns(i) = (b - a) / max(a, b),  in [-1, 1]",
         "s near 1 means compact and well separated; near 0 means on the boundary; "
         "negative means misassigned. Averaging over points gives the reported "
         "score.",
         "Silhouette 0.71 with cluster sizes 9,900 and 100 is a warning, not a "
         "success \u2014 the score hides a singleton. Always print the size "
         "distribution with the score."),
        ("Agglomerative linkage costs",
         "single:    min pair distance      -> chains, can produce long thin clusters\ncomplete:  max pair distance      -> compact, biased to equal sizes\naverage:   mean pair distance     -> compromise\nWard:       |A||B|/(|A|+|B|) ||mu_A - mu_B||^2",
         "Each linkage encodes a different notion of similarity. Ward is preferred "
         "because its merge cost is interpretable as variance added, matching "
         "k-means' objective.",
         "Two distant groups bridged by one intermediate point: single linkage merges "
         "everything into one cluster; complete and Ward keep three."),
        ("Cost of agglomerative clustering",
         "distance matrix: n^2 doubles = 8n^2 bytes\nnaive implementation: O(n^3)\nwith a priority queue on Ward costs: O(n^2 log n)\nrule of thumb: n < 10,000",
         "Memory is the binding constraint, exactly like kernel SVMs. For larger n, "
         "sample, use k-means, or use a sparse-tree approximation.",
         "n = 5,000 needs 200 MB for the matrix; n = 50,000 needs 20 GB. Ward with a "
         "heap is fine to ~20k, k-means has no such ceiling."),
    ],
    math_traps=[
        "Reading the elbow as an objective criterion rather than a judgement call.",
        "Averaging the silhouette over clusters instead of over points, which lets a huge cluster dominate.",
        "Forgetting to standardise and then blaming the algorithm.",
        "Cutting the dendrogram at an arbitrary height and calling the segments 'natural'.",
        "Computing the Ward merge cost on raw scales where variance is not comparable.",
    ],
    math_problems=[
        "Run Lloyd's algorithm by hand on 6 two-dimensional points with k=2, starting from given centroids.",
        "Show inertia(k) is non-increasing by proving that the optimal k-cluster solution has inertia at most that of the optimal (k+1)-cluster solution.",
        "Compute the silhouette for a point with a = 1.0 and b = 4.0, and again with a = 4.0 and b = 1.0.",
        "Apply Ward's cost formula to merge clusters of size 3 (mean (0,0)) and size 5 (mean (2,0)).",
        "Compute memory for agglomerative at n = 2,000, 10,000 and 50,000, and state the crossover to k-means.",
    ],
    tree="""src/com/ml/lab07/
  Main.java                driver: 3 blobs + a crescent, k sweep
  KMeans.java              k-means++ seeding, Lloyd iterations, predict, inertia
  Agglomerative.java       single/average/complete/Ward linkage, dendrogram merge list
  Dendrogram.java          merge records with heights, cut(tree, k)
  ClusterEvaluator.java    inertia curve, silhouette, size distribution""",
    tree_note="KMeans caches the full centroid-by-point distance matrix once per "
              "iteration; recomputing inside the assignment loop is the usual "
              "10x slowdown people hit before optimising anything else.",
    types=[
        ("KMeans", "fit with k-means++ and restarts; exposes inertia() and predict()"),
        ("Agglomerative", "linkage strategy, merge list, cut(nClusters)"),
        ("Dendrogram", "ordered merge records with heights, printable as text"),
        ("ClusterEvaluator", "inertia curve, mean silhouette, cluster size report"),
    ],
    patterns=[
        ("k-means++ seeding and Lloyd iteration with an inertia cache",
         "Seeding samples centroids proportional to squared distance; the loop "
         "caches centroid distances so assignment is a matrix scan.",
         """public double fit(double[][] x, int k, int restarts) {
    double best = Double.POSITIVE_INFINITY;
    for (int r = 0; r < restarts; r++) {
        double[][] centroids = kMeansPlusPlusInit(x, k, seed + r);   // independent seeding
        for (int iter = 0; iter < maxIter; iter++) {
            double[][] d = assign(x, centroids);                      // one full cache
            double inertia = 0;
            int[] counts = new int[k];
            double[][] sums = new double[k][x[0].length];
            for (int i = 0; i < x.length; i++) {
                int c = nearest(d[i]);
                inertia += d[i][c];
                counts[c]++;
                for (int j = 0; j < x[0].length; j++) sums[c][j] += x[i][j];
            }
            for (int c = 0; c < k; c++)                          // update step
                if (counts[c] > 0) for (int j = 0; j < sums[c].length; j++)
                    centroids[c][j] = sums[c][j] / counts[c];
            if (iter > 0 && Math.abs(inertia - prevInertia) < 1e-9) break;
            prevInertia = inertia;
        }
        if (inertia < best) { best = inertia; bestCentroids = centroids; }
    }
    return best;                                                 // best of restarts
}"""),
        ("Ward merge selection with a priority queue",
         "Merge costs are recomputed only for the clusters touched by the previous "
         "merge; the heap holds the rest. That turns O(n\u00b3) into roughly O(n\u00b2 log n).",
         """public List<Merge> ward(double[][] x) {
    int n = x.length;
    int[] parent = new int[n];
    double[] size = new double[n];
    double[][] sum = new double[n][];
    for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; sum[i] = x[i].clone(); }
    PriorityQueue<Merge> pq = new PriorityQueue<>(Merge::compareTo);
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) pq.add(new Merge(i, j, wardCost(i, j)));
    List<Merge> merges = new ArrayList<>();
    while (pq.size() > 1 && merges.size() < n - 1) {
        Merge m = pq.poll();
        if (parent[m.a] != m.a || parent[m.b] != m.b) continue;  // stale heap entry
        merges.add(new Merge(rootOf(m.a), rootOf(m.b), m.height));
        int r = union(rootOf(m.a), rootOf(m.b));                  // size-weighted sums
        for (int j = 0; j < n; j++)
            if (parent[j] == j && j != r) pq.add(new Merge(j, r, wardCost(j, r)));
    }
    return merges;
}"""),
    ],
    costs=[
        ("k-means iteration", "O(n k d)", "cache centroid distances to avoid recomputation"),
        ("k-means++ seeding", "O(n k d)", "one pass per new centroid, negligible in total"),
        ("Agglomerative with a heap", "O(n\u00b2 log n) time, O(n\u00b2) memory", "memory is the real limit"),
        ("Silhouette computation", "O(n\u00b2)", "can be approximated by sampling 1,000 points"),
    ],
    numerics=[
        "Standardise before clustering; assert stability after scaling in a test.",
        "Seed k-means++ and run at least 5 restarts, reporting the best inertia.",
        "Stop on inertia change below tolerance, not on a fixed iteration count.",
        "Print the cluster size distribution alongside any silhouette score.",
        "Use `Math.fma` in the distance loop where available; the accumulation is long.",
    ],
    tests=[
        "Well-separated 3-blob data with k = 3 recovers the true labels up to permutation.",
        "k-means++ with 5 restarts never returns worse inertia than a single random seed on average.",
        "Single linkage chains through an intermediate point; Ward does not.",
        "Scaling every feature by 1000 leaves the cluster assignment unchanged.",
        "Silhouette of a perfectly separated synthetic set exceeds 0.8.",
        "Two runs with the same seed produce identical labels.",
    ],
    extensions=[
        "Implement DBSCAN for irregular shapes and compare against k-means on a crescent dataset.",
        "Add a stability test: bootstrap the data, recluster, and report the adjusted Rand index across runs.",
        "Implement Gaussian mixtures with EM and show it beats k-means on unequal-variance clusters.",
    ],
    code_checklist=[
        "Scaling happens inside the estimator",
        "k-means++ seeding with an explicit seed and multiple restarts",
        "Convergence on inertia change, logged per iteration",
        "Cluster size distribution printed with every score",
        "Agglomerative respects the O(n\u00b2) memory limit, enforced by an n guard",
        "Clusters are validated against an external outcome before being named",
    ],
    exercise_selfcheck=[
        "I chose k with a reason I can write down",
        "I print cluster sizes next to any quality score",
        "I can state the spherical assumption and when it fails",
        "My results are reproducible from a seed",
    ],
    exercises=[
        ("Implement k-means from scratch",
         "Lloyd's algorithm plus k-means++ seeding.",
         ["Implement k-means++ seeding.",
          "Implement assignment and update with an inertia cache.",
          "Verify on 3 synthetic blobs that k = 3 recovers them.",
          "Compare 1 restart against 10 on a harder dataset."],
         "A verified implementation and an inertia comparison."),
        ("Choose k with evidence",
         "Elbow plus silhouette plus a business constraint.",
         ["Compute inertia for k = 1..10 and print the curve.",
          "Compute mean silhouette for the same range.",
          "Print cluster sizes at each k.",
          "Pick k using all three and write the justification."],
         "A curve table, size distributions and a written k decision."),
        ("Agglomerative with four linkages",
         "See the difference the linkage makes.",
         ["Implement single, average, complete and Ward.",
          "Cluster a dataset with a bridging intermediate point.",
          "Print the dendrogram merges with heights for each linkage.",
          "Explain which linkage fails and why."],
         "Four dendrograms and a written explanation of chaining."),
        ("Cut the dendrogram as a variance budget",
         "Turn the dendrogram into a decision.",
         ["Implement cut(dendrogram, k) and cutByHeight().",
          "Find the height where Ward merge cost exceeds a variance budget.",
          "Compare that cut against cut-by-k.",
          "Check whether the resulting clusters agree."],
         "Two cut strategies compared with an agreement metric."),
        ("Stability under resampling",
         "The only real validation available without labels.",
         ["Bootstrap the data 20 times; recluster each sample.",
          "Match clusters across runs by maximum overlap (Hungarian-style greedy).",
          "Report the adjusted Rand index per pair.",
          "Conclude whether the segmentation is stable."],
         "An ARI distribution and a stability verdict."),
        ("Outlier detection from cluster geometry",
         "Use the clustering to find rows worth inspecting.",
         ["Compute each point's distance to its centroid.",
          "Flag points beyond the 99th percentile.",
          "Inspect the flagged rows for data-quality problems.",
          "Compare flags against a rule-based range check."],
         "A flagged-row table and a note on whether they are bugs or genuine rare cases."),
        ("k-means++ versus random seeding",
         "Quantify the initialisation effect.",
         ["Run 100 single-restart fits with random seeding.",
          "Run 100 single-restart fits with k-means++.",
          "Compare worst-case and mean final inertia.",
          "Compute the effective restart count needed."],
         "A distribution comparison with a recommendation."),
        ("Ship a segment service",
         "Serve cluster assignments with an explanation payload.",
         ["Serialise centroids and the scaler.",
          "Serve POST /segment returning cluster id, distance to centroid and the top distinguishing features.",
          "Assert assignments match offline.",
          "Log cluster population per day for drift."],
         "A running endpoint and a population-by-day chart."),
    ],
    quiz=[
        ("Why can k-means not find crescent-shaped clusters?", ["It is too slow", "Voronoi cells are convex", "It requires scaling", "It minimises a linear objective"], 1, "Assignment regions are convex, so non-convex shapes cannot be recovered."),
        ("What does k-means++ improve?", ["Convergence speed only", "The probability of reaching a good local optimum", "Memory usage", "Cluster interpretability"], 1, "Distance-weighted seeding avoids several centroids landing in the same cluster."),
        ("Inertia always...", ["Increases with k", "Decreases with k", "Stays constant", "Is undefined for k > n"], 1, "More clusters always fit better, which is why inertia cannot select k by itself."),
        ("A silhouette of 0.7 with cluster sizes 9,900 and 100 means...", ["Excellent segmentation", "The score hides a possible singleton and needs the size distribution", "k should be doubled", "Features must be scaled"], 1, "Report sizes alongside the average; large clusters dominate the mean."),
        ("Which linkage is most prone to chaining?", ["Ward", "Complete", "Single", "Average"], 2, "Single linkage merges via the single closest pair, so a chain of near neighbours joins distant clusters."),
        ("Why standardise before clustering?", ["It makes k-means faster", "Otherwise the largest-variance axis defines the geometry", "It reduces the number of clusters", "It is required for Ward"], 1, "Distance-based methods inherit the units of the features."),
        ("Ward linkage minimises...", ["Maximum pairwise distance", "The increase in within-cluster variance", "Total pairwise distance", "Cluster count"], 1, "Its cost is |A||B|/(|A|+|B|) ||mu_A - mu_B||\u00b2, the variance added by merging."),
        ("What is agglomerative clustering's memory limit?", ["O(n)", "O(n\u00b2) for the distance matrix", "O(n log n)", "No practical limit"], 1, "All pairwise distances must be held, so 8n\u00b2 bytes bounds n at a few tens of thousands."),
        ("Silhouette assumes clusters are...", ["Uniformly distributed in density", "Spherical and similarly sized", "Linearly separable", "Gaussian with equal covariance"], 1, "It is a convexity and separation measure, so it inherits those assumptions."),
        ("How do you validate clusters with no labels?", ["Trust the silhouette", "Stability under resampling plus external outcome correlation", "Pick the smallest k", "Look at the inertia curve"], 1, "Stability and external validation are the only honest options."),
        ("Lloyd's algorithm is best described as...", ["Gradient descent", "Hard-assignment EM", "Newton's method", "Genetic search"], 1, "EM for spherical equal-variance Gaussians with responsibilities fixed to 0/1."),
        ("What does an uneven cluster size distribution suggest?", ["A good model", "A scaling or initialisation problem worth investigating", "Perfect separation", "The data is normal"], 1, "One cluster absorbing almost everything usually signals a feature-scale or seeding problem."),
        ("A dendrogram cut at a fixed height is...", ["Always optimal", "A variance-budget decision under Ward linkage", "Guaranteed stable", "Equivalent to choosing k"], 1, "Ward heights are variance increases, so the height choice is a budget."),
        ("Which is the best use of clustering in a production system?", ["Replacing labelled models everywhere", "Exploratory segmentation and outlier detection", "Automatically creating training labels", "Reducing model latency"], 1, "Clusters are hypotheses; using them as ground truth is circular."),
    ],
    vision=dict(
        future="Clustering fragments into three live uses: unsupervised exploration, "
               "outlier and novelty detection, and embedding-space segmentation for "
               "retrieval systems. The centre of gravity is away from 'find k "
               "clusters' toward density-aware and embedding-based methods that "
               "admit non-convex structure.",
        good=[
            "k is chosen with a written reason combining an internal metric and a business constraint.",
            "Cluster size distributions and stability are reported with every segmentation.",
            "Features are scaled inside the pipeline and the decision is recorded.",
            "Clusters are treated as hypotheses until an external outcome validates them.",
        ],
        ladder=[
            ("L1", "Segment", "Run k-means, print inertia and sizes, describe the clusters."),
            ("L2", "Choose k honestly", "Elbow plus silhouette plus sizes, with the reasoning written down."),
            ("L3", "Test stability", "Resample, recluster, report adjusted Rand index across runs."),
            ("L4", "Operate it", "Track population drift, flag outlier rows, and version the segmentation."),
        ],
        behaviors="Print the sizes before the score. Treat k-means as a first pass, "
                  "not a verdict. Validate against something outside the data before "
                  "anyone builds a campaign on your segments.",
        anti=[
            "Naming clusters from a two-line k-means run and shipping a campaign.",
            "Clustering unscaled features and calling the result a customer taxonomy.",
            "Reporting a silhouette without the size distribution.",
            "Using clusters as pseudo-labels and then 'validating' with a model trained on them.",
        ],
        trends=[
            "Density-based methods (HDBSCAN, UMAP-based density) for irregular shapes and noise.",
            "Embedding-space clustering where a neural encoder supplies the geometry.",
            "Concept drift in segmentation becoming a first-class monitoring signal.",
            "Cluster-based sampling for active labelling and rare-case discovery.",
        ],
        d30="Implement k-means with k-means++ and multiple restarts; verify on 3 blobs.",
        d60="Implement all four linkages and produce dendrograms you can read.",
        d90="Build a stability harness with adjusted Rand index and serve a segment endpoint with drift tracking.",
        metrics=[
            "I can state my k choice and defend it in writing.",
            "I always print cluster sizes next to a quality score.",
            "I can measure stability across resamples.",
            "I know which algorithm to switch to when k-means fails.",
        ],
        closer="Clustering produces the questions; only validation produces the "
               "decisions.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Customer Segmentation with a Stability Report",
        brief="Segment customers with k-means and agglomerative clustering, choose k "
              "with evidence, prove the segmentation is stable, and serve it.",
        timebox="3\u20134 hours",
        why="Segmentation projects fail at the validation step. This one forces "
            "stability, size distributions and an external-outcome check before any "
            "segment gets a name.",
        requirements=[
            "Load a customer dataset (RFM-style or the Online Retail dataset) or synthesise one with realistic structure.",
            "Standardise features inside the pipeline; log the scaler statistics.",
            "Run k-means for k = 2..10 with 10 restarts; plot inertia and mean silhouette; print size distributions.",
            "Run agglomerative with Ward; cut it at a variance budget and compare to the k-means cut with adjusted Rand index.",
            "Bootstrap 20 times; report the ARI distribution as a stability measure.",
            "Validate against an external outcome (spend or churn) and name the segments only if they differ on it.",
            "Serve POST /segment returning cluster id, distance to centroid and population drift per day.",
        ],
        steps=[
            ("1", "25m", "Load data, engineer 2-4 features, standardise inside the estimator", "A documented feature pipeline"),
            ("2", "30m", "k-means sweep with 10 restarts; inertia and silhouette curves", "Two curves plus size distributions"),
            ("3", "25m", "Agglomerative Ward; cut by variance budget", "A dendrogram and a cut height"),
            ("4", "20m", "ARI between the two segmentations", "An agreement number"),
            ("5", "30m", "Bootstrap stability: 20 resamples, ARI distribution", "A stability verdict"),
            ("6", "25m", "External-outcome validation by cluster", "A table of spend/churn per segment"),
            ("7", "25m", "Segment endpoint with population drift tracking", "A working endpoint and a drift chart"),
        ],
        diagram="""customers --> features (recency, frequency, value, tenure)
                        |
                   Standardiser (in-pipeline)
                        |
     +------------------+------------------+
     |                  |                  |
   k-means            Ward cut          sizes + drift
   (10 restarts)      (variance budget)      |
     |                  |                  |
     +--------+---------+---------+---------+
                              |
        ARI agreement | bootstrap ARI | external outcome table
                              |
                    POST /segment (id, distance, top features)""",
        notes=[
            "If your segments do not differ on an external outcome, stop: you have found geometry, not customers.",
            "ARI is the right agreement metric because it is invariant to cluster label permutations.",
            "A 9,000-vs-100 split is a modelling problem, not a segment \u2014 investigate before naming.",
            "Population drift per day is the first production question; build it in from the start.",
        ],
        deliverables=[
            "One-command run producing curves, sizes, ARI agreement and stability.",
            "Dendrogram with the chosen cut height marked.",
            "External-outcome validation table.",
            "Segment endpoint plus a population-by-day drift chart.",
        ],
        grading=[
            ("Correctness", "30%", "Algorithms verified; scaling in-pipeline; ARI implemented correctly"),
            ("k selection", "20%", "Curves, sizes and a written justification"),
            ("Validation", "25%", "Stability plus external-outcome evidence"),
            ("Engineering", "15%", "Deterministic, endpoint works, drift tracked"),
            ("Communication", "10%", "Segments named only where evidence supports it"),
        ],
        stretch=[
            "Add DBSCAN to capture a crescent-shaped segment and compare segment shapes.",
            "Replace the hand-chosen features with a PCA-whitened space and see if segmentation changes.",
            "Build an active-labelling queue that picks the most informative boundary rows.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Retail Customer Segmentation Service",
        scenario="A 2.4M-customer retailer needs segments that marketing campaigns "
                 "actually use, refreshed weekly, stable enough that a campaign "
                 "measured over six weeks still refers to the same population. You "
                 "own the segmentation and the drift alarm.",
        scale=[
            ("Population", "2.4M active customers, 900k with a purchase in the last 90 days"),
            ("Refresh cadence", "weekly full re-segmentation; daily incremental scoring"),
            ("Consumers", "6 campaign tools, CRM, warehouse audiences, finance reporting"),
            ("Serving SLO", "p99 lookup < 60 ms; weekly job done before Monday 06:00"),
            ("Contract", "Segments must be reconcilable month over month for campaign ROI"),
        ],
        diagram=""" CRM + orders + web events --> warehouse (daily)
                                        |
                             weekly feature build (RFM + category mix)
                                        |
                    +-------------------+-------------------+
                    |                                       |
          full re-segmentation (k-means,          stability check (ARI vs
          10 restarts, k chosen + versioned)      last week's labels)
                    |                                       |
                    +-------------------+-------------------+
                                        |
                              segment registry (versioned)
                                        |
              +-------------------+------+------+-------------------+
              |                       |                     |
         campaign tools            CRM UI               warehouse audiences
      (segment + size in payload)  (daily lookup)        (Parquet export)

   Monitoring: population drift per segment, PSI on features, job freshness""",
        components=[
            ("Feature build",
             ["RFM features plus category-mix entropy, all computed from a frozen window definition",
              "Features standardised with statistics stored alongside the version, not recomputed downstream",
              "Zero-activity customers handled explicitly rather than by imputation guesswork",
              "Feature snapshot ID attached to every assignment so it is replayable"]),
            ("Segmentation and registry",
             ["k-means with 10 restarts; k chosen once and versioned with a written justification",
              "Stability gate: adjusted Rand index against last week's labels above a threshold, else investigate",
              "Segment ID and description in a registry, with the run that produced it",
              "Non-parametric labels for stability (0 = most stable week in the last 12)"]),
            ("Serving and consumption",
             ["Lookup service serving customer to segment with the version, p99 under 60 ms",
              "Campaign tools receive segment plus size so a stale audience is visible at send time",
              "Warehouse Parquet export for analysts, partitioned by snapshot date",
              "No consumer may join on a segment ID without the version"]),
            ("Drift and operations",
             ["Weekly population share per segment; alert on a shift beyond 5 points",
              "PSI on the RFM features to catch upstream data problems",
              "Job freshness SLO with a fallback to the previous week's segmentation",
              "Reconciliation report so finance can tie campaign ROI to segment version"]),
        ],
        timeline=[
            ("Week 1", "Ship descriptive stats and a fixed-size quartile baseline so every later claim has a reference"),
            ("Week 2", "Feature build with frozen window definitions and snapshot versioning"),
            ("Week 3", "Weekly segmentation job with the stability gate; run three weeks before trusting it"),
            ("Week 4", "Registry, lookup service, Parquet export; migrate one campaign tool"),
            ("Week 5", "All campaign tools migrated; drift alerts live; rollback drill documented and timed"),
        ],
        runbook=[
            "# Which segmentation is live, and how fresh is it?",
            "curl -s localhost:8080/admin/segmentation | jq '{version,builtAt,rows,freshnessHours}'",
            "",
            "# Population share per segment vs last week",
            "curl -s 'localhost:8080/admin/populations?window=2w' | jq '.segments,.delta'",
            "",
            "# Feature PSI since the last snapshot",
            "curl -s 'localhost:8080/admin/drift?feature=recency' | jq '.psi,.threshold'",
            "",
            "# Roll back to the previous week's segmentation",
            "curl -XPOST localhost:8080/admin/segmentation/rollback -d '{\"to\":\"seg-2026-09-21\"}'",
            "",
            "# Reconcile one campaign's audience size against the registry",
            "curl -s 'localhost:8080/admin/audience?campaignId=c-8842' | jq '.segment,.size,.version'",
        ],
        metrics=[
            "SLO: weekly job completes before Monday 06:00; lookup p99 < 60 ms; availability 99.9%.",
            "Stability: adjusted Rand index against the previous week, monitored as a distribution not a single value.",
            "Business: campaign lift and ROI per segment, reported with the segment version attached.",
            "Drift: population share shift per segment; feature PSI with an alert threshold of 0.2.",
            "Consumption: number of consumers still joining without a version (target zero).",
        ],
        failures=[
            ("Weekly job misses the Monday deadline", "Feature build slowed by an upstream schema change", "Serve the previous week's segmentation with a stale banner; page the data owner"),
            ("Segment population share shifts by 20%", "A large acquisition campaign or a returns-driven feature change", "Investigate feature PSI before re-clustering; do not silently re-cut k"),
            ("Stability gate fails two weeks running", "Data quality change rather than real drift", "Freeze the segmentation version, escalate to data engineering, keep serving the last good one"),
            ("Campaign audience size disagrees with the registry", "A consumer joined without the version column", "Block the export without a version; this is a contract failure, not a dashboard bug"),
            ("Lookup p99 breaches 60 ms", "Cache miss storm after a snapshot swap", "Pre-warm the cache before publishing the new version"),
        ],
        backlog=[
            "Automated stability report including per-segment member overlap with the prior week.",
            "Cluster-in-cluster monitoring so a segment that fragments is detected before campaigns notice.",
            "Incremental daily assignment instead of full weekly re-segmentation.",
            "Timed rollback drill each quarter with the result published to the marketing team.",
        ],
        urls=URLS_ML,
        closer="The deliverable is a segmentation that means the same population "
               "for six weeks, is versioned, is reconciled by finance, and pages you "
               "before a campaign notices.",
    ),
))

# ---------------------------------------------------------------- lab08
SPECS.append(dict(
    track="ml", lab="lab08", full_set=True, level="Intermediate",
    title="Principal Component Analysis", main_class="com.ml.lab08.Main",
    problem="You have more features than you can reason about, some of them "
            "correlated, and you need fewer dimensions without losing the variance "
            "that matters.",
    why_now="PCA is the preprocessing step that unblocks other algorithms: it "
             "regularises collinearity, decorrelates for neural networks, and "
             "compresses for serving.",
    objectives=[
        "Derive PCA as the projection that maximises variance",
        "Implement PCA via eigendecomposition of the covariance matrix and via SVD of the centred data",
        "Compute explained variance ratio and choose k with a cumulative-variance target",
        "Interpret loadings correctly and distinguish them from feature importance",
        "Explain when PCA hurts: sparse data, categorical features, interpretability needs",
        "Use PCA as a preprocessing step and justify the fit on training data only",
    ],
    concepts=[
        ("PCA as maximum-variance projection",
         "PCA finds the orthogonal direction along which the data varies most, then "
         "removes it and repeats. The directions are the eigenvectors of the "
         "covariance matrix, sorted by eigenvalue. No labels are used, so PCA is "
         "unsupervised \u2014 and can happily preserve variance you do not care about."),
        ("Two routes to the same answer",
         "Eigendecomposition of the covariance matrix works for small p; SVD of the "
         "centred data matrix is numerically superior and works for large p, because "
         "you never form p\u00d7p. The singular values relate to eigenvalues by "
         "\u03bb\u1d62 = s\u1d62\u00b2/(n\u22121). Both give identical components up to sign."),
        ("Explained variance and choosing k",
         "Explained variance ratio is \u03bb\u1d62/\u03a3\u03bb. Cumulative explained variance answers "
         "'how many components to keep' \u2014 but the 95% threshold is a convention, not "
         "a law. Better: fit k components, then choose k by downstream validation "
         "error or reconstruction error."),
        ("Loadings, scores and interpretation",
         "Loadings are the eigenvectors (the directions in feature space). Scores are "
         "the projected data. Loadings are not importance: a small-loading feature "
         "can be decisive in combination. With correlated features, individual "
         "loadings are unstable even when components are stable \u2014 the component "
         "is the interpretable unit, not the coefficient."),
        ("Standardise or not",
         "Unscaled PCA finds directions of maximum total variance, so a feature in "
         "cents dominates. Standardised PCA finds directions of maximum correlation "
         "structure, which is usually what you want when features are on different "
         "scales. The choice must be stated, because it changes the answer."),
        ("When PCA is the wrong tool",
         "Sparse text destroys variance-based structure \u2014 use truncated SVD on "
         "term counts instead. Categorical encodings have no meaningful variance. "
         "Interpretability-critical models should keep their features. And any "
         "supervised goal is better served by a supervised projection."),
    ],
    formulas=[
        ("\u03a3 = (1/(n\u22121)) X\u1d40X (centred X)", "Sample covariance", "the matrix whose eigenvectors we want"),
        ("\u03a3v\u1d62 = \u03bb\u1d62v\u1d62", "Eigenproblem", "directions and their variance"),
        ("EV ratio = \u03bb\u1d62 / \u03a3\u1d62\u03bb\u1d62", "Explained variance ratio", "share of variance per component"),
        ("z\u1d62 = (x\u1d62 \u2212 \u03bc) W\u2096", "Projection", "score in the new basis"),
        ("x\u0302 = \u03bc + z W\u2096\u1d40", "Reconstruction", "rank-k approximation of X"),
        ("\u03bb\u1d62 = s\u1d62\u00b2 / (n\u22121)", "Singular-value link", "why SVD avoids forming \u03a3"),
        ("total variance = \u03a3\u1d62 var(x\u1d62)", "Trace relation", "explained ratios must sum to 1"),
    ],
    flow=[
        "Decide whether to standardise: yes if units differ, no if they are comparable and total variance is meaningful.",
        "Centre the data (mean subtract). PCA does not centre for you.",
        "Decompose: eigendecomposition of the covariance matrix for small p, SVD of the centred matrix otherwise.",
        "Sort components by descending eigenvalue; check the eigenvalue spectrum for a natural elbow.",
        "Choose k from a cumulative-variance target or, better, from downstream validation error.",
        "Store the scaler, the mean vector and the component matrix together \u2014 a transform is not just a matrix.",
    ],
    assumptions=[
        "Variance is the structure worth preserving; if the target matters, PCA is unsupervised and blind to it",
        "Linear relationships \u2014 PCA finds linear subspace structure only",
        "Features are numeric and (after optional scaling) comparable",
        "Outliers have not been allowed to dominate the covariance",
        "The dominant variance directions are the directions you want to keep",
        "The transformation is fit on training data and applied unchanged to serving data",
    ],
    pitfalls=[
        ("All the variance ends up in one component", "features on wildly different scales", "standardise before fitting"),
        ("Test-time scores look nothing like training", "PCA refit on the full dataset or on serving data", "fit once on the training fold and serialise mean + components"),
        ("k chosen by the 95% rule and downstream accuracy drops", "retained variance is not the same as useful variance", "choose k by validation error, not by cumulative variance"),
        ("Loadings say feature 7 dominates", "correlated features split the weight unpredictably", "interpret the component, and use permutation importance for the model"),
        ("Text classification gets worse after PCA", "truncated SVD, not PCA, is right for sparse counts", "use latent semantic indexing / TruncatedSVD on the sparse matrix"),
        ("Components flip sign between runs", "sign is arbitrary in eigendecomposition", "fix the sign convention (largest-magnitude loading positive) and serialise it"),
    ],
    java=[
        ("Eigenvalue decomposition (QR iteration)", "the didactic route for small p, plus a symmetric-matrix solver"),
        ("Jacobi eigenvalue algorithm", "simple, stable for real symmetric matrices like covariance"),
        ("Arrays.sort on eigenvalues with paired index sort", "keeping eigenvalues and eigenvectors aligned is the classic bug"),
        ("DoubleSummaryStatistics", "streaming mean and variance for the centring step"),
        ("record PcaModel(double[] mean, double[][] components, double[] eigenvalues)", "the transform plus its metadata, in one serialisable unit"),
    ],
    links=[
        "**Lab 01** benefits directly: PCA removes the collinearity that inflates OLS standard errors.",
        "**Lab 05** benefits most: it mitigates the curse of dimensionality.",
        "**Lab 03** is a warning \u2014 PCA is rotation-sensitive in the wrong way for trees.",
        "**Lab 07** uses PCA as preprocessing when clusters are not spherical.",
    ],
    checklist=[
        "I can derive PCA from the variance-maximisation constraint",
        "I know when to standardise and can justify the choice",
        "I choose k from validation error, not only from cumulative variance",
        "I can explain loadings versus importance",
        "I know PCA is blind to the target",
        "My transform artifact contains mean, scale and components together",
    ],
    cards=[
        ("What does PCA maximise?", "The variance of the projected data along each successive orthogonal direction."),
        ("Do you need to centre the data before PCA?", "Yes. Without centring the first component points at the mean direction, which is meaningless."),
        ("When should you standardise before PCA?", "When features have different units or materially different variances; otherwise total variance rather than structure is maximised."),
        ("Eigenvalue to explained variance ratio?", "\u03bb\u1d62 / sum(\u03bb), the share of total variance captured by component i."),
        ("Is the sign of a component meaningful?", "No. The eigenvector and its negation are equally valid; fix the convention so runs are reproducible."),
        ("Why is SVD numerically better than eigendecomposition?", "It works on the data matrix directly, never forms the covariance matrix, so its condition number is not squared."),
        ("What is a loading?", "The eigenvector coordinates \u2014 the direction of the component in original feature space. Not the same as feature importance."),
        ("Why does PCA sometimes hurt classification?", "It preserves variance, not class signal; with correlated features the useful direction may have low variance."),
    ],
    extra_cards=[
        ("What is TruncatedSVD and when do I use it?", "A sparse-friendly factorisation that does not centre; it is the right tool for sparse term-count matrices."),
        ("How do I pick k in practice?", "Sweep k and choose by downstream cross-validated performance, using cumulative variance only as a starting point."),
        ("Can PCA be inverted exactly?", "Only for a full-rank projection. A rank-k projection is lossy by construction."),
        ("How do I detect that PCA is a bad idea here?", "Sparse data, categorical features, tiny n relative to p, or a requirement for per-feature interpretability."),
    ],
    math_why="PCA is one Lagrange multiplier and a symmetric eigenproblem. Once "
             "you see that maximising projection variance under a unit-norm "
             "constraint gives the eigenvectors of the covariance matrix, everything "
             "\u2014 reconstruction, explained variance, the SVD equivalence \u2014 follows.",
    math=[
        ("Variance maximisation as an eigenproblem",
         "max_w Var(w'x) = w' S w  s.t.  w'w = 1\nLagrangian: S w - lambda w = 0\n=> w = eigenvector of S with the largest eigenvalue",
         "One constraint turns a quadratic optimisation into an eigenproblem. The "
         "optimum is a unit vector because the objective is homogeneous of degree "
         "two, so without the constraint it is unbounded.",
         "A 2D dataset with S = [[3, 2], [2, 3]] has eigenvalues 5 and 1 with "
         "eigenvectors (1,1)/\u221a2 and (1,\u22121)/\u221a2. PC1 keeps 5/6 = 83% of variance."),
        ("Explained variance and the cumulative curve",
         "explained_i = lambda_i / trace(S)\ntrace(S) = sum_j var(x_j)\ncumulative_k = sum_{i<=k} lambda_i / trace(S)",
         "The trace is total variance, so the ratios must sum to 1. A steep drop "
         "followed by a flat tail is the natural place to cut; the 95% convention is "
         "a starting point, not a decision.",
         "Eigenvalues 5.0, 1.0, 0.5, 0.3, 0.2 total 7.0. k = 2 keeps 85.7%, k = 3 "
         "keeps 92.9%, k = 4 keeps 97.1%."),
        ("Eigen-decomposition versus SVD",
         "X_c = X - 1 mu'  (centred)\nS = X_c' X_c / (n-1)\nSVD: X_c = U S V'  =>  lambda_i = s_i^2 / (n-1)\ncomponents W = V",
         "SVD avoids forming the p\u00d7p covariance matrix, so the conditioning cost "
         "of squaring is not paid. The eigenvalues of the covariance are the squared "
         "singular values, scaled.",
         "p = 50,000 features: forming X\u1d40X needs 20 GB and squares the condition "
         "number. Truncated SVD on X_c needs O(p\u00b7k) and never forms it."),
        ("Reconstruction error from the spectrum",
         "||X_c - Z_k W_k'||_F^2 = sum_{i>k} s_i^2\nrelative error = 1 - cumulative_k",
         "Because the components are orthogonal, the discarded variance is exactly "
         "the sum of the dropped eigenvalues. That makes k selection a pure "
         "trade-off curve with no fitting required.",
         "Dropping a component with eigenvalue 0.5 out of 7.0 total adds a relative "
         "error of 7.1% \u2014 visible, but often harmless if that direction is noise."),
        ("Whitening and why it changes distance geometry",
         "whitened = Z_k / s_i  (each component scaled to unit variance)\neigenvalues of Cov(whitened) = I",
         "Whitening removes all residual variance differences between components, so "
         "euclidean distance no longer favours high-variance directions. Useful for "
         "k-means and k-NN after PCA; usually harmful if you want to keep the "
         "importance structure.",
         "Components with s = 10 and s = 1 contribute 100:1 to unwhitened distance "
         "and 1:1 after whitening \u2014 a large change in which points look close."),
        ("Choosing k by downstream performance",
         "for k in 1..p_max:\n  Z_k = X_c W_k\n  score_k = cross_val_score(model, Z_k)\nchoose argmax_k score_k - lambda * k",
         "Retained variance is not usefulness. The right k is the one that maximises "
         "held-out performance of the model you actually care about, which can be "
         "far below the variance threshold.",
         "For a text classifier, k = 50 keeps 40% of variance but often beats k = 300 "
         "which keeps 95%, because the extra dimensions are noise."),
    ],
    math_traps=[
        "Forgetting to centre, which makes PC1 point at the mean vector.",
        "Sorting eigenvalues without permuting the eigenvectors with them.",
        "Assuming the eigenvector sign is meaningful.",
        "Dividing by n rather than n\u22121 in the covariance, biasing eigenvalues low.",
        "Treating cumulative explained variance as a decision rule rather than a diagnostic.",
    ],
    math_problems=[
        "Compute the covariance matrix and both eigenvalues by hand for the 2D example [[3,2],[2,3]].",
        "Derive the eigenvectors of the same matrix and verify S w = lambda w.",
        "Show that the reconstruction error equals the sum of dropped eigenvalues.",
        "Given eigenvalues 5.0, 1.0, 0.5, 0.3, 0.2, find k for 85%, 93% and 97% cumulative variance.",
        "Demonstrate that PCA on unscaled data collapses to the highest-variance axis for a 2D case.",
    ],
    tree="""src/com/ml/lab08/
  Main.java                driver: 4D data reduced to 2D, variance report
  Pca.java                 fit via covariance eigendecomposition, transform, inverseTransform
  SvdPca.java              same results via SVD of the centred matrix
  Eigen.java               Jacobi eigenvalue solver for real symmetric matrices
  VarianceReport.java      explained ratios, cumulative curve, reconstruction error""",
    tree_note="Eigen.java is a symmetric-matrix solver, not a general eigensolver. "
              "Keeping it symmetric-specialised removes an entire class of bugs and "
              "is stable for the small p where this route is appropriate.",
    types=[
        ("Pca", "mean, components, eigenvalues; fit/transform/inverseTransform"),
        ("SvdPca", "the numerically preferred path; cross-checked against Pca in tests"),
        ("Eigen", "Jacobi iteration returning eigenvalues and eigenvectors for a symmetric matrix"),
        ("VarianceReport", "explained ratios, cumulative curve, reconstruction error per k"),
    ],
    patterns=[
        ("Fit as a complete, serialisable transform",
         "Scaling, centring and the component matrix travel together. A PCA that "
         "ships as a bare matrix is a bug waiting for a unit mismatch.",
         """public record PcaModel(double[] featureMean, double[] featureScale,
                         double[][] components, double[] eigenvalues,
                         boolean standardised) {

    public double[][] transform(double[][] x) {
        int n = x.length, k = components.length;
        double[][] z = new double[n][k];
        for (int i = 0; i < n; i++) {
            for (int c = 0; c < k; c++) {
                double s = 0;
                for (int j = 0; j < components[c].length; j++) {
                    double v = standardised ? (x[i][j] - featureMean[j]) / featureScale[j]
                                             : (x[i][j] - featureMean[j]);
                    s += v * components[c][j];
                }
                z[i][c] = s;
            }
        }
        return z;
    }
}"""),
        ("Eigen-decomposition via the Jacobi method",
         "Jacobi rotations iteratively zero off-diagonal entries of a symmetric "
         "matrix, converging to eigenvalues on the diagonal and eigenvectors as "
         "columns of the rotation product.",
         """static Eigen decompose(double[][] a) {
    int n = a.length;
    double[][] m = deepCopy(a);              // working copy: never mutate the input
    double[][] v = identity(n);              // accumulates rotations into eigenvectors
    for (int sweep = 0; sweep < 50; sweep++) {
        double off = 0;
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) off += m[i][j] * m[i][j];
        if (off < 1e-20) break;              // converged: off-diagonal mass ~ 0
        for (int p = 0; p < n - 1; p++) {
            for (int q = p + 1; q < n; q++) {
                if (Math.abs(m[p][q]) < 1e-18) continue;
                double theta = (m[q][q] - m[p][p]) / (2 * m[p][q]);
                double t = Math.signum(theta) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
                double c = 1 / Math.sqrt(t * t + 1), s = t * c;   // stable rotation
                rotate(m, v, p, q, c, s);
            }
        }
    }
    double[] values = new double[n];
    for (int i = 0; i < n; i++) values[i] = m[i][i];            // eigenvalues
    sortDescendingKeepingColumns(values, v);                    // eigenvalues AND vectors
    fixSignConvention(v);                                       // reproducible sign
    return new Eigen(values, v);
}"""),
    ],
    costs=[
        ("Covariance construction", "O(np\u00b2)", "fine to p \u2248 1000"),
        ("Jacobi eigenvalue sweeps", "O(sweeps \u00b7 p\u00b3)", "typically 5\u201310 sweeps for a symmetric matrix"),
        ("Transformation of new data", "O(n\u00b7p\u00b7k)", "k = retained components"),
        ("Truncated SVD instead", "O(np\u00b7k)", "the route to use when p is large"),
    ],
    numerics=[
        "Always centre; make it part of fit so callers cannot forget.",
        "Sort eigenvalues and permute eigenvector columns together \u2014 a classic silent bug.",
        "Fix the sign convention so two runs produce byte-identical models.",
        "Use (n\u22121) in the covariance, and never form X\u1d40X when p is large.",
        "Assert the explained ratios sum to 1 within 1e-9; it catches most implementation errors.",
    ],
    tests=[
        "Explained variance ratios sum to 1 \u00b1 1e-9.",
        "Pca and SvdPca agree on components up to sign within 1e-8.",
        "Two runs produce byte-identical component matrices (sign convention holds).",
        "Transform then inverseTransform reconstructs to within 1e-8 when k = p.",
        "Truncating to k components gives a reconstruction error matching 1 - cumulative_k.",
        "A dataset with one dominant axis puts PC1 on that axis when not standardised.",
    ],
    extensions=[
        "Implement truncated SVD on a sparse matrix and compare with covariance PCA.",
        "Add whitening and show the effect on k-means cluster shapes.",
        "Implement incremental PCA (online updating) for streaming features.",
    ],
    code_checklist=[
        "Centring is inside fit, not the caller's responsibility",
        "Standardisation is an explicit, recorded flag",
        "Eigenvalue/vector pairs are permuted together",
        "Sign convention fixed and asserted in a test",
        "Mean, scale and components serialised as one unit",
        "k chosen with downstream validation, not only cumulative variance",
    ],
    exercise_selfcheck=[
        "I can derive PCA from the constrained optimisation",
        "I can justify standardising (or not) for my data",
        "I chose k with evidence beyond a variance threshold",
        "My transform artifact is complete and self-consistent",
    ],
    exercises=[
        ("Derive and implement PCA by eigendecomposition",
         "Build the covariance matrix and solve the symmetric eigenproblem.",
         ["Centre and standardise a 4-feature dataset.",
          "Build the covariance matrix and run Jacobi.",
          "Sort descending and fix the sign convention.",
          "Project to 2 components and reconstruct; report the error."],
         "A PCA implementation plus a reconstruction error matching 1 - cumulative k."),
        ("Eigen versus SVD must agree",
         "Two routes, one answer \u2014 this is the numerics lesson.",
         ["Implement truncated SVD of the centred matrix.",
          "Relate singular values to eigenvalues via lambda = s\u00b2/(n-1).",
          "Assert components agree up to sign within 1e-8.",
          "Explain why SVD is preferable at large p."],
         "A passing cross-check test and a written numerical argument."),
        ("Choosing k honestly",
         "Beat the 95% convention with evidence.",
         ["Sweep k = 1..p and record cumulative variance.",
          "Train a downstream model per k; cross-validate.",
          "Plot validation error against k.",
          "Choose k from the curve and explain where it sits versus the variance rule."],
         "Two curves and a k chosen from the downstream one."),
        ("Loadings versus importance",
         "Show why PCA coefficients are not feature importance.",
         ["Fit PCA on data with two strongly correlated features.",
          "Compare loadings against a tree's permutation importance.",
          "Show loadings are unstable across bootstrap samples while components are stable.",
          "Explain what the component, not the coefficient, means."],
         "A comparison table plus a written interpretation rule."),
        ("Whitening for clustering",
         "Fix non-spherical clusters with a linear transform.",
         ["Generate three clusters with different variances.",
          "Cluster raw: report silhouette.",
          "Apply PCA then whitening; re-cluster.",
          "Report the silhouette change and why."],
         "Before/after silhouettes with a written explanation."),
        ("Sparsity stress test",
         "See where covariance PCA fails and TruncatedSVD wins.",
         ["Build a sparse term-count matrix.",
          "Apply PCA with explicit densification; measure cost.",
          "Apply truncated SVD without centring; measure cost and quality.",
          "Recommend one for text."],
         "A cost comparison and a written recommendation."),
        ("PCA as leakage canary",
         "Prove that fitting PCA on everything leaks.",
         ["Run a pipeline with in-fold versus full-dataset PCA.",
          "Compare cross-validated scores.",
          "Quantify the optimism.",
          "Add a test asserting PCA is fit inside the fold."],
         "A quantified optimism number and a regression test."),
        ("Ship a compression transform",
         "Reduce serving payload while monitoring the loss.",
         ["Serialise the PcaModel to a compact text format; reload it.",
          "Assert reload reproduces predictions exactly.",
          "Report compression ratio and downstream error delta on a test set.",
          "Add a drift check comparing incoming variance to the fitted spectrum."],
         "A working loader, a parity test and a drift check."),
    ],
    quiz=[
        ("What does the first principal component maximise?", ["The mean of the features", "The variance of the projected data", "The number of features", "The correlation with the target"], 1, "It is the direction of maximum variance in the centred data."),
        ("Why must data be centred before PCA?", ["To avoid negative eigenvalues", "Otherwise the first component points at the mean direction", "To speed up the eigen solver", "It does not matter"], 1, "Without centring, PC1 captures the offset rather than the structure."),
        ("When should features be standardised first?", ["Never", "When units or variances differ materially", "Only for tree models", "Only when p is small"], 1, "Otherwise total variance rather than correlation structure is maximised."),
        ("Explained variance ratio for component i is...", ["lambda_i / p", "lambda_i / sum(lambda)", "sqrt(lambda_i)", "cumulative variance"], 1, "It is the share of total variance (the trace of the covariance) held by that component."),
        ("Is the sign of a principal component meaningful?", ["Yes, positive means better", "No, it is arbitrary", "Only for PC1", "Only after whitening"], 1, "Eigenvectors are defined up to sign, so fix a convention for reproducibility."),
        ("Why prefer SVD over eigendecomposition?", ["It is exact", "It never forms the covariance matrix, avoiding squared conditioning", "It uses labels", "It handles categoricals"], 1, "Working on X directly avoids the p\u00d7p matrix and its squared condition number."),
        ("Loading versus feature importance", ["They are identical", "A loading is a direction coefficient, not a contribution measure", "Loadings require labels", "Importance requires scaling"], 1, "Importance asks what the model uses; a loading asks where the component points."),
        ("When does PCA hurt a classifier?", ["When the data is small", "When high-variance directions are noise rather than signal", "Always", "Never with correlated features"], 1, "PCA is unsupervised, so it can preserve exactly the wrong variance."),
        ("Reconstruction error after dropping components equals...", ["The mean squared error", "The sum of the dropped eigenvalues", "The largest eigenvalue", "Zero"], 1, "Orthogonality makes the discarded energy exactly the sum of dropped eigenvalues."),
        ("PCA is unsupervised, so...", ["It cannot be used before supervised models", "It can preserve variance unrelated to the label", "It always improves accuracy", "It requires a target column"], 1, "That blindness is why k is best chosen by downstream validation."),
        ("What is TruncatedSVD used for?", ["Whitening", "Sparse matrices like term counts without centring", "Non-linear structure", "Classification directly"], 1, "Centring densifies a sparse matrix; truncated SVD avoids that entirely."),
        ("Why can PCA loadings be unstable?", ["Correlated features let the weight be split arbitrarily among them", "The solver is buggy", "Loadings depend on labels", "They are always stable"], 0, "The component is stable even though individual coefficients are not."),
        ("The 95% cumulative-variance rule is...", ["A mathematical law", "A convention and a poor substitute for validation", "Required by scikit-learn", "Optimal for classification"], 1, "It is a starting point; validation error should decide k."),
        ("Whitening does what?", ["Centres the data only", "Scales each component to unit variance", "Removes the mean", "Adds label information"], 1, "It removes residual variance differences, changing which points look close in distance."),
    ],
    vision=dict(
        future="PCA stays the default first move for linear preprocessing, but the "
               "frontier has moved to embeddings for non-linear structure and to "
               "supervised projections when the label matters. Its role shifts from "
               "'feature reduction' to 'conditioning for the next stage'.",
        good=[
            "The transform artifact contains mean, scale and components as one versioned unit.",
            "Scaling or not is an explicit, recorded decision.",
            "k is chosen by downstream validation, with cumulative variance as a diagnostic.",
            "Interpretations are stated at the component level when features are correlated.",
        ],
        ladder=[
            ("L1", "Reduce", "Fit PCA, keep 95%, plot the scores."),
            ("L2", "Decide correctly", "Justify scaling, choose k by validation, check the spectrum."),
            ("L3", "Condition", "Use PCA to fix collinearity or dimensionality for another model, and prove the gain."),
            ("L4", "Go beyond linear", "Compare against an embedding or a supervised projection on the same task."),
        ],
        behaviors="State the scaling decision before fitting. Choose k with a "
                  "validation curve. Treat components as the interpretable unit, not "
                  "coefficients.",
        anti=[
            "SVD because a tutorial said PCA, on a sparse count matrix.",
            "A PCA transform shipped without its mean and scale.",
            "k = 95% variance rule quoted as a decision.",
            "PCA loadings presented to a stakeholder as feature importance.",
        ],
        trends=[
            "Autoencoders and embedding models replacing PCA where structure is non-linear.",
            "Supervised dimensionality reduction when the label carries the signal.",
            "Incremental and randomised PCA for streaming and very wide data.",
            "Whitening and kernel PCA as preprocessing for k-means and k-NN in embedding spaces.",
        ],
        d30="Implement PCA by eigendecomposition and verify explained ratios sum to 1.",
        d60="Cross-check against SVD and explain the numerical difference.",
        d90="Choose k by downstream validation, compare with an embedding, and ship a versioned transform with a drift check.",
        metrics=[
            "I can derive PCA from the constrained optimisation.",
            "I justify the scaling decision explicitly.",
            "I choose k with a validation curve.",
            "My transform artifact is complete enough to reproduce scoring exactly.",
        ],
        closer="PCA is where you learn that retained variance and retained signal "
               "are different things \u2014 a lesson that outlasts the algorithm.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Dimensionality Reduction for a Credit Scorecard",
        brief="Reduce a correlated feature set, choose components with evidence, "
              "and ship a compression transform with a monitored spectrum.",
        timebox="3 hours",
        why="Credit modelling is full of near-duplicate features (income variants, "
            "debt ratios), so collinearity is real and PCA both diagnoses and fixes it.",
        requirements=[
            "Load a lending-style dataset (or synthesise correlated features deliberately).",
            "Standardise, fit PCA, and print the eigenvalue spectrum with a cumulative-variance curve.",
            "Sweep k and compare downstream logistic-regression validation error; choose k from that curve.",
            "Compare PCA features against the raw correlated features and against ridge; report all three.",
            "Interpret the top 3 components by loading pattern and write a paragraph each.",
            "Ship the transform with mean, scale and components; add a drift check comparing incoming variance to the fitted spectrum.",
        ],
        steps=[
            ("1", "25m", "Build the feature matrix with deliberately correlated columns; quantify VIF", "A collinearity report"),
            ("2", "25m", "Fit PCA; print eigenvalues, ratios and cumulative curve", "A spectrum table"),
            ("3", "30m", "Sweep k; cross-validated logistic regression per k", "A validation-error-vs-k curve"),
            ("4", "25m", "Compare raw, PCA and ridge on the same folds", "A three-row comparison table"),
            ("5", "25m", "Interpret the top 3 components from loadings", "Three written interpretations"),
            ("6", "25m", "Serialise the transform; verify prediction parity after reload", "A parity test"),
            ("7", "20m", "Add the spectrum drift check and a model card", "A monitoring stub and a card"),
        ],
        diagram="""applications.csv --> feature matrix (correlated)
                        |
        Standardiser (frozen in artifact)
                        |
   eigen-decomposition of covariance  |  SVD cross-check
                        |
   component scores --> logistic regression (k sweep)
                        |
   raw vs PCA vs ridge comparison
                        |
   serialised transform + spectrum drift check""",
        notes=[
            "If PCA and ridge perform identically, that is a finding: say so rather than shipping PCA for its own sake.",
            "Correlated features make individual loadings unstable; report component patterns, not a ranking of coefficients.",
            "The spectrum drift check catches a change in the input distribution that would silently invalidate the transform.",
            "Verify parity after reload: rounding in the serialised format has bitten everyone.",
        ],
        deliverables=[
            "One-command run producing the spectrum, k sweep and three-way comparison.",
            "Top-3 component interpretations in plain language.",
            "Serialised transform with a parity test.",
            "Model card including the collinearity finding and a retrain trigger.",
        ],
        grading=[
            ("Correctness", "30%", "PCA verified against SVD; scaling and centring inside the artifact"),
            ("k selection", "25%", "Downstream validation used, not the 95% convention"),
            ("Comparison", "20%", "Raw vs PCA vs ridge on identical folds"),
            ("Interpretation", "15%", "Component-level interpretation, honest about instability"),
            ("Communication", "10%", "Model card states the operational caveat"),
        ],
        stretch=[
            "Add whitening and report the effect on the downstream model's coefficient stability.",
            "Implement incremental PCA and update the transform weekly as data accrues.",
            "Compare against a supervised projection on the same folds and write the recommendation.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Feature Compression for a Real-Time Risk Service",
        scenario="A payments risk service scores authorisations in 8 ms from 480 "
                 "features, many of them near-duplicates accumulated over six years "
                 "of feature work. Latency budget is tight and the team wants "
                 "fewer, faster features without losing accuracy.",
        scale=[
            ("Feature count", "480 features, median 0.3 pairwise |correlation| above 0.8"),
            ("Latency budget", "p99 < 8 ms per authorisation, peak 4,200 auth/s"),
            ("Retrain cadence", "weekly challenger, monthly champion review"),
            ("Downstream model", "gradient-boosted trees today, a candidate linear model under evaluation"),
            ("Constraint", "explanations must remain attributable to business features for disputes"),
        ],
        diagram=""" feature store (480 cols, versioned)
                        |
              drift checks + correlation census
                        |
        +---------------+----------------+
        |                                |
   PCA transform (fit weekly,     keep-all baseline
   versioned, k from validation)
        |                                |
        +---------------+----------------+
                        |
            challenger scores 100% of traffic in shadow
                        |
        +---------------+----------------+
        |               |                |
    champion        explanation      warehouse copy
   (k components)   (map back to     (full features
                      features)        for analysis)

   Guardrails: parity test, spectrum drift alert, rollback to keep-all""",
        components=[
            ("Feature store and correlation census",
             ["480 versioned features with owners, freshness SLAs and a correlation census",
              "Near-duplicate groups identified and reported quarterly, independent of any model",
              "Null and staleness rates per feature, alerting when a feature silently dies",
              "Feature definition changes require a shadow window before enforcement"]),
            ("Transform tier",
             ["PCA fit weekly on a trailing window, frozen for the week's scoring",
              "Mean, scale and component matrix versioned as one artifact; parity asserted on load",
              "k selected from downstream validation, with the curve attached to the model record",
              "Spectrum drift check: incoming per-feature variance compared to the fitted spectrum"]),
            ("Scoring and shadow evaluation",
             ["Champion scores the k components; challenger scores full features",
              "Both evaluated on matured outcomes weekly; promotion requires parity or better",
              "Latency measured per path so the compression benefit is visible in p99",
              "Rollback to keep-all is one command and rehearsed quarterly"]),
            ("Explainability bridge",
             ["Component contributions mapped back to the original features for disputes",
              "Explanations phrased as feature contributions, not component coordinates",
              "Component-to-feature mapping versioned alongside the transform",
              "Dispute path tested end to end before the transform reaches champion"]),
        ],
        timeline=[
            ("Week 1", "Correlation census and the keep-all baseline; publish latency and accuracy together"),
            ("Week 2", "PCA challenger in shadow with parity tests and spectrum drift checks"),
            ("Week 3", "k sweep with validation curves; latency comparison per path"),
            ("Week 4", "Explainability bridge and a dispute dry run with the risk operations team"),
            ("Week 5", "Champion cutover at 10% then 100%; rollback drill timed and documented"),
        ],
        runbook=[
            "# Champion version, k, and transform age",
            "curl -s localhost:8080/admin/model | jq '{version,k,transformVersion,ageHours}'",
            "",
            "# Latency by path (champion components vs challenger full)",
            "curl -s 'localhost:8080/admin/latency?window=15m' | jq '.p50,.p95,.p99'",
            "",
            "# Spectrum drift: incoming vs fitted per-feature variance",
            "curl -s 'localhost:8080/admin/drift?spectrum=1' | jq '.features,.maxDelta,.threshold'",
            "",
            "# Roll back to the keep-all path",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"risk-gb-full-v14\"}'",
            "",
            "# Explain one decision in original feature terms",
            "curl -s 'localhost:8080/admin/explain?txnId=t-884213' | jq '.contributions,.features'",
        ],
        metrics=[
            "SLO: p99 authorisation scoring < 8 ms; availability 99.99%.",
            "Business: fraud loss basis points, measured against the pre-compression champion.",
            "Model: matured-outcome accuracy of champion versus challenger, weekly.",
            "Efficiency: p99 latency and p99 CPU per scoring path, before and after compression.",
            "Guardrails: parity test pass rate; spectrum drift alert volume; dispute explanation coverage.",
        ],
        failures=[
            ("Accuracy drops after the champion cutover", "k too small, or a correlated pair was informative", "Roll back to keep-all, re-sweep k on a longer window, re-promote only with parity evidence"),
            ("Spectrum drift alert fires on a subset of merchants", "A new integration changed feature semantics", "Freeze the transform, investigate per-feature variance, version the feature change"),
            ("p99 latency regresses after compression", "Transform applied on the request path without caching", "Precompute or cache; compression must not add per-request work"),
            ("Dispute cannot be explained in feature terms", "Mapping missing for a new component", "Block promotion until the mapping and dispute test exist"),
            ("Parity test fails intermittently", "Floating-point ordering difference after serialisation", "Round-trip test in CI; fix the serialisation precision, not the tolerance"),
        ],
        backlog=[
            "Automated near-duplicate feature detection with owner notification.",
            "Whitening experiment for the candidate linear model's coefficient stability.",
            "Component-to-feature explanation quality review with the disputes team each quarter.",
            "Incremental transform updates instead of full weekly refits.",
            "Documented rollback drill with measured detection-to-mitigation time.",
        ],
        urls=URLS_ML,
        closer="The deliverable is 8 ms scoring with parity against the full-feature "
               "path, explanations that a disputes team can read in business "
               "terms, and a rollback that has been rehearsed.",
    ),
))
