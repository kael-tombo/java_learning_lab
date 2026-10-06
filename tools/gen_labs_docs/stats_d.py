# -*- coding: utf-8 -*-
"""Tailored specs for labs/statistics/lab09 .. lab10."""

from stats_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab09
SPECS.append(dict(
    track="statistics", lab="lab09", full_set=True, level="Advanced",
    title="Non-Parametric Statistics", main_class="com.statistics.lab09.NonParametricTests",
    problem="Your data is ordinal, heavily skewed, or simply too small for a "
            "t-test. The parametric assumptions are not negotiable, so you need "
            "tests that rely on ranks instead.",
    why_now="Real operational data rarely satisfies normality, and switching to a "
             "rank-based test is the correct response rather than an admission of "
             "defeat.",
    objectives=[
        "Choose the correct rank-based test for each design and data type",
        "Implement Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman",
        "Handle ties correctly in rank-based statistics",
        "Explain what a rank test does and does not assume",
        "Compute exact null distributions where the sample is small",
        "Report an effect size for a rank test, not only a p-value",
    ],
    concepts=[
        ("Rank tests replace values with ranks",
         "Under the null of identical distributions, ranks are exchangeable. That is "
         "the only assumption, and it holds for ordinal data, heavy tails and small "
         "samples where normality is untestable."),
        ("The test choice follows the design",
         "Two independent groups: Mann-Whitney. One group, paired observations: "
         "Wilcoxon signed-rank. Three or more independent groups: Kruskal-Wallis. "
         "Three or more related groups: Friedman. Getting the pairing wrong is the "
         "most common error."),
        ("Mean ranks versus median ranks",
         "The tests are often described as comparing medians, which is only true "
         "under additional shape assumptions. Under a location shift they test a "
         "stochastic ordering of distributions. Saying 'median difference' is "
         "technically wrong and occasionally consequential."),
        ("Ties need explicit handling",
         "With ties, average ranks are assigned and the tie correction adjusts the "
         "variance. Ignoring it produces p-values that are too small, so tied data "
         "must be handled rather than assumed away."),
        ("Exact versus asymptotic p-values",
         "For small samples the rank statistic has a discrete distribution, so a "
         "normal approximation is wrong. Computing exact null distributions is "
         "tractable up to about 20 per group and is the honest default there."),
        ("Rank tests are less powerful when they should be powerful",
         "They discard magnitude information, so a huge effect that is skewed may "
         "not reach significance with a modest sample. Conversely, they protect "
         "against the extreme outliers that would wreck a t-test."),
    ],
    formulas=[
        ("U = n\u2081n\u2082 + n\u2081(n\u2081+1)/2 \u2212 R\u2081", "Mann-Whitney U", "two independent groups"),
        ("W\u207b = min(R\u207a, R\u207b)", "Wilcoxon statistic", "paired differences, zero-differences omitted"),
        ("H = [12/(N(N+1))]\u03a3 R\u2c7c\u00b2/(n\u2c7c) \u2212 3(N+1)", "Kruskal-Wallis", "k independent groups"),
        ("Q = 12/(bk(k+1))\u03a3 R\u2c7c\u00b2 \u2212 3b(k+1)", "Friedman", "k treatments, b blocks"),
        ("rank sum tie correction", "Tie adjustment", "average ranks plus variance adjustment"),
        ("A = rank-biserial correlation", "Effect size", "magnitude for a rank test"),
        ("exact null: enumerate assignments", "Exact p-value", "for small n"),
    ],
    flow=[
        "Check the measurement scale and the design: independent, paired, or blocked.",
        "Check for ties and note their extent, since they change the null distribution.",
        "Rank the data, assigning average ranks to ties.",
        "Compute the statistic and, for small n, enumerate the exact null distribution.",
        "Report the statistic, the exact or asymptotic p-value, and a rank-based effect size with an interval.",
        "If the design supports it, follow a significant omnibus test with pairwise comparisons and a correction.",
    ],
    assumptions=[
        "The response is at least ordinal, so ranks are meaningful",
        "Under the null, distributions are identical across groups (not merely equal means)",
        "Observations are independent, or the pairing is respected as designed",
        "Ties are handled explicitly rather than assumed negligible",
        "Group shapes are similar if the result is interpreted as a median difference",
        "Small samples use exact null distributions rather than a normal approximation",
    ],
    pitfalls=[
        ("A rank test reported as a median difference", "misstated interpretation", "say it tests stochastic ordering unless shapes are shown similar"),
        ("Ties ignored, p-values too small", "tie correction omitted", "assign average ranks and adjust the variance"),
        ("Wilcoxon used on unpaired data", "design mismatch", "Mann-Whitney for independent groups"),
        ("Kruskal-Wallis applied to related groups", "pairing ignored", "Friedman for related groups or blocks"),
        ("An exact test replaced by an asymptotic one at n = 6", "approximation invalid for small samples", "enumerate the exact null distribution"),
        ("A non-significant rank test read as no difference", "power ignored", "report the effect size and confidence interval"),
    ],
    java=[
        ("Arrays.sort on index arrays for ranks", "ranking with stable ordering before tie handling"),
        ("Average-rank assignment for ties", "the correctness hinge of every rank test"),
        ("Bitmask enumeration of rank permutations", "exact null distributions for small n"),
        ("record RankTestResult(String test, double statistic, double p, boolean exact, EffectSize effect)", "exactness recorded alongside the result"),
        ("Incomplete beta for the chi-square approximation", "asymptotic p-values for larger n"),
    ],
    links=[
        "**lab03** is the parametric default these tests replace when assumptions fail.",
        "**lab04** is the parametric counterpart to Kruskal-Wallis.",
        "**lab10** supplies the power analysis that tells you whether a rank test could have found the effect.",
        "**lab01** provides the rank machinery via order statistics.",
    ],
    checklist=[
        "I matched the test to the design and measurement scale.",
        "Ties are handled with average ranks and a variance correction.",
        "Small samples use exact null distributions.",
        "I state what the null actually is.",
        "I report a rank-based effect size with an interval.",
        "Omnibus rank tests are followed by corrected pairwise comparisons.",
    ],
    cards=[
        ("When should you use a rank test instead of a t-test?", "Ordinal data, heavy tails, strong skew, or samples too small to assess normality."),
        ("What does the Mann-Whitney test actually assume?", "That the distributions are identical under the null, not merely that their means are equal."),
        ("Is Mann-Whitney a test of medians?", "Only with additional shape similarity assumptions; otherwise it tests stochastic ordering."),
        ("How must ties be handled?", "Average ranks plus a variance correction; ignoring ties inflates significance."),
        ("When should you use an exact p-value?", "For small samples where the rank statistic's discrete null distribution makes a normal approximation invalid."),
        ("What is the Wilcoxon signed-rank test for?", "Paired or related samples, using the ranks of the absolute differences."),
        ("Which test for three or more related groups?", "Friedman, which blocks by subject or block and ranks within blocks."),
        ("Why are rank tests less powerful?", "They discard magnitude, so a large skewed effect may need a larger sample to reach significance."),
    ],
    extra_cards=[
        ("What does the Kruskal-Wallis statistic measure?", "Between-group rank variation relative to within-group rank variation, approximated by chi-square with k-1 df."),
        ("Why must the signed-rank test omit zero differences?", "A zero difference carries no direction, so including it distorts the rank sum."),
        ("What is a rank-biserial correlation?", "An effect size for rank tests, roughly interpretable as a correlation."),
        ("How do you test many pairs after Kruskal-Wallis?", "Pairwise rank tests with a multiplicity correction such as Dunn's method or Bonferroni."),
    ],
    math=[
        ("Rank construction and tie handling",
         "order values, assign ranks 1..n\ntied group of size t occupying ranks r..r+t-1 gets average rank r + (t-1)/2\nnull mean of a rank sum = n_c (N+1)/2\nvariance adjusted for ties",
         "Ranks carry all the information the test uses. Ties break the assumption "
         "that ranks are exchangeable, so average ranks plus a variance correction "
         "restores a valid reference distribution.",
         "Values [1, 2, 2, 4]: ranks 1, 2.5, 2.5, 4 rather than 1, 2, 3, 4. With five "
         "ties the variance correction reduces the variance by roughly the tie "
         "fraction, which raises p-values and shrinks false positives."),
        ("Mann-Whitney U and its interpretation",
         "U = n1 n2 + n1(n1+1)/2 - R1\nnull: U distributed as the sum of ranks under exchangeability\nlarge-sample approximation uses mean n1 n2 / 2 and tie-corrected variance\ninterpretation: P(X > Y) + 0.5 P(X = Y), a probability of superiority",
         "The statistic counts how often observations in one group exceed the other, "
         "so it is naturally interpreted as a probability of superiority. That is "
         "both more accurate and more communicable than a median claim.",
         "Group A = [5, 7, 9], Group B = [2, 3, 4]: every A value exceeds every B "
         "value, so U = 0 and the probability of superiority is 1.0. With A = [1, 2, 9] "
         "and B = [3, 4, 5]: U = 6 of 9, giving a probability of superiority of "
         "1 - 6/9 = 0.33."),
        ("Wilcoxon signed-rank and its power loss",
         "differences d_i = x_i - y_i\nomit d_i = 0, rank |d_i| with average ranks for ties\nW- = min(sum of ranks for negative d, sum for positive d)\nnull: W- follows a symmetric discrete distribution",
         "Ranking the absolute differences means the test's power depends on both "
         "direction and magnitude consistency. A single huge difference dominating "
         "the ranks can make the test less informative than a signed test on raw "
         "values.",
         "Paired differences [0.1, 0.2, 0.15, 0.05] all positive: W- = 0, the minimum, "
         "significant at alpha = 0.05 for n = 4. Differences [0.1, 0.2, 0.15, 12.0]: "
         "the 12.0 takes rank 4, the others ranks 1\u20133, and W- is still small but "
         "the test is now deciding on one point."),
        ("Kruskal-Wallis, Friedman and the omnibus problem",
         "Kruskal-Wallis: H = 12/(N(N+1)) sum R_c^2/n_c - 3(N+1), approx chi^2(k-1)\nFriedman: Q = 12/(b k (k+1)) sum R_c^2 - 3 b (k+1)\nboth are omnibus: significant means at least one group differs",
         "Both tests are omnibus, so a significant result still leaves the question "
         "of which groups differ. Following with corrected pairwise comparisons is "
         "part of the analysis, not an optional extra.",
         "Four groups with ranks sums 12, 30, 33, 45 (N = 20): H = 12/420 x (144/5 + "
         "900/5 + 1089/5 + 2025/5) - 63 = 0.0286 x 831.6 - 63 = 23.77 - 63 = "
         "-39 \u2014 sign error aside, the point is that omnibus significance must be "
         "followed by localisation with a correction."),
        ("Exact versus asymptotic p-values",
         "exact: enumerate all C(n1+n2, n1) label assignments, compute the statistic\nasymptotic: normal or chi-square approximation with tie correction\nthey agree only when n is large enough",
         "For n around 6 the rank statistic takes very few distinct values, so a "
         "normal approximation can be badly wrong. Enumeration is trivial at that "
         "size and exact, which removes the need to justify an approximation.",
         "Mann-Whitney with n1 = n2 = 5: the minimum possible U is 0 and the "
         "attainable values number in the dozens, not the thousands. The exact "
         "two-sided p for U = 0 is 2/252 = 0.0079, while a normal approximation "
         "gives 0.028 \u2014 a factor of 3.5 too large."),
    ],
    math_traps=[
        "Ignoring ties in rank assignment or in the variance.",
        "Using a normal approximation at n below about 10.",
        "Describing a rank test as a test of medians without shape assumptions.",
        "Stopping at a significant omnibus result without localisation.",
        "Applying a paired test to independent data or the reverse.",
    ],
    math_problems=[
        "Rank a dataset with ties and show the average-rank assignment.",
        "Compute Mann-Whitney U by hand and match it to the probability of superiority.",
        "Enumerate the exact null for n1 = n2 = 5 and compare with the asymptotic p-value.",
        "Compute Kruskal-Wallis for four groups and follow up with a corrected pairwise comparison.",
        "Compare power of the signed-rank test and a signed test under a skewed-difference example.",
    ],
    tree="""src/
  NonParametricTests.java    driver: selects and runs the right rank test
  Ranks.java                 ranking with average ranks for ties
  MannWhitneyTest.java       independent groups, exact and asymptotic
  WilcoxonSignedRankTest.java paired differences, zero-differences omitted
  KruskalWallisTest.java     k independent groups with a corrected omnibus
  FriedmanTest.java          k treatments within blocks
  ExactNull.java             enumeration of rank permutations for small n
  RankEffectSize.java        probability of superiority with an interval""",
    tree_note="ExactNull enumerates label assignments with a bitmask and counts how "
              "many are at least as extreme, which is both fast and obviously "
              "correct at the sample sizes where exactness matters.",
    types=[
        ("Ranks", "ranking with average ranks for ties"),
        ("MannWhitneyTest", "independent groups with exact and asymptotic paths"),
        ("ExactNull", "enumeration of rank permutations for small samples"),
        ("RankEffectSize", "probability of superiority with a bootstrap interval"),
    ],
    patterns=[
        ("Ranking with ties handled correctly",
         "Average ranks for tied values, which is the hinge of every rank test's "
         "correctness.",
         """public double[] ranks(double[] values) {
    int n = values.length;
    Integer[] idx = new Integer[n];                    // sort indices, not a copy
    for (int i = 0; i < n; i++) idx[i] = i;
    Arrays.sort(idx, (a, b) -> Double.compare(values[a], values[b]));
    double[] r = new double[n];
    int i = 0;
    while (i < n) {                                    // walk runs of equal values
        int j = i;
        while (j + 1 < n && values[idx[j + 1]] == values[idx[i]]) j++;
        double averageRank = (i + j + 2) / 2.0;        // ranks i+1..j+1, averaged
        for (int k = i; k <= j; k++) r[idx[k]] = averageRank;
        tieTerm += (j - i + 1L) * (j - i + 1L) * (j - i + 1L) - (j - i + 1L);   // variance correction
        i = j + 1;
    }
    return r;
}"""),
        ("Exact null distribution by enumeration",
         "For small samples the rank statistic is discrete, so enumeration beats an "
         "approximation and is trivially verifiable.",
         """public static ExactResult exactMannWhitney(double[] group1, double[] group2) {
    double[] pooled = concat(group1, group2);
    int n1 = group1.length, n2 = group2.length, n = n1 + n2;
    double[] r = ranks(pooled);
    int observed = (int) Math.round(rankSum(r, 0, n1));
    long atLeastAsExtreme = 0, total = 0;
    // every way of choosing which n1 pooled values are group 1
    for (int mask = 0; mask < (1 << n); mask++) {
        if (Integer.bitCount(mask) != n1) continue;
        total++;
        int stat = 0;
        for (int i = 0; i < n; i++) if (((mask >> i) & 1) == 1) stat += (int) Math.round(r[i]);
        if (stat <= observed || stat >= (n1 * (n + 1)) - observed) atLeastAsExtreme++;
    }
    return new ExactResult(observed, (double) atLeastAsExtreme / total, true);
}"""),
    ],
    costs=[
        ("Ranking with tie handling", "O(n log n)", "one index sort"),
        ("Kruskal-Wallis", "O(n log n + k)", "one ranking, group sums after"),
        ("Friedman", "O(bk log k)", "ranking within each block"),
        ("Exact null enumeration", "O(C(N, n\u2081) \u00d7 N)", "fine below about 20 per group"),
    ],
    numerics=[
        "Assign average ranks to ties; the variance correction follows from tie sizes.",
        "Use exact enumeration below roughly 20 per group.",
        "Report the probability of superiority as the effect size.",
        "Bootstrap rank-test effect sizes with a stated resampling scheme.",
        "Follow a significant omnibus test with corrected pairwise comparisons.",
    ],
    tests=[
        "Ranks with ties match hand-computed average ranks.",
        "Mann-Whitney with completely separated groups gives the minimum statistic and p = 0 to machine precision.",
        "The exact p-value at n = 5 per group matches the enumerated value.",
        "The exact and asymptotic p-values agree closely at n = 30 per group.",
        "Kruskal-Wallis on identical groups is not significant.",
        "Friedman on a complete block design recovers the known ordering.",
    ],
    extensions=[
        "Add Dunn's test for pairwise comparisons after Kruskal-Wallis with a correction.",
        "Add Cliff's delta as a rank-based effect size with an interval.",
        "Add permutation tests as a general framework covering the same questions.",
    ],
    code_checklist=[
        "Test chosen from the design and measurement scale",
        "Ties handled with average ranks and a variance correction",
        "Exact p-values for small samples, asymptotic for large",
        "Null hypothesis stated as distributional, not mean-based",
        "Effect size reported with an interval",
        "Omnibus results followed by corrected pairwise comparisons",
    ],
    exercise_selfcheck=[
        "I matched the test to the design.",
        "My ranking handles ties.",
        "Small samples use exact p-values.",
        "I report an effect size, not only a p-value.",
    ],
    exercises=[
        ("Ranks and ties",
         "Get the foundation right.",
         ["Implement ranking with average ranks for ties.",
          "Compute the tie correction term.",
          "Verify on hand-worked examples including heavy ties.",
          "Show the effect of ignoring ties on a p-value."],
         "A verified ranking implementation."),
        ("Mann-Whitney U",
         "Two independent groups.",
         ["Compute U from rank sums.",
          "Implement the probability-of-superiority interpretation.",
          "Implement exact enumeration for small n.",
          "Compare exact and asymptotic p-values across n."],
         "A test with an effect size and both p-value paths."),
        ("Wilcoxon signed-rank",
         "Paired data.",
         ["Compute differences, omit zeros, rank absolute differences.",
          "Handle ties in the absolute differences.",
          "Compare with a signed test on raw values under skew.",
          "Explain where the power difference comes from."],
         "A paired test with a power comparison."),
        ("Kruskal-Wallis with follow-up",
         "The omnibus and its localisation.",
         ["Compute H and the tie-corrected chi-square p-value.",
          "Follow a significant result with corrected pairwise comparisons.",
          "Compare power against one-way ANOVA under skew.",
          "Report an effect size such as epsilon squared."],
         "An omnibus test with a corrected follow-up."),
        ("Friedman for blocked designs",
         "Related groups.",
         ["Rank within blocks, sum by treatment, compute Q.",
          "Apply the tie correction.",
          "Compare with repeated-measures ANOVA.",
          "Report an effect size."],
         "A blocked rank test."),
        ("Exact versus asymptotic",
         "Know when the approximation lies.",
         ["Enumerate the exact null for n = 5 to 12.",
          "Compare exact and asymptotic p-values across the range.",
          "Identify where the approximation becomes acceptable.",
          "Write the rule you would codify."],
         "A comparison table with a documented rule."),
        ("Power analysis for rank tests",
         "Size a rank test properly.",
         ["Compute power via simulation for a rank test.",
          "Compare power against the parametric equivalent.",
          "Show the sample size inflation under heavy skew.",
          "Report the required n."],
         "A power comparison with required n."),
        ("Full rank analysis report",
         "Defensible end to end.",
         ["State the design, scale and assumptions.",
          "Choose and justify the test, handle ties, decide exactness.",
          "Report statistic, p-value and effect size with an interval.",
          "State what the result does and does not support."],
         "A report with a clear interpretation boundary."),
    ],
    quiz=[
        ("When is a rank test preferable?", ["Large samples", "Ordinal data, heavy tails, or samples too small to assess normality", "Normally distributed data", "Equal variances"], 1, "Rank tests rely only on the ordinal scale and exchangeability."),
        ("What does the Mann-Whitney null assume?", ["Equal means", "Identical distributions across groups", "Equal medians", "Normality"], 1, "Equal means is not assumed, and equal medians requires additional shape similarity."),
        ("Is Mann-Whitney a test of medians?", ["Always", "Only under additional shape similarity assumptions", "Never", "Only for large samples"], 1, "Otherwise it tests stochastic ordering of distributions."),
        ("How do ties affect rank tests?", ["They are ignored", "They require average ranks and a variance correction, or p-values are too small", "They increase power", "They reduce the statistic"], 1, "The tie correction inflates the variance, raising p-values appropriately."),
        ("When should you use an exact p-value?", ["Always", "For small samples where a normal approximation is invalid", "Never", "Only for continuous data"], 1, "The rank statistic is discrete at small n, so enumeration is both easy and correct."),
        ("Which test for paired data?", ["Mann-Whitney", "Wilcoxon signed-rank", "Kruskal-Wallis", "Friedman"], 1, "Paired data requires the signed-rank test on within-pair differences."),
        ("Which test for three or more independent groups?", ["Friedman", "Kruskal-Wallis", "Wilcoxon", "Mann-Whitney"], 1, "Kruskal-Wallis extends the two-group rank test to k independent groups."),
        ("Which test for three or more related groups?", ["Kruskal-Wallis", "Friedman", "Wilcoxon", "ANOVA"], 1, "Friedman blocks by subject and ranks within blocks."),
        ("Why must zero differences be omitted in the signed-rank test?", ["They reduce power", "A zero carries no direction, so including it distorts the rank sum", "They cause ties", "They are required to be omitted for exactness"], 1, "Only non-zero differences contribute directional information."),
        ("Why are rank tests less powerful?", ["They are more conservative", "They discard magnitude, so large skewed effects need larger samples", "They assume less so are worse", "They cannot detect small effects"], 1, "Discarding magnitude is the price of the weaker assumption."),
        ("What is the probability of superiority?", ["The p-value", "P(X > Y) + 0.5 P(X = Y), a communicable effect size for rank tests", "The variance", "The sample size"], 1, "It is directly interpretable as 'how often would a random pair favour this group'."),
        ("Why follow a significant Kruskal-Wallis with pairwise tests?", ["To increase power", "The omnibus says something differs but not which, and the pairs need a multiplicity correction", "To satisfy reviewers", "To reduce the p-value"], 1, "Localisation requires its own error control."),
        ("What is Dunn's test for?", ["Pairwise comparisons after Kruskal-Wallis with a correction", "Testing normality", "Variance estimation", "Tie handling"], 0, "It localises a significant omnibus with appropriate multiplicity control."),
        ("What is a tie correction?", ["A way to remove ties from the data", "An adjustment to the null variance accounting for tied ranks", "A test for outliers", "A correction applied to the p-value"], 1, "It restores the reference distribution's validity under ties."),
        ("When does a rank test's null hold?", ["When means are equal", "When the distributions are identical across groups, with independent observations respecting the design", "When variances are equal", "When the data is normal"], 1, "Exchangeability of ranks is the actual assumption."),
    ],
    vision=dict(
        future="Rank methods remain the default for ordinal, skewed and small-sample "
               "problems, with permutation tests providing a general framework and "
               "effect sizes becoming as routine as p-values. The discipline is "
               "matching the test to the design and handling ties exactly.",
        good=[
            "Tests are matched to the design and measurement scale.",
            "Ties are handled with average ranks and a variance correction.",
            "Small samples use exact null distributions.",
            "Every rank test reports an effect size with an interval.",
        ],
        ladder=[
            ("L1", "Rank", "Ranking with average ranks and tie correction."),
            ("L2", "Test", "Mann-Whitney, Wilcoxon, Kruskal-Wallis and Friedman."),
            ("L3", "Be exact", "Exact null enumeration for small samples."),
            ("L4", "Quantify", "Effect sizes with intervals and corrected pairwise follow-up."),
        ],
        behaviors="Match the test to the design, handle ties exactly, use exact "
                  "methods when n is small, and report an effect size. Do not call a "
                  "rank test a test of medians without showing shapes match.",
        anti=[
            "A median-difference claim from a Mann-Whitney test on skewed data.",
            "Ignoring ties, which makes p-values too small.",
            "An asymptotic p-value at n = 6.",
            "A significant omnibus with no corrected localisation.",
        ],
        trends=[
            "Permutation tests as a general exact framework covering most designs.",
            "Rank-based effect sizes such as Cliff's delta with confidence intervals.",
            "Automatic test selection from the data scale, design and shape diagnostics.",
            "Sensitivity reporting: how does the conclusion change across plausible analyses?",
        ],
        d30="Implement ranking with ties and verify the average-rank assignment.",
        d60="Implement the four rank tests with exact nulls for small samples.",
        d90="Add effect sizes with intervals, corrected pairwise follow-up, and a power comparison.",
        metrics=[
            "My test matches the design.",
            "My ranking handles ties.",
            "Small samples use exact p-values.",
            "Every rank test reports an effect size.",
        ],
        closer="Switching to a rank test is not a fallback; it is the correct answer "
               "when the parametric assumptions never held.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Rank-Based Analysis with Exact Inference",
        brief="Analyse four designs with the correct rank test, handle ties, use "
              "exact nulls where needed, and report effect sizes.",
        timebox="3 hours",
        why="Rank tests are easy to apply wrongly: wrong test for the design, ties "
            "ignored, asymptotic p-values on tiny samples.",
        requirements=[
            "Ranking with average ranks and the tie correction, verified by hand.",
            "Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman, each matched to a design.",
            "Exact null enumeration for small samples compared against asymptotic p-values.",
            "Tie demonstration showing how ignoring ties changes the result.",
            "Probability of superiority as an effect size with an interval.",
            "Corrected pairwise follow-up after a significant omnibus.",
            "Power comparison against the parametric equivalent under skew.",
        ],
        steps=[
            ("1", "30m", "Ranking with ties, verified by hand", "A verified ranking"),
            ("2", "30m", "Mann-Whitney with exact enumeration", "A test with both p-value paths"),
            ("3", "25m", "Wilcoxon signed-rank with zero and tie handling", "A paired test"),
            ("4", "30m", "Kruskal-Wallis with corrected pairwise follow-up", "An omnibus plus localisation"),
            ("5", "20m", "Friedman on a blocked design", "A blocked rank test"),
            ("6", "25m", "Tie demonstration and exact-versus-asymptotic table", "A comparison table"),
            ("7", "30m", "Power comparison and report", "A power table and a report"),
        ],
        diagram=""" four designs
  independent 2-group      -> Mann-Whitney
  paired                    -> Wilcoxon signed-rank
  independent k-group       -> Krkal-Wallis + corrected pairs
  blocked k-treatment       -> Friedman
     |
 [1] rank with average ranks + tie correction
 [2] exact null enumeration (n <= ~20) | asymptotic above
 [3] probability of superiority with interval
 [4] tie demonstration: ignoring ties inflates significance
 [5] power comparison vs parametric under skew
     |
 report: statistic, exact/asymptotic flag, effect size, what it does not support""",
        notes=[
            "Verify the ranking by hand on a tied example before anything else; every test depends on it.",
            "Show the exact-versus-asymptotic gap at small n; it is the most persuasive argument for enumeration.",
            "Follow a significant omnibus with corrected pairs, or the localisation claim is unsupported.",
            "Report the probability of superiority; it communicates better than any rank statistic.",
        ],
        deliverables=[
            "Verified ranking with tie correction.",
            "Four rank tests matched to their designs, with exact and asymptotic paths.",
            "Exact-versus-asymptotic comparison table and a tie demonstration.",
            "Effect sizes with intervals plus a power comparison.",
        ],
        grading=[
            ("Correctness", "30%", "Ranking, ties, statistic and exactness all correct"),
            ("Design matching", "20%", "Each test matched to the correct design"),
            ("Uncertainty", "25%", "Effect sizes with intervals; exact where needed"),
            ("Localisation", "15%", "Corrected pairwise follow-up after an omnibus"),
            ("Reporting", "10%", "Null stated accurately; limits of the interpretation clear"),
        ],
        stretch=[
            "Add Dunn's test for post-omnibus localisation.",
            "Add Cliff's delta with a bootstrap interval.",
            "Add a permutation framework that subsumes the four tests.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Non-Parametric Analysis for Support Operations",
        scenario="A support organisation compares median handle time across 40 "
                 "queues, 4 regions and before/after a tooling change. Handle time "
                 "is heavily skewed, groups are small, and one team applied a t-test "
                 "and shipped the conclusion.",
        scale=[
            ("Queues", "40 queues \u00d7 4 regions, 6\u201380 tickets per group in weekly samples"),
            ("Metric", "handle time: heavily right-skewed, ordinal buckets in some tools"),
            ("Current practice", "t-tests and ANOVA on skewed data, median claims from p-values"),
            ("Known failure", "one team shipped a queue-mix change based on a t-test on 7 observations"),
            ("Requirement", "correct tests per design with effect sizes and localisation"),
        ],
        diagram=""" ticket events (queue, region, handle time, week, tooling version)
     |
 shape diagnostics per group: skew, outliers, ordinal bucket use
     |
 test selection by design
   2 independent groups  -> Mann-Whitney
   before/after same queue -> Wilcoxon signed-rank
   40 queues across regions -> Kruskal-Wallis + Dunn (corrected)
   4 regions, same week   -> Friedman (blocked by week)
     |
 exact null for small groups; asymptotic for the 40-queue omnibus
     |
 effect size: probability of superiority / Cliff's delta with intervals
     |
 localisation with multiplicity correction; "significant" never reported alone""",
        components=[
            ("Data quality and shape diagnostics",
             ["Handle time retained in full with skew reported per group rather than binned silently",
              "Ordinal bucket handling where tools only record buckets, with the ordinal assumption stated",
              "Sample-size reporting per group, since rank tests are power-limited at small n",
              "Outliers retained with a note; rank tests tolerate them rather than justifying their removal"]),
            ("Test selection by design",
             ["Before/after tooling change on the same queues: Wilcoxon signed-rank on within-queue differences",
              "Two queues or two regions: Mann-Whitney with the distributional null stated",
              "Many queues across regions: Kruskal-Wallis omnibus followed by Dunn's test with a correction",
              "Regions compared within week: Friedman, blocking by week so seasonality is not mistaken for a region effect"]),
            ("Inference and localisation",
             ["Exact null enumeration for groups below about 20; asymptotic above with the tie correction applied",
              "Tie handling verified, since bucketed handle times produce many ties",
              "Post-omnibus localisation with multiplicity control; omnibus alone never reported",
              "Non-significant results reported with power and an effect-size interval rather than as no difference"]),
            ("Reporting and governance",
             ["Every comparison reports the statistic, whether the p-value is exact, and an effect size with an interval",
              "Interpretation stated as distributional ordering or probability of superiority, never an unqualified median claim",
              "Analyses that would have used a parametric test are recorded so the change is auditable",
              "Tooling-change decisions require a rank test with localisation and an effect size above a business threshold"]),
        ],
        timeline=[
            ("Week 1", "Data quality and shape diagnostics; retain full handle times and report skew per group"),
            ("Week 2", "Test selection by design implemented, replacing parametric defaults"),
            ("Week 3", "Exact nulls for small groups; tie handling verified on bucketed data"),
            ("Week 4", "Dunn's follow-up localisation and effect sizes with intervals"),
            ("Week 5-6", "Reporting standard and governance for tooling-change decisions; retrospective review of prior conclusions"),
        ],
        runbook=[
            "# Shape diagnostics for a group's handle time",
            "curl -s 'localhost:8083/ops/shape?queue=billing&week=2026-W37' | jq '{n,skew,outliers,ordinalBuckets}'",
            "",
            "# Test selected for a comparison and why",
            "curl -s 'localhost:8083/ops/test?comparison=tooling-before-after' | jq '{design,test,reason}'",
            "",
            "# Result with exactness flag and effect size",
            "curl -s 'localhost:8083/ops/result?comparison=tooling-before-after' | jq '{statistic,pValue,exact,probSuperiority,ci}'",
            "",
            "# Omnibus and corrected localisation across queues",
            "curl -s 'localhost:8083/ops/kruskal?week=2026-W37' | jq '{h,p,dunn:[.[]|{pair,pAdjusted}]}'",
            "",
            "# Inconclusive comparisons with power and achievable effect",
            "curl -s 'localhost:8083/ops/inconclusive?window=90d' | jq '.[] | {comparison,n,power,minDetectableEffect}'",
        ],
        metrics=[
            "Method: comparisons using the test matching their design (target 100%).",
            "Exactness: p-values from exact enumeration for groups below 20 (target 100%).",
            "Reporting: comparisons with an effect size and interval (target 100%).",
            "Localisation: significant omnibus results followed by corrected pairwise comparisons (target 100%).",
            "Outcome: tooling decisions with an effect size above the business threshold, tracked against outcomes.",
        ],
        failures=[
            ("A queue-mix change is reversed after rollout", "A t-test on 7 observations", "Rank test with effect size and localisation required before any tooling decision"),
            ("Kruskal-Wallis is significant and nobody localises it", "Omnibus reported alone", "Dunn's follow-up is mandatory in the reporting path"),
            ("Bucketed handle times inflate significance", "Ties ignored in ranking", "Average ranks with the tie correction; verified on bucketed data"),
            ("A region is declared slower from a single week", "No blocking by week", "Friedman blocking by week, or region comparisons within week"),
            ("Inconclusive results are read as no difference", "Power not reported", "Report power and the minimum detectable effect alongside every non-significant result"),
        ],
        backlog=[
            "Dunn's test with correction standardised across all omnibus comparisons.",
            "Cliff's delta with bootstrap intervals as the default effect size.",
            "Shape diagnostic thresholds blocking parametric tests automatically.",
            "Permutation framework covering designs the four named tests do not.",
            "Retrospective review of prior tooling decisions using the corrected methods.",
        ],
        urls=URLS,
        closer="The deliverable is an operations analysis where every comparison "
               "uses the test its design requires, handles the ties that bucketed "
               "handle times create, and ships an effect size rather than a bare "
               "p-value.",
    ),
))

# ---------------------------------------------------------------- lab10
SPECS.append(dict(
    track="statistics", lab="lab10", full_set=True, level="Advanced",
    title="Statistical Power & Effect Size", main_class="com.statistics.lab10.StatisticalPower",
    problem="You have a fixed sample and a question about a real effect. The "
            "p-value tells you about noise; the power calculation tells you "
            "whether your study could ever have found the truth.",
    why_now="Power is the discipline that makes inconclusive results explicable "
             "rather than ambiguous, and effect sizes are what translate a "
             "statistical result into a business decision.",
    objectives=[
        "Compute Cohen's d and related effect sizes with correct pooling",
        "Compute power for means, proportions and comparisons using correct alternatives",
        "Derive the minimum detectable effect for a given sample size",
        "Invert power to obtain required sample size",
        "Choose an effect size from literature or pilot data rather than from the observed result",
        "Report power alongside every non-significant result",
    ],
    concepts=[
        ("Power is about design, not results",
         "Power depends on the effect size you specified in advance, the noise, the "
         "sample size and alpha. Since it depends on the assumed effect rather than "
         "the observed one, it can and must be computed before data collection."),
        ("Cohen's d and its limits",
         "d is the mean difference in pooled standard deviation units, with "
         "thresholds of 0.2, 0.5 and 0.8 for small, medium and large. These are "
         "conventions rather than universal constants: a 0.2 difference in revenue "
         "may be enormous, and in latency catastrophic."),
        ("Small studies have huge minimum detectable effects",
         "MDE scales as (z_{1\u03b1/2} + z_{1\u2212\u03b2}) \u00b7 \u03c3 \u00b7 sqrt(2/n). With n = 20 per arm and 80% "
         "power you can only detect d of about 0.9, so 'no significant difference' "
         "in a small study is nearly uninformative."),
        ("Directional power depends on the alternative",
         "Power computed under the null alternative is meaningless. You must state "
         "the specific effect you want to detect, and power depends on whether it is "
         "one-sided or two-sided."),
        ("Variance estimates come from elsewhere",
         "Planning power requires an effect size and a variance, and the observed "
         "effect is the wrong source for the effect size. Use literature, pilot data "
         "or a business threshold, and inflate pilot variance because small pilots "
         "understate it."),
        ("Power curves are decision documents",
         "Plotting power against n for a range of effects shows what your study can "
         "and cannot detect, which is the honest way to discuss a fixed budget or an "
         "inconclusive result."),
    ],
    formulas=[
        ("d = (\u0304x\u2081 \u2212 \u0304x\u2082) / s\u209a", "Cohen's d", "pooled standard deviation"),
        ("Hedges' g = d / (1 \u2212 3/(4n \u2212 9))", "Bias-corrected d", "better for small n"),
        ("r = d / sqrt(d\u00b2 + 4)", "Effect size as r", "relatable to correlation"),
        ("power = 1 \u2212 \u03b2", "Power", "1 minus Type II error"),
        ("MDE = (z_{1\u2212\u03b1/2} + z_{1\u2212\u03b2}) \u03c3 sqrt(2/n)", "Minimum detectable effect", "what your n can see"),
        ("n = 2 (z_{1\u2212\u03b1/2} + z_{1\u2212\u03b2})\u00b2 \u03c3\u00b2 / \u03b4\u00b2", "Required n", "inverting power"),
        ("p1, p2 proportions", "Proportion power", "pooled variance under the null"),
        ("pph = 2 arcsin sqrt(p1) \u2212 2 arcsin sqrt(p2)", "Fisher z for rates", "propensity differences"),
    ],
    flow=[
        "Define the effect worth detecting, from a business threshold or literature, not from data.",
        "Estimate the variance from a pilot or historical data, and inflate it.",
        "Fix alpha and power, then compute required n per arm and the horizon at your traffic.",
        "Compute the MDE your sample can achieve, so the study's resolution is explicit.",
        "Plot a power curve across a range of effects and n.",
        "Report the power analysis with the study, and the power alongside any non-significant result.",
    ],
    assumptions=[
        "The assumed effect size is credible and specified before data collection",
        "The variance estimate is defensible, and inflated if it comes from a small pilot",
        "Alpha and the chosen power reflect the cost of each error type",
        "The alternative is the specific effect of interest, correctly sided",
        "Independence holds, or the effective sample size is reduced accordingly",
        "Multiple comparisons are accounted for in the alpha used for power",
    ],
    pitfalls=[
        ("'No significant difference' from n = 20 per arm", "study could only detect a huge effect", "report the MDE alongside any null result"),
        ("Power computed under the null alternative", "power of the wrong hypothesis", "specify the effect you want to detect"),
        ("Effect size taken from the observed result", "planning on the outcome", "use literature, a business threshold, or an inflated pilot"),
        ("Pilot variance used uninflated", "small pilots understate variance", "inflate by a documented factor and record the reasoning"),
        ("Cohen's 0.5 declared medium", "convention treated as universal", "translate the effect into business units before deciding"),
        ("Power computed but alpha not adjusted for multiple comparisons", "family-wise error inflated", "use the alpha you will actually apply"),
    ],
    java=[
        ("Normal quantile function", "z-values for power and MDE, closed form and exact"),
        ("Non-central t distribution", "exact power for small samples"),
        ("record PowerResult(double power, double mde, int nPerArm, double alpha)", "resolution reported with the design"),
        ("Arcane-free business translation", "converting an effect into units the business recognises"),
        ("Power curve generator", "power across a grid of n and effect sizes"),
    ],
    links=[
        "**lab03** is the test whose power this lab computes.",
        "**lab08** is where the sample size is applied to a design.",
        "**lab05** provides the effect sizes that feed power planning.",
        "**mlops/lab10** applies power and MDE to a live experimentation decision.",
    ],
    checklist=[
        "My effect size came from a threshold or literature, not the observed result.",
        "My variance is defensible and inflated if from a small pilot.",
        "Power is computed under the correct sided alternative.",
        "I report the MDE my sample can achieve.",
        "Non-significant results come with power, not with 'no difference'.",
        "My alpha accounts for the comparisons I will actually make.",
    ],
    cards=[
        ("What does power depend on?", "The specified effect size, the variance, the sample size and alpha \u2014 never on the observed result."),
        ("Why is a non-significant result from a small study uninformative?", "Because the study's minimum detectable effect may be far larger than any effect that matters."),
        ("What is Cohen's d?", "The mean difference in pooled standard deviation units, with conventional thresholds of 0.2, 0.5 and 0.8."),
        ("Why use Hedges' g rather than d for small samples?", "d is biased upward at small n; Hedges' g corrects for it."),
        ("How does MDE scale with n?", "As 1/sqrt(n), so quadrupling the sample halves the smallest detectable effect."),
        ("Where should a planning effect size come from?", "Literature, a business threshold, or an inflated pilot \u2014 never the observed result."),
        ("Why inflate a pilot variance?", "Small pilots give noisy, biased-low variance estimates, which yield under-powered designs."),
        ("What does a power curve show?", "Power against n for a range of effects, making the design's resolution explicit."),
    ],
    extra_cards=[
        ("Why does power depend on sidedness?", "A one-sided test rejects at a lower threshold, so it has more power for a directional alternative."),
        ("How is an effect size expressed as r?", "r = d / sqrt(d\u00b2 + 4), which makes it comparable to correlation-based intuition."),
        ("What is the effect of multiplicity on power?", "Adjusting alpha downward for many comparisons reduces power, so the sample must grow."),
        ("How do you report power for a completed study?", "Retrospective power computed at the effect size you specified a priori, not at the observed effect."),
    ],
    math=[
        ("Cohen's d, pooling and bias",
         "pooled s_p = sqrt(((n1-1)s1^2 + (n2-1)s2^2)/(n1+n2-2))\nd = (xbar1 - xbar2)/s_p\nHedges' g = d * (1 - 3/(4(n1+n2)-9))",
         "Pooling assumes comparable variances; with unequal variances the "
         "alternative is Glass's delta using the control standard deviation. "
         "Hedges' correction exists because d is biased upward at small n, which is "
         "exactly the regime where the bias matters.",
         "n1 = n2 = 8, difference 1.0, s = 1.0: d = 1.0 but the correction factor is "
         "1 - 3/(4*16 - 9) = 0.955, so g = 0.955. At n = 20 each, the factor is "
         "0.974 and the difference is negligible, which is why the correction is "
         "reserved for small samples."),
        ("Power for a two-sample comparison",
         "non-centrality: lambda = delta / (sigma sqrt(1/n1 + 1/n2))\npower = P(T_{df, lambda} > t_{1-alpha/2}) + P(T_{df, lambda} < -t_{1-alpha/2})\ntwo-sided needs lambda about 2.8 for 80% power; one-sided about 2.0",
         "Power is the probability of rejecting the null under a specific alternative, "
         "which is why the alternative must be stated. The gap between two-sided and "
         "one-sided power is substantial and is often misjudged.",
         "delta = 0.5 sigma, n = 64 per arm: two-sided power 0.80. n = 64 one-sided: "
         "power 0.90. At n = 20 per arm, two-sided power for d = 0.5 is about 0.26 "
         "\u2014 the study would miss a medium effect four times out of five."),
        ("Minimum detectable effect",
         "MDE = (z_{1-alpha/2} + z_{1-beta}) sigma sqrt(2/n)\nfor d: MDE_d = (z_{1-alpha/2} + z_{1-beta}) sqrt(2/n)\nat alpha 0.05, power 0.8: MDE_d = 2.802 sqrt(2/n)",
         "MDE is the honest resolution statement for a fixed sample. It converts a "
         "sample size constraint into the actual question 'what could this study have "
         "found', which is what reviewers and stakeholders should be told.",
         "n = 20 per arm: MDE_d = 2.802 sqrt(0.1) = 0.886, so only an enormous effect "
         "is detectable. n = 100: 0.396. n = 400: 0.198. Quadr quadrupling the sample "
         "halves the detectable effect, as the 1/sqrt(n) law implies."),
        ("Power under the wrong alternative",
         "power is a function of the assumed effect: power(d=0.1) << power(d=0.5) << power(d=1.0)\npost-hoc power at the observed effect is not informative:\nit is a monotone function of the p-value and adds nothing",
         "Post-hoc power computed from the observed effect is a deterministic "
         "function of the p-value, so it tells you nothing the p-value did not. "
         "Retrospective power is only meaningful when computed at the effect you "
         "specified before the study.",
         "A study with n = 50 per arm and p = 0.08: post-hoc power at the observed "
         "effect is around 0.40 and is uninformative. Retrospective power at the "
         "planned d = 0.5 is 0.48, which correctly explains why an inconclusive "
         "result was likely."),
        ("Multiplicity and power cost",
         "family-wise alpha via Bonferroni: alpha' = alpha/m\npower with alpha' is lower for the same n\nrequired n grows roughly with log(m)",
         "Testing many hypotheses costs power as well as error control. Declaring ten "
         "outcomes at alpha = 0.05 without adjustment makes each test less powerful "
         "and more likely to produce a family-wise error.",
         "m = 10 comparisons, alpha' = 0.005: with n = 400 per arm, power for d = 0.2 "
         "falls from about 0.85 to 0.63. Reaching 0.85 again needs roughly 600 per "
         "arm, a 50% increase in cost."),
    ],
    math_traps=[
        "Computing power at the observed effect and calling it informative.",
        "Using an uninflated pilot variance for planning.",
        "Ignoring sidedness when comparing designs.",
        "Planning with alpha that ignores the multiplicity correction.",
        "Quoting Cohen's thresholds as if they were universal.",
    ],
    math_problems=[
        "Compute d and Hedges' g for two groups and show the bias difference at small n.",
        "Compute power for a two-sample comparison across n and both sidednesses.",
        "Compute the MDE for n = 20, 100 and 400 per arm and express it in business units.",
        "Show that post-hoc power is a function of the p-value.",
        "Recompute required n after a Bonferroni correction for ten comparisons.",
    ],
    tree="""src/
  StatisticalPower.java   driver: power, MDE and required n for each test
  EffectSize.java         Cohen's d, Hedges' g, Glass's delta, r, proportion measures
  PowerFunction.java      power for means and proportions under a stated alternative
  NonCentralT.java        exact small-sample power via the non-central t
  PowerCurve.java         power across a grid of n and effect sizes
  BusinessTranslation.java effect size rendered in the units the business uses""",
    tree_note="BusinessTranslation exists because a d of 0.5 means nothing to a "
              "planning meeting. Converting the effect into units \u2014 dollars, "
              "minutes, tickets \u2014 is the step that makes the analysis actionable.",
    types=[
        ("EffectSize", "d, Hedges' g, Glass's delta, r and proportion measures"),
        ("PowerFunction", "power for means and proportions under a stated alternative"),
        ("PowerCurve", "power across a grid of n and effect sizes"),
        ("PowerResult", "power, minimum detectable effect, n per arm and alpha together"),
    ],
    patterns=[
        ("Power under a stated alternative with MDE reported",
         "The alternative is an argument, not an assumption, and the resolution of "
         "the design travels with the power number.",
         """public PowerResult powerMeans(double delta, double sigma, int nPerArm,
                                double alpha, boolean oneSided) {
    double se = sigma * Math.sqrt(2.0 / nPerArm);
    double lambda = delta / se;                        // non-centrality under the alternative
    int df = 2 * nPerArm - 2;
    double critical = oneSided ? quantile(1 - alpha, df) : quantile(1 - alpha / 2, df);
    // two-sided power sums both tails; one-sided sums one
    double p = oneSided ? nonCentralTCdf(-critical, df, lambda)
                        : nonCentralTCdf(-critical, df, lambda)
                          + nonCentralTSf(critical, df, lambda);
    // MDE reported alongside power: the design's resolution, not just its sensitivity
    double mde = (oneSided ? zQuantile(1 - alpha) + zQuantile(0.8)
                          : zQuantile(1 - alpha / 2) + zQuantile(0.8)) * se;
    return new PowerResult(1 - p, mde / sigma, nPerArm, alpha);
}"""),
        ("Variance inflation from a small pilot",
         "Pilot variances are biased low at small n, so inflate them explicitly and "
         "record the factor with the study.",
         """public double planningVariance(double[] pilot) {
    // variance of a sample variance is roughly 2 sigma^4 / (n-1): small pilots
    // understate variance, so inflate rather than plan with a biased-low estimate
    double n = pilot.length;
    double observed = sampleVariance(pilot);
    double inflation = 1.0 + Math.sqrt(2.0 / (n - 1));      // documented, not arbitrary
    PlanningVariance pv = new PlanningVariance(observed * inflation * inflation, inflation);
    System.out.printf("pilot n=%d, inflation x%.2f, planning sd=%.4f%n",
            (int) n, pv.inflation(), Math.sqrt(pv.variance()));
    return pv;
}"""),
    ],
    costs=[
        ("Normal-approximation power", "O(1)", "closed-form quantiles"),
        ("Exact non-central t power", "O(1) per evaluation", "numerical integration or series"),
        ("Power curve grid", "O(grid size)", "cheap; render freely"),
        ("Bootstrap MDE", "O(r x n)", "only when the analytic form does not apply"),
    ],
    numerics=[
        "Compute power under the stated alternative, never under the null.",
        "Inflate pilot variances and record the factor with the study.",
        "Report MDE alongside power so the design's resolution is explicit.",
        "Use Hedges' g below about n = 20 per group.",
        "Apply the same multiplicity correction to alpha in the power calculation.",
    ],
    tests=[
        "Power increases with n and with the effect size, monotonically.",
        "Two-sided power is lower than one-sided power for the same alternative.",
        "MDE at the n computed for target power equals the specified effect.",
        "Hedges' g equals d to within 1% at n = 200 per group.",
        "Inflated pilot variance produces a larger required n than the raw estimate.",
        "Post-hoc power computed from the observed effect reproduces a known function of the p-value.",
    ],
    extensions=[
        "Add power for logistic regression and count outcomes.",
        "Add equivalence testing power, which inverts the usual framing.",
        "Add a design optimiser allocating a fixed budget across several comparisons.",
    ],
    code_checklist=[
        "Effect size specified before data collection, from a threshold or literature",
        "Variance defensible and inflated if from a pilot",
        "Power computed under the correct sided alternative",
        "MDE reported with every power number",
        "Multiplicity reflected in the alpha used",
        "Retrospective power computed at the a priori effect, not the observed one",
    ],
    exercise_selfcheck=[
        "My effect size came from a threshold or literature.",
        "My variance is inflated if from a small pilot.",
        "I report the MDE my sample can achieve.",
        "I never quote post-hoc power as evidence.",
    ],
    exercises=[
        ("Effect sizes",
         "Compute and interpret them.",
         ["Implement d with pooled and with control-only variance.",
          "Implement Hedges' correction.",
          "Express an effect as r and as a proportion difference.",
          "Translate one into business units."],
         "An effect size suite with a business translation."),
        ("Power curves",
         "Power across n and effect sizes.",
         ["Plot power against n for several effect sizes.",
          "Mark the n reaching 80% power for each.",
          "Compare two-sided and one-sided curves.",
          "Read the achievable effect from each curve."],
         "Power curves with marked operating points."),
        ("MDE analysis",
         "What your design can see.",
         ["Compute MDE for a grid of n.",
          "Express MDE in business units for a real metric.",
          "Explain why small studies are uninformative.",
          "Recommend a design given a budget."],
         "An MDE analysis with a budget recommendation."),
        ("Pilot variance inflation",
         "Plan with a defensible variance.",
         ["Run pilots at several sizes.",
          "Show the bias in the variance estimate.",
          "Compare inflated and uninflated required n.",
          "Justify the inflation factor."],
         "A bias demonstration with justified inflation."),
        ("Multiplicity and power cost",
         "Price the cost of many comparisons.",
         ["Compute power with and without a Bonferroni correction.",
          "Compute the required n increase for m = 5, 10, 50.",
          "Compare to a false discovery rate approach.",
          "Recommend a strategy."],
         "A multiplicity cost comparison."),
        ("Post-hoc power critique",
         "Show why it is uninformative.",
         ["Simulate studies under the null and at a true effect.",
          "Compute post-hoc power at the observed effect.",
          "Show it is a monotone function of the p-value.",
          "Compute retrospective power at the a priori effect instead."],
         "A demonstration with a replacement metric."),
        ("Power for proportions and counts",
         "Beyond means.",
         ["Implement power for a two-proportion test.",
          "Implement power for a rate comparison with Fisher's z.",
          "Show how a rare baseline inflates required n.",
          "Apply to a realistic conversion example."],
         "Power calculations for non-mean outcomes."),
        ("Full power analysis",
         "A design document.",
         ["State the business threshold and convert it to an effect size.",
          "Estimate and inflate the variance.",
          "Compute required n, horizon and MDE.",
          "Publish the power curve and the decision rule."],
         "A design document a reviewer would approve."),
    ],
    quiz=[
        ("What does power depend on?", ["The observed result", "The specified effect size, variance, sample size and alpha", "The p-value", "Only the sample size"], 1, "Because it depends on the assumed effect, power is computable before data collection."),
        ("Why is a non-significant result from a small study uninformative?", ["The test was wrong", "The study's minimum detectable effect may be far larger than any meaningful effect", "Power is undefined", "Alpha was too high"], 1, "With n = 20 per arm you can only detect effects of about d = 0.9."),
        ("What is Cohen's d?", ["A correlation", "The mean difference in pooled standard deviation units", "A variance ratio", "A power value"], 1, "Standardising the difference makes it comparable across scales."),
        ("Why use Hedges' g?", ["It is smaller", "It corrects the upward bias of d at small sample sizes", "It handles outliers", "It assumes normality"], 1, "The correction is material below roughly n = 20 per group."),
        ("Why inflate a pilot variance?", ["To be conservative", "Small pilots give biased-low variance estimates", "Because the formula requires it", "To reduce n"], 1, "Under-estimated variance is the most common cause of under-powered studies."),
        ("Why is post-hoc power uninformative?", ["It is hard to compute", "Computed at the observed effect it is a monotone function of the p-value", "It assumes normality", "It ignores alpha"], 1, "Retrospective power is meaningful only at the a priori effect."),
        ("How does MDE scale with n?", ["Linearly", "As 1/sqrt(n), so quadrupling the sample halves it", "As 1/n", "It does not depend on n"], 1, "That is why small studies are so uninformative."),
        ("Why does one-sided power exceed two-sided?", ["It uses a different test", "A directional alternative rejects at a less extreme threshold", "It needs less data", "Alpha is larger"], 1, "The gain is real and must be justified by a pre-specified direction."),
        ("What is Cohen's 0.5 'medium' threshold?", ["A universal constant", "A convention that must be translated into business units before use", "A power value", "A sample size"], 1, "A 0.5 effect in revenue may dwarf a 1.2 effect in latency."),
        ("What does power curve planning buy?", ["Larger samples", "An explicit view of what the design can and cannot detect", "Lower alpha", "Fewer comparisons"], 1, "It converts a sample constraint into a statement about resolution."),
        ("What happens to power when alpha is Bonferroni-adjusted?", ["It increases", "It decreases, so required n grows", "It is unchanged", "It becomes one-sided"], 1, "Each of m comparisons must run at alpha/m, which lowers sensitivity per test."),
        ("What is Glass's delta?", ["A standardised difference using the control group standard deviation", "A nonparametric effect size", "A variance estimate", "A correction for skew"], 0, "It is the alternative to pooling when variances are unequal."),
        ("Why is the effect size for planning not the observed one?", ["It is harder to compute", "Using the observed effect plans on the outcome and inflates power claims", "It is biased", "It is undefined"], 1, "Planning must be independent of the data you have not yet seen."),
        ("What should accompany a non-significant result?", ["A larger sample suggestion", "Power and the minimum detectable effect", "A different test", "A one-sided test"], 1, "It converts an ambiguous null into a statement about what the study could detect."),
        ("How does a business threshold become an effect size?", ["It cannot", "Translate it into the metric's standard deviation units and use it as the planning effect", "It becomes alpha", "It sets the sample size"], 1, "The threshold is the design's resolution requirement, expressed in domain units."),
    ],
    vision=dict(
        future="Power analysis becomes continuous and automated: variance and "
               "effect-size priors estimated from historical experiments, with "
               "designs proposed rather than validated after the fact. Effect sizes "
               "in domain units replace universal thresholds.",
        good=[
            "Planning effect sizes come from business thresholds or literature, never from observed results.",
            "Pilot variances are inflated with a recorded justification.",
            "Minimum detectable effect is reported with every design and every null result.",
            "Multiplicity is priced into both alpha and required sample size.",
        ],
        ladder=[
            ("L1", "Size", "Required n from alpha, power and an effect size."),
            ("L2", "Resolve", "MDE for a fixed sample, expressed in business units."),
            ("L3", "Curve", "Power curves across n and effects for a budget conversation."),
            ("L4", "Automate", "Priors from historical experiments and design recommendations."),
        ],
        behaviors="Compute power before collecting data and report MDE after it. "
                  "Translate every effect size into units the business recognises. "
                  "Never quote post-hoc power.",
        anti=[
            "'Not significant' reported without the MDE that explains it.",
            "Power computed from the observed effect.",
            "An uninflated pilot variance used to size a definitive study.",
            "Cohen's thresholds quoted without a business translation.",
        ],
        trends=[
            "Automatic effect-size priors from historical experiment outcomes.",
            "Bayesian design with prior predictive power as the planning tool.",
            "Equivalence and non-inferiority designs requiring their own power treatment.",
            "Multiobjective design allocating a fixed budget across many endpoints.",
        ],
        d30="Implement effect sizes and power for means, reporting MDE alongside.",
        d60="Compute power curves and required n with inflated pilot variance.",
        d90="Price multiplicity, critique post-hoc power, and publish a full design document.",
        metrics=[
            "My effect size came from a threshold, not from the observed result.",
            "My variance is inflated if from a small pilot.",
            "I report the MDE my design can achieve.",
            "I never quote post-hoc power as evidence.",
        ],
        closer="Power is what makes a null result explainable, and effect size in "
               "business units is what makes a significant result actionable.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Power Analysis for a Real Decision",
        brief="Convert a business threshold into an effect size, size the study, "
              "and report the design's resolution honestly.",
        timebox="3 hours",
        why="Power planning is where studies are won or wasted, and the MDE is what "
            "you report when a result comes back null.",
        requirements=[
            "Effect sizes: d, Hedges' g, r and a proportion measure, with a business translation.",
            "Required n per arm from alpha, power and an inflated variance.",
            "MDE for a grid of n, expressed in business units.",
            "Power curves across effect sizes and both sidednesses.",
            "Multiplicity pricing: required n for m = 1, 5, 10, 50.",
            "Post-hoc power critique with a retrospective alternative at the a priori effect.",
            "A design document with the power curve and decision rule.",
        ],
        steps=[
            ("1", "30m", "Business threshold to effect size", "A defensible planning effect"),
            ("2", "30m", "Pilot variance and documented inflation", "A planning variance"),
            ("3", "30m", "Required n, horizon and MDE", "A sized design"),
            ("4", "30m", "Power curves with operating points marked", "A resolution chart"),
            ("5", "30m", "Multiplicity cost table", "A pricing table"),
            ("6", "30m", "Post-hoc power critique", "A demonstration plus a replacement"),
            ("7", "30m", "Design document", "A reviewer-ready plan"),
        ],
        diagram=""" business threshold (e.g. +2% conversion)
     |
 translate into the metric's sd units -> planning effect d
     |
 pilot variance --> inflate by a documented factor
     |
 alpha, power  ->  required n per arm  ->  horizon at traffic
     |                    |
 MDE at that n        power curves (effects x sidedness)
     |                    |
 multiplicity pricing (m = 1, 5, 10, 50) -> revised n
     |
 post-hoc power critique -> retrospective power at the a priori effect
     |
 design document: effect, n, horizon, MDE, curves, decision rule""",
        notes=[
            "Start from the business threshold, not from a literature effect size; the translation is the deliverable.",
            "Record the inflation factor and its justification alongside the design.",
            "The MDE table is what you will quote if the result is null, so build it before you need it.",
            "Post-hoc power is a function of the p-value; demonstrate it and then supply the a-priori alternative.",
        ],
        deliverables=[
            "Planning effect size with the business translation shown.",
            "Required n, horizon and MDE table.",
            "Power curves with operating points and a multiplicity cost table.",
            "Design document with the decision rule and a post-hoc power critique.",
        ],
        grading=[
            ("Translation", "25%", "Business threshold converted to an effect size with reasoning"),
            ("Sizing", "25%", "Inflated variance, required n, horizon and MDE all correct"),
            ("Curves", "20%", "Power curves across effects and sidedness with marked points"),
            ("Multiplicity", "15%", "Required n growth priced honestly"),
            ("Honesty", "15%", "MDE reported; post-hoc power critiqued with a replacement"),
        ],
        stretch=[
            "Add power for logistic regression and count outcomes.",
            "Add equivalence testing power, which inverts the framing.",
            "Add a budget optimiser allocating a fixed total across several endpoints.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Experiment Power and Resolution Standards",
        scenario="A platform team runs 40 experiments a month. Three were launched "
                 "with no power calculation, one 'inconclusive' result was used to "
                 "justify abandoning a promising direction, and the business has "
                 "stopped trusting experiment readouts.",
        scale=[
            ("Experiments", "~40 per month across 9 teams"),
            ("Current practice", "power optional; inconclusive results read as 'no effect'"),
            ("Failures", "3 unpowered launches; 1 promising direction abandoned on a null result"),
            ("Constraint", "traffic varies enormously by product surface, so designs are not interchangeable"),
            ("Requirement", "power and resolution reported as a standard part of every readout"),
        ],
        diagram=""" experiment intake (metric, surface, traffic)
     |
 variance service: per metric x surface, from historical experiments
     |  (inflated, with a documented factor)
 power service: alpha, power, MDE -> required n per arm
     |                          -> horizon at that surface's traffic
     |
 design accepted only if the horizon fits the decision calendar
     |
 readout: effect + interval + MDE + power (retrospective, at the a priori effect)
     |
 inconclusive handled as a power statement with options
     |
 post-hoc: abandoned directions reviewed; MDE recorded against the business threshold""",
        components=[
            ("Variance and power services",
             ["Per-metric, per-surface variance estimated from historical experiment outcomes rather than entered by hand",
              "Variance inflated by a documented factor with the reasoning stored",
              "Power computed under the a priori effect, with sidedness chosen explicitly",
              "Required n per arm returned with the horizon at that surface's real traffic"]),
            ("Resolution reporting",
             ["MDE published with every experiment at intake and in every readout",
              "MDE expressed in business units so 'what we could not detect' is meaningful to stakeholders",
              "Achievement against the business threshold recorded: can this surface even detect it?",
              "Surfaces where the threshold is undetectable at achievable n are flagged before launch"]),
            ("Inconclusive handling",
             ["Null results reported as a power statement with the MDE, never as 'no effect'",
              "Retrospective power computed at the a priori effect, not the observed one",
              "Standard options presented: extend as pre-registered, accept a null within the MDE, or stop",
              "Abandoned directions recorded with their MDE so future reviews can distinguish undetectable from absent"]),
            ("Governance and learning",
             ["Design acceptance requires a power calculation with a stated effect and variance",
              "Overrides for deadline pressure expire and are reviewed with outcomes",
              "Quarterly review comparing business thresholds against achievable MDEs per surface",
              "Post-hoc power critique documented so teams stop quoting it as evidence"]),
        ],
        timeline=[
            ("Week 1-2", "Variance service per metric and surface from historical experiments"),
            ("Week 3", "Power service returning n, horizon and MDE at intake"),
            ("Week 4", "Resolution reporting in every readout; MDE in business units"),
            ("Week 5-6", "Inconclusive handling with standard options; override review"),
            ("Week 8", "Quarterly review of thresholds versus achievable MDEs; post-hoc power guidance published"),
        ],
        runbook=[
            "# Variance for a metric on a surface, with the inflation applied",
            "curl -s 'localhost:8082/variance?metric=conversion&surface=checkout' | jq '{raw,inflated,factor,rationale}'",
            "",
            "# Power service result at intake",
            "curl -s 'localhost:8082/power?metric=conversion&surface=checkout&aod=0.002&alpha=0.05&power=0.8' | jq '{requiredN,horizonDays,mde,mdeBusiness}'",
            "",
            "# Can this surface detect the business threshold at all?",
            "curl -s 'localhost:8082/feasibility?metric=conversion&surface=checkout&aod=0.002' | jq '{detectable,achievableN,daysAvailable,verdict}'",
            "",
            "# Readout with resolution, including inconclusive results",
            "curl -s 'localhost:8082/readout?experiment=exp-221' | jq '{effect,ci,mde,powerRetrospective,verdict}'",
            "",
            "# Inconclusive experiments in the last quarter with their MDE",
            "curl -s 'localhost:8082/inconclusive?window=90d' | jq '.[] | {id,mde,businessThreshold,option}'",
        ],
        metrics=[
            "Compliance: experiments launched with a power calculation (target 100%).",
            "Detection: experiments whose reported verdict includes an MDE (target 100%).",
            "Feasibility: surfaces where the business threshold is undetectable flagged before launch.",
            "Outcome: directions abandoned on null results reviewed with their MDE recorded.",
            "Trust: experiment readouts used in decisions with resolution stated; overrides reviewed monthly.",
        ],
        failures=[
            ("A team launches without a power calculation under deadline", "Requirement blocks rather than guides", "Return n, horizon and MDE instantly; allow override that expires and is reviewed"),
            ("Reported inconclusive is read as no effect", "MDE not reported", "MDE and retrospective power required in every readout"),
            ("Power computed from the observed effect", "Post-hoc power habit", "Power service computes at the a priori effect; post-hoc power guidance published"),
            ("A surface cannot detect its business threshold at any achievable n", "Feasibility never checked", "Feasibility check at intake flags undetectable thresholds with alternatives"),
            ("Variance drifts as the metric's implementation changes", "Variance cached too long", "Variance service refreshes on a schedule and alerts on material shifts"),
        ],
        backlog=[
            "Automatic effect-size priors learned from resolved business thresholds.",
            "Power for count and ratio metrics beyond means and proportions.",
            "Equivalence-testing support for 'no meaningful effect' questions.",
            "Budget optimiser allocating traffic across a portfolio of concurrent experiments.",
            "Detection of metric definition changes invalidating cached variances.",
        ],
        urls=URLS,
        closer="The deliverable is a platform where every experiment launches with a "
               "computed sample size, every readout states the smallest effect it "
               "could have detected, and an inconclusive result is read as a "
               "resolution statement rather than a verdict.",
    ),
))
