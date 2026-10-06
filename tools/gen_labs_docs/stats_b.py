# -*- coding: utf-8 -*-
"""Tailored specs for labs/statistics/lab04 .. lab06."""

from stats_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab04
SPECS.append(dict(
    track="statistics", lab="lab04", full_set=True, level="Intermediate",
    title="ANOVA", main_class="com.statistics.lab04.Anova",
    problem="Three or more groups and one question: does at least one of them "
            "differ? If yes, the interesting work is finding which pairs differ, "
            "not just declaring an omnibus result.",
    why_now="Comparing groups one pair at a time inflates the error rate; ANOVA "
             "is the design that avoids it and then localises differences properly.",
    objectives=[
        "Compute one-way and two-way ANOVA tables by hand",
        "Read the F-statistic and its degrees of freedom correctly",
        "Explain why post-hoc comparisons need their own correction",
        "Implement Tukey, Bonferroni and Scheffe methods",
        "Verify assumptions and know which test replaces ANOVA when they fail",
        "Report effect size, not just the F-test result",
    ],
    concepts=[
        ("Variance partitioning",
         "Total variability splits into between-group and within-group components. "
         "The F-statistic is the ratio of mean squares: if groups are really "
         "identical, that ratio is approximately 1 regardless of group means."),
        ("One-way versus two-way",
         "One-way compares k groups on one factor. Two-way adds a second factor and "
         "splits variance into both main effects plus their interaction. The "
         "interaction is the part most analyses skip and most often matters."),
        ("Post-hoc tests are not optional",
         "A significant omnibus test says something differs, not what. Comparing all "
         "pairs with t-tests inflates the family-wise error rate, which is why "
         "Tukey, Bonferroni and Scheffe exist: each spends alpha differently across "
         "the family of comparisons."),
        ("Assumptions matter, and they are checkable",
         "Normality within groups, homogeneity of variance, independent observations. "
         "Welch's ANOVA handles unequal variances; rank-based alternatives handle "
         "non-normality, and both exist because violations are common."),
        ("Effect size is the answer",
         "Eta-squared is the proportion of variance explained by the factor. An F "
         "test on large data is significant for trivial effects, so the omnibus test "
         "must be paired with an effect size."),
        ("Fixed versus random effects",
         "Fixed effects test specific levels you chose. Random effects test whether "
         "a sample of levels generalises, which changes the error term and the "
         "interpretation of the p-value."),
    ],
    formulas=[
        ("SS_total = SS_between + SS_within", "Variance decomposition", "the identity behind ANOVA"),
        ("F = MS_between / MS_within", "F-statistic", "1 under a true null"),
        ("MS_between = SSB/(k\u22121)", "Mean square between", "df for the numerator"),
        ("MS_within = SSW/(N\u2212k)", "Mean square within", "df for the denominator"),
        ("\u03b7\u00b2 = SSB/SST", "Eta-squared", "share of variance explained"),
        ("interaction SS = SST - SSA - SSB", "Two-way interaction", "the term usually skipped"),
        ("Tukey HSD = q / sqrt(MSS/n)", "Post-hoc", "family-wise controlled"),
        ("Bonferroni: alpha' = alpha / m", "Correction", "conservative, always valid"),
    ],
    flow=[
        "State the hypothesis: at least one group mean differs, with any planned contrasts specified in advance.",
        "Check assumptions: independence, residual normality, homogeneity of variance.",
        "Compute the ANOVA table by hand and verify the variance decomposition sums.",
        "If significant, run a post-hoc method chosen for the comparison structure.",
        "Report the effect size with a confidence interval, not only the F-test.",
        "If assumptions fail, switch to Welch's ANOVA or the rank-based alternative.",
    ],
    assumptions=[
        "Observations are independent within and between groups",
        "Residuals are approximately normal within each group",
        "Group variances are homogeneous for the classical F-test",
        "Groups are independent samples, not repeated measures on the same subject",
        "Any planned contrasts were specified before seeing the data",
        "Sample sizes per group are known and reported, since they affect power",
    ],
    pitfalls=[
        ("Significant omnibus test, no idea what differs", "stopping at the F-test", "run a post-hoc method and report which pairs"),
        ("Pairwise t-tests without correction", "family-wise error inflation", "Tukey, Bonferroni or Scheffe, chosen for the comparison structure"),
        ("ANOVA on clearly different variances", "homogeneity violated", "Welch's ANOVA, and check the residual plot"),
        ("A significant result with eta-squared of 0.002", "large n, tiny effect", "report the effect size; the F-test alone is uninformative"),
        ("Repeated measures on the same subjects analysed as independent", "independence violated", "use a repeated-measures ANOVA or a mixed model"),
        ("The interaction term omitted from a two-way design", "wrong error term", "fit the interaction; it often changes the main-effect conclusions"),
    ],
    java=[
        ("Grouped accumulation for SSB, SSW, SST", "one pass per group with Welford statistics"),
        ("Incomplete beta for the F CDF", "p-values without lookup tables"),
        ("Q distribution for Tukey HSD", "studentised range function by numerical integration"),
        ("record AnovaTable(double f, int df1, int df2, double p, double etaSquared)", "statistic and effect size together"),
        ("Residual diagnostics from a fitted linear model", "assumption checks feed the choice of test"),
    ],
    links=[
        "**lab03** is the two-group special case ANOVA generalises.",
        "**lab05** provides the regression machinery that produces the ANOVA decomposition.",
        "**lab09** provides the rank-based alternatives when assumptions fail.",
        "**lab10** supplies the power calculation for a given number of groups.",
    ],
    checklist=[
        "I can compute an ANOVA table by hand and verify the decomposition sums.",
        "I know whether my design is one-way, two-way or repeated measures.",
        "I run a post-hoc method after a significant omnibus test.",
        "I report an effect size with an interval.",
        "I check homogeneity of variance before using the classical F-test.",
        "I fit the interaction term in a two-way design.",
    ],
    cards=[
        ("What does an F-statistic of 1 mean?", "The between-group variance equals the within-group variance, exactly what a true null predicts."),
        ("Why is eta-squared reported alongside the F-test?", "Because with large n any tiny effect becomes significant, so the F-test alone says nothing about magnitude."),
        ("Why not run pairwise t-tests after ANOVA?", "The family-wise error rate inflates with the number of pairs, producing false differences."),
        ("What does Tukey's HSD control?", "The family-wise error rate across all pairwise comparisons, using the studentised range distribution."),
        ("How does Bonferroni differ from Tukey?", "Bonferroni divides alpha by the number of comparisons and is conservative; Tukey uses the range distribution and is less conservative."),
        ("What violates the ANOVA assumptions most often?", "Unequal variances and non-normal residuals, especially with small n."),
        ("What is Welch's ANOVA for?", "Unequal variances; it adjusts the error degrees of freedom instead of assuming homogeneity."),
        ("When does the interaction term matter most?", "When the effect of one factor depends on the level of another, which changes the main-effect interpretation."),
    ],
    extra_cards=[
        ("What is the error term in a two-way ANOVA?", "Usually the residual mean square, including the interaction; omitting the interaction changes it."),
        ("How do I choose between Tukey, Bonferroni and Scheffe?", "Tukey for all pairs, Bonferroni for a few pre-planned contrasts, Scheffe for all possible contrasts including complex ones."),
        ("What does fixed versus random effect change?", "Which levels the error term is estimated from, and therefore how the p-value generalises."),
        ("Why does ANOVA need replication?", "Without within-cell replication the error term cannot be separated from the interaction."),
    ],
    math=[
        ("One-way ANOVA decomposition",
         "SSB = sum_j n_j (xbar_j - xbar)^2\nSSW = sum_j sum_i (x_ij - xbar_j)^2\nSST = SSB + SSW\nF = (SSB/(k-1)) / (SSW/(N-k)), df = (k-1, N-k)",
         "The decomposition holds identically, which makes it easy to verify by hand. "
         "The F statistic compares variance explained by grouping against variance "
         "left over, so it is 1 in expectation under a true null regardless of group "
         "means.",
         "Groups [10, 12, 11], [14, 16, 15], [9, 10, 8]: means 11, 15, 9; grand mean "
         "11.667. SSB = 3(0.667\u00b2 + 3.333\u00b2 + 2.667\u00b2) = 48.67; SSW = 2(1 + 1 + 0) + "
         "2(1 + 1 + 0) + 2(1 + 0 + 1.333) = 8.67. F = 16.22/2.89 = 5.62 with df (2, 6), "
         "p \u2248 0.046."),
        ("Effect size and why the F-test alone is misleading",
         "eta^2 = SSB/SST\nwith large N, t \u2248 effect_size * sqrt(N)\nso p can be tiny while eta^2 is negligible",
         "The test statistic grows with sample size while the effect size does not. "
         "A large-n study can detect a difference of almost no practical "
         "consequence, which is why the omnibus test must be reported with an "
         "effect size and ideally a confidence interval on it.",
         "n = 10,000 per group with a true difference of 0.02 standard deviations: "
         "t \u2248 2.83, p \u2248 0.005, yet eta\u00b2 = 0.0002, explaining 0.02% of variance. "
         "Statistically significant, operationally irrelevant."),
        ("Multiple comparisons and family-wise error",
         "family-wise error = 1 - (1 - alpha)^m for m independent tests at alpha\nBonferroni: alpha' = alpha/m, exact bound by union inequality\nTukey: uses the studentised range, less conservative and still FWER controlled",
         "Any pair of comparisons increases the chance of at least one false "
         "positive. Bonferroni is valid by the union bound regardless of "
         "dependence, which is why it is the safe default; Tukey is more powerful "
         "because it exploits the joint distribution.",
         "m = 10 comparisons at alpha = 0.05: unadjusted FWER is "
         "1 - 0.95^10 = 0.40. Bonferroni uses alpha' = 0.005 per test, giving FWER at "
         "most 0.05. Tukey typically needs alpha' around 0.017 for the same family."),
        ("Welch's ANOVA and unequal variances",
         "group i weight w_i = n_i/s_i^2\nF = sum w_i (xbar_i - xbar_w)^2 / (k-1)\ndf = ((sum w_i (xbar_i - xbar_w)^2)^2 / (k-1)) / (sum (1/(n_i-1))(1 - w_i/W)^2)",
         "Equal variances are not needed; Welch down-weights noisy groups. The "
         "fractional error degrees of freedom are smaller than the classical N-k, "
         "which is the conservative direction, and Welch's test is never less "
         "powerful asymptotically than the classical one.",
         "Group variances of 1, 1 and 9 with n = 10 each: the classical F test is "
         "dominated by the noisy group and its p-value is anti-conservative. "
         "Welch's df falls well below 27, widening the interval and correcting the "
         "p-value."),
        ("Two-way ANOVA and the interaction",
         "SST = SSA + SSB + SSAB + SSE\nSSAB = SST - SSA - SSB - SSE\ntest each against SSE",
         "The interaction captures whether the effect of one factor depends on the "
         "level of the other. When it is significant, main effects should not be "
         "interpreted on their own, and a separate-effects analysis is the honest "
         "follow-up.",
         "Factor A at two levels, B at two, with a 5-unit effect of A at B=low and "
         "zero at B=high: SSA is positive, but the true story is the interaction. "
         "Reporting only main effects would say 'A matters, B does not' and be wrong "
         "about half the cells."),
    ],
    math_traps=[
        "Computing MS within as SSW/N instead of SSW/(N-k).",
        "Reporting an F-test p-value with no effect size.",
        "Comparing pairs with unadjusted t-tests.",
        "Omitting the interaction from a two-way design.",
        "Using the classical F-test when variances differ substantially.",
    ],
    math_problems=[
        "Compute a full one-way ANOVA table by hand for three groups and verify SST = SSB + SSW.",
        "Compute eta-squared and a confidence interval for it for a given design.",
        "Show the family-wise error inflation for m comparisons at alpha = 0.05.",
        "Compare classical and Welch ANOVA on data with variances in a 1:9 ratio.",
        "Fit a two-way design with replication and decompose the interaction term.",
    ],
    tree="""src/
  Anova.java              driver: one-way, two-way, post-hoc, diagnostics
  AnovaTable.java         SSB, SSW, SST, df, F, p, eta-squared
  OneWayAnova.java        variance partitioning and the F test
  TwoWayAnova.java        main effects plus interaction
  PostHoc.java            Tukey, Bonferroni, Scheffe
  AssumptionChecks.java   residual normality, homogeneity, independence notes""",
    tree_note="AnovaTable carries eta-squared alongside the p-value, so the "
              "omnibus result cannot be reported as a bare 'significant' in this "
              "codebase.",
    types=[
        ("AnovaTable", "sums of squares, degrees of freedom, F, p-value and effect size"),
        ("OneWayAnova", "single-factor partition and F test with a Welch variant"),
        ("TwoWayAnova", "both main effects plus interaction, each against the residual"),
        ("PostHoc", "Tukey HSD, Bonferroni and Scheffe with a declared method"),
    ],
    patterns=[
        ("Variance partitioning verified by identity",
         "The decomposition is asserted to sum, which catches transcription errors "
         "immediately, and eta-squared travels with the p-value.",
         """public AnovaTable oneWay(List<double[]> groups) {
    double grand = 0; int n = 0;
    for (double[] g : groups) { for (double v : g) grand += v; n += g.length; }
    grand /= n;
    double ssb = 0, ssw = 0;
    for (double[] g : groups) {                        // within-group deviations
        double m = mean(g);
        ssb += g.length * (m - grand) * (m - grand);
        for (double v : g) ssw += (v - m) * (v - m);
    }
    double sst = ssb + ssw;                            // identity, asserted below
    assertClose(sst, totalSumOfSquares(groups, grand), 1e-9);
    int k = groups.size();
    double f = (ssb / (k - 1)) / (ssw / (n - k));
    return new AnovaTable(ssb, ssw, sst, f, k - 1, n - k,
            fSurvival(f, k - 1, n - k), ssb / sst);     // effect size, not optional
}"""),
        ("Assumption checks that choose the test",
         "Homogeneity is tested and the decision recorded; unequal variances route "
         "to Welch rather than being ignored.",
         """public AnovaTable analyse(List<double[]> groups, boolean allowWelch) {
    AssumptionReport checks = AssumptionChecks.inspect(groups);
    if (checks.heteroscedastic() && !allowWelch)
        return AnovaTable.withWarning(oneWayWelch(groups),
                "variances differ materially; classical F p-value is anti-conservative");
    if (!checks.normalResiduals())
        return AnovaTable.withWarning(oneWayWelch(groups),
                "residual normality doubtful at this n; prefer the rank-based alternative");
    return oneWay(groups);
}"""),
    ],
    costs=[
        ("Group statistics", "O(N)", "one Welford pass per group"),
        ("One-way F test", "O(1) after statistics", "incomplete beta evaluation"),
        ("Two-way decomposition", "O(N)", "same data, more partitions"),
        ("All-pairs post-hoc", "O(k\u00b2) comparisons", "studentised range per comparison"),
    ],
    numerics=[
        "Compute SSW with n-k, not n, for the denominator mean square.",
        "Evaluate the F distribution with an incomplete beta function, not a table.",
        "Always report an effect size with the omnibus test.",
        "Test homogeneity before choosing classical or Welch.",
        "Fit the interaction term whenever a second factor is present.",
    ],
    tests=[
        "SSB + SSW equals SST to 1e-9 for random data.",
        "Data from identical distributions yields F near 1 and a large p-value.",
        "Eta-squared equals SSB/SST and lies in [0, 1].",
        "Welch reproduces classical results when variances are equal.",
        "A two-way decomposition with an additive design shows near-zero interaction.",
        "Tukey's family-wise error is at or below alpha in a simulation under the null.",
    ],
    extensions=[
        "Add Welch's ANOVA and the rank-based alternative in the same interface.",
        "Add planned contrasts with the correct error term.",
        "Add repeated-measures ANOVA for within-subject designs.",
    ],
    code_checklist=[
        "Variance decomposition asserted to sum",
        "Effect size reported with every omnibus test",
        "Post-hoc method declared and family-wise error controlled",
        "Assumption checks recorded and used to choose the test",
        "Interaction fitted whenever a second factor exists",
        "Degrees of freedom reported for both numerator and denominator",
    ],
    exercise_selfcheck=[
        "I can build an ANOVA table by hand.",
        "My omnibus test always comes with an effect size.",
        "I know which post-hoc method my comparison structure needs.",
        "I check homogeneity before using the classical F-test.",
    ],
    exercises=[
        ("One-way ANOVA from scratch",
         "The table, computed and verified.",
         ["Compute group means, grand mean, SSB, SSW and SST.",
          "Assert the decomposition sums.",
          "Compute F, df and the p-value.",
          "Compute eta-squared and verify on a hand example."],
         "A verified ANOVA implementation."),
        ("Post-hoc comparisons",
         "Localise the differences properly.",
         ["Implement Tukey HSD with the studentised range.",
          "Implement Bonferroni and Scheffe.",
          "Compare pairwise p-values across methods on the same data.",
          "Explain the conservatism differences."],
         "A three-method comparison with an explanation."),
        ("Assumptions and alternatives",
         "Know when ANOVA is the wrong tool.",
         ["Generate residual plots and test homogeneity.",
          "Show the classical F-test is anti-conservative under unequal variances.",
          "Implement Welch's ANOVA and compare.",
          "Route non-normal residuals to the rank-based test."],
         "A violation demonstration with a working alternative."),
        ("Two-way ANOVA",
         "Main effects and the interaction.",
         ["Decompose variance into A, B, interaction and error.",
          "Test each against the residual mean square.",
          "Construct data where the interaction is significant.",
          "Explain why main effects must not be read alone."],
         "A two-way analysis with an interaction story."),
        ("Effect size and power",
         "Is the difference worth anything?",
         ["Compute eta-squared for a large-n, tiny-effect design.",
          "Compute statistical power for a given effect and group count.",
          "Report the minimum detectable effect at the chosen n.",
          "Write the interpretation for a non-technical reader."],
         "An effect size and power report."),
        ("Multiple comparisons in practice",
         "Measure the inflation you create.",
         ["Run all pairwise t-tests on data with one real difference.",
          "Measure the family-wise false positive rate.",
          "Apply Tukey and Bonferroni and re-measure.",
          "Compare the false discovery counts."],
         "A measured correction comparison."),
        ("Planned contrasts",
         "Test what you actually planned.",
         ["Implement contrast coefficients summing to zero.",
          "Test planned contrasts against the correct error term.",
          "Compare with post-hoc after a significant omnibus.",
          "Explain why planning reduces the burden."],
         "A contrast implementation with a comparison."),
        ("Full ANOVA report",
         "Produce something defensible.",
         ["Design the study with a power calculation.",
          "Run the analysis with assumption checks.",
          "Run post-hoc and report pairwise differences with intervals.",
          "Write the conclusion in business terms with limitations."],
         "A report a reviewer would accept."),
    ],
    quiz=[
        ("What does an F-statistic near 1 indicate?", ["Groups are identical", "Between-group variance equals within-group variance, as a true null predicts", "The test failed", "The effect is large"], 1, "F is a variance ratio, so 1 is the null's expectation."),
        ("What does eta-squared measure?", ["Statistical significance", "The proportion of total variance explained by the factor", "The sample size", "The power"], 1, "It is the effect size that keeps a large-n significant result from being over-read."),
        ("Why run post-hoc tests after a significant ANOVA?", ["To increase power", "The omnibus test says something differs, not which; comparisons need family-wise error control", "To reduce error", "To increase sample size"], 1, "Uncontrolled pairwise tests inflate the family-wise error rate."),
        ("How does Bonferroni differ from Tukey?", ["Bonferroni is less conservative", "Bonferroni divides alpha by the number of comparisons; Tukey uses the studentised range", "They are identical", "Tukey requires normality"], 1, "Bonferroni is valid by the union bound; Tukey exploits the joint distribution."),
        ("What violates ANOVA assumptions most often?", ["Too much data", "Unequal variances and non-normal residuals", "The number of groups", "Replication"], 1, "Both are common at small n and both have well-known corrections."),
        ("What is Welch's ANOVA for?", ["Non-normality", "Unequal variances, with fractional error degrees of freedom", "Repeated measures", "Planned contrasts"], 1, "It down-weights noisy groups and widens the interval conservatively."),
        ("When does the interaction term matter most?", ["When main effects are large", "When the effect of one factor depends on the level of the other", "When n is large", "When residuals are normal"], 1, "Significant interaction means main effects cannot be read on their own."),
        ("Why can a significant ANOVA have a negligible effect size?", ["It cannot", "With large n any small difference becomes statistically significant", "Because eta-squared is unreliable", "Because p is miscomputed"], 1, "The test statistic scales with sqrt(n) while the effect does not."),
        ("What is the denominator mean square's degrees of freedom?", ["k \u2212 1", "N \u2212 k", "N \u2212 1", "k"], 1, "The residual df is N minus the number of groups."),
        ("Fixed versus random effects changes...", ["The data", "Which levels the error term is estimated from, and how the result generalises", "The sample size", "The null hypothesis"], 1, "Random effects generalise to a population of levels rather than the levels tested."),
        ("Why does a two-way design need replication?", ["For accuracy", "To separate the interaction from the error term", "To reduce cost", "To satisfy assumptions"], 1, "Without within-cell replication the error and interaction are confounded."),
        ("What is Scheffe's method for?", ["Few pre-planned contrasts", "All possible contrasts including complex comparisons, with FWER control", "Repeated measures", "Non-normality"], 1, "It generalises to arbitrary contrasts but is the most conservative."),
        ("A significant F but no post-hoc difference found means...", ["Nothing happened", "Check power and the pairwise method; the omnibus may be driven by one pair", "The test failed", "The data is normal"], 1, "With many groups the omnibus can detect a small overall difference that individual pairs cannot localise."),
        ("How do you report an ANOVA result?", ["F and p only", "F, df, p, effect size with an interval, and the post-hoc detail", "Eta-squared only", "The group means only"], 1, "A bare F-test p-value is uninterpretable without magnitude and localisation."),
        ("What is the rank-based alternative to one-way ANOVA?", ["Friedman test", "Kruskal-Wallis test", "Wilcoxon signed-rank", "Sign test"], 1, "Kruskal-Wallis compares k independent groups without the normality assumption."),
    ],
    vision=dict(
        future="ANOVA persists as the workhorse for comparing groups, increasingly "
               "alongside mixed-effects models that handle nesting, repeated "
               "measures and varying variance structure. The discipline that matters "
               "is reporting effect sizes and controlling multiplicity, not "
               "memorising tables.",
        good=[
            "Variance decompositions are verified by the summing identity.",
            "Every omnibus test is reported with an effect size and an interval.",
            "Post-hoc methods are chosen for the comparison structure and declared.",
            "Assumption checks determine the test, not a footnote.",
        ],
        ladder=[
            ("L1", "Test", "One-way ANOVA table, F, df and p-value."),
            ("L2", "Quantify", "Eta-squared and a confidence interval on it."),
            ("L3", "Localise", "Tukey, Bonferroni or Scheffe with a declared method."),
            ("L4", "Adapt", "Welch, mixed effects, and rank-based alternatives as needed."),
        ],
        behaviors="Report magnitude with every test. Control the family-wise error "
                  "rate rather than comparing everything. Check assumptions and let "
                  "them pick the method.",
        anti=[
            "A bare 'F(2, 27) = 4.1, p < .05, significant' with no effect size.",
            "Twenty pairwise t-tests after a significant omnibus.",
            "A two-way analysis with the interaction dropped to make main effects look clean.",
            "Classical F-tests on variances differing by an order of magnitude.",
        ],
        trends=[
            "Mixed-effects models replacing fixed-effect ANOVA for nested and repeated designs.",
            "Variance-component estimation with heteroscedasticity-robust standard errors.",
            "Automatic reporting of effect sizes with confidence intervals in statistical software.",
            "Multiplicity control framed as expected false discoveries rather than family-wise error.",
        ],
        d30="Implement the one-way table with the decomposition asserted and effect size attached.",
        d60="Implement Tukey, Bonferroni and Scheffe and compare their conservatism.",
        d90="Add Welch's ANOVA, a two-way design with interaction, and assumption-driven test selection.",
        metrics=[
            "I can build an ANOVA table by hand.",
            "My omnibus tests always carry an effect size.",
            "My post-hoc method matches the comparison structure.",
            "Assumption checks choose the test rather than decorate the report.",
        ],
        closer="A significant F-test tells you something differed; the effect size "
               "and the post-hoc detail tell you whether anyone should care.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Multi-Group Comparison with Honest Reporting",
        brief="Design a multi-group study, run the ANOVA with assumption checks, "
              "and localise differences with a declared post-hoc method.",
        timebox="3 hours",
        why="Comparing groups is where statistical inflation hides: omnibus tests "
            "without effect sizes, and pairwise tests without correction.",
        requirements=[
            "One-way ANOVA computed by hand with the decomposition asserted.",
            "Effect size with a confidence interval for every test.",
            "Three post-hoc methods compared, with a simulation measuring family-wise error.",
            "Assumption checks that route to Welch or a rank-based alternative when violated.",
            "Two-way design with interaction, showing a case where main effects mislead.",
            "Power and minimum detectable effect for the chosen design.",
            "A report that localises differences and states limitations.",
        ],
        steps=[
            ("1", "30m", "One-way table by hand with the identity asserted", "A verified implementation"),
            ("2", "25m", "Effect size with an interval", "Magnitude attached by construction"),
            ("3", "35m", "Tukey, Bonferroni, Scheffe plus a family-wise error simulation", "A corrected comparison"),
            ("4", "30m", "Assumption checks routing to Welch", "A violation demonstration"),
            ("5", "30m", "Two-way design with a significant interaction", "An interaction story"),
            ("6", "25m", "Power and minimum detectable effect", "A design table"),
            ("7", "25m", "Report with localisation and limitations", "A defensible report"),
        ],
        diagram=""" groups (k >= 3)
    |
 [1] SSB / SSW / SST with SST = SSB + SSW asserted
 [2] F, df, p  +  eta-squared with CI     (never alone)
 [3] assumption checks --> classical | Welch | rank-based
 [4] omnibus significant?
        | yes
 [5] post-hoc: Tukey | Bonferroni | Scheffe (declared)
 [6] two-way: SSA + SSB + SSAB + SSE, each tested
 [7] power + MDE for the design
    |
 report: which pairs differ, by how much, and what it costs""",
        notes=[
            "Assert the decomposition identity; it catches transcription errors immediately.",
            "A family-wise error simulation makes the correction argument concrete.",
            "Construct data where the interaction is significant, because that is where analyses go wrong.",
            "Report pairwise differences with intervals, not just significance stars.",
        ],
        deliverables=[
            "Verified ANOVA implementation with effect sizes and intervals.",
            "Post-hoc comparison with a measured family-wise error rate.",
            "Assumption-driven test selection demonstration.",
            "Two-way analysis plus a report that localises differences.",
        ],
        grading=[
            ("Correctness", "30%", "Tables verified; degrees of freedom correct; decomposition asserted"),
            ("Localisation", "25%", "Post-hoc with a declared method and intervals"),
            ("Rigor", "25%", "Effect sizes, assumption routing, multiplicity control"),
            ("Design", "20%", "Power and MDE computed for the chosen design"),
        ],
        stretch=[
            "Add mixed-effects modelling for a nested design.",
            "Add heteroscedasticity-robust standard errors and compare.",
            "Replace family-wise error with expected false discovery control and compare.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Experiment Platform Multi-Variant Analysis",
        scenario="A marketplace runs weekly copy tests across 6 variants with 200,000 "
                 "sessions each. The team reports 'variant 3 won, F = 6.2, p < 0.05' "
                 "and last quarter they shipped a variant that was worse on revenue "
                 "while better on clicks.",
        scale=[
            ("Variants", "6 arms, roughly equal allocation, ~200k sessions each"),
            ("Frequency", "one multi-arm test per week, plus weekly re-tests"),
            ("Metrics", "click-through, conversion, GMV per session, refund rate"),
            ("Problem", "omnibus test without effect size, and no multiplicity control across variants"),
            ("Constraint", "decisions must land within the weekly release window"),
        ],
        diagram=""" experiment registry (variants, primary metric, planned contrasts)
     |
 assignment + telemetry --> per-arm summaries (n, mean, variance)
     |
 [1] assumption checks: variance ratio, residual shape, sample sizes
 [2] omnibus: one-way ANOVA with Welch fallback
     |                  + effect size with CI per arm vs control
 [3] multiplicity: Tukey for all pairs, Bonferroni for planned contrasts
 [4] guardrails as non-inferiority bounds
     |
 decision: promote only where the interval clears the business threshold
     |
 report: which variants differ, by how much, in business units""",
        components=[
            ("Analysis pipeline",
             ["Per-arm summaries computed once and shared with the test and the report",
              "Assumption checks recorded per test, with the test choice recorded alongside the result",
              "Effect size with confidence interval per arm against the control, not only a global eta-squared",
              "Welch's ANOVA used automatically when the variance ratio is material"]),
            ("Multiplicity control",
             ["Tukey for all pairwise comparisons against the control arm",
              "Bonferroni for pre-planned contrasts declared at registration",
              "Multiplicity method declared in the test record, not chosen after seeing results",
              "A simulation harness that verifies the family's error rate on this data's variance structure"]),
            ("Guardrails and decision rules",
             ["GMV per session as the primary business metric, with click-through and refunds as guardrails",
              "Guardrails evaluated as non-inferiority bounds with pre-agreed margins",
              "Promotion requires the effect interval to clear a pre-agreed threshold",
              "A variant that wins on clicks while losing on GMV is reported as a failure, with the interval shown"]),
            ("Reporting and learning",
             ["Every test report names which variants differ, by how much, with intervals in business units",
              "Re-test variance tracked so repeated weekly tests on the same variant are accounted for",
              "Post-hoc analysis of reversed decisions feeds the pre-registration defaults",
              "Weekly portfolio view: tests run, variants shipped, variants reverted"]),
        ],
        timeline=[
            ("Week 1", "Centralise per-arm summaries; add assumption checks and effect sizes with intervals"),
            ("Week 2", "Multiplicity control in the analysis path with a declared method per test"),
            ("Week 3", "Business-threshold promotion rule and guardrail non-inferiority checks"),
            ("Week 4-5", "Re-test variance tracking and weekly portfolio dashboard"),
            ("Week 6", "Post-hoc review of the reversed decision; defaults updated in registration templates"),
        ],
        runbook=[
            "# Per-arm summaries for a test",
            "curl -s 'localhost:8089/tests/t-221/arms' | jq '.[] | {arm,n,mean,sd}'",
            "",
            "# Assumption checks and the test chosen",
            "curl -s 'localhost:8089/tests/t-221/assumptions' | jq '{varianceRatio,residualShape,test,reason}'",
            "",
            "# Omnibus result with effect size and interval",
            "curl -s 'localhost:8089/tests/t-221/anova' | jq '{f,df1,df2,p,etaSquared,ci}'",
            "",
            "# Pairwise differences against control with multiplicity control",
            "curl -s 'localhost:8089/tests/t-221/pairs?method=tukey' | jq '.[] | {arm,delta,ci,pAdjusted,clearsThreshold}'",
            "",
            "# Guardrail status as non-inferiority bounds",
            "curl -s 'localhost:8089/tests/t-221/guardrails' | jq '.[] | {metric,delta,bound,status}'",
        ],
        metrics=[
            "Process: multiplicity method declared at registration for 100% of tests.",
            "Decision quality: promoted variants whose effect interval clears the business threshold.",
            "Reversals: reverts per quarter with a recorded cause, trending down.",
            "Integrity: tests reporting effect sizes with intervals rather than a bare p-value.",
            "Learning: post-hoc reviews feeding updated registration defaults.",
        ],
        failures=[
            ("A variant wins on clicks and ships while GMV falls", "No business metric threshold", "Require the effect interval to clear a pre-agreed business threshold on the primary metric"),
            ("A false winner is reported", "Uncontrolled pairwise comparisons", "Tukey across arms, method declared at registration"),
            ("Weekly re-tests of the same variant compound error", "Repeated looks across weeks", "Track re-test variance and account for repeated testing of the same variant"),
            ("The omnibus test is significant but no pair localises", "Low power for pairwise comparison at this n", "Report power for the pairwise step; consider pooling or extending the horizon as registered"),
            ("Variance differences across arms distort the F test", "Homogeneity violated", "Automatic Welch routing with the reason recorded"),
        ],
        backlog=[
            "Variance-reduction technique applied consistently across arms.",
            "Automatic assumption checks that block reporting when unverified.",
            "Expected false discovery control offered as an alternative to family-wise error.",
            "Hierarchical or Bayesian model for repeated variants across weekly tests.",
            "Post-hoc analysis automation feeding registration defaults.",
        ],
        urls=URLS,
        closer="The deliverable is a weekly test process where every decision names "
               "which variants differ, by how much, with intervals in business "
               "units, and no click-through win can ship against revenue.",
    ),
))

# ---------------------------------------------------------------- lab05
SPECS.append(dict(
    track="statistics", lab="lab05", full_set=True, level="Intermediate",
    title="Correlation & Regression", main_class="com.statistics.lab05.CorrelationAndRegression",
    problem="Two variables move together. You need to know how strongly, whether "
            "linearly, and what the relationship predicts \u2014 without pretending "
            "association is cause.",
    objectives=[
        "Compute Pearson and Spearman correlation and explain the difference",
        "Build simple and multiple linear regression by least squares",
        "Interpret slope, intercept, R\u00b2 and coefficient uncertainty correctly",
        "Diagnose residuals for nonlinearity, heteroscedasticity and leverage",
        "Distinguish association from causation and name the confounding risks",
        "Use regularisation and transformations when the linear model is inadequate",
    ],
    concepts=[
        ("Pearson measures linear association",
         "Pearson correlation is the cosine between centred vectors. It is maximised "
         "by any linear relationship and completely blind to monotone non-linear "
         "relationships, so a curvilinear relationship can report r near zero."),
        ("Spearman measures monotone association",
         "Spearman is Pearson on ranks, so it captures any monotone relationship "
         "and is far more robust to outliers. If Spearman is high and Pearson low, "
         "you have curvature or heavy tails, not independence."),
        ("Least squares minimises vertical error",
         "The regression line is the one with the smallest sum of squared vertical "
         "distances. It is not the shortest perpendicular distance, and the slope is "
         "influential to outliers, which is why robust regression exists."),
        ("R\u00b2 is in-sample",
         "R\u00b2 is the share of variance explained in the data you fitted. It rises "
         "whenever you add a predictor and falls on new data, so it is a description "
         "of the fit rather than evidence of generalisation."),
        ("Residuals are the model's complaints",
         "Residual against fitted shows curvature; against a predictor shows "
         "unmodelled structure; leverage versus squared residual identifies the "
         "points that matter most. Reading these three plots is the difference "
         "between fitting and understanding."),
        ("Association is not causation",
         "A correlation can arise from a confounder, from reverse causation, or "
         "from coincidence. Only a designed experiment or a credible causal design "
         "supports a causal claim, and no amount of regression fixes that."),
    ],
    formulas=[
        ("r = \u03a3(x\u2212x\u0304)(y\u2212\u03fc) / (s_x s_y)", "Pearson correlation", "\u22121 to 1, linear only"),
        ("\u03c1 = Pearson on ranks", "Spearman correlation", "monotone association, robust"),
        ("\u03b2\u0301 = cov(x,y)/var(x)", "Slope", "change in y per unit x"),
        ("\u03b1\u0302 = \u03fc \u2212 \u03b2\u0301 x\u0304", "Intercept", "y at x = 0, often meaningless"),
        ("R\u00b2 = 1 \u2212 SS_res/SS_tot", "Coefficient of determination", "in-sample variance explained"),
        ("SE(\u03b2\u0301) = s / sqrt(SS_x)", "Slope standard error", "uncertainty in the slope"),
        ("t = \u03b2\u0301 / SE(\u03b2\u0301)", "Coefficient test", "tests H\u2080: slope = 0"),
        ("\u03b2\u0302 = (X\u1d40X)\u207b\u00b9X\u1d40y", "Least squares", "the normal equation"),
    ],
    flow=[
        "Plot the data first; a scatter reveals curvature, clusters and outliers that no coefficient can.",
        "Compute Pearson and Spearman; a large gap tells you which one describes the relationship.",
        "Fit simple or multiple regression by least squares, checking residual plots afterwards.",
        "Inspect residuals against fitted and against each predictor, plus leverage against squared residual.",
        "Report coefficients with standard errors, R\u00b2 and an honest note that it is in-sample.",
        "If the linear form fails, transform, regularise or move to a non-parametric model.",
    ],
    assumptions=[
        "Linearity of the mean response in the predictors",
        "Independent observations; time series needs autocorrelation-aware errors",
        "Homoscedastic residuals for the classical standard errors",
        "No influential outliers distorting the slope",
        "Predictors measured without error, or errors-in-variables methods used",
        "For causal claims, no unmeasured confounding, which regression cannot verify",
    ],
    pitfalls=[
        ("r = 0.02 on a clear parabola", "Pearson is blind to non-linear relationships", "plot the data and compute Spearman; consider a quadratic term"),
        ("R\u00b2 = 0.95 cited as generalisation", "in-sample statistic", "report cross-validated error alongside R\u00b2"),
        ("A causal claim from an observational regression", "confounding and reverse causation", "use a designed experiment, or phrase it as association"),
        ("One point moves the slope drastically", "high leverage or an outlier", "check leverage and squared residual; report a robust fit"),
        ("Coefficients flip sign after adding a variable", "multicollinearity or a lurking variable", "check VIF and the sign logic of each predictor"),
        ("Confident p99 predictions from a straight line", "extrapolation beyond the data range", "flag extrapolation; use a model that saturates"),
    ],
    java=[
        ("Arrays.sort for rank-based correlation", "Spearman via Pearson on ranks with tie handling"),
        ("Apache Commons Math RealMatrix for the solve", "multiple regression via Gaussian elimination or QR"),
        ("Records for Residuals / Leverage", "e, e\u00b2, leverage and studentised residuals together"),
        ("Welford for stable variance in correlation", "avoids cancellation when x and y have large means"),
        ("record Coefficient(double estimate, double se, double t, double p, double ciLow, double ciHigh)", "uncertainty attached to every coefficient"),
    ],
    links=[
        "**labs/ml/lab01** is the full treatment of the single-predictor case.",
        "**lab03** provides the significance test attached to each coefficient.",
        "**lab08** supplies the design that would justify a causal claim.",
        "**lab06** offers a probabilistic alternative to least squares under uncertainty.",
    ],
    checklist=[
        "I plot the data before computing any coefficient.",
        "I compute Spearman as well as Pearson and explain any gap.",
        "I inspect residuals against fitted, against predictors, and leverage.",
        "I report coefficients with standard errors and intervals.",
        "I label R\u00b2 as in-sample and report validated error alongside it.",
        "I never make a causal claim from observational data alone.",
    ],
    cards=[
        ("What does Pearson correlation fail to see?", "Monotone non-linear relationships, because it only measures linear association."),
        ("When is Spearman the better choice?", "When the relationship is monotone but curved, or when outliers would dominate Pearson."),
        ("Why can R\u00b2 rise with useless predictors?", "It is in-sample and increases whenever a predictor is added, even with no real gain."),
        ("What do residuals against fitted values reveal?", "Curvature, which means the functional form is wrong rather than the parameters."),
        ("What identifies the influential points?", "Leverage against squared residual in a leverage-versus-residuals-squared plot."),
        ("Does a strong correlation support a causal claim?", "No; confounding and reverse causation can both produce it."),
        ("Why does adding a variable flip a coefficient's sign?", "Multicollinearity or an omitted variable that was absorbing the effect."),
        ("What does the intercept mean?", "The predicted response at x = 0, which is meaningless when zero lies outside the data range."),
    ],
    extra_cards=[
        ("What is VIF and why does it matter?", "Variance inflation factor per predictor: how much its variance is inflated by correlation with the others."),
        ("Why is least squares called least squares?", "It minimises the sum of squared vertical residuals, not perpendicular distances."),
        ("How do you test a slope?", "t = slope divided by its standard error, referenced to the t distribution with n minus 2 degrees of freedom."),
        ("When should you regularise?", "When predictors are correlated or numerous relative to n, and the goal is prediction rather than interpretation."),
    ],
    math=[
        ("Correlation as cosine and what it misses",
         "r = sum((x-xbar)(y-ybar)) / (n sx sy)\nsince z-scored vectors have unit length, r = cos(theta)\nso r is maximal for a linear relationship and blind to curvature",
         "Because r is a cosine between centred vectors, only the component of y "
         "aligned with x is measured. A symmetric parabola has near-zero correlation "
         "with x even though knowing x tells you a great deal about y.",
         "y = x\u00b2 for x uniform on [-1, 1]: r = 0 because the covariance is zero by "
         "symmetry. Adding a quadratic term raises R\u00b2 from 0 to about 1, which "
         "shows the information was always there and the model form was wrong."),
        ("Regression coefficients and their uncertainty",
         "slope b = Sxy/Sxx, intercept a = ybar - b xbar\nSE(b) = s / sqrt(Sxx)\nR\u00b2 = Sxy\u00b2/(Sxx Syy), t = b/SE(b) with df = n - 2",
         "The slope is a ratio of covariance to variance, so its uncertainty depends "
         "on the spread of x: with little variation in x, the slope is poorly "
         "determined even when the relationship is real.",
         "x with sd 0.1 instead of 1.0, same true relationship: SE(b) grows by 10x, "
         "so the t-statistic falls by 10x. The same data with x spread across its "
         "range is far more informative, which is why design beats analysis here."),
        ("Residual diagnostics",
         "e_i = y_i - yhat_i\ne vs fitted: curvature => wrong functional form\ne vs predictor: structure left unmodelled\nleverage vs e\u00b2: points with both high leverage and large residual are influential",
         "Residuals are the only direct evidence about model adequacy, and the three "
         "standard plots test different failures. Looking at a single residual "
         "histogram tests only normality.",
         "Fitting a straight line to y = 2x + 0.5x\u00b2 leaves a symmetric parabola of "
         "residuals against fitted: average residual is zero, so a residual mean "
         "check passes while the model is wrong. Only the residual-versus-fitted plot "
         "shows it."),
        ("Multiple regression and multicollinearity",
         "beta_hat = (X'X)^-1 X'y\nVIF_j = 1/(1 - R\u00b2_j) where R\u00b2_j regresses x_j on the others\nsign flips occur when correlated predictors split a shared effect",
         "Least squares is unbiased but its variance grows sharply with collinearity, "
         "so coefficients become unstable without necessarily being wrong. The "
         "prediction may be fine while the individual coefficients are meaningless.",
         "Two predictors correlated at r = 0.99: VIF \u2248 50, so standard errors grow "
         "about 7x. Both coefficients can wander in magnitude and sign across samples "
         "while their sum, the interpretable quantity, stays stable."),
        ("Association versus causation",
         "observed association: y = \u03b2\u2080 + \u03b2\u2081x\u2081 + \u03b2\u2082x\u2082 + \u03b5\nrequires for a causal reading: exchangeability (no unmeasured confounding), consistency, positivity\nregression cannot test any of these",
         "Regression adjusts for measured variables only. The causal assumption that "
         "matters most, exchangeability, is untestable from the data, which is why "
         "observational coefficients are associations no matter how significant they "
         "look.",
         "Ice cream sales and drownings correlate strongly; temperature confounds "
         "both. Adjusting for temperature removes the association entirely, and no "
         "amount of significance survives that adjustment."),
    ],
    math_traps=[
        "Reporting R\u00b2 without cross-validated error.",
        "Using Pearson where the relationship is monotone but curved.",
        "Interpreting a coefficient's sign when VIF is high.",
        "Extrapolating beyond the observed range of x and reporting confident intervals.",
        "Describing an observational coefficient as an effect.",
    ],
    math_problems=[
        "Show r = 0 for y = x\u00b2 on a symmetric interval, then show a quadratic fit recovers the relationship.",
        "Compute Pearson and Spearman for a dataset with an outlier and compare.",
        "Compute slope, intercept, SE, t and R\u00b2 by hand and verify against a code implementation.",
        "Compute VIF for two predictors correlated at r = 0.9 and explain the standard error inflation.",
        "Take an observational dataset, adjust for an obvious confounder, and describe how the conclusion changes.",
    ],
    tree="""src/
  CorrelationAndRegression.java  driver: correlation, fits, diagnostics, report
  Correlation.java          Pearson and Spearman with tie-aware ranking
  LinearModel.java          coefficients, fitted values, residuals, leverage
  Regression.java          simple and multiple least squares with SEs
  Diagnostics.java          residual plots, influence, VIF, curvature test
  Coefficient.java          estimate, standard error, t, p, interval together""",
    tree_note="Coefficient carries the interval, so a table of coefficients "
              "without uncertainty cannot be produced from this API. Influence "
              "diagnostics live next to residuals rather than in a separate tool, "
              "because they are read together.",
    types=[
        ("Correlation", "Pearson and Spearman with tie-aware average ranks"),
        ("LinearModel", "coefficients, fitted values, residuals, leverage"),
        ("Diagnostics", "residual plots, influence measures, VIF, curvature check"),
        ("Coefficient", "estimate, standard error, t, p-value and interval"),
    ],
    patterns=[
        ("Regression with uncertainty attached to every coefficient",
         "The covariance matrix gives standard errors directly, and the coefficient "
         "record makes an interval mandatory.",
         """public Regression fit(double[][] x, double[] y) {
    int n = x.length, p = x[0].length + 1;                 // +1 for the intercept
    double[][] design = new double[n][p];
    for (int i = 0; i < n; i++) { design[i][0] = 1.0; System.arraycopy(x[i], 0, design[i], 1, p - 1); }
    double[][] xtx = new double[p][p];
    double[] xty = new double[p];
    for (int i = 0; i < n; i++)
        for (int a = 0; a < p; a++) {
            xty[a] += design[i][a] * y[i];
            for (int b = 0; b < p; b++) xtx[a][b] += design[i][a] * design[i][b];
        }
    double[] beta = Matrix.solve(xtx, xty);
    double sse = 0;
    for (int i = 0; i < n; i++) { double e = y[i] - dot(beta, design[i]); sse += e * e; }
    double s2 = sse / (n - p);                            // residual variance
    double[][] inv = Matrix.inverse(xtx);                  // SE_j = sqrt(s2 * inv_jj)
    Coefficient[] coefs = new Coefficient[p];
    for (int j = 0; j < p; j++) {
        double se = Math.sqrt(s2 * inv[j][j]);
        double t = beta[j] / se;
        coefs[j] = new Coefficient(beta[j], se, t, tSurvivalTwoSided(t, n - p),
                beta[j] - 1.96 * se, beta[j] + 1.96 * se);
    }
    return new Regression(coefs, 1 - sse / totalSumOfSquares(y), residuals(design, beta, y));
}"""),
        ("Influence and diagnostics computed with the residuals",
         "Leverage, squared residuals and Cook's distance come from the same "
         "decomposition, so they are read together as they should be.",
         """public Diagnostics diagnose(Regression r) {
    double[] e = r.residuals();
    double n = e.length, p = r.coefficients().length;
    double[] leverage = new double[(int) n];
    for (int i = 0; i < n; i++) {
        leverage[i] = designRow.dot(invXtX, designRow);   // h_i in [0, 1]
        if (leverage[i] < 0 || leverage[i] > 1) throw new IllegalStateException("bad leverage");
    }
    double[] cooks = new double[(int) n];
    for (int i = 0; i < n; i++) {
        double studentised = e[i] / (r.residualSd() * Math.sqrt(1 - leverage[i]));
        cooks[i] = studentised * studentised * leverage[i] / (p * (1 - leverage[i]));
    }
    // curvature: compare residual correlation with fitted against what independence implies
    double curvature = pearson(r.fitted(), e);
    return new Diagnostics(leverage, e, cooks, vif(r), curvature);
}"""),
    ],
    costs=[
        ("Pearson correlation", "O(n)", "one pass with Welford-style accumulators"),
        ("Spearman correlation", "O(n log n)", "two sorts plus tie-aware ranking"),
        ("Multiple regression fit", "O(np\u00b2 + p\u00b3)", "building X\u1d40X dominates"),
        ("Diagnostics including VIF", "O(np\u00b2)", "auxiliary regressions per predictor"),
    ],
    numerics=[
        "Compute correlation from centred deviations, not from raw products, to reduce cancellation.",
        "Handle ties in Spearman with average ranks.",
        "Compute standard errors from the covariance matrix rather than by differencing sums of squares.",
        "Report the interval with every coefficient, not the estimate alone.",
        "Inspect leverage and squared residual together; neither alone finds influence.",
    ],
    tests=[
        "Pearson on a perfect positive line is 1 and on a negative line is -1.",
        "Pearson on y = x\u00b2 over a symmetric interval is approximately 0.",
        "Spearman on any strictly monotone relationship is approximately 1.",
        "A perfect fit reproduces coefficients exactly and gives zero residuals.",
        "Standard errors match a known analytical case for simple regression.",
        "VIF exceeds a threshold when two predictors are strongly correlated.",
    ],
    extensions=[
        "Add weighted least squares for heteroscedastic errors.",
        "Add robust regression to down-weight outliers in the slope estimate.",
        "Add polynomial and spline bases with the same diagnostic discipline.",
    ],
    code_checklist=[
        "Data plotted before coefficients computed",
        "Pearson and Spearman both reported with any gap explained",
        "Every coefficient carries a standard error and interval",
        "Residuals inspected against fitted, predictors and leverage",
        "R\u00b2 labelled in-sample with validated error alongside",
        "Language distinguishes association from causation",
    ],
    exercise_selfcheck=[
        "I plotted the data before fitting.",
        "My coefficients carry intervals.",
        "I inspected residual-versus-fitted for curvature.",
        "I do not make causal claims from observational data.",
    ],
    exercises=[
        ("Correlation, both kinds",
         "Linear versus monotone.",
         ["Implement Pearson with centred accumulation.",
          "Implement Spearman with tie-aware ranking.",
          "Compare on linear, curved and outlier-contaminated data.",
          "Explain each gap."],
         "A correlation suite with interpretation."),
        ("Simple regression by hand",
         "The full arithmetic.",
         ["Compute slope, intercept, residuals and R\u00b2 by hand.",
          "Compute the standard error of the slope.",
          "Test the slope and construct a confidence interval.",
          "Verify against the code implementation."],
         "A hand-verified regression."),
        ("Multiple regression with intervals",
         "More than one predictor.",
         ["Build the design matrix with an intercept.",
          "Solve via the normal equation and via QR.",
          "Report coefficients with standard errors and intervals.",
          "Add a polynomial term and compare."],
         "A multiple regression with a complete coefficient table."),
        ("Diagnostics",
         "Read the complaints.",
         ["Plot residuals against fitted and against each predictor.",
          "Compute leverage, studentised residuals and Cook's distance.",
          "Identify the influential points.",
          "Refit without them and compare."],
         "A diagnostics report with a refit comparison."),
        ("Multicollinearity and VIF",
         "See coefficients become unstable.",
         ["Add a near-duplicate predictor and compute VIF.",
          "Show standard errors growing.",
          "Show sign flips across resamples.",
          "Show ridge stabilising estimates while keeping the sum stable."],
         "A collinearity demonstration with a remedy."),
        ("Nonlinearity and transforms",
         "Repair the functional form.",
         ["Fit a line to a parabola and inspect residuals.",
          "Add a quadratic term and show R\u00b2 and residuals improve.",
          "Try a log transform on skewed data.",
          "Explain why R\u00b2 alone would not have found it."],
         "A form-selection demonstration."),
        ("Association versus causation",
         "Find the confounder.",
         ["Construct data where a confounder drives both variables.",
          "Show the naive association is strong.",
          "Adjust for the confounder and show it collapse.",
          "Explain what regression can and cannot establish."],
         "A confounding demonstration."),
        ("Full regression report",
         "Produce a defensible analysis.",
         ["State the question and the estimand.",
          "Fit with intervals and diagnostics.",
          "Validate on held-out data and report validated error.",
          "Write limitations: extrapolation, confounding, omitted variables."],
         "A report with an honest limitations section."),
    ],
    quiz=[
        ("What does Pearson correlation measure?", ["Any association", "Linear association only", "Causation", "Agreement"], 1, "It is a cosine between centred vectors, so curvature is invisible to it."),
        ("Why is Pearson near zero for y = x\u00b2?", ["The relationship is weak", "Symmetry makes the covariance zero even though knowing x predicts y", "The sample is small", "It is a computational error"], 1, "The linear component cancels; a quadratic term recovers the relationship."),
        ("When should Spearman be preferred?", ["Large samples", "Monotone but curved relationships, or with influential outliers", "Categorical data", "Whenever n is odd"], 1, "Ranks capture any monotone relationship and are robust to outliers."),
        ("Why can adding a predictor increase R\u00b2 with no real gain?", ["It cannot", "R\u00b2 is in-sample and rises whenever a predictor is added", "Because R\u00b2 is random", "Because of rounding"], 1, "Use adjusted R\u00b2 or, better, validated error."),
        ("What does a residual-versus-fitted parabola indicate?", ["Random noise", "Wrong functional form: curvature left unmodelled", "Heteroscedasticity", "An outlier"], 1, "Symmetry means residual means stay zero, so only the plot reveals it."),
        ("Which diagnostics find influential points?", ["Residual histogram", "Leverage against squared residual", "Q-Q plot", "Scatter of the predictors"], 1, "Both high leverage and large residual together make a point influential."),
        ("What does high VIF indicate?", ["Good fit", "That the predictor's variance is inflated by correlation with others, so its coefficient is unstable", "Multicollinearity in the residuals", "A nonlinear relationship"], 1, "Predictions may be fine while individual coefficients are meaningless."),
        ("Can a regression coefficient be called an effect?", ["Always", "Only from a designed experiment or a credible causal design", "If p < 0.05", "If R\u00b2 is high"], 1, "Exchangeability cannot be tested from observational data."),
        ("Why does SE of the slope depend on the spread of x?", ["It does not", "Because the slope is a ratio of covariance to variance in x", "Because of sample size", "Because of the units of y"], 1, "Small variation in x makes the slope poorly determined even when the relationship is real."),
        ("What does the intercept mean when x = 0 is out of range?", ["The true y at zero", "A mathematical artefact with no physical meaning", "The sample mean of y", "Nothing at all, and it should be dropped"], 1, "Dropping the intercept changes the slopes, so it is a modelling decision, not a cleanup."),
        ("Heteroscedastic residuals invalidate what?", ["The point estimates", "The classical standard errors and confidence intervals", "R\u00b2", "The residual plots"], 1, "Coefficients stay unbiased; the inference needs robust errors or a transform."),
        ("What is the difference between correlation and regression?", ["None", "Correlation measures association; regression estimates a relationship and quantifies uncertainty", "Correlation is for categorical data", "Regression requires normality"], 1, "Regression gives coefficients with standard errors, which correlation does not."),
        ("Why should you plot before fitting?", ["It looks professional", "Scatter reveals curvature, clusters and outliers that no coefficient exposes", "Plotting is required by software", "To compute R\u00b2"], 1, "Coefficients are summaries; they hide structure that the scatter shows immediately."),
        ("What does a sign flip after adding a predictor suggest?", ["Randomness", "Multicollinearity or an omitted variable absorbing the effect", "A calculation error always", "Normal residuals"], 0, "Both are plausible, and both need checking rather than dismissal."),
        ("How should you report predictive performance?", ["R\u00b2", "Validated error on data not used for fitting, with the interval", "The residual standard deviation", "The correlation"], 1, "R\u00b2 describes the fit; validated error describes performance."),
    ],
    vision=dict(
        future="Regression gives way to regularised and distributional models for "
               "prediction, and to explicit causal designs for explanation. The "
               "persisting skill is reading residual and influence diagnostics "
               "honestly rather than accepting a coefficient.",
        good=[
            "Data is plotted and both correlations computed before any fit.",
            "Coefficients carry standard errors and intervals.",
            "Residual and influence diagnostics are part of every fit, not an optional extra.",
            "Language distinguishes association from causation.",
        ],
        ladder=[
            ("L1", "Fit", "Simple and multiple regression with a coefficient table."),
            ("L2", "Diagnose", "Residuals, leverage, influence, VIF and curvature."),
            ("L3", "Repair", "Transforms, robust fitting and regularisation with validation."),
            ("L4", "Claim", "Causal language only when a design supports it."),
        ],
        behaviors="Plot first, fit second, diagnose third. Report uncertainty with "
                  "every estimate. Never call an observational coefficient an effect.",
        anti=[
            "R\u00b2 quoted as accuracy with no validated error.",
            "A causal claim from a dashboard regression.",
            "A confident prediction outside the observed range of x.",
            "A model with high VIF presented as interpretable.",
        ],
        trends=[
            "Regularisation and sparse models where prediction is the goal.",
            "Heteroscedasticity-robust and Bayesian inference for coefficient uncertainty.",
            "Causal inference frameworks making the identifying assumption explicit.",
            "Distributional regression for heteroscedastic and heavy-tailed outcomes.",
        ],
        d30="Implement Pearson and Spearman and explain any gap between them.",
        d60="Implement multiple regression with intervals and full residual diagnostics.",
        d90="Handle collinearity and nonlinearity, validate on held-out data, and write causal limitations.",
        metrics=[
            "I plot before I fit.",
            "My coefficients carry intervals.",
            "I inspect residuals and influence on every fit.",
            "I never describe an observational coefficient as an effect.",
        ],
        closer="The coefficient is the smallest part of a regression; the "
               "diagnostics and the design are the analysis.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Regression with Diagnostics and Honest Claims",
        brief="Fit a real relationship, diagnose it thoroughly, and write claims "
              "that match what the design supports.",
        timebox="3\u20134 hours",
        why="Regression is where statistical care pays for itself most visibly: the "
            "diagnostics find problems no coefficient can.",
        requirements=[
            "Pearson and Spearman with an explanation of any gap.",
            "Simple and multiple regression with standard errors and intervals.",
            "Residual diagnostics: against fitted, against predictors, leverage against squared residual.",
            "Collinearity demonstration with VIF and a remedy.",
            "Nonlinearity repair with a quadratic term or transform, validated on held-out data.",
            "A confounding demonstration showing what adjustment does.",
            "A report with an explicit limitations section.",
        ],
        steps=[
            ("1", "30m", "Correlations and a scatter plot; explain the gap", "A correlation report"),
            ("2", "35m", "Simple regression with hand verification", "A verified coefficient table"),
            ("3", "35m", "Multiple regression with intervals", "A complete table"),
            ("4", "30m", "Residual, leverage and influence diagnostics", "A diagnostics report"),
            ("5", "30m", "Collinearity with VIF and a remedy", "A remedy demonstration"),
            ("6", "30m", "Nonlinearity repair plus held-out validation", "A form-selection report"),
            ("7", "30m", "Confounding demonstration and limitations section", "An honest report"),
        ],
        diagram=""" data --> scatter plot (first, always)
     |
 Pearson + Spearman --> gap explained (curvature, outliers, ties)
     |
 least squares (simple -> multiple) with SE and intervals
     |
 diagnostics: e vs fitted | e vs each predictor | leverage vs e^2 | Cook's D
     |
 repair: VIF -> ridge/drop | curvature -> quadratic/transform | outliers -> robust fit
     |
 validate on held-out data (not R^2)
     |
 confounding analysis + limitations: extrapolation, unmeasured confounders""",
        notes=[
            "Plot before fitting; curvature and clusters are obvious in a scatter and invisible in a coefficient.",
            "Compute the slope standard error by hand for the simple case so the machinery is understood.",
            "Influence needs both high leverage and a large residual; neither alone is enough.",
            "The limitations section is the deliverable most reviewers read first.",
        ],
        deliverables=[
            "Correlation report with a scatter plot and explained gaps.",
            "Regression with complete coefficient tables and diagnostics.",
            "Collinearity and nonlinearity remedies with validated error.",
            "Confounding analysis and an honest limitations section.",
        ],
        grading=[
            ("Correctness", "30%", "Coefficients, standard errors and diagnostics verified"),
            ("Diagnostics", "25%", "Residual and influence plots interpreted correctly"),
            ("Remediation", "20%", "Collinearity and nonlinearity addressed with evidence"),
            ("Validation", "15%", "Held-out error reported alongside R\u00b2"),
            ("Honesty", "10%", "Limitations and causal caveats explicit"),
        ],
        stretch=[
            "Add weighted least squares and compare intervals.",
            "Add robust regression and show the slope difference.",
            "Add a causal-inference framing with explicit exchangeability assumptions.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Revenue Driver Model with Governed Claims",
        scenario="A commerce team fits weekly revenue to traffic, price, promotion "
                 "and macro indicators, then presents coefficients as 'what drives "
                 "revenue' in a planning meeting. The model has 0.88 R\u00b2, two "
                 "coefficients that flip sign between runs, and no one can say what "
                 "it predicts on new data.",
        scale=[
            ("Data", "104 weekly observations, 6 predictors, 2 years"),
            ("Current state", "R\u00b2 0.88 reported as accuracy; sign flips between refits"),
            ("Problem", "multicollinearity, no validation, causal language in planning"),
            ("Consumers", "revenue planning meeting, finance forecast, pricing review"),
            ("Requirement", "validated model with diagnostics and claim boundaries"),
        ],
        diagram=""" weekly fact table --> scatter matrix + correlation review
     |
 [1] collinearity census (VIF) --> drop or regularise, with justification
 [2] least squares with SE and intervals per coefficient
 [3] diagnostics: residual vs fitted, leverage vs e^2, Cook's D
     |
 [4] form check: curvature -> term or transform
     |
 [5] validation: rolling-origin backtest, not in-sample R^2
     |
 [6] claim register: association stated, causal claims refused
     |
 consumers: planning (interval), pricing (no causal claim), finance (validated forecast)""",
        components=[
            ("Model build",
             ["Weekly fact table with promotion and macro features joined before analysis, never after",
              "Collinearity census per predictor with VIF, and a documented decision to drop or regularise",
              "Coefficient table with standard errors, intervals and a stability measure across refits",
              "Nonlinearity handled with terms or transforms validated by backtest rather than by in-sample fit"]),
            ("Diagnostics and validation",
             ["Residual, leverage and influence plots published with every model version",
              "Rolling-origin backtest rather than a random split, because weeks are ordered",
              "Validated error reported alongside R\u00b2, with the model version recorded",
              "Coefficient sign-stability tracked across refits as a drift signal"]),
            ("Claim governance",
             ["Claim register distinguishing association from causation for every published statement",
              "Consumers told explicitly what questions the model cannot answer",
              "Pricing review gets association language only, with the confounding risk named",
              "Any causal claim requires a designed experiment, not this model"]),
            ("Operations",
             ["Model versioned with its data snapshot and coefficient table",
              "Refit schedule with automated sign-stability alerting",
              "Consumer-specific views: planning gets intervals, finance gets validated forecasts",
              "Documented response when a coefficient sign flips or validation error degrades"]),
        ],
        timeline=[
            ("Week 1", "Rebuild the fact table; scatter matrix and correlation review with the team"),
            ("Week 2", "Collinearity census; drop or regularise with a recorded decision"),
            ("Week 3-4", "Diagnostics published; rolling-origin backtest replacing in-sample R\u00b2 as the headline"),
            ("Week 5", "Claim register and consumer views; pricing review reframed around association"),
            ("Week 6", "Sign-stability alerting and refit schedule; first quarterly model review"),
        ],
        runbook=[
            "# Coefficient table with standard errors and intervals",
            "curl -s 'localhost:8085/models/revenue/v7/coefficients' | jq '.[] | {term,estimate,se,ciLow,ciHigh,vif}'",
            "",
            "# Diagnostics for a model version",
            "curl -s 'localhost:8085/models/revenue/v7/diagnostics' | jq '{curvature,maxLeverage,maxCook,signStable}'",
            "",
            "# Rolling-origin validation versus in-sample fit",
            "curl -s 'localhost:8085/models/revenue/v7/validation' | jq '{r2InSample,rmseBacktest,weeks}'",
            "",
            "# Coefficient sign stability across recent refits",
            "curl -s 'localhost:8085/models/revenue/sign-stability' | jq '.[] | {term,flips,lastFiveSigns}'",
            "",
            "# What the model may and may not be used to claim",
            "curl -s localhost:8085/models/revenue/claims | jq '{allowed,refused,reasons}'",
        ],
        metrics=[
            "Validation: rolling-origin backtest error reported with every version; R\u00b2 labelled in-sample.",
            "Stability: coefficient sign flips per quarter, expected zero after the collinearity fix.",
            "Diagnostics: influence and curvature published with every model version.",
            "Governance: published claims audited against the claim register (target 100%).",
            "Use: consumers stating questions the model cannot answer, tracked in review notes.",
        ],
        failures=[
            ("Coefficients flip sign every quarter", "Residual collinearity", "VIF census, drop or regularise, and alert on sign flips"),
            ("Backtest error far worse than in-sample R\u00b2 suggests", "Overfitting or time-ordered structure ignored", "Use rolling-origin backtest as the headline metric and add regularisation"),
            ("Planning cites the model as causal", "Model used for attribution", "Claim register refuses causal language; causal questions require an experiment"),
            ("A high-leverage week changes the whole coefficient table", "Influential point not handled", "Influence diagnostics published; refit with robust weighting and report both"),
            ("The model is refit monthly and quietly replaces itself", "No versioning of model or data", "Version the model with its snapshot and coefficient table; changes reviewed"),
        ],
        backlog=[
            "Regularised variants evaluated on the same rolling backtest.",
            "Hierarchical model by category so global coefficients stop being averages of opposites.",
            "Automated curvature detection proposing terms before refit.",
            "Counterfactual and experimental designs for the questions the model refuses.",
            "Quarterly model review with sign-stability and validation as standing agenda items.",
        ],
        urls=URLS,
        closer="The deliverable is a revenue model whose diagnostics are published, "
               "whose validation is out of sample, and whose claims register stops "
               "a planning meeting from reading association as causation.",
    ),
))

# ---------------------------------------------------------------- lab06
SPECS.append(dict(
    track="statistics", lab="lab06", full_set=True, level="Advanced",
    title="Bayesian Statistics", main_class="com.statistics.lab06.BayesianStatistics",
    problem="You have a prior belief, new evidence, and a parameter you care about. "
            "Frequentist testing answers a different question than the one you have.",
    why_now="Bayesian methods let you express prior knowledge, propagate "
             "uncertainty and make probability statements about parameters \u2014 which "
             "is what most business decisions actually require.",
    objectives=[
        "Apply Bayes' theorem to update a belief with evidence",
        "Use conjugate priors where appropriate and recognise their limits",
        "Compute a posterior distribution and summarise it properly",
        "Compute credible intervals and interpret them correctly",
        "Compare posteriors, such as P(A better than B), by sampling",
        "Choose and justify a prior, including when to use a weakly informative one",
    ],
    concepts=[
        ("Bayes in three lines",
         "Posterior is proportional to likelihood times prior. The posterior is a "
         "distribution over the parameter, so you can make direct probability "
         "statements about it: P(p > 0.5 | data) is exactly the question you want."),
        ("Conjugate priors simplify, sometimes too much",
         "A beta prior with a binomial likelihood yields a beta posterior in closed "
         "form. Convenience is real, but conjugate pairs often encode a strong "
         "assumption about the prior shape, and modern computation makes the closed "
         "form unnecessary."),
        ("Weakly informative priors do real work",
         "With little data, the prior dominates; with lots of data, the likelihood "
         "overwhelms it. A prior that rules out absurd values \u2014 negative rates, "
         "probabilities above one, variances of zero \u2014 regularises without "
         "materially moving the answer when the data is informative."),
        ("Prior sensitivity must be checked",
         "Run the analysis under two or more defensible priors. If the conclusion "
         "changes, that is a finding to report. 'The prior does not matter' is "
         "something to demonstrate, not assert."),
        ("Credible intervals are not confidence intervals",
         "A 95% credible interval contains the parameter with probability 0.95 "
         "under the posterior. A 95% confidence interval covers the parameter in 95% "
         "of repeated samples. Only the first answers 'what is the probability that "
         "the parameter is in this range'."),
        ("MCMC is a tool, not a method",
         "Posterior draws are computed by a sampler. Convergence diagnostics are "
         "not optional: chains that have not mixed produce confident nonsense, and "
         "the effective sample size, not the iteration count, is what determines "
         "interval accuracy."),
    ],
    formulas=[
        ("p(\u03b8 | data) \u221d p(data | \u03b8) p(\u03b8)", "Bayes' rule", "posterior proportional to likelihood times prior"),
        ("Beta(a + s, b + f)", "Beta-binomial posterior", "conjugate update"),
        ("E[post] = a'/(a' + b')", "Posterior mean", "the point estimate"),
        ("HDI = narrowest interval with 95% posterior mass", "Highest density interval", "the honest summary"),
        ("P(A > B) from posterior draws", "Posterior comparison", "the decision-relevant quantity"),
        ("Posterior predictive: p(y_new | data)", "Predictive distribution", "includes parameter uncertainty"),
        ("P(data) = \u222b p(data | \u03b8) p(\u03b8) d\u03b8", "Evidence", "the normalising constant"),
    ],
    flow=[
        "State the question as a probability about a parameter, not a test of a null.",
        "Choose a prior with a stated rationale, and check at least one alternative.",
        "Compute the posterior by closed form, or by sampling with convergence diagnostics.",
        "Summarise with a posterior mean or median plus an interval, never a point alone.",
        "Answer the decision question directly, such as P(A beats B) or P(effect exceeds a threshold).",
        "Produce a prior-predictive check before fitting, to confirm the prior permits data like yours.",
    ],
    assumptions=[
        "A prior is chosen deliberately and its influence assessed, not defaulted",
        "The likelihood is correctly specified for the data-generating process",
        "Convergence of the sampler is demonstrated, not assumed",
        "Summaries report posterior spread, not just a point estimate",
        "Prior predictive checks are run so the model is falsifiable before seeing data",
        "Posterior comparisons account for parameter uncertainty rather than comparing point estimates",
    ],
    pitfalls=[
        ("A confident conclusion from a vague prior", "prior not stated or not varied", "state the prior rationale and run a sensitivity check"),
        ("MCMC chains have not mixed but the interval looks tight", "convergence ignored", "check R-hat and effective sample size before summarising"),
        ("95% credible interval described as 95% confidence", "conceptual confusion", "credible intervals are statements about the parameter given the model"),
        ("Comparing two point estimates instead of posteriors", "parameter uncertainty ignored", "sample from both posteriors and compute P(A > B)"),
        ("Prior rules out the observed data", "prior predictive not checked", "run a prior predictive check and adjust the prior"),
        ("Using conjugate priors only for convenience", "the conjugacy encodes a strong prior shape", "use a weakly informative prior with modern computation"),
    ],
    java=[
        ("SplittableRandom for MCMC and prior sampling", "reproducible posterior draws"),
        ("logGamma for the beta and gamma densities", "stable log-density evaluation"),
        ("Sorted draws plus cumulative mass for an HDI", "the interval containing the specified mass"),
        ("record PosteriorSummary(double mean, double median, double hdiLow, double hdiHigh, int ess)", "spread reported alongside the point"),
        ("Empirical quantiles from posterior draw arrays", "posterior comparison by sampling"),
    ],
    links=[
        "**lab03** is the frequentist comparison; the same data supports both readings.",
        "**lab10** supplies the effect-size thinking that a posterior makes explicit.",
        "**mlops/lab10** applies P(A beats B) to a live A/B decision.",
        "**lab08** supplies the design that makes a prior defensible rather than a guess.",
    ],
    checklist=[
        "I state the prior and why it is defensible for this problem.",
        "I run a sensitivity check with an alternative prior.",
        "I verify convergence before summarising any sampler output.",
        "I report an interval or a posterior distribution, not a point estimate.",
        "I run a prior predictive check before fitting.",
        "I answer the decision question as a probability about parameters.",
    ],
    cards=[
        ("What does a credible interval mean?", "The posterior places 95% probability on the parameter being in that range, given the model and data."),
        ("How does it differ from a confidence interval?", "A confidence interval concerns repeated sampling; a credible interval is a probability statement about the parameter itself."),
        ("What is conjugate convenience hiding?", "That the conjugate prior is a specific shape, often stronger than intended."),
        ("When does the prior matter most?", "When the data is uninformative; with lots of data the likelihood overwhelms any reasonable prior."),
        ("Why run a prior predictive check?", "To see whether the prior permits data like yours, before you look at the real data."),
        ("What does R-hat measure?", "Whether independent chains agree; values near 1 indicate convergence, higher values indicate mixing problems."),
        ("What is effective sample size?", "The number of effectively independent draws, which determines interval accuracy far better than iteration count."),
        ("How do you compare two models with posteriors?", "Sample from both and compute P(A > B), which accounts for parameter uncertainty."),
    ],
    extra_cards=[
        ("Why not just compare posterior means?", "Means hide uncertainty; two posteriors with the same mean can imply very different odds."),
        ("What is posterior predictive checking?", "Comparing data simulated from the posterior to the observed data, testing the model rather than the parameters."),
        ("What makes a prior weakly informative?", "It encodes genuine prior knowledge while regularising away absurd values without dominating informative data."),
        ("What is the evidence P(data)?", "The normalising constant, which lets you compare models by Bayes factors but is hard to compute."),
    ],
    math=[
        ("Conjugate beta-binomial update",
         "prior p ~ Beta(a, b)\ndata: s successes, f failures\nposterior p ~ Beta(a + s, b + f)\nmean = (a+s)/(a+b+s+f)",
         "Conjugacy turns the integral into arithmetic. The update is exactly the prior "
         "pseudo-counts plus the observed counts, which is why a and b are "
         "interpretable as prior successes and failures.",
         "Prior Beta(1,1) (uniform), 240 successes and 760 failures: posterior "
         "Beta(241,761), mean 0.2405, 95% HDI roughly [0.212, 0.271]. Prior Beta(20,20) "
         "with the same data: mean 0.2616 \u2014 a different answer, which is a "
         "sensitivity finding to report."),
        ("Prior versus likelihood influence",
         "posterior mean with conjugate prior = (a + s)/(a + b + n)\nweight on prior ~ (a + b)/(a + b + n)\nso a + b acts as pseudo-observations",
         "The prior's influence scales as its total pseudo-count relative to n. With "
         "10 prior pseudo-observations and n = 10,000, the prior moves the answer by "
         "roughly 0.1%, which is the justification for calling it weakly "
         "informative.",
         "Prior Beta(1,1) with n = 20 observations: posterior mean is (1+10)/22 = "
         "0.500, entirely prior-driven. With n = 10,000: (1+4900)/10002 = 0.4900, "
         "where the prior is negligible. Same prior, completely different reliance."),
        ("Credible intervals and highest density intervals",
         "equal-tailed: quantiles at 2.5% and 97.5%\nHDI: narrowest interval containing 95% of the mass\nfor skewed posteriors the two differ",
         "Equal-tailed intervals can be arbitrarily wide while the posterior is "
         "extremely concentrated in the middle, so the HDI is usually the more "
         "informative summary for skewed posteriors.",
         "Posterior samples concentrated near 0.1 with a long right tail: equal-tailed "
         "95% is roughly [0.08, 0.22], while the HDI is roughly [0.086, 0.135]. The "
         "latter is the honest summary of where the mass is."),
        ("Posterior comparison for decisions",
         "draw p_A^(1..N) from posterior A, p_B^(1..N) from B\nP(A > B) = mean(1[p_A > p_B])\nwith N = 10,000 the Monte Carlo SE of this proportion is about 0.005",
         "This is the decision-relevant quantity and it accounts for parameter "
         "uncertainty on both sides. Comparing point estimates answers a different and "
         "usually less useful question.",
         "Posterior A: mean 0.2405, sd 0.015; posterior B: mean 0.2400, sd 0.020. "
         "The means differ by 0.0005, yet sampling gives P(A > B) \u2248 0.48. The "
         "honest answer is 'a coin flip', not 'A is marginally better'."),
        ("Prior predictive check and MCMC diagnostics",
         "prior predictive: y_sim ~ p(y | \u03b8 ~ prior)\ncompare distribution of y_sim to observed y\nR-hat near 1 and ESS >> iteration count indicate usable draws",
         "A prior predictive check tests the model before the data: if simulated data "
         "cannot look like your data, the model is wrong. MCMC diagnostics test "
         "whether the draws are usable, which is a separate question.",
         "Prior Beta(0.1, 0.1) with 5,000 observed successes out of 10,000: the prior "
         "predicts rates near 0 or 1, so simulated datasets look nothing like yours. "
         "A Beta(1,1) or a weakly informative rate prior passes the check."),
    ],
    math_traps=[
        "Comparing posterior means instead of sampling both posteriors.",
        "Reporting a credible interval as if it were a confidence interval.",
        "Trusting chains that have not mixed.",
        "Using conjugacy without checking whether the prior shape is defensible.",
        "Skipping the prior predictive check and discovering a model misspecification late.",
    ],
    math_problems=[
        "Compute a beta-binomial posterior by hand and verify against a sampled posterior.",
        "Show prior weight as a function of prior pseudo-counts and n; find the n at which the prior moves the mean by under 1%.",
        "Compare equal-tailed and HDI intervals on a skewed posterior sample.",
        "Compute P(A > B) by sampling and report the Monte Carlo standard error.",
        "Run a prior predictive check for a rate model and adjust the prior when it fails.",
    ],
    tree="""src/
  BayesianStatistics.java     driver: conjugate and sampled posteriors, comparisons
  BetaPosterior.java        conjugate beta-binomial update, mean, HDI
  PriorPredictiveCheck.java simulate from the prior and compare to observed data
  McmcSampler.java          seeded sampler with diagnostics: R-hat, ESS
  PosteriorSummary.java     mean, median, HDI, effective sample size
  PosteriorComparison.java  P(A > B) from draws with a Monte Carlo interval""",
    tree_note="PosteriorSummary carries the effective sample size next to the "
              "interval. It is not possible in this codebase to print a posterior "
              "interval without also reporting whether the draws justify it.",
    types=[
        ("BetaPosterior", "conjugate beta-binomial update with mean, variance and HDI"),
        ("McmcSampler", "seeded sampler exposing R-hat and effective sample size"),
        ("PriorPredictiveCheck", "simulates from the prior and compares to observed data"),
        ("PosteriorComparison", "P(A > B) from draws with a Monte Carlo interval"),
    ],
    patterns=[
        ("Conjugate update with prior interpretation",
         "Prior parameters are pseudo-counts, which makes the update arithmetic and "
         "the prior auditable.",
         """public BetaPosterior update(BetaPrior prior, int successes, int failures) {
    // a and b are interpretable as prior pseudo-successes and pseudo-failures
    double a = prior.a() + successes;
    double b = prior.b() + failures;
    return new BetaPosterior(a, b);
}

public double mean() { return a / (a + b); }

public double variance() {
    // beta variance: a b / ((a+b)^2 (a+b+1))
    return a * b / (Math.pow(a + b, 2) * (a + b + 1));
}

public Interval hdi(double mass, double[] sortedDraws) {
    // narrowest interval containing `mass` of the posterior, which is more
    // informative than equal-tailed for skewed posteriors
    int width = (int) Math.floor(mass * sortedDraws.length);
    int best = 0;
    for (int i = 0; i + width < sortedDraws.length; i++)
        if (sortedDraws[i + width] - sortedDraws[i]
                < sortedDraws[best + width] - sortedDraws[best]) best = i;
    return new Interval(sortedDraws[best], sortedDraws[best + width]);
}"""),
        ("MCMC with diagnostics that must pass before summarising",
         "Chains are compared and the effective sample size computed, because an "
         "interval from unmixed chains is confidently wrong.",
         """public PosteriorSummary summarise(List<double[]> chains, int warmup) {
    // discard warmup, then compare chains: R-hat near 1 means they agree
    List<double[]> kept = chains.stream().map(c -> Arrays.copyOfRange(c, warmup, c.length))
            .toList();
    double rHat = gelmanRubin(kept);
    int ess = effectiveSampleSize(kept);
    double[] pooled = poolDraws(kept);
    Arrays.sort(pooled);
    if (rHat > 1.01 || ess < 1000)
        throw new NotConvergedException("R-hat=" + rHat + " ESS=" + ess
                + "; an interval from these draws would be confidently wrong");
    return new PosteriorSummary(mean(pooled), quantile(pooled, 0.5),
            hdi(pooled, 0.95), ess);      // spread and justification travel together
}"""),
    ],
    costs=[
        ("Conjugate update", "O(1)", "arithmetic on two parameters"),
        ("HDI from sorted draws", "O(n log n)", "sort plus a linear window scan"),
        ("Posterior comparison P(A > B)", "O(N)", "Monte Carlo over paired draws"),
        ("MCMC with diagnostics", "O(iterations x cost)", "R-hat and ESS are O(chains x draws)"),
    ],
    numerics=[
        "Work with log densities for stability when the posterior is concentrated.",
        "Sort draws once and reuse for both the HDI and quantiles.",
        "Report Monte Carlo standard error with any sampled probability.",
        "Increase draws until the reported probability is stable to three decimal places.",
        "Seed the sampler so a reported probability can be reproduced exactly.",
    ],
    tests=[
        "Conjugate posterior mean matches the pseudo-count arithmetic.",
        "HDI contains the specified posterior mass and is no wider than equal-tailed.",
        "A non-converged sampler raises rather than returning an interval.",
        "P(A > B) matches the analytic value for two known posteriors within Monte Carlo error.",
        "A prior predictive check fails for a prior that cannot generate data like the observed.",
        "Increasing the number of draws narrows the Monte Carlo interval as expected.",
    ],
    extensions=[
        "Add MCMC for a non-conjugate model with the same diagnostic interface.",
        "Add posterior predictive p-values for model checking.",
        "Add a model comparison via Bayes factors for nested models.",
    ],
    code_checklist=[
        "Prior stated with a rationale and a sensitivity check",
        "Prior predictive check run before fitting",
        "Convergence verified before any posterior summary",
        "Intervals are HDIs with the effective sample size reported",
        "Decisions expressed as probabilities about parameters",
        "Sampler seeded for exact reproducibility",
    ],
    exercise_selfcheck=[
        "My prior has a stated rationale and I varied it.",
        "My chains converged before I summarised them.",
        "My interval says what it is: a credible interval.",
        "My decision is a probability, not a point comparison.",
    ],
    exercises=[
        ("Conjugate beta-binomial",
         "The arithmetic, then the intuition.",
         ["Implement the conjugate update and the posterior mean.",
          "Compute an HDI from sampled draws.",
          "Compare equal-tailed and HDI on a skewed posterior.",
          "Interpret a prior as pseudo-counts."],
         "A conjugate implementation with an HDI."),
        ("Prior sensitivity",
         "Does the prior matter here?",
         ["Run the analysis under three defensible priors.",
          "Compare posteriors and conclusions.",
          "Compute prior weight as a function of n.",
          "Find the n at which the prior stops mattering."],
         "A sensitivity table with a justified conclusion."),
        ("Prior predictive checks",
         "Test the model before the data.",
         ["Simulate datasets from the prior.",
          "Compare simulated to observed summaries.",
          "Show a bad prior failing the check.",
          "Adjust the prior and re-check."],
         "A prior predictive report."),
        ("MCMC with diagnostics",
         "Do not trust unverified draws.",
         ["Implement a seeded sampler for a simple posterior.",
          "Compute R-hat across chains and effective sample size.",
          "Show a deliberately poorly mixed sampler failing.",
          "Summarise only after diagnostics pass."],
         "A sampler with enforced diagnostics."),
        ("Posterior comparison",
         "Answer the decision question.",
         ["Sample two posteriors for competing designs.",
          "Compute P(A > B) with a Monte Carlo interval.",
          "Compare with a naive point-estimate comparison.",
          "Write the recommendation."],
         "A comparison with a decision probability."),
        ("Posterior predictive checking",
         "Test the model, not just the parameters.",
         ["Simulate y from the posterior.",
          "Compare a test statistic of simulated to observed.",
          "Detect a model misspecification this way.",
          "Revise the model and re-check."],
         "A predictive check that catches a misspecification."),
        ("Credible versus confidence",
         "Make the distinction concrete.",
         ["Compute both intervals for the same data.",
          "Explain each in one sentence a stakeholder understands.",
          "Show where they differ and why.",
          "Report both correctly in a written summary."],
         "A comparison write-up."),
        ("Full Bayesian analysis",
         "An end-to-end report.",
         ["State the question as a probability about a parameter.",
          "Choose and justify the prior; run sensitivity and predictive checks.",
          "Compute the posterior and summarise with an HDI.",
          "Answer the decision question and write limitations."],
         "A complete Bayesian report."),
    ],
    quiz=[
        ("What does a credible interval express?", ["Repeated-sampling coverage", "The posterior probability that the parameter lies in the range", "The probability the hypothesis is true", "Sampling error"], 1, "It is a statement about the parameter given the model, which is why it needs the prior."),
        ("How does a credible interval differ from a confidence interval?", ["It is narrower", "It concerns the parameter under the posterior; a confidence interval concerns repeated sampling", "It uses the normal", "It requires a large sample"], 1, "Only the credible interval answers 'what is the probability of this range'."),
        ("What is conjugacy?", ["A prior that is unbiased", "A prior-likelihood pair with a closed-form posterior", "A prior that is non-informative", "A sampler technique"], 1, "Convenient, but the conjugate prior is a specific shape that may be too strong."),
        ("When does the prior matter most?", ["With large samples", "When the data is uninformative relative to the prior", "Never", "Only for discrete data"], 1, "Prior influence scales as its pseudo-counts relative to n."),
        ("What is a weakly informative prior?", ["Uninformative", "One encoding genuine knowledge while ruling out absurd values without dominating data", "A uniform prior", "A prior fitted to the data"], 1, "It regularises without materially moving an answer that the data determines."),
        ("What does R-hat measure?", ["Posterior variance", "Agreement between independent chains, indicating convergence", "Effective sample size", "Prior sensitivity"], 1, "Values near 1 indicate chains mixing and agreeing."),
        ("Why must you check convergence?", ["Convention", "An interval from unmixed chains is confidently wrong", "To speed up sampling", "To compute the mean"], 1, "Diagnostics are what make a posterior summary trustworthy."),
        ("What does a prior predictive check test?", ["The prior's mean", "Whether the model can generate data like the observed", "Posterior spread", "Sampling speed"], 1, "It makes the model falsifiable before the real data is used."),
        ("How should two competing models be compared?", ["Compare posterior means", "Sample from both and compute P(A > B)", "Compare the HDI widths", "Compare the priors"], 1, "Sampling accounts for parameter uncertainty on both sides."),
        ("Why is comparing posterior means a mistake?", ["Means are biased", "Means hide uncertainty; two posteriors can share a mean and imply different odds", "Means require conjugate priors", "Means are unstable"], 1, "The decision-relevant quantity is a probability, not a difference of point estimates."),
        ("What is posterior predictive checking for?", ["Sampling diagnostics", "Testing model adequacy by comparing simulated to observed data", "Prior selection", "Interval construction"], 1, "It tests whether the model, not merely the parameter values, is adequate."),
        ("What does the evidence P(data) do?", ["Normalise the posterior", "Let you compare models via Bayes factors, though it is hard to compute", "Set the prior", "Define the interval"], 1, "It is the normalising constant, valuable for model comparison and expensive to compute."),
        ("If two defensible priors give different conclusions, what do you report?", ["The one with the higher evidence", "The sensitivity as a finding, with the conclusion qualified accordingly", "The uniform prior", "Average them"], 1, "Prior-sensitivity findings belong in the report, not in a footnote."),
        ("What is the effective sample size?", ["Number of iterations", "Number of effectively independent draws, which determines interval accuracy", "Chain count", "Prior strength"], 1, "Many correlated draws carry less information than ESS suggests."),
        ("Why does Bayesian inference suit A/B testing?", ["It is faster", "It answers the decision question directly as a probability about which variant is better", "It avoids data", "It removes the need for a control"], 1, "P(variant A beats control | data) is exactly the question a product manager asks."),
    ],
    vision=dict(
        future="Bayesian methods become the default for decision-making as "
               "calibration and posterior predictive checking mature, with "
               "conjugate shortcuts giving way to flexible computation. The "
               "discipline that matters is stating priors and checking them, not "
               "the sampler.",
        good=[
            "Priors are stated with a rationale and varied in a sensitivity analysis.",
            "Prior predictive checks run before fitting.",
            "Convergence is verified before any posterior summary.",
            "Decisions are expressed as probabilities about parameters.",
        ],
        ladder=[
            ("L1", "Update", "Conjugate priors and closed-form posteriors."),
            ("L2", "Check", "Prior predictive checks and sensitivity analysis."),
            ("L3", "Sample", "MCMC or sampling with verified convergence and HDIs."),
            ("L4", "Decide", "Posterior comparisons as decision probabilities, with predictive checking."),
        ],
        behaviors="State the prior and show it does not dominate. Verify convergence "
                  "before summarising. Answer the decision question as a probability "
                  "about parameters.",
        anti=[
            "A confident posterior from an unexamined prior.",
            "An interval from chains that never mixed.",
            "Comparing two point estimates instead of two distributions.",
            "A credible interval described with confidence-interval language.",
        ],
        trends=[
            "Posterior predictive checking as the default model validation.",
            "Automatic prior sensitivity reporting as a standard output.",
            "Bayesian decision analysis embedding costs directly in the decision.",
            "Conjugate approximations where they suffice, with honest error bounds.",
        ],
        d30="Implement the conjugate beta-binomial update and an HDI.",
        d60="Run prior predictive checks and a three-prior sensitivity analysis.",
        d90="Build MCMC with enforced diagnostics and answer a decision as P(A > B).",
        metrics=[
            "My prior has a stated rationale and I varied it.",
            "My chains converged before I summarised them.",
            "My intervals say what they are.",
            "My decisions are probabilities about parameters.",
        ],
        closer="The Bayesian advantage is not the posterior; it is being forced to "
               "state what you believed before you saw the data.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Bayesian A/B Evaluation with Verified Posteriors",
        brief="Analyse a conversion experiment as a posterior comparison, with "
              "prior checks, convergence diagnostics and a decision probability.",
        timebox="3\u20134 hours",
        why="This is the deliverable a business actually wants: the probability "
            "that one option beats another, with its uncertainty.",
        requirements=[
            "Conjugate beta-binomial posterior with an HDI, verified against sampled draws.",
            "Three defensible priors with a sensitivity analysis and a stated conclusion.",
            "Prior predictive check that passes before fitting.",
            "MCMC or sampling with R-hat and effective sample size enforced before summarising.",
            "P(variant beats control) with a Monte Carlo interval, compared with a point-estimate comparison.",
            "Posterior predictive check for an alternative model to detect misspecification.",
            "A report whose headline is a probability.",
        ],
        steps=[
            ("1", "30m", "Conjugate posterior and HDI; verify against samples", "A verified posterior"),
            ("2", "30m", "Three priors with a sensitivity table", "A sensitivity conclusion"),
            ("3", "25m", "Prior predictive check", "A passing predictive check"),
            ("4", "35m", "Sampler with R-hat and ESS enforced", "Verified draws"),
            ("5", "30m", "P(A beats B) with a Monte Carlo interval", "A decision probability"),
            ("6", "30m", "Posterior predictive check on an alternative model", "A misspecification detection"),
            ("7", "30m", "Report with the probability as the headline", "A business-facing report"),
        ],
        diagram=""" experiment data (conversions / exposures per arm)
    |
 [1] prior predictive check  -> fails? adjust the prior
 [2] three defensible priors -> posterior per arm per prior
 [3] sensitivity table -> conclusion qualified if priors disagree
 [4] sampler with R-hat + ESS enforced before any summary
 [5] HDI per arm, and P(A > B) with Monte Carlo interval
 [6] posterior predictive check on an alternative model
    |
 decision memo: P(variant beats control) as the headline""",
        notes=[
            "Run the prior predictive check first; a prior that cannot generate your data makes every later step meaningless.",
            "Enforce convergence in code so an interval cannot be printed from unverified draws.",
            "Report the Monte Carlo interval on P(A > B); a bare probability invites over-precision.",
            "The decision memo should be readable by someone who has never heard the word posterior.",
        ],
        deliverables=[
            "Conjugate posterior with HDI, verified against samples.",
            "Prior sensitivity table across three defensible priors.",
            "Sampler with enforced diagnostics and a passing prior predictive check.",
            "Decision memo whose headline is P(variant beats control) with an interval.",
        ],
        grading=[
            ("Prior discipline", "25%", "Rationale stated, predictive check run, sensitivity reported"),
            ("Inference", "25%", "Convergence enforced, HDIs computed correctly"),
            ("Decision", "30%", "P(A > B) with a Monte Carlo interval and honest comparison"),
            ("Model checking", "10%", "Posterior predictive check catches a misspecification"),
            ("Communication", "10%", "Memo readable by a non-statistician"),
        ],
        stretch=[
            "Add a model with an over-dispersed likelihood and compare posteriors.",
            "Add a decision-theoretic layer converting the probability into expected value.",
            "Extend to a continuous outcome with a conjugate normal model.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Experiment Decision Platform with Posterior Reporting",
        scenario="A marketplace runs 40 experiments a month and reports binary "
                 "p-values. Three teams interpret p = 0.06 differently, two "
                 "shipped changes on noisy data, and nobody can say the probability "
                 "that a variant actually beats control.",
        scale=[
            ("Experiments", "~40 per month, mostly binary conversion metrics"),
            ("Current reporting", "p-values from frequentist tests, inconsistent interpretation"),
            ("Problem", "no decision probability; teams disagree on thresholds; rare misses unquantified"),
            ("Constraint", "reporting must integrate with existing dashboards and guardrails"),
            ("Requirement", "decision probabilities with priors, diagnostics and calibrated reporting"),
        ],
        diagram=""" experiment results (conversions, exposures per arm)
    |
 [1] prior predictive check per experiment type
 [2] declared prior per experiment type + sensitivity record
 [3] posterior per arm: mean, HDI, ESS (enforced)
 [4] decision layer: P(variant beats control), P(variant clears MDE)
 [5] guardrails as non-inferiority posteriors
     |
 dashboard: decision probability as headline, interval always
     |
 experiment registry: prior, diagnostic status, decision, outcome
     |
 post-hoc calibration: do decisions with P > 0.9 actually win?""",
        components=[
            ("Prior and model configuration",
             ["A declared default prior per experiment type, with its rationale recorded in the registry",
              "Prior predictive check run per experiment type and re-checked when traffic mix shifts",
              "Prior sensitivity recorded for each decision: the conclusion under two priors, not just one",
              "Experiment type determines the likelihood, so a metric family does not silently use the wrong model"]),
            ("Inference and diagnostics",
             ["Conjugate update where the model allows, sampling with enforced R-hat and effective sample size otherwise",
              "Interval reported as an HDI with the effective sample size alongside",
              "Guardrails evaluated as non-inferiority posteriors rather than point comparisons",
              "Convergence failures block reporting rather than producing a quiet interval"]),
            ("Decision layer",
             ["Headline metric is P(variant beats control), computed from paired posterior draws",
              "Secondary metric P(variant clears the minimum detectable effect) separates 'better' from 'materially better'",
              "Guardrail posteriors block promotion when the probability of harm exceeds a threshold",
              "Inconclusive outcomes report the probability and, where registered, the option to extend the horizon"]),
            ("Calibration and learning",
             ["Post-hoc calibration: outcomes of decisions taken at P > 0.9 tracked against realised win rates",
              "Calibration report published quarterly per experiment type",
              "Decision registry linking prior, diagnostic status, probability, guardrails and final outcome",
              "Registry used to refine default priors and the MDE defaults"]),
        ],
        timeline=[
            ("Week 1-2", "Declare default priors per experiment type with rationales; run prior predictive checks"),
            ("Week 3", "Posterior computation per arm with HDI and enforced diagnostics"),
            ("Week 4", "Decision layer with P(variant beats control) and P(clears MDE)"),
            ("Week 5-6", "Guardrail posteriors blocking promotion on probable harm"),
            ("Week 8", "Post-hoc calibration report and registry review feeding prior defaults"),
        ],
        runbook=[
            "# Decision summary for an experiment",
            "curl -s 'localhost:8087/experiments/exp-221/decision' | jq '{pBeatsControl,pClearsMde,guardrails}'",
            "",
            "# Posterior per arm with interval and diagnostics",
            "curl -s 'localhost:8087/experiments/exp-221/posteriors' | jq '.[] | {arm,mean,hdiLow,hdiHigh,ess,rhat}'",
            "",
            "# Prior used, rationale, and the sensitivity conclusion",
            "curl -s 'localhost:8087/experiments/exp-221/prior' | jq '{prior,rationale,sensitivity}'",
            "",
            "# Guardrail posteriors and the harm probability",
            "curl -s 'localhost:8087/experiments/exp-221/guardrails' | jq '.[] | {metric,pHarm,pNoHarm}'",
            "",
            "# Post-hoc calibration: realised win rate by probability band",
            "curl -s 'localhost:8087/calibration?window=180d' | jq '.bands[] | {band,predicted,realised,n}'",
        ],
        metrics=[
            "Coverage: 100% of experiments report a decision probability with an interval.",
            "Diagnostics: convergence enforced; zero reports published from unverified draws.",
            "Calibration: realised win rate by probability band, published quarterly per experiment type.",
            "Decision quality: P > 0.9 decisions that actually win, tracked against the nominal 90%.",
            "Discipline: sensitivity recorded for 100% of shipped decisions.",
        ],
        failures=[
            ("A decision with P = 0.55 is shipped as a win", "Probability misread as a threshold crossing", "Report the probability prominently; require P above a declared threshold tied to the cost of being wrong"),
            ("A posterior is reported from unverified draws", "Diagnostics not enforced", "Block reporting on R-hat and effective sample size failures"),
            ("Two teams reach opposite conclusions on the same data", "Different priors and models used", "One prior per experiment type, declared in the registry, with sensitivity recorded"),
            ("A guardrail harm probability is ignored", "Guardrails reported as point comparisons", "Guardrails become non-inferiority posteriors that block promotion on probable harm"),
            ("The calibration report shows P = 0.9 decisions winning 75% of the time", "Probabilities not calibrated for the decision context", "Recalibrate or re-express as frequentist intervals with a declared interpretation"),
        ],
        backlog=[
            "Automatic prior updates from the decision registry, reviewed by a statistician.",
            "Posterior predictive checks per experiment type in the reporting pipeline.",
            "Decision-theoretic expected-value layer incorporating the cost of shipping.",
            "Continuous metrics modelled with conjugate normal-inverse-gamma posteriors.",
            "Calibration dashboards per experiment type with alerting on drift from nominal.",
        ],
        urls=URLS,
        closer="The deliverable is a platform where every experiment reports the "
               "probability that a variant wins, the probability that the win "
               "matters, and the probability that a guardrail was harmed \u2014 with "
               "calibration proving those numbers mean what they say.",
    ),
))
