# -*- coding: utf-8 -*-
"""Tailored specs for labs/statistics/lab01 .. lab03."""

URLS = [
    ("NIST/SEMATECH e-Handbook of Statistical Methods",
     "https://www.itl.nist.gov/div898/handbook/",
     "Authoritative reference for estimators, measures of central tendency and "
     "dispersion, with the guidance on when each is appropriate."),
    ("SciPy \u2014 statistics module documentation",
     "https://docs.scipy.org/doc/scipy/reference/stats.html",
     "Reference implementations of distributions, hypothesis tests and descriptive "
     "statistics; the semantics this lab re-implements in plain Java."),
]

SPECS = []

# ---------------------------------------------------------------- lab01
SPECS.append(dict(
    track="statistics", lab="lab01", full_set=True, level="Foundational",
    title="Descriptive Statistics", main_class="com.statistics.lab01.DescriptiveStatistics",
    problem="A dataset arrives with 400,000 rows and you have ten seconds to say "
            "something true about it before a meeting starts.",
    why_now="Every analytical claim downstream rests on knowing which summary to "
             "trust. The mean of a skewed distribution is a number nobody should "
             "quote without the median beside it.",
    objectives=[
        "Compute mean, median and mode and know when each is the honest summary",
        "Distinguish population from sample variance and defend the divisor",
        "Compute quantiles, IQR and detect outliers with the 1.5 IQR rule",
        "Use Welford's algorithm for numerically stable streaming variance",
        "Report dispersion with a spread, not just a centre",
        "Recognise how shape, skew and outliers invalidate a single-number summary",
    ],
    concepts=[
        ("Mean, median, mode",
         "The mean uses every value and is dragged by outliers. The median uses "
         "position and is robust. The mode is the most frequent value and the only "
         "one that works for categorical data. Reporting all three is the cheapest "
         "honesty available."),
        ("Population versus sample variance",
         "Dividing by n gives the average squared deviation of the population you "
         "have. Dividing by n\u22121 gives an unbiased estimator of the population "
         "variance from a sample. Reporting the population variance of a sample as if "
         "it were the population variance understates spread."),
        ("Welford's algorithm",
         "A single-pass update, mean \u2190 mean + (x \u2212 mean)/n and M2 \u2190 M2 + (x \u2212 mean)(x \u2212 "
         "mean_new), gives numerically stable variance. Naively summing squares and "
         "subtracting a large mean loses precision catastrophically on real data."),
        ("Quantiles and IQR",
         "Q1, Q2, Q3 divide the ordered sample into quarters; IQR = Q3 \u2212 Q1 measures "
         "the middle 50% and is unaffected by outliers. The 1.5 IQR fence is a "
         "distributional rule of thumb for flagging points worth inspecting."),
        ("Shape is part of the summary",
         "Skewness and kurtosis tell you whether a mean describes anything. Latency "
         "is right-skewed, so quote p50, p90 and p99 and describe the tail rather "
         "than pretending a mean plus a standard deviation characterises it."),
        ("Summaries are lossy",
         "Mean and standard deviation destroy shape. Two datasets with identical "
         "mean and variance can have completely different distributions, which is "
         "why a distribution comparison and a two-number summary are different tools."),
    ],
    formulas=[
        ("x\u0304 = (1/n)\u03a3x\u1d62", "Mean", "uses every value, sensitive to outliers"),
        ("median = middle order statistic", "Median", "robust to outliers and skew"),
        ("s\u00b2 = \u03a3(x\u1d62 \u2212 x\u0304)\u00b2 / (n\u22121)", "Sample variance", "unbiased estimator of population variance"),
        ("\u03c3\u00b2 = \u03a3(x\u1d62 \u2212 \u03bc)\u00b2 / n", "Population variance", "divisor n for a complete population"),
        ("IQR = Q3 \u2212 Q1", "Interquartile range", "spread of the middle 50%"),
        ("outlier if x < Q1 \u2212 1.5 IQR or x > Q3 + 1.5 IQR", "Fence rule", "flag, do not delete automatically"),
        ("skew = m\u2083 / s\u00b3", "Sample skewness", "sign and magnitude of asymmetry"),
        ("M2 update: M2 += (x\u2212mean)(x\u2212mean_new)", "Welford", "stable single-pass variance"),
    ],
    flow=[
        "Load the data and check size, null count and type before summarising anything.",
        "Compute the centre three ways: mean, median, mode, and compare them.",
        "Compute dispersion with variance, standard deviation, IQR and range.",
        "Inspect shape: histogram, quantiles, skewness and kurtosis.",
        "Apply the 1.5 IQR fence and inspect every flagged row rather than deleting it.",
        "Report a distribution-appropriate summary: p50/p90/p99 for skewed data, mean \u00b1 sd for symmetric.",
    ],
    assumptions=[
        "Order statistics assume a defined ordering, which needs a real numeric scale",
        "Sample variance assumes an i.i.d. sample from a finite-variance population",
        "The mode is only meaningful for discrete or categorised data",
        "Quantile definitions differ between conventions; state which one you used",
        "The IQR fence assumes roughly unimodal data and is a screen, not a test",
        "Summaries computed on a sample describe that sample; population claims need inference",
    ],
    pitfalls=[
        ("Latency reported as mean 240 ms \u00b1 60 ms", "mean plus sd on a heavy right tail", "report p50, p90, p99 and describe the tail"),
        ("Variance computed by summing squares then subtracting", "catastrophic cancellation", "use Welford or a two-pass algorithm"),
        ("Sample variance divided by n", "biased-low spread quoted as the population value", "use n\u22121 for sample variance and say which you used"),
        ("Outliers silently removed before summarising", "the interesting rows deleted by a fence rule", "flag them, inspect them, report both with and without"),
        ("Averaging across SKUs gives 3.4 but no SKU is 3.4", "Simpson's paradox across segments", "report per-segment statistics alongside the aggregate"),
        ("Mode reported for a continuous variable", "binning choices invented the mode", "use a density estimate or say the distribution is unimodal"),
    ],
    java=[
        ("DoubleSummaryStatistics", "streaming mean, variance and count without holding the data"),
        ("Arrays.sort for order statistics", "median and quartiles from a sorted copy"),
        ("Map<Double,Integer> for mode counts", "frequency counting with a single pass"),
        ("HashMap for quantile type frequencies", "detecting discrete distributions before choosing a summary"),
        ("record Summary(double mean, double median, double mode, double sd, double iqr, double p90)", "one immutable result so summaries travel together"),
    ],
    links=[
        "**lab02** turns these distributions into probabilities you can reason with.",
        "**lab03** uses the standard error from this lab as the denominator of a test statistic.",
        "**lab07** needs these summaries as the baseline for a trend line.",
        "**lab10** needs the effect size that starts from a mean difference and a pooled variance.",
    ],
    checklist=[
        "I report mean, median and mode together and explain any disagreement.",
        "I use n\u22121 for sample variance and state it.",
        "My variance is computed stably (Welford or two-pass).",
        "For skewed data I quote percentiles rather than mean \u00b1 sd.",
        "I flag outliers and inspect them rather than deleting them.",
        "I check per-segment statistics before quoting an aggregate.",
    ],
    cards=[
        ("When should you quote the median instead of the mean?", "Whenever the distribution is skewed or heavy-tailed, such as latency, income or claim size."),
        ("Why divide by n minus one?", "Because the sample mean already consumed one degree of freedom, so n\u22121 gives an unbiased estimator of the population variance."),
        ("What is Welford's algorithm for?", "Computing mean and variance in one pass with numerical stability that a sum-of-squares formula lacks."),
        ("What does IQR measure?", "The spread of the middle 50% of the data, which is why it is unaffected by outliers."),
        ("What is the 1.5 IQR fence for?", "Flagging points worth inspecting; it is a screen, not an automatic deletion rule."),
        ("Can two datasets share a mean and standard deviation but differ completely?", "Yes; the two numbers discard shape, which is why distribution comparison is a separate tool."),
        ("What is Simpson's paradox in a reporting context?", "An aggregate trend reverses inside every segment, because segment sizes differ."),
        ("Which summary works for categorical data?", "The mode; means and medians are undefined without an ordering."),
    ],
    extra_cards=[
        ("What does skewness of 2.3 tell you?", "Strong right skew: a small number of very large values pull the mean well above the median."),
        ("Why is a histogram alone insufficient?", "Bin width is a free parameter that can create or hide modes; compare across bin choices."),
        ("What is a trimmed mean for?", "A compromise that uses ordering to reduce outlier influence without discarding data entirely."),
        ("How do you report a percentile?", "State the estimation convention, since different definitions interpolate differently."),
    ],
    math=[
        ("Sample versus population variance",
         "s^2 = sum(x_i - xbar)^2 / (n - 1)\nsigma^2 = sum(x_i - mu)^2 / n\nE[s^2] = sigma^2  (the n\u22121 divisor makes the estimator unbiased)",
         "One degree of freedom is spent estimating the mean, so the residual sum of "
         "squares has expectation (n\u22121)\u03c3\u00b2, not n\u03c3\u00b2. Dividing by n gives a "
         "biased-low estimate of spread.",
         "Values [2,4,5,4,5]: mean 4. Deviations [-2,0,1,0,1], sum of squares 6. "
         "Population variance 1.2, sample variance 1.5, sample sd 1.2247. Reporting "
         "1.2 as a sample variance is the common error."),
        ("Numerical stability: why naive variance fails",
         "naive: var = (sum x^2)/n - (mean)^2\nstable (two-pass): var = sum(x_i - xbar)^2 / (n-1)\nWelford: single pass, no cancellation",
         "When the mean is large relative to the spread, sum of squares and the "
         "squared mean are nearly equal, and subtracting them loses most significant "
         "digits. Real data (latency in microseconds, money in cents) hits this "
         "constantly.",
         "Ten values around 1,000,000 with sd 100: sum x\u00b2/n is about 1e12, mean\u00b2 is "
         "1e12, and their difference is 1e4. Double precision keeps about 4 of 16 "
         "digits, so the naive variance can be off by tens of percent. Welford is "
         "exact to machine precision."),
        ("Quartiles and the IQR fence",
         "Q1 = quantile(0.25), Q3 = quantile(0.75)\nIQR = Q3 - Q1\nfences: [Q1 - 1.5 IQR, Q3 + 1.5 IQR]\nvalues outside are flagged",
         "The fence is scale-free and outlier-robust because it is built from "
         "order statistics. For roughly normal data it flags a small fraction; for "
         "heavy tails it flags more, which is a property of the shape, not a defect.",
         "Sorted [1..9] plus 100: Q1 = 3, Q3 = 8, IQR = 5, upper fence 15.5, so 100 "
         "is flagged. Sorted [1..100] uniformly: Q1 = 25.75, Q3 = 75.25, IQR = 49.5, "
         "upper fence 149.5, so nothing is flagged."),
        ("Percentiles versus mean plus standard deviation",
         "for right-skewed latency, report p50, p90, p99\nmean + sd implies a symmetric distribution around the mean\nskewness = m3 / s^3, kurtosis = m4 / s^4 - 3",
         "A symmetric summary actively misdescribes a skewed distribution: the "
         "mean is not a typical observation, and the stated range is wrong. "
         "Percentiles describe what actually happens to a fraction of traffic.",
         "Latency [10, 10, 12, 14, 900]: mean 189.2, sd 400.1, median 12, p90 738. "
         "Quoting 189 \u00b1 400 suggests typical values near 189; the median says a "
         "typical request takes 12 ms and the tail is the problem."),
        ("Skewness and kurtosis",
         "m3 = (1/n) sum(x_i - xbar)^3\nskewness = m3 / s^3\nkurtosis = m4 / s^4 - 3 (excess kurtosis)",
         "Skewness gives the direction and strength of asymmetry; excess kurtosis "
         "gives tail weight relative to normal. Both decide which summary family "
         "and which tail analysis to use.",
         "Latency [10,10,12,14,900]: m3 dominated by 900, skewness about 2.5, so "
         "mean is unrepresentative. Log-transforming latency gives near-zero skew "
         "and makes a mean \u00b1 sd defensible on the log scale."),
    ],
    math_traps=[
        "Dividing by n for sample variance and calling it unbiased.",
        "Computing variance as sum of squares minus the squared mean.",
        "Quoting mean \u00b1 sd for a right-skewed variable such as latency or spend.",
        "Deleting flagged outliers before computing any summary.",
        "Reporting an aggregate that reverses inside every segment.",
    ],
    math_problems=[
        "Compute mean, median, mode, population and sample variance for [2,4,5,4,5] and check unbiasedness by simulation.",
        "Construct data where sum-of-squares variance is off by 20% while Welford is exact, and quantify the error.",
        "Compute quartiles and the IQR fence for a dataset with a deliberate outlier, and explain the flag.",
        "Compare mean \u00b1 sd reporting against percentiles for a lognormal sample.",
        "Demonstrate Simpson's paradox with three segments and show the aggregate reversing.",
    ],
    tree="""src/
  DescriptiveStatistics.java   driver: summarises the dataset and prints a report
  Summary.java                immutable record of every measure
  CentralTendency.java        mean, median, mode with tie handling
  Dispersion.java             variance (Welford and two-pass), sd, IQR, range
  Quantiles.java              interpolated quantiles, p50/p90/p99
  Shape.java                  skewness, excess kurtosis, histogram bins
  OutlierFence.java           1.5 IQR fence returning flagged rows, not deletions""",
    tree_note="Summary is a single record, so a caller cannot report a mean "
              "without the median and standard deviation travelling with it. That "
              "is a small design choice that prevents a whole category of bad "
              "reports.",
    types=[
        ("Summary", "immutable record of centre, dispersion, shape and percentiles"),
        ("CentralTendency", "mean, median and mode with tie handling"),
        ("Dispersion", "Welford and two-pass variance, standard deviation, IQR"),
        ("Shape", "skewness, excess kurtosis and a histogram with declared bin width"),
    ],
    patterns=[
        ("Welford streaming variance",
         "One pass, no cancellation, no retained data. The deltas form is the "
         "whole point, so it is written in the stable ordering.",
         """public static Variance update(Variance acc, double x) {
    acc.n++;
    double delta = x - acc.mean;
    acc.mean += delta / acc.n;               // stable: mean moves a little each step
    acc.m2 += delta * (x - acc.mean);        // second moment of deviations
    return acc;
}

public static double sampleVariance(Variance acc) {
    // n - 1 because one degree of freedom went to estimating the mean
    return acc.n > 1 ? acc.m2 / (acc.n - 1) : Double.NaN;
}

// verify against the naive formula on data with a large mean and small spread:
// sum-of-squares loses precision that Welford keeps
static double naiveVariance(double[] xs) {
    double sum = 0, sumSq = 0;
    for (double x : xs) { sum += x; sumSq += x * x; }
    double mean = sum / xs.length;
    return sumSq / xs.length - mean * mean;   // cancellation: avoid this in production
}"""),
        ("A summary that cannot be reported partially",
         "Centre, dispersion, shape and percentiles are computed together so a "
         "skewed distribution cannot be reported with a mean alone.",
         """public Summary summarise(double[] x) {
    Variance acc = new Variance();
    for (double v : x) acc = update(acc, v);        // one stable pass
    double[] sorted = x.clone();
    Arrays.sort(sorted);
    double p50 = quantile(sorted, 0.50);
    double p90 = quantile(sorted, 0.90);
    double p99 = quantile(sorted, 0.99);
    Map<Double, Integer> counts = modeCounts(x);
    double iqr = quantile(sorted, 0.75) - quantile(sorted, 0.25);
    // skewness is reported so the caller sees when the mean is unrepresentative
    return new Summary(acc.mean / acc.n, p50, mostFrequent(counts),
                       Math.sqrt(sampleVariance(acc)), iqr, skewness(x, acc),
                       p90, p99, Math.abs(p50 - acc.mean / acc.n) > 0.5 * sdOf(acc)
                               ? DistributionShape.SKEWED : DistributionShape.SYMMETRIC);
}"""),
    ],
    costs=[
        ("Streaming mean and variance", "O(n) time, O(1) space", "the default for large data"),
        ("Quantiles", "O(n log n) with a sort", "or O(n) expected with a selection algorithm"),
        ("Mode", "O(n) time, O(distinct) space", "a hash map of frequencies"),
        ("Histogram", "O(n + bins)", "bin width must be declared, not assumed"),
    ],
    numerics=[
        "Use Welford or a two-pass algorithm for variance, never sum-of-squares.",
        "Use n\u22121 for sample variance and state the divisor in the output.",
        "Compare mean against the median; a large gap is the signal that shape matters.",
        "Compute percentiles by interpolation and state the convention.",
        "Flag outliers with the IQR fence and inspect them; never delete silently.",
    ],
    tests=[
        "Welford variance matches a two-pass computation to 1e-10 on random data.",
        "Welford beats the naive formula on data with a large mean and small spread.",
        "Sample variance of a constant array is zero; population variance likewise.",
        "Median of an even-length array averages the two central values.",
        "The IQR fence flags a planted outlier and leaves a uniform sample unflagged.",
        "A right-skewed dataset is reported as skewed and the summary carries percentiles.",
    ],
    extensions=[
        "Add a trimmed mean and compare its sensitivity to the median.",
        "Add robust scale estimators such as the median absolute deviation.",
        "Add histogram bin-width sensitivity analysis so mode claims are bin-independent.",
    ],
    code_checklist=[
        "Variance computed with a numerically stable algorithm",
        "Divisor (n or n\u22121) stated in the output",
        "Mean, median and mode reported together",
        "Percentiles included whenever skewness is non-trivial",
        "Outliers flagged with rows retained for inspection",
        "Per-segment summaries available alongside aggregates",
    ],
    exercise_selfcheck=[
        "I can explain why my variance is stable.",
        "I report the divisor I used.",
        "My summary would be wrong to read if the data were skewed.",
        "I have not deleted flagged rows.",
    ],
    exercises=[
        ("Implement the summaries",
         "Centre and dispersion, correctly.",
         ["Implement mean, median and mode.",
          "Implement variance with n\u22121 and compare against n.",
          "Compute standard deviation, IQR and range.",
          "Verify on a hand-worked example."],
         "A Summary implementation verified by hand."),
        ("Numerical stability lab",
         "See the naive formula fail.",
         ["Implement naive and Welford variance.",
          "Construct data with a large mean and small spread.",
          "Quantify the relative error of each.",
          "Document when the naive version is acceptable."],
         "A measured error comparison."),
        ("Quantiles and the fence",
         "Percentiles plus outlier screening.",
         ["Implement interpolated p50, p90 and p99.",
          "Implement the 1.5 IQR fence.",
          "Flag rows and inspect them for data-quality causes.",
          "Report summaries with and without flagged rows."],
         "A fence report with row-level detail."),
        ("Shape statistics",
         "Decide which summary family to use.",
         ["Implement skewness and excess kurtosis.",
          "Apply to symmetric, right-skewed and bimodal samples.",
          "Show the log transform reduces right skew.",
          "Write the reporting rule you would adopt."],
         "A shape report with a reporting rule."),
        ("Streaming statistics",
         "One pass, no retention.",
         ["Implement Welford for mean and variance.",
          "Stream 10M generated values.",
          "Compare against a two-pass result on a subset.",
          "Report throughput."],
         "A streaming implementation with a benchmark."),
        ("Segment versus aggregate",
         "Find the reversal.",
         ["Build three segments with opposite trends.",
          "Compute aggregate and per-segment statistics.",
          "Show the aggregate reversing.",
          "Write the reporting practice that prevents it."],
         "A Simpson's paradox demonstration."),
        ("Robust alternatives",
         "Compare the summaries.",
         ["Implement the trimmed mean and MAD.",
          "Compare sensitivity to planted outliers.",
          "Choose a primary and a secondary summary per dataset.",
          "Document the choice criteria."],
         "A robustness comparison table."),
        ("Summary reporting tool",
         "Produce a report that cannot mislead.",
         ["Emit a summary with centre, dispersion, shape and percentiles.",
          "Include a histogram and a quantile table.",
          "Flag skewness and outliers explicitly in the output.",
          "Print the divisor and quantile convention used."],
         "A report tool whose output is defensible."),
    ],
    quiz=[
        ("Which summary is most robust to outliers?", ["Mean", "Median", "Variance", "Standard deviation"], 1, "The median depends on position, not magnitude, so extreme values barely move it."),
        ("Why does sample variance divide by n minus one?", ["Convenience", "One degree of freedom is used estimating the mean, so n\u22121 makes it unbiased", "To make it smaller", "Because of rounding"], 1, "E[s\u00b2] equals \u03c3\u00b2 only with the n\u22121 divisor."),
        ("Why is sum-of-squares variance numerically unstable?", ["It is slower", "Subtracting two nearly equal large numbers loses significant digits", "It cannot handle negatives", "It ignores the mean"], 1, "With a large mean and small spread, the difference is tiny relative to both terms."),
        ("What does an IQR of 30 tell you?", ["The mean is 30", "The middle 50% of values span 30 units", "The range is 30", "The variance is 30"], 1, "IQR is Q3 minus Q1, the width of the middle half."),
        ("What should you do with a point outside the 1.5 IQR fence?", ["Delete it", "Flag and inspect it for a data-quality cause", "Replace it with the median", "Ignore it"], 1, "Outliers are often the interesting rows, and deletion is a decision to record."),
        ("Which summary should you report for p99 latency?", ["Mean \u00b1 sd", "Mean and median", "p50, p90, p99 and tail analysis", "Mode"], 2, "Latency is right-skewed, so percentiles describe what traffic experiences."),
        ("Can mean and standard deviation describe a bimodal distribution?", ["Yes", "No", "Only if modes are close", "Only with small n"], 1, "Two numbers cannot encode two modes; the summary hides the structure."),
        ("What is Simpson's paradox?", ["A numerical error", "An aggregate trend that reverses inside every segment", "A sampling artifact", "A correlation fallacy"], 1, "It appears whenever segment sizes are unbalanced."),
        ("A skewness of 2.4 indicates...", ["Symmetric data", "Strong right skew, so the mean sits above the typical value", "Left skew", "Bimodality"], 1, "Positive skew means a right tail pulling the mean up."),
        ("Why does mode work for categorical data but mean does not?", ["Mode is cheaper", "Categories have no meaningful numeric ordering to average", "Means require sorting", "Modes are more accurate"], 1, "Averaging categories is meaningless without an ordering."),
        ("What does kurtosis describe?", ["The centre", "Tail weight relative to a normal distribution", "The range", "The sample size"], 1, "Excess kurtosis above zero means heavier tails than normal."),
        ("If two datasets share mean and standard deviation, can they differ?", ["No", "Yes; the two numbers discard shape", "Only if n is large", "Only if the median matches"], 1, "This is why distribution comparison is a separate tool."),
        ("Which estimator gives an unbiased population variance?", ["Dividing by n", "Dividing by n\u22121", "Taking the square root", "Using the range"], 1, "The n\u22121 divisor is exactly the Bessel correction."),
        ("Why compute quantiles by interpolation?", ["Speed", "Order statistics alone are coarse and bin-width sensitive", "Accuracy of the mean", "To reduce memory"], 1, "Interpolation gives a smoother, more stable estimate between order statistics."),
        ("What is the safest single number to report for skewed business data?", ["Mean", "Median", "Range", "Variance"], 1, "The median represents a typical observation when the mean does not."),
    ],
    vision=dict(
        future="Descriptive statistics survives as the first line of every "
               "analysis and the last sanity check before every model. The frontier "
               "is summary statistics that carry their own uncertainty and shape, so "
               "a single number can no longer mislead.",
        good=[
            "Centre, dispersion, shape and percentiles are reported together.",
            "The divisor and quantile convention are stated with the numbers.",
            "Flagged outliers are inspected and reported, never silently dropped.",
            "Segment statistics accompany every aggregate.",
        ],
        ladder=[
            ("L1", "Summarise", "Mean, median, mode, standard deviation, IQR."),
            ("L2", "Check shape", "Skewness, kurtosis, percentiles, histogram with declared bins."),
            ("L3", "Stream", "Stable one-pass statistics for data you cannot hold."),
            ("L4", "Communicate", "Reports that cannot be quoted misleadingly, with segment context."),
        ],
        behaviors="Compare the mean to the median first; a gap tells you shape matters. "
                  "Compute variance stably. Never let a summary outlive the "
                  "convention used to compute it.",
        anti=[
            "A dashboard of means with no distributions.",
            "Outliers removed before anyone looked at them.",
            "Population variance of a sample quoted as the population value.",
            "An aggregate metric quoted after a segment reversal was observed.",
        ],
        trends=[
            "Resistant and robust statistics as defaults in streaming analytics.",
            "Summary statistics carrying uncertainty rather than point estimates.",
            "Automatic shape-aware reporting that picks the summary family.",
            "Streaming sketches for datasets that cannot be retained.",
        ],
        d30="Implement the full summary set with a numerically stable variance.",
        d60="Add shape statistics, quantiles and the outlier fence with row inspection.",
        d90="Build a reporting tool whose output cannot mislead and add streaming statistics.",
        metrics=[
            "I can explain why my variance is numerically stable.",
            "I state the divisor and quantile convention.",
            "My summary would be obviously wrong to read if the shape changed.",
            "I have segment context for every aggregate I quote.",
        ],
        closer="A summary is a claim about a distribution; the moment it is more "
               "precise than the data, it stops being useful.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Distribution-Aware Summary Report",
        brief="Build a summariser that detects shape, picks the right summary "
              "family, flags outliers and reports per segment.",
        timebox="3 hours",
        why="Almost every bad analytical report fails at this step: quoting a mean "
            "for a skewed variable, or deleting the rows that mattered.",
        requirements=[
            "Full summary: mean, median, mode, sample and population variance, sd, IQR, range.",
            "Welford streaming variance verified against a two-pass computation and against the naive formula on adversarial data.",
            "Shape statistics: skewness, excess kurtosis, p50/p90/p99, histogram with a declared bin width.",
            "1.5 IQR fence flagging rows with a data-quality explanation for each.",
            "Automatic summary-family selection: symmetric reports mean \u00b1 sd, skewed reports percentiles.",
            "Per-segment summaries alongside every aggregate, plus a Simpson's paradox demonstration.",
            "A report tool whose output states the divisor, quantile convention and any flags.",
        ],
        steps=[
            ("1", "30m", "Centre and dispersion with n\u22121; verify by hand", "A verified Summary implementation"),
            ("2", "30m", "Welford versus naive on adversarial data", "A measured precision comparison"),
            ("3", "30m", "Shape statistics and a bin-width sensitivity check", "A shape report"),
            ("4", "30m", "IQR fence with row-level data-quality inspection", "A flag report with causes"),
            ("5", "25m", "Automatic summary-family selection rule", "A documented rule and its output"),
            ("6", "25m", "Segment reporting plus a Simpson's paradox demo", "A reversal demonstration"),
            ("7", "20m", "Report tool with conventions stated", "A defensible report"),
        ],
        diagram=""" raw data
    |
 [1] stable pass (Welford): mean, variance
 [2] order statistics: median, quartiles, p90, p99
 [3] mode counts | density shape
 [4] skewness + excess kurtosis
    |
 shape classification --> SYMMETRIC: report mean +/- sd
                        --> SKEWED:    report p50/p90/p99
 [5] IQR fence --> flagged rows (kept, annotated, cause per row)
    |
 [6] per-segment summaries + aggregate reversal check
    |
 report with divisor, quantile convention, flags""",
        notes=[
            "Build the adversarial dataset for the naive formula deliberately; large mean, small spread.",
            "Check bin-width sensitivity before claiming any mode from a histogram.",
            "Annotate every flagged row with a suspected cause rather than deleting it.",
            "The reporting rule must be written down and applied automatically, not decided per report.",
        ],
        deliverables=[
            "Verified summary implementation with a precision comparison table.",
            "Shape report with bin-width sensitivity analysis.",
            "Flag report with a suspected cause for every flagged row.",
            "Report tool with stated conventions and per-segment context.",
        ],
        grading=[
            ("Correctness", "30%", "Divisors, stability and quantiles verified"),
            ("Shape awareness", "25%", "Shape statistics and the summary-family rule applied"),
            ("Outlier handling", "20%", "Flagged rows retained, annotated and explained"),
            ("Honesty", "15%", "Conventions stated; segment context present"),
            ("Communication", "10%", "Report is readable and cannot mislead"),
        ],
        stretch=[
            "Add robust alternatives (trimmed mean, MAD) and compare sensitivity.",
            "Add histogram-free mode estimation via kernel density.",
            "Add streaming mode estimation for large categorical streams.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Latency and Throughput Reporting for a Serving Fleet",
        scenario="A 200-node serving fleet reports p50 45 ms and mean 190 ms on "
                 "the same dashboard. Nobody agrees which number the SLO should "
                 "use, and two outlier nodes were quietly excluded from the "
                 "reporting last quarter.",
        scale=[
            ("Fleet", "200 nodes, ~90k requests/second aggregate"),
            ("Reporting today", "p50 45 ms and mean 190 ms on one chart"),
            ("Dispute", "no agreed primary metric, so no agreed SLO"),
            ("Data issue", "two nodes excluded from reporting without a record"),
            ("Requirement", "shape-aware reporting with segment context and stated conventions"),
        ],
        diagram=""" request telemetry (path, model version, node, region)
    |
 stable streaming stats per node (Welford)
    |
 segment by: node | region | model version | endpoint | traffic class
    |
 shape classification per segment
    |
 report: symmetric -> mean +/- sd; skewed -> p50/p90/p99
    |
 exclusions require a recorded reason and an expiry
    |
 SLO defined on the primary metric with the convention stated""",
        components=[
            ("Metric definition",
             ["Primary latency metric agreed as p99 per node, with the estimator and quantile convention documented",
              "Secondary metrics p50, p90, mean and sd retained so disagreements can be inspected rather than argued",
              "Metric computed per segment: node, region, model version, endpoint and traffic class",
              "Throughput reported alongside latency so a latency improvement bought by rejection is visible"]),
            ("Stable computation",
             ["Streaming Welford statistics so a 90k/s stream is summarised without retention",
              "Quantiles from a bounded reservoir with a declared sampling method",
              "Shape classification per segment so skewed segments do not inherit a symmetric summary",
              "Cross-checks against a full-recomputation sample to validate the streaming estimate"]),
            ("Exclusion discipline",
             ["Excluding a node requires a recorded reason, an owner and an expiry",
              "Excluded nodes remain visible in a separate panel rather than vanishing",
              "Weekly review of exclusions with automatic expiry",
              "Any exclusion overlapping a bad node is flagged to the on-call engineer"]),
            ("Reporting and SLO",
             ["One chart per segment with shape-appropriate summary selection",
              "SLO stated on the primary metric with its convention in the panel title",
              "Segment context always accompanies an aggregate, so reversals cannot hide",
              "Distribution-level incident detection: shape change as well as threshold breach"]),
        ],
        timeline=[
            ("Week 1", "Agree and document the primary metric, estimator and quantile convention"),
            ("Week 2", "Streaming statistics per segment with cross-checks against full recomputation"),
            ("Week 3", "Shape classification per segment; automated summary-family selection"),
            ("Week 4", "Exclusion discipline with recorded reasons, owners and expiry"),
            ("Week 5", "Per-segment dashboards plus a distribution-level incident detector"),
        ],
        runbook=[
            "# Primary metric for a segment, with the convention in the response",
            "curl -s 'localhost:9090/latency?segment=region:eu-west&metric=p99&estimator=reservoir' | jq '.value,.unit,.convention'",
            "",
            "# Full shape report for a segment (skewness, percentiles, mean/sd)",
            "curl -s 'localhost:9090/latency/shape?segment=node:eu-17' | jq '{skewness,p50,p90,p99,mean,sd,classification}'",
            "",
            "# Current exclusions with reason, owner and expiry",
            "curl -s 'localhost:9090/exclusions' | jq '.[] | {segment,reason,owner,expiresAt}'",
            "",
            "# Cross-check streaming stats against a full recomputation sample",
            "curl -s 'localhost:9090/latency/verify?segment=region:eu-west' | jq '.streaming,.recomputed,.delta'",
            "",
            "# Segment breakdown for an aggregate you are about to quote",
            "curl -s 'localhost:9090/latency/breakdown?window=15m' | jq '.segments[] | {segment,p99,shape}'",
        ],
        metrics=[
            "Definition: primary metric, estimator and quantile convention documented and versioned.",
            "Accuracy: streaming statistic versus full recomputation delta below 1% on every segment.",
            "Coverage: segments with shape classification at 100%, and exclusions all with reasons and expiry.",
            "SLO: percentage of nodes meeting the stated p99, reported per segment and in aggregate.",
            "Trust: aggregate quotes accompanied by segment breakdowns (measured in reviews).",
        ],
        failures=[
            ("Aggregate p99 looks healthy while one region is degraded", "Aggregate masking segment shape", "Per-segment reporting is mandatory; the aggregate always ships with a breakdown"),
            ("Streaming statistic drifts from the true value", "Reservoir sampling bias or non-stationary stream", "Cross-check against full recomputation on a sample; alert on the delta"),
            ("A node is excluded without a record", "No exclusion discipline", "Exclusions require reason, owner and expiry, and appear in a visible panel"),
            ("Latency improves while error rate rises", "Rejections moved out of the latency path", "Report throughput and error rate beside latency so the trade is visible"),
            ("SLO disputes recur", "No agreed primary metric and convention", "Version the metric definition; disagreements are about estimation, not performance"),
        ],
        backlog=[
            "Distribution-level incident detection that alerts on shape change as well as thresholds.",
            "Per-traffic-class latency reporting so mix shift cannot hide a regression.",
            "Automated summary-family selection driven by measured skewness.",
            "Cross-region percentile aggregation that does not average averages.",
            "Monthly audit of exclusions and metric definition changes.",
        ],
        urls=URLS,
        closer="The deliverable is a fleet dashboard where one number is the agreed "
               "SLO, its convention is written down, its shape is known per segment, "
               "and every exclusion is visible with an expiry.",
    ),
))

# ---------------------------------------------------------------- lab02
SPECS.append(dict(
    track="statistics", lab="lab02", full_set=True, level="Foundational",
    title="Probability Distributions", main_class="com.statistics.lab02.ProbabilityDistributions",
    problem="You need to say how likely things are: a wait time, a count of events "
            "in an hour, a measurement that clusters around a mean.",
    why_now="Choosing the wrong distribution turns a real signal into noise. "
             "Knowing which family a process belongs to is what lets you compute "
             "probabilities at all.",
    objectives=[
        "Distinguish discrete from continuous distributions and pick between them",
        "Implement normal, binomial, Poisson and exponential densities and CDFs",
        "Compute CDF values without a lookup table, using approximations with stated error",
        "Sample from each distribution with a correct, seedable algorithm",
        "Use the central limit theorem to justify normal approximations",
        "Recognise when a Poisson assumption (constant rate, independent events) is violated",
    ],
    concepts=[
        ("Discrete versus continuous",
         "Discrete distributions put mass on countable outcomes (counts), continuous "
         "ones describe measurements over a range. Normal and exponential are "
         "continuous; binomial and Poisson are discrete. Mixing them up is why "
         "probabilities come out above one."),
        ("Normal distribution",
         "The workhorse for continuous data, symmetric with mean \u03bc and variance "
         "\u03c3\u00b2. Its practical importance comes from the central limit theorem: sums "
         "of independent, non-identically distributed variables tend toward normal, "
         "which is why it appears everywhere."),
        ("Binomial distribution",
         "Counts of successes in n independent Bernoulli trials. It is the right "
         "model for a proportion or a small count with a known rate. The normal "
         "approximation to the binomial needs np and n(1\u2212p) both above about 5."),
        ("Poisson distribution",
         "Counts of events in a fixed interval at a constant rate with independent "
         "occurrences. If the rate varies with time (rush hour, seasonality) the "
         "Poisson assumption breaks and the count is overdispersed \u2014 a real risk in "
         "operational data."),
        ("Exponential distribution",
         "Waiting time between Poisson events, memoryless. It is the basis of "
         "exponential backoff in retries, and its memoryless property is exactly "
         "why backoff has that shape."),
        ("Sampling and simulation",
         "Sampling algorithms let you reason about distributions you cannot evaluate "
         "in closed form, and they let you estimate quantities analytically "
         "available. Seeded sampling makes Monte Carlo estimates reproducible, which "
         "is what turns an estimate into a testable result."),
    ],
    formulas=[
        ("f(x) = exp(\u2212(x\u2212\u03bc)\u00b2/2\u03c3\u00b2) / (\u03c3\u221a2\u03c0)", "Normal PDF", "continuous density"),
        ("\u03a6(z) = P(Z \u2264 z), z = (x\u2212\u03bc)/\u03c3", "Normal CDF", "standardised to N(0,1)"),
        ("P(X = k) = C(n,k) p^k (1\u2212p)^(n\u2212k)", "Binomial PMF", "k successes in n trials"),
        ("P(X = k) = \u03bb^k e^\u2212\u03bb / k!", "Poisson PMF", "events in an interval at rate \u03bb"),
        ("f(x) = \u03bb e^\u2212\u03bbx", "Exponential PDF", "waiting time, x \u2265 0"),
        ("P(T > t) = e^\u2212\u03bbt", "Survival function", "memoryless property"),
        ("X\u0303 \u2192 N(n\u03bc, n\u03c3\u00b2/n)", "CLT", "justifies normal approximations"),
        ("u1, u2 ~ U(0,1) => z = sqrt(\u22122 ln u1) cos(2\u03c0 u2)", "Box-Muller", "normal sampling"),
    ],
    flow=[
        "Classify the variable: a count, a waiting time, or a continuous measurement.",
        "Check the distributional assumptions: independence, constant rate, finite variance.",
        "Estimate parameters by maximum likelihood or method of moments, and state which.",
        "Evaluate the CDF at the decision point rather than reasoning in densities.",
        "Approximate where closed forms do not exist, and state the error bound you can justify.",
        "Sample with a seeded generator when you need to simulate rather than evaluate.",
    ],
    assumptions=[
        "Binomial: fixed n, independent trials, constant success probability",
        "Poisson: constant rate \u03bb, independent occurrences, counts in a fixed interval",
        "Exponential: the underlying process is Poisson, so waiting times are memoryless",
        "Normal approximations need a variance that exists and a sufficiently large n",
        "Parameter estimates treat the observed sample as i.i.d.",
        "Sampling algorithms use a seeded generator so results are reproducible",
    ],
    pitfalls=[
        ("A Poisson count is far more variable than predicted", "the rate is not constant, so events cluster", "use a negative binomial or model rate variation"),
        ("Normal approximation used with np below 5", "approximation invalid in the tail that matters", "check the continuity correction and both expected counts"),
        ("Densities compared instead of CDFs", "density values are not probabilities", "integrate to a CDF before drawing a conclusion"),
        ("A simulation gives different answers each run", "unseeded generator", "seed it; an unreproducible estimate cannot be checked"),
        ("Exponential used for a rate that varies with time of day", "non-homogeneous process", "split the interval or use a time-varying hazard"),
        ("Binomial applied to dependent events", "independence assumption violated", "correlated trials inflate variance; use a different model"),
    ],
    java=[
        ("SplittableRandom / Random with an explicit seed", "reproducible sampling"),
        ("Math.log1p, Math.expm1 for CDF tails", "avoiding catastrophic cancellation in the tails"),
        ("Box-Muller transform for normal sampling", "two uniforms to two normals, exactly"),
        ("Incomplete gamma for the Poisson CDF", "avoiding factorial overflow for large k"),
        ("record Estimate(String name, double value, double lower, double upper)", "Monte Carlo estimates with intervals"),
    ],
    links=[
        "**lab03** uses these CDFs to compute p-values for tests.",
        "**lab09** needs them when checking normality before a rank test.",
        "**lab10** needs them to compute the standard error of an estimate.",
        "**lab07** uses the exponential distribution as the basis for backoff.",
    ],
    checklist=[
        "I classify the variable before choosing a distribution.",
        "I check the distributional assumptions, especially rate constancy for Poisson.",
        "I evaluate CDFs rather than comparing densities.",
        "My approximations state their validity conditions.",
        "All sampling is seeded and reproducible.",
        "I check for overdispersion before trusting a Poisson model.",
    ],
    cards=[
        ("When is Poisson appropriate?", "Counts of events in a fixed interval at a constant rate with independent occurrences."),
        ("What does overdispersion indicate?", "The rate is not constant, so events cluster and the variance exceeds the mean."),
        ("Why does the normal approximation to the binomial need np and n(1\u2212p) above 5?", "The approximation is asymptotic, and small expected counts in a tail make it invalid exactly where decisions are made."),
        ("What is the memoryless property?", "P(T > s + t | T > s) = P(T > t), which is why exponential backoff has that shape."),
        ("What does the central limit theorem actually say?", "Sums of independent, non-identically distributed variables with finite variance tend toward normal as n grows."),
        ("How do you sample from a normal distribution?", "Box-Muller: transform two independent uniforms into two normals."),
        ("Why compare CDFs rather than densities?", "A density value is not a probability; the CDF is the cumulative probability."),
        ("When does an exponential distribution fail?", "When the event rate varies with time, such as rush hour arrivals."),
    ],
    extra_cards=[
        ("What is a continuity correction for?", "Correcting the discrete-to-continuous step when approximating a binomial or Poisson tail with a normal."),
        ("How do you estimate a Poisson rate?", "By maximum likelihood or method of moments; both give the sample mean of the counts."),
        ("What is the variance of a binomial?", "np(1\u2212p), which is why the proportion estimator's standard error shrinks as sqrt(n)."),
        ("Why does overflow matter in a Poisson PMF?", "The k! term overflows a double around k = 170; a log-space or gamma-function evaluation avoids it."),
    ],
    math=[
        ("Log-space evaluation and cancellation",
         "log P(X=k) = k log(lambda) - lambda - lgamma(k+1)\nnormal CDF tail: Phi(-z) = 0.5 erfc(z / sqrt(2))\nPoisson CDF: P(X <= k) = gammainc(k+1, lambda) upper regularised form",
         "Evaluating the raw expressions loses all precision in the tails, which is "
         "where decisions are made. Log-space and complementary error function forms "
         "keep relative accuracy everywhere.",
         "Poisson with lambda = 5, k = 40: P(X=40) = 5^40 e^-5/40! \u2248 2.7e-22, which "
         "underflows nothing at lambda 5, but at lambda = 200, k = 800 the factorial "
         "overflows a double while the true probability is about 1e-14. Log-space "
         "returns it correctly."),
        ("Normal approximation validity",
         "binomial to normal: require np >= 5 and n(1-p) >= 5\nwith continuity correction: P(X <= k) \u2248 Phi((k + 0.5 - np) / sqrt(np(1-p)))\nerror of order 1/sqrt(np(1-p))",
         "The approximation is a version of the CLT applied to Bernoulli sums. Its "
         "error scales inversely with the smaller expected count, which is why the "
         "rule of thumb exists.",
         "n = 10, p = 0.05: np = 0.5, far below 5, so the normal approximation is "
         "useless in the tail that matters for a 5% rate. Use the exact binomial or "
         "a Poisson approximation with lambda = np = 0.5."),
        ("Central limit theorem in practice",
         "X_i i.i.d. with mean mu, variance sigma^2\n(Xbar - mu) / (sigma/sqrt(n)) -> N(0,1)\nskewness of Xbar ~ skewness(X) / sqrt(n)",
         "The CLT justifies normal approximations for large samples and explains why "
         "sample means are better behaved than individual observations. It does not "
         "make heavy tails disappear at small n.",
         "Lognormal with median 10, sigma = 1: individual values have skewness 2.1, "
         "so a mean \u00b1 sd misdescribes them. The mean of 100 such values has skewness "
         "0.21 and an approximate normal shape, so n = 100 makes the mean summary "
         "defensible."),
        ("Exponential memorylessness and backoff",
         "f(t) = lambda e^(-lambda t)\nP(T > s + t | T > s) = e^(-lambda t) = P(T > t)\nmean wait 1/lambda, sd 1/lambda",
         "Memorylessness means a failure that has not happened after s units of time "
         "is indistinguishable from a fresh start. That is exactly the assumption "
         "behind exponential backoff, and its limit when the assumption fails.",
         "lambda = 0.1/s (mean 10 s): the chance of surviving 10 s is e^-1 = 0.368. "
         "With backoff doubling instead, after 10 s the effective hazard is halved, "
         "which is a different policy against the same unknown dependency."),
        ("Poisson overdispersion check",
         "under Poisson: Var(X) = mean(X)\ndispersion statistic: Var(X)/mean(X)\nvalues >> 1 indicate a rate that varies in time",
         "The Poisson's defining property is variance equal to mean. When the count "
         "varies more, the constant-rate assumption has failed and a negative "
         "binomial or a model with rate covariates is required.",
         "Requests per minute with mean 100 and variance 240: the dispersion ratio "
         "is 2.4. A single Poisson overpredicts the probability of an extreme peak, "
         "which is precisely the tail that matters for capacity planning."),
    ],
    math_traps=[
        "Evaluating factorials directly for large Poisson parameters.",
        "Comparing densities instead of CDFs when drawing a probability conclusion.",
        "Using a normal approximation with an expected count below 5.",
        "Applying a homogeneous Poisson model to a rate that varies by time of day.",
        "Reporting a Monte Carlo estimate without an interval.",
    ],
    math_problems=[
        "Evaluate a Poisson tail at lambda = 200, k = 800 in both direct and log space, and compare.",
        "Apply the continuity correction to a binomial tail and compare with the exact value.",
        "Sample 100 lognormals, show the skewness of the sample mean is about skew/sqrt(n), and verify with a histogram.",
        "Compute the memoryless residual life distribution for an exponential and compare with a Weibull alternative.",
        "Compute a dispersion ratio for hourly counts across a day and decide whether Poisson is adequate.",
    ],
    tree="""src/
  ProbabilityDistributions.java   driver: evaluates and samples each distribution
  NormalDistribution.java     PDF, CDF via erfc, sampling via Box-Muller
  BinomialDistribution.java   PMF in log space, CDF, normal approximation with continuity correction
  PoissonDistribution.java   log-space PMF, CDF via incomplete gamma, dispersion check
  ExponentialDistribution.java PDF, survival, memorylessness check
  MonteCarlo.java            seeded estimator with an interval from repeated runs""",
    tree_note="Binomial and Poisson both evaluate in log space with the same "
              "helper, so the underflow fix cannot be applied to one and forgotten "
              "in the other.",
    types=[
        ("NormalDistribution", "PDF, CDF via the complementary error function, Box-Muller sampling"),
        ("BinomialDistribution", "log-space PMF, exact CDF, approximation with a validity check"),
        ("PoissonDistribution", "log-space PMF, gamma-function CDF, dispersion statistic"),
        ("MonteCarlo", "seeded estimator returning a value and an interval"),
    ],
    patterns=[
        ("Log-space evaluation that survives large parameters",
         "Everything that can overflow is computed in log space, so tails stay "
         "accurate where the decision actually lives.",
         """public static double logPmf(int k, double lambda) {
    if (k < 0 || lambda <= 0) return Double.NEGATIVE_INFINITY;
    // lgamma(k+1) is log(k!) without ever forming k!, which overflows around 170
    return k * Math.log(lambda) - lambda - logGamma(k + 1);
}

public static double cdf(int k, double lambda) {
    if (k < 0) return 0.0;
    // upper regularised incomplete gamma: numerically stable in both tails,
    // unlike summing PMFs which loses all relative accuracy for large k
    return regularisedGammaQ(k + 1.0, lambda);
}

public static double normalCdf(double z) {
    // erfc form, not 1 - Phi(z): the tail keeps its relative accuracy
    return 0.5 * erfc(-z / Math.sqrt(2.0));
}"""),
        ("Sampling with a seed and validating the result",
         "Seeded sampling makes an estimate reproducible; a chi-square style check "
         "confirms the sampler actually matches the intended distribution.",
         """public static double[] sampleNormal(int n, double mu, double sigma, long seed) {
    SplittableRandom rnd = new SplittableRandom(seed);   // reproducible: a Monte Carlo
    double[] out = new double[n];                        // estimate you cannot check is not an estimate
    for (int i = 0; i < n; i += 2) {
        double u1 = Math.max(rnd.nextDouble(), 1e-12);
        double u2 = rnd.nextDouble();
        double r = Math.sqrt(-2 * Math.log(u1));
        double theta = 2 * Math.PI * u2;
        out[i]     = mu + sigma * r * Math.cos(theta);   // Box-Muller: two uniforms,
        out[i + 1] = mu + sigma * r * Math.sin(theta);   // two normals, exactly
    }
    return out;
}

public static boolean validateSampler(double[] sample, double mu, double sigma) {
    Variance acc = sampleMeanAndVariance(sample);         // compare against theory
    return Math.abs(acc.mean() - mu) < 4 * sigma / Math.sqrt(sample.length)
            && Math.abs(acc.sd() - sigma) / sigma < 0.1;   // sampling error aware
}"""),
    ],
    costs=[
        ("PDF/CDF evaluation", "O(1) or O(k) for exact tails", "log space keeps it constant"),
        ("Normal sampling", "O(n)", "Box-Muller produces two normals per pair of uniforms"),
        ("Exact Poisson or binomial CDF", "O(k)", "use the gamma form when k is large"),
        ("Monte Carlo estimate with an interval", "O(r x n)", "r repeats, n samples each"),
    ],
    numerics=[
        "Evaluate in log space whenever a factorial or power can overflow.",
        "Use the complementary error function for normal tails, not 1 minus the CDF.",
        "Use a regularised gamma function for large Poisson or binomial tails.",
        "Seed every generator; an unreproducible estimate cannot be checked.",
        "Report Monte Carlo results with an interval from repeated independent runs.",
    ],
    tests=[
        "Poisson PMF sums to 1 within 1e-9 for lambda = 3, 30 and 300.",
        "Binomial PMF sums to 1 within 1e-9 for n = 10, 100 and 1000.",
        "Direct and log-space PMF agree to 1e-12 where direct is finite.",
        "Normal CDF matches known values at z = 0, 1.96 and 3 to 1e-9.",
        "A seeded sampler produces identical output across runs and passes the moment check.",
        "Normal approximation agrees with the exact binomial within 2% when np >= 5, and the validity check rejects it otherwise.",
    ],
    extensions=[
        "Add a negative binomial for overdispersed counts and compare dispersion.",
        "Add a Weibull for non-memoryless waiting times and compare likelihoods.",
        "Add importance sampling for rare-event probability estimation.",
    ],
    code_checklist=[
        "All tail evaluation in log space with a stated error",
        "Approximations gated by a validity check, not applied blindly",
        "Sampling seeded and validated against theoretical moments",
        "Monte Carlo results reported with intervals",
        "Distributional assumptions checked, especially rate constancy",
        "Assumption violations reported rather than silently modelled around",
    ],
    exercise_selfcheck=[
        "I classified the variable before choosing a distribution.",
        "My tails are computed in log space.",
        "I checked for overdispersion before trusting Poisson.",
        "My simulation is reproducible and validated.",
    ],
    exercises=[
        ("Implement the four distributions",
         "PDF, CDF and PMF for each.",
         ["Implement normal, binomial, Poisson and exponential.",
          "Compute CDFs without lookup tables.",
          "Verify each distribution sums or integrates to one.",
          "Compare against known reference values."],
         "A verified distribution suite."),
        ("Numerical stability",
         "Break and fix the direct formulas.",
         ["Evaluate a Poisson tail at large lambda.",
          "Show factorial overflow and fix it with log space.",
          "Show normal tail cancellation with 1 - Phi.",
          "Fix both with the gamma and erfc forms."],
         "A stability report with before/after values."),
        ("Seeded sampling and validation",
         "Make simulation trustworthy.",
         ["Implement samplers for all four distributions.",
          "Verify moments against theory with a sampling-aware tolerance.",
          "Verify with a goodness-of-fit check.",
          "Show identical output for identical seeds."],
         "Validated, reproducible samplers."),
        ("Normal approximation with validity checks",
         "Know when it is allowed.",
         ["Compare the binomial CDF to its normal approximation across n and p.",
          "Implement the continuity correction.",
          "Implement and test the np >= 5 validity gate.",
          "Find where the approximation fails and explain why."],
         "An approximation comparison with a working validity gate."),
        ("Central limit theorem demonstration",
         "See non-normal data become normal in the mean.",
         ["Sample lognormals and heavily skewed data.",
          "Show the sample distribution is skewed at n = 10.",
          "Show the sample mean approaches normal by n = 1000.",
          "Report skewness against n against theory."],
         "A CLT demonstration with a skewness-versus-n curve."),
        ("Poisson overdispersion",
         "Find the violated assumption.",
         ["Generate hourly counts with a time-varying rate.",
          "Compute the dispersion ratio.",
          "Show the Poisson overstates extreme quantiles.",
          "Fit a negative binomial and compare."],
         "A dispersion analysis with an alternative model."),
        ("Exponential backoff simulation",
         "Connect distributions to a real design choice.",
         ["Simulate retries against exponential versus fixed backoff.",
          "Model a dependency that fails for a window then recovers.",
          "Compare total requests and time to recovery.",
          "Recommend a policy with numbers."],
         "A backoff simulation with a recommendation."),
        ("Monte Carlo with intervals",
         "Estimate quantities with no closed form.",
         ["Estimate a tail probability or integral by sampling.",
          "Repeat the estimate across independent seeds.",
          "Report the interval and its width.",
          "Show the interval narrows as sqrt(r)."],
         "A Monte Carlo report with intervals and a convergence check."),
    ],
    quiz=[
        ("Which distribution models waiting time between Poisson events?", ["Normal", "Exponential", "Binomial", "Poisson"], 1, "The exponential is continuous and memoryless; the Poisson counts events in an interval."),
        ("What is the defining property of a Poisson count?", ["Constant mean", "Variance equal to mean, from a constant rate with independent events", "Symmetry", "Bounded support"], 1, "Variance equals mean, so a ratio above one indicates the assumption failed."),
        ("What does overdispersion tell you?", ["Sampling error", "The event rate varies over time, so events cluster", "The sample is too small", "The mean is biased"], 1, "A non-constant rate breaks the model, usually toward a negative binomial."),
        ("When is the normal approximation to the binomial valid?", ["Always", "When np and n(1\u2212p) are both about 5 or more", "When n exceeds 1000", "When p is near 0.5"], 1, "Small expected counts in a tail invalidate the approximation exactly where it matters."),
        ("What does the central limit theorem require?", ["Normality of the data", "Independence and finite variance, not normality", "A large sample", "Symmetry"], 1, "Normality of the inputs is explicitly not required."),
        ("Why use the complementary error function for the normal CDF?", ["Speed", "1 minus the CDF loses relative accuracy in the tail", "Memory", "Precision near zero"], 1, "The subtraction cancels; erfc keeps the tail accurate."),
        ("Why does Poisson PMF evaluation overflow?", ["Large sample", "k! exceeds double range around k = 170", "Slow generator", "Rounding"], 1, "Log-space evaluation with a log-gamma function avoids forming k!."),
        ("What is the memoryless property?", ["P(X = x) declines exponentially", "Survival probability does not depend on time already elapsed", "Mean equals variance", "Independent events"], 1, "It is the assumption behind exponential backoff."),
        ("Box-Muller transforms...", ["One uniform into one normal", "Two independent uniforms into two normals", "Normals into uniforms", "Counts into rates"], 1, "It exploits the polar form of the bivariate normal."),
        ("Why compare CDFs rather than densities?", ["CDFs are cheaper", "A density value is not a probability", "Densities do not exist for discrete data", "CDFs are smoother"], 1, "Conclusions about likelihood need cumulative probability."),
        ("What does a Monte Carlo estimate require to be trustworthy?", ["Many samples", "A seed and an interval across independent runs", "Normal data", "A closed form"], 1, "An unreproducible estimate with no interval cannot be checked."),
        ("When should you use a Poisson rather than a binomial?", ["When trials are dependent or numerous with a small rate", "Never", "When you need a mean and variance", "For continuous measurements"], 0, "The Poisson is the limit of the binomial as n grows and p shrinks with np fixed."),
        ("What is a continuity correction for?", ["Correcting rounding", "Adjusting a discrete boundary when approximating with a continuous distribution", "Reducing variance", "Fixing skewness"], 1, "P(X \u2264 k) is approximated by Phi((k + 0.5 \u2212 np)/sqrt(np(1\u2212p)))."),
        ("How do you estimate a Poisson rate?", ["The median of the counts", "The sample mean of the counts, by maximum likelihood or moments", "The variance", "The maximum count"], 1, "Both estimators give the sample mean, which is the Poisson's sufficient statistic."),
        ("Why does an unseeded sampler undermine a Monte Carlo result?", ["It is slower", "The estimate cannot be reproduced or checked", "It biases the result", "It uses more memory"], 1, "Reproducibility is what turns a number into a result you can defend."),
    ],
    vision=dict(
        future="Distributions remain the vocabulary for reasoning under "
               "uncertainty, with heavy-tailed and compound families replacing "
               "normals wherever real operational data lives. The frontier is "
               "diagnostics: knowing which family a process belongs to, quickly, "
               "rather than assuming it.",
        good=[
            "The variable is classified before a family is chosen.",
            "Assumptions are checked, especially rate constancy and independence.",
            "Tails are evaluated in log space with stated approximation validity.",
            "Simulations are seeded and reported with intervals.",
        ],
        ladder=[
            ("L1", "Evaluate", "PDF, PMF and CDF for the four standard families."),
            ("L2", "Approximate", "Normal approximations with validity checks and continuity correction."),
            ("L3", "Sample", "Seeded samplers validated against theoretical moments."),
            ("L4", "Diagnose", "Detect overdispersion and rate variation, and choose alternatives."),
        ],
        behaviors="Check the assumptions before trusting the family. Evaluate tails "
                  "in log space. Seed everything, and report simulation results with "
                  "intervals.",
        anti=[
            "A Poisson model on hourly traffic that visibly varies with time of day.",
            "A tail probability computed as 1 minus a CDF in double precision.",
            "A simulation reported without a seed, an interval or a validation check.",
        ],
        trends=[
            "Heavy-tailed and compound distributions for operational metrics like latency and claim size.",
            "Automatic family selection with diagnostic tests rather than assumption by habit.",
            "Bayesian posterior predictive checks replacing goodness-of-fit tables.",
            "Simulation-based calibration for models whose tails cannot be evaluated.",
        ],
        d30="Implement the four standard distributions with verified normalisation.",
        d60="Make all tail evaluation stable and gate approximations with validity checks.",
        d90="Build validated seeded samplers and detect overdispersion with an alternative model.",
        metrics=[
            "I check assumptions before trusting a family.",
            "My tails are computed stably.",
            "My approximations state their validity conditions.",
            "My simulations are reproducible and reported with intervals.",
        ],
        closer="Most statistical mistakes with distributions are not arithmetic "
               "errors; they are confident applications to data the family does not "
               "describe.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Distribution Diagnostics and Stable Tails",
        brief="Build a distribution toolkit with log-space tails, seeded samplers, "
              "and diagnostics that detect when a family is wrong.",
        timebox="3 hours",
        why="The value here is not evaluating four formulas; it is knowing when the "
            "formula you are using does not apply.",
        requirements=[
            "Normal, binomial, Poisson and exponential with verified normalisation.",
            "Log-space evaluation with a stability comparison against the naive formula.",
            "Normal approximation with a continuity correction and an automatic validity gate.",
            "Seeded samplers validated against theoretical moments with sampling-aware tolerances.",
            "Overdispersion detection on real-shaped operational data, with an alternative model compared.",
            "Monte Carlo estimator with intervals and a convergence check.",
            "A backoff simulation connecting the exponential distribution to a real design decision.",
        ],
        steps=[
            ("1", "30m", "Implement the four distributions; verify normalisation", "A verified suite"),
            ("2", "30m", "Log-space evaluation and a stability report", "A before/after comparison"),
            ("3", "30m", "Normal approximation with continuity correction and validity gate", "A gated approximation"),
            ("4", "30m", "Seeded samplers with moment validation", "Validated samplers"),
            ("5", "35m", "Overdispersion detection with an alternative model", "A dispersion analysis"),
            ("6", "25m", "Monte Carlo estimate with intervals and convergence", "An interval report"),
            ("7", "25m", "Backoff simulation with a policy recommendation", "A recommendation with numbers"),
        ],
        diagram=""" observed process
    |
 classify: count | waiting time | continuous
    |
 family assumption check (independence, constant rate)
    |
 [1] evaluate (log space, verified normalisation)
 [2] approximate (validity gate + continuity correction)
 [3] sample (seeded, moment-validated)
 [4] diagnose (dispersion ratio, rate variation)
    |                        |
 normal family          overdispersed --> alternative model
    |                        |
 [5] Monte Carlo with intervals
 [6] backoff simulation --> policy recommendation""",
        notes=[
            "Construct the overflow case deliberately; lambda = 200, k = 800 makes the failure obvious.",
            "Sampling validation needs sampling-aware tolerances or it will reject correct samplers.",
            "Overdispersion analysis is more valuable than another distribution: it tells you the model is wrong.",
            "Tie the exponential distribution to retry backoff so the mathematics has an operational consequence.",
        ],
        deliverables=[
            "Verified distribution suite with a stability report.",
            "Gated normal approximation with continuity correction.",
            "Validated seeded samplers and a moment-check table.",
            "Overdispersion analysis with an alternative model, plus a backoff recommendation.",
        ],
        grading=[
            ("Correctness", "30%", "Normalisation verified; tails stable; approximation gated"),
            ("Validation", "25%", "Samplers moment-checked with sampling-aware tolerances"),
            ("Diagnosis", "25%", "Overdispersion detected with a justified alternative"),
            ("Communication", "10%", "Clear report connecting distributions to decisions"),
            ("Reproducibility", "10%", "Seeded throughout with intervals on estimates"),
        ],
        stretch=[
            "Add importance sampling for rare-event probability estimation.",
            "Add a negative binomial and a Weibull, comparing likelihoods on real data.",
            "Add simulation-based calibration for a model with hard-to-evaluate tails.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Arrival and Latency Modelling for Capacity",
        scenario="A payments platform sizes its infrastructure on request "
                 "arrivals and authorisation latency. Capacity was set from a "
                 "Poisson assumption while traffic clearly varies by time of day, "
                 "and last Black Friday peak latency was four times the predicted "
                 "p99.",
        scale=[
            ("Traffic", "steady 2,100/s, peak 11,000/s during Black Friday"),
            ("Latency target", "p99 under 250 ms; actual peak p99 was 980 ms"),
            ("Model today", "homogeneous Poisson for arrivals, normal for latency"),
            ("Failure", "peak capacity underestimated because arrivals cluster"),
            ("Requirement", "a distributional model that matches observed shape and drives capacity"),
        ],
        diagram=""" edge + gateway telemetry (timestamp, region, endpoint, outcome)
    |
 [1] arrivals per second --> dispersion ratio, rate variation by time of day
    |                             |
 Poisson adequate?         overdispersed --> negative binomial / rate model
    |
 [2] latency distribution --> skewness, tail percentiles, mixture check
    |                             |
 normal adequate?             skewed --> lognormal / mixture / tail model
    |
 [3] capacity model: queue depth vs service rate at observed arrival shapes
    |
 peak forecast with intervals, not point estimates
    |
 alerts on shape change (dispersion, skewness) as well as rate""",
        components=[
            ("Arrival modelling",
             ["Per-second and per-minute arrival counts by region and endpoint, with the raw series retained",
              "Dispersion ratio computed per window; overdispersion routed to a negative binomial or a rate model",
              "Rate modelled by time of day and day of week rather than as a single constant lambda",
              "Peak quantiles estimated from the fitted model with intervals, plus a direct empirical quantile for comparison"]),
            ("Latency modelling",
             ["Full latency distribution retained per endpoint, not just aggregates",
              "Skewness and tail percentiles computed; a lognormal or mixture compared against the normal",
              "Mixture detection across success and timeout paths, which have different shapes",
              "Service rate and its variability estimated to drive queueing-based capacity"]),
            ("Capacity model and forecasting",
             ["Queueing relationship between arrival shape, service rate and queue depth, using measured inputs",
              "Peak forecast produced with intervals from the fitted arrival model",
              "Scenario comparison: homogeneous Poisson versus time-varying negative binomial",
              "The chosen model published with its assumptions and its known limits"]),
            ("Operational integration",
             ["Capacity thresholds derived from the fitted quantiles rather than assumed percentiles",
              "Alerts on shape change (dispersion ratio, skewness) alongside rate thresholds",
              "Model refitted on a schedule with drift detection on the fitted parameters",
              "Analyst-facing summary showing empirical versus model quantiles side by side"]),
        ],
        timeline=[
            ("Week 1", "Retain arrival and latency series at full resolution; compute dispersion and skewness by window"),
            ("Week 2", "Fit time-varying arrival and latency models; compare against the homogeneous Poisson baseline"),
            ("Week 3", "Build the capacity model from measured arrival shape and service rate"),
            ("Week 4", "Scenario forecast with intervals; compare predictions against the Black Friday outcome"),
            ("Week 5", "Operational integration: thresholds from fitted quantiles, shape-change alerts, scheduled refits"),
        ],
        runbook=[
            "# Arrival shape now: dispersion ratio and rate by time of day",
            "curl -s 'localhost:9090/traffic/arrivals?window=24h' | jq '{dispersionRatio,lambdaByHour,model}'",
            "",
            "# Latency shape per endpoint, empirical and modelled quantiles",
            "curl -s 'localhost:9090/traffic/latency?endpoint=auth' | jq '{skewness,empirical:.p99,modelled:.p99Model,mixture}'",
            "",
            "# Capacity scenario comparison at the modelled peak",
            "curl -s 'localhost:9090/traffic/capacity?scenario=black-friday' | jq '{model,peakQps,queueDepth,p99Lower,p99Upper}'",
            "",
            "# What the homogeneous Poisson would have predicted",
            "curl -s 'localhost:9090/traffic/capacity?scenario=poisson' | jq '{peakQps,p99}'",
            "",
            "# Fitted parameter drift since last refit",
            "curl -s 'localhost:9090/traffic/model/drift' | jq '{lambdaDelta,dispersionDelta,refitAgeHours}'",
        ],
        metrics=[
            "Model fit: empirical versus modelled peak quantiles within a stated tolerance for each scenario.",
            "Shape: dispersion ratio and skewness tracked per window with alerts on change.",
            "Capacity: predicted peak queue depth versus observed across the last four events.",
            "Impact: peak latency relative to target, and capacity headroom at modelled peak.",
            "Trust: forecast intervals wide enough to be honest, verified against outcomes.",
        ],
        failures=[
            ("Peak p99 four times the forecast", "Homogeneous Poisson ignored rate variation", "Fit a time-varying model; compare scenarios explicitly; alert on dispersion change"),
            ("Fitted quantiles disagree with empirical quantiles", "Model family mismatch or fit drift", "Report both side by side; refit on a schedule; alert on parameter drift"),
            ("A timeout path inflates latency percentiles", "Success and timeout responses have different shapes", "Model them separately and combine by mixture weights"),
            ("Capacity threshold fires on normal peak variation", "Thresholds assumed rather than derived", "Derive thresholds from fitted quantiles with an agreed service level"),
            ("Model fits history and fails the next event", "No out-of-sample verification", "Backtest on the last four events and publish the error"),
        ],
        backlog=[
            "Negative binomial arrival model with time-of-day and event covariates.",
            "Automated family selection between Poisson, negative binomial and mixtures.",
            "Simulation-based calibration for the arrival model tail.",
            "Service-rate variability model feeding a queueing-based capacity model.",
            "Per-region model comparison with a single source of truth for capacity planning.",
        ],
        urls=URLS,
        closer="The deliverable is a capacity model that admits traffic clusters, "
               "reports its forecast with intervals, and is verified against the "
               "last four peak events rather than trusted.",
    ),
))

# ---------------------------------------------------------------- lab03
SPECS.append(dict(
    track="statistics", lab="lab03", full_set=True, level="Intermediate",
    title="Hypothesis Testing", main_class="com.statistics.lab03.HypothesisTesting",
    problem="A metric moved. Is it a real effect worth acting on, or the kind of "
            "movement that appears in every dataset you have ever looked at?",
    why_now="Testing is the discipline that separates an engineer who measures "
             "from one who narrates. The failure mode is not a wrong formula; it is "
             "the wrong test or an uncorrected test after twenty looks.",
    objectives=[
        "State null and alternative hypotheses precisely, including direction",
        "Compute t, z and chi-square statistics with correct degrees of freedom",
        "Compute p-values without a lookup table and interpret them correctly",
        "Distinguish Type I and Type II error and relate them to alpha and power",
        "Choose between paired and independent designs correctly",
        "Explain why p-values are not effect sizes and never say '5% chance it is null'",
    ],
    concepts=[
        ("Hypotheses are claims, not conclusions",
         "The null is usually 'no difference' or 'no association'. The alternative "
         "may be one-sided (a specific direction worth acting on) or two-sided. "
         "Choosing the direction after seeing the data inflates the false positive "
         "rate, so it must be pre-specified."),
        ("Type I and Type II error",
         "Type I is rejecting a true null, controlled by alpha. Type II is failing "
         "to reject a false null, equal to beta, and 1\u2212beta is power. Every "
         "significance choice is a trade between these two, which is why 'just lower "
         "alpha' is not a free improvement."),
        ("p-values are not what people say they are",
         "A p-value is the probability of data at least as extreme as observed, "
         "*given* the null. It is not the probability the null is true, and not the "
         "probability the result is a fluke. Reports that say '5% chance this is "
         "noise' are wrong in a way that misleads decisions."),
        ("Choosing the test follows the data type",
         "Means with unknown variance use t; proportions use z or chi-square; "
         "paired observations use a paired t on the differences. Chi-square tests "
         "categorical counts; it does not test means."),
        ("Multiple looks break the error rate",
         "Testing daily and stopping when p < 0.05 inflates the false positive rate "
         "far above 5%. Either fix the sample size and horizon in advance, or use a "
         "sequential method that controls the error rate while permitting early "
         "stopping."),
        ("Practical significance is separate",
         "A 0.3% difference can be highly significant on large samples and irrelevant "
         "as a business outcome. Report the effect size with an interval, then "
         "translate it. Statistical significance answers whether it is noise; it "
         "never answers whether it matters."),
    ],
    formulas=[
        ("H\u2080: \u03bc_A = \u03bc_B vs H\u2081: \u03bc_A \u2260 \u03bc_B", "Two-sample hypothesis", "state direction before data"),
        ("t = (x\u0304_A \u2212 x\u0304_B) / (s_p sqrt(1/n_A + 1/n_B))", "Two-sample t", "Welch unless equal variances"),
        ("df = n_A + n_B \u2212 2", "Degrees of freedom", "pooled version only"),
        ("z = (x\u0304 \u2212 \u03bc\u2080) / (\u03c3/sqrt(n))", "One-sample z", "known sigma"),
        ("\u03c7\u00b2 = \u03a3(O\u1d62 \u2212 E\u1d62)\u00b2 / E\u1d62", "Chi-square", "counts, not means"),
        ("df = k \u2212 1", "Chi-square df", "k categories"),
        ("p = P(T \u2265 |t|) under H\u2080", "p-value", "conditional on the null, not P(H\u2080)"),
        ("power = P(reject H\u2080 | H\u2081 true)", "Power", "1 \u2212 beta"),
    ],
    flow=[
        "Pre-specify the hypothesis, the direction, alpha, the test and the sample size.",
        "Verify the assumptions: independence, approximate normality for small n, equal variances for the pooled t.",
        "Choose the test from the data type and design: paired, independent, proportion or count.",
        "Compute the statistic and the p-value from the appropriate distribution.",
        "Report the effect size with a confidence interval alongside the p-value.",
        "If the test is inconclusive, report power rather than declaring no difference.",
    ],
    assumptions=[
        "Observations are independent within groups",
        "The test statistic's reference distribution is approximately correct at this n",
        "Equal variances hold for the pooled t; Welch is safer without that assumption",
        "The sample size was chosen for a target power, not for convenience",
        "The direction of the alternative was fixed before looking at the data",
        "Multiple comparisons across tests are accounted for",
    ],
    pitfalls=[
        ("'There is a 5% chance this is due to chance'", "p-value misquoted", "a p-value is P(data | H\u2080), not P(H\u2080 | data)"),
        ("p < 0.05 and reported as a 0.4% improvement worth shipping", "effect size ignored", "report the interval and translate to a business decision"),
        ("The null was not rejected, so the treatments are equivalent", "absence of evidence read as evidence of absence", "report the confidence interval and power"),
        ("Twenty daily tests, one reached p < 0.05", "uncorrected multiple looks", "fix the horizon, correct for looks, or use a sequential test"),
        ("A pooled t used with unequal variances and small n", "assumption violated", "Welch's test by default"),
        ("Direction chosen after seeing the improvement", "post-hoc one-sided test", "pre-specify, or adjust the alpha for the two looks"),
    ],
    java=[
        ("logGamma / incomplete beta for t and F CDFs", "p-values without lookup tables"),
        ("erfc for the normal CDF tail", "accurate in the far tail where p is small"),
        ("Welford statistics per group", "means and variances in one stable pass"),
        ("record TestResult(String test, double statistic, int df, double p, EffectSize effect, Interval ci)", "p-value and effect size travel together"),
        ("record Interval(double low, double high, double level)", "confidence intervals as a first-class type"),
    ],
    links=[
        "**lab04** extends mean comparison to three or more groups.",
        "**lab05** covers association and the regression model behind these tests.",
        "**lab09** provides the alternatives when normality fails.",
        "**lab10** supplies the power calculation that fixes sample size in advance.",
    ],
    checklist=[
        "Hypothesis, direction, alpha and sample size are pre-specified.",
        "I report the effect size and interval, not just the p-value.",
        "I never describe a p-value as the probability the null is true.",
        "I use Welch's t unless equal variances are justified.",
        "A non-significant result is reported with power, not as 'no effect'.",
        "Multiple looks and multiple comparisons are corrected.",
    ],
    cards=[
        ("What does a p-value actually mean?", "P(data at least as extreme as observed | the null is true). It is not P(null | data)."),
        ("What are Type I and Type II errors?", "Rejecting a true null (controlled by alpha) and failing to reject a false null (beta)."),
        ("Why prefer Welch's t?", "It does not assume equal variances, and with unequal n and small samples it is much less prone to distortion."),
        ("When is a paired test correct?", "When observations are paired, such as before and after on the same subject; the test runs on the differences."),
        ("What does failing to reject mean?", "Insufficient evidence at the chosen power, not evidence of no effect."),
        ("Why does p < 0.05 not mean a 5% chance of being wrong?", "The p-value is conditional on the null and does not express the probability that the conclusion is false."),
        ("Why is a very small p-value on a tiny effect a problem?", "With a large enough n any tiny difference becomes significant, which says nothing about business value."),
        ("How do multiple looks break Type I error?", "Each look is another chance to cross alpha, so the effective error rate far exceeds the nominal one."),
    ],
    extra_cards=[
        ("What does the confidence interval tell you that the p-value does not?", "The range of plausible effect sizes, which is what a decision actually needs."),
        ("Why is 'no significant difference' not 'the same'?", "Because you only know the data was insufficient to detect a difference at your power."),
        ("What is the standard error of a mean?", "s / sqrt(n): the standard deviation divided by the square root of the sample size."),
        ("What does one-sided versus two-sided really change?", "The alternative hypothesis, and therefore the threshold; choosing after seeing data inflates error."),
    ],
    math=[
        ("Test statistic and the reference distribution",
         "Welch: t = (xbar_A - xbar_B) / sqrt(s_A^2/n_A + s_B^2/n_B)\ndf (Welch) = (s_A^2/n_A + s_B^2/n_B)^2 / [ (s_A^2/n_A)^2/(n_A-1) + (s_B^2/n_B)^2/(n_B-1) ]\np = P(T_df >= |t|)",
         "The statistic measures the difference in units of its standard error, and "
         "the degrees of freedom determine which t distribution to compare against. "
         "Welch's df is fractional and always smaller than the pooled version, which "
         "is the conservative direction.",
         "n_A = n_B = 20, means differ by 0.4, s_A = s_B = 1.0: SE = sqrt(2/20) = "
         "0.316, t = 1.265, df = 38, p \u2248 0.21. With unequal variances, say s_A = "
         "1.0 and s_B = 3.0, Welch gives SE = sqrt(0.05 + 0.45) = 0.707, t = 0.566, "
         "p \u2248 0.58, whereas the pooled test wrongly reports t = 2.29 and p = 0.03."),
        ("Type I, Type II and power",
         "alpha = P(reject H_0 | H_0 true)\nbeta = P(fail to reject | H_1 true)\npower = 1 - beta\npower rises with n, with effect size, and with alpha",
         "Alpha and beta trade against each other at fixed n. That trade is the "
         "reason sample size is computed before the experiment: fixing alpha without "
         "considering power leaves you with a test that cannot detect the effect you "
         "care about.",
         "Effect size d = 0.5, alpha = 0.05 two-sided, power 0.80: n = 64 per group. "
         "Power 0.50 needs only n = 33, so the same study at half the size would miss "
         "half the real effects it was designed to find."),
        ("Confidence interval versus p-value",
         "difference estimate d-hat with SE = s/sqrt(n)\nCI = d-hat \u00b1 t_{1-alpha/2, df} SE\nCI excluding 0 is equivalent to p < alpha, but the interval carries magnitude",
         "The interval and the p-value encode the same decision, but only one of "
         "them tells you the size of the effect and its precision. Reports that give "
         "only a p-value force readers to guess the magnitude.",
         "d-hat = 0.40, SE = 0.12, CI = [0.16, 0.64], p = 0.001. The p-value says "
         "'significant'; the interval says the effect could plausibly be 0.16, which "
         "may or may not matter commercially."),
        ("Multiple looks and the inflation",
         "under the null, per-look alpha behaves as ~1 - (1 - alpha)^k\nk looks at alpha = 0.05: k=2 -> 0.0975, k=5 -> 0.226, k=10 -> 0.401\nfix the horizon, or use a sequential design",
         "Each additional look is another opportunity to cross alpha by chance. The "
         "inflation grows quickly, which is why teams that 'watch and stop' ship "
         "noise at a rate far above their nominal 5%.",
         "A metric monitored daily for 14 days with a stop at first p < 0.05 has an "
         "effective error rate near 52%. A sequential design with alpha spending "
         "holds the true rate at 5% while still permitting early stopping."),
    ],
    math_traps=[
        "Interpreting a p-value as P(null | data).",
        "Using the pooled t when variances are unequal and n is small.",
        "Declaring equivalence from a non-significant result.",
        "Testing many times and reporting only the crossing test.",
        "Choosing a one-sided alternative after seeing the direction.",
    ],
    math_problems=[
        "Compute Welch's t and fractional degrees of freedom for two groups with unequal variances.",
        "Derive the per-look false positive inflation for k looks at a given alpha.",
        "Compute a confidence interval and verify it excludes 0 exactly when the test is significant.",
        "Design a test for a given effect size, alpha and power; report n and the achievable MDE.",
        "Take a real metric you track daily, simulate the null, and measure the false positive rate of your current process.",
    ],
    tree="""src/
  HypothesisTesting.java     driver: runs each test on fixtures and prints results
  TestResult.java            statistic, df, p-value, effect size, interval together
  TTest.java                 one-sample, two-sample Welch, paired on differences
  ZTest.java                 one-sample and two-proportion with a known sigma
  ChiSquareTest.java         goodness of fit and independence on counts
  EffectSize.java            Cohen's d, Hedges' g, risk difference, ratio
  Interval.java              confidence interval with its level as a type""",
    tree_note="TestResult carries the effect size and interval alongside the "
              "p-value. It is structurally impossible in this codebase to print a "
              "p-value without the effect attached.",
    types=[
        ("TestResult", "statistic, degrees of freedom, p-value, effect size and interval together"),
        ("TTest", "one-sample, two-sample Welch, and paired implemented on differences"),
        ("ChiSquareTest", "goodness of fit and independence on integer counts with expected-count checks"),
        ("EffectSize", "Cohen's d, Hedges' g, risk difference and risk ratio"),
    ],
    patterns=[
        ("Welch's t with fractional degrees of freedom",
         "No equal-variance assumption, and the fractional df is what makes the "
         "reference distribution conservative.",
         """public static TestResult welch(double[] a, double[] b) {
    Variance va = meanAndVariance(a), vb = meanAndVariance(b);
    double seA = va.variance() / a.length, seB = vb.variance() / b.length;
    double se = Math.sqrt(seA + seB);
    double t = (va.mean() - vb.mean()) / se;
    // Welch-Satterthwaite: fractional df, always smaller than the pooled version,
    // so the reference distribution is conservative when variances differ
    double df = Math.pow(seA + seB, 2)
            / (Math.pow(seA, 2) / (a.length - 1) + Math.pow(seB, 2) / (b.length - 1));
    double p = 2 * (1 - studentTCdf(Math.abs(t), df));
    return new TestResult("welch", t, df, p,
            effectSize(a, b), meanDifferenceInterval(va, vb, df));
}"""),
        ("Effect size and interval attached to every test",
         "The p-value never travels alone, which removes the most common reporting "
         "failure in practice.",
         """public record TestResult(String test, double statistic, double df, double pValue,
                      double effectSize, Interval effectCi, String assumptions) {}

static TestResult interpret(TestResult r, double alpha) {
    // a non-significant result must be reported with power, never as 'no effect'
    if (r.pValue() >= alpha)
        return r.withNote("inconclusive at alpha=" + alpha
                + "; report the confidence interval and the achieved power");
    // a significant result must carry magnitude, because significance says nothing about value
    return r.withNote("significant, effect " + fmt(r.effectSize())
            + " with CI " + r.effectCi() + "; decide on the interval, not the p-value");
}"""),
    ],
    costs=[
        ("Statistic computation", "O(n)", "one stable pass per group"),
        ("p-value from t, F or chi-square", "O(1) to O(k)", "incomplete beta and gamma evaluations"),
        ("Bootstrap interval", "O(r x n)", "r resamples when no closed form exists"),
        ("Power calculation", "O(1)", "non-central t or normal approximations"),
    ],
    numerics=[
        "Compute p-values from incomplete beta and gamma functions, not lookup tables.",
        "Use erfc for normal tails so small p-values stay accurate.",
        "Prefer Welch's t; use the pooled version only with an explicit variance check.",
        "Attach the effect size and interval to every result, structurally.",
        "Report power alongside a non-significant result.",
    ],
    tests=[
        "Welch's t reduces to the pooled t when variances are equal.",
        "A paired test on identical groups gives a zero difference and p = 1.",
        "Chi-square expected counts below 5 are detected and reported as a warning.",
        "The confidence interval excludes 0 exactly when p < alpha.",
        "A result with p >= alpha carries a note demanding power reporting.",
        "Simulating the null at alpha = 0.05 yields a rejection rate within tolerance.",
    ],
    extensions=[
        "Add bootstrap and permutation alternatives that assume less.",
        "Add multiple-comparison correction across a family of tests.",
        "Add a sequential test with alpha spending for monitoring-style data.",
    ],
    code_checklist=[
        "Hypothesis, direction and alpha pre-specified before computation",
        "Welch's t by default; pooled only with justification",
        "p-values computed from distributions, not tables",
        "Effect size and confidence interval attached to every result",
        "Non-significant results reported with power, not as no effect",
        "Multiple looks and comparisons accounted for",
    ],
    exercise_selfcheck=[
        "I can state what my p-value means in one sentence.",
        "My reports never show a p-value without an effect size.",
        "I report power when a result is inconclusive.",
        "My test choice matches the data type and design.",
    ],
    exercises=[
        ("Implement the test suite",
         "Correct statistics and honest reporting.",
         ["Implement one-sample, Welch two-sample and paired t.",
          "Implement chi-square goodness of fit and independence.",
          "Compute effect sizes and confidence intervals for each.",
          "Verify against hand calculations."],
         "A verified test suite with effect sizes attached."),
        ("Assumptions that fail",
         "Test the edge cases.",
         ["Use highly unequal variances with small n; show the pooled test failing.",
          "Compare pooled and Welch p-values.",
          "Detect expected counts below 5 in chi-square.",
          "Write the reporting note for each violated assumption."],
         "A comparison showing why assumptions matter."),
        ("Interpretation drill",
         "Fix the sentences people actually write.",
         ["Take ten real reported results.",
          "Rewrite each p-value claim correctly.",
          "Attach effect sizes and intervals.",
          "Mark which conclusions were unsupported."],
         "A rewritten report with corrected reasoning."),
        ("Power and sample size",
         "Size the test before running it.",
         ["Compute required n for an effect size, alpha and power.",
          "Compute achievable MDE at a given n.",
          "Show power at a deliberately underpowered n.",
          "Report the risk of a false negative."],
         "A power table with an underpowered example."),
        ("Multiple looks",
         "Measure the inflation you create by watching.",
         ["Simulate the null metric over k looks.",
          "Measure the false positive rate for k = 1, 5, 10, 20.",
          "Implement a sequential alpha-spending correction.",
          "Show the corrected rate."],
         "An inflation measurement with a correction."),
        ("Permutation and bootstrap alternatives",
         "Reduce distributional assumptions.",
         ["Implement a permutation test for a difference in means.",
          "Implement a bootstrap interval for a median.",
          "Compare results against the parametric tests.",
          "Explain where each agrees and where they diverge."],
         "An assumption-light comparison."),
        ("Multiple comparisons",
         "Correct for the family of tests.",
         ["Run 20 tests under the null.",
          "Measure the family-wise false positive rate.",
          "Apply Bonferroni and false discovery rate control.",
          "Show how many true findings survive."],
         "A correction comparison with a verdict."),
        ("Full analysis write-up",
         "Produce something you would defend.",
         ["Design a pre-registered test with power.",
          "Run it on a real or realistic dataset.",
          "Report hypothesis, assumptions, statistic, p, effect, interval and limitations.",
          "Write the decision and its business translation."],
         "A complete write-up a reviewer accepts."),
    ],
    quiz=[
        ("What does a p-value of 0.03 mean?", ["3% chance the null is true", "P(data this extreme | the null is true)", "3% chance of being wrong", "The effect is 3%"], 1, "It is conditional on the null, which is the part almost always misreported."),
        ("Type I error is...", ["Failing to reject a false null", "Rejecting a true null", "Using the wrong test", "Sampling error"], 1, "Type I error is controlled by alpha; Type II is beta."),
        ("Power is...", ["1 - alpha", "1 - beta, the probability of detecting a real effect", "The sample size", "The effect size"], 1, "Power is the probability of rejecting a false null."),
        ("Why prefer Welch's t?", ["It is simpler", "It does not assume equal variances", "It needs less data", "It gives a smaller p"], 1, "The pooled test badly distorts p-values when variances differ and n is small."),
        ("When is a paired test correct?", ["When groups are large", "When observations are paired, such as before and after", "When variance is low", "Always"], 1, "The test runs on within-pair differences, which removes between-unit variation."),
        ("What does a non-significant result tell you?", ["The treatments are equal", "Insufficient evidence at the achieved power", "The test was wrong", "The effect is zero"], 1, "Absence of evidence is not evidence of absence; report power and the interval."),
        ("Why does p < 0.05 on a tiny effect not mean it matters?", ["It does mean it", "With large n any small difference becomes significant, so magnitude must be judged separately", "p-values are biased", "It means the test failed"], 1, "Significance answers whether it is noise, never whether it is worth acting on."),
        ("What does testing daily and stopping at p < 0.05 do?", ["Nothing", "Inflates the false positive rate far above 5%", "Reduces the p-value", "Improves power"], 1, "Repeated uncorrected looks behave like multiple testing."),
        ("How do you fix the multiple-look problem?", ["Use a smaller alpha", "Fix the horizon in advance or use a sequential design with alpha control", "Test less often", "Use a larger sample"], 1, "Alpha spending or always-valid confidence sequences preserve the error rate."),
        ("What is chi-square used for?", ["Comparing means", "Testing categorical counts for goodness of fit or independence", "Testing proportions directly", "Any test"], 1, "Chi-square operates on counts; it is not a test of means."),
        ("Why does expected count below 5 matter in chi-square?", ["It slows the test", "The chi-square approximation to the null distribution assumes expected counts of about 5 or more", "It changes df", "It biases the effect size"], 1, "Small expected counts make the reference distribution unreliable in the tails."),
        ("Choosing a one-sided alternative after seeing data...", ["Is fine", "Inflates the error rate; the direction must be pre-specified", "Reduces power", "Is required for small n"], 1, "Choosing the direction post hoc is a second look in disguise."),
        ("What does the confidence interval give you that p does not?", ["A smaller number", "The plausible range of effect magnitudes, which drives the decision", "Higher power", "Fewer assumptions"], 1, "Only the interval tells you how big the effect might be."),
        ("What does H\u2080 being 'no difference' mean?", ["It is true", "It is a claim to be evaluated with its probability of being detected, not an assumption of truth", "The alternative is false", "Nothing"], 1, "The null is a hypothesis whose rejection rate you control with alpha."),
        ("Why fix sample size before collecting data?", ["For ethics", "Power is a function of n; collecting first risks a test that cannot detect the effect you care about", "To reduce cost", "To simplify analysis"], 1, "Choosing n after seeing effect sizes is the most common source of invalid inference."),
    ],
    vision=dict(
        future="Hypothesis testing shifts toward always-valid inference, "
               "estimation-first practice with intervals as the primary output, and "
               "causal designs that make the counterfactual explicit. The p-value "
               "survives as a technical detail rather than a headline.",
        good=[
            "Hypothesis, direction, alpha and sample size are pre-registered.",
            "Every result carries an effect size and an interval.",
            "Non-significant results report power rather than claiming no effect.",
            "Multiple looks and comparisons are corrected.",
        ],
        ladder=[
            ("L1", "Test", "Pick the right test, compute the statistic and the p-value."),
            ("L2", "Report", "Attach effect size, interval and assumptions."),
            ("L3", "Design", "Pre-register power, direction and the stopping rule."),
            ("L4", "Control", "Sequential inference, multiplicity correction, permutation alternatives."),
        ],
        behaviors="Estimate first and test second. Report intervals, not verdicts. "
                  "Design the test before looking, and treat a non-significant result "
                  "as a power question rather than a finding.",
        anti=[
            "'5% chance this is due to chance' in a slide deck.",
            "A p < 0.05 headline with no magnitude.",
            "'No significant difference, so the features are equivalent'.",
            "A metric watched daily with a stop at first significance.",
        ],
        trends=[
            "Estimation-first reporting with intervals as the headline.",
            "Always-valid confidence sequences replacing fixed-horizon significance.",
            "Frequentist and Bayesian convergence on posterior intervals for well-specified models.",
            "Equivalence and non-inferiority designs replacing 'not significant' conclusions.",
        ],
        d30="Implement t, z and chi-square tests with effect sizes attached.",
        d60="Add confidence intervals and report power for every inconclusive result.",
        d90="Add sequential inference and multiplicity correction, and pre-register a real analysis.",
        metrics=[
            "I can state what my p-value means without hedging.",
            "My reports never show a p-value without an effect size.",
            "I report power when a result is inconclusive.",
            "My tests are pre-registered with a sample size from power.",
        ],
        closer="A p-value without an interval is a verdict without a measurement, "
               "and it is not evidence that anything matters.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Pre-Registered Experiment with Honest Inference",
        brief="Design a powered test, run it, and report the result with an effect "
              "size, an interval and an honest conclusion.",
        timebox="3\u20134 hours",
        why="Everything in this lab exists to prevent one specific failure: a "
            "confident claim that a small noisy difference is a result.",
        requirements=[
            "Pre-registered plan: hypothesis, direction, alpha, power, sample size and stopping rule.",
            "Implementation of one-sample, Welch two-sample, paired t and chi-square, all verified by hand.",
            "Effect size and confidence interval attached to every result, structurally.",
            "Assumption checks with reporting notes for violated assumptions.",
            "Power and MDE computed before data collection; achievable MDE reported.",
            "Simulation measuring the false positive rate of a daily-look process versus a fixed-horizon process.",
            "Written analysis reporting the decision in business units.",
        ],
        steps=[
            ("1", "30m", "Pre-registration with power and sample size", "A plan with real arithmetic"),
            ("2", "40m", "Implement the tests with effect sizes and intervals", "A verified suite"),
            ("3", "25m", "Assumption checks with reporting notes", "Assumption-violation handling"),
            ("4", "30m", "Run on realistic data; report effect and interval", "A result with magnitude"),
            ("5", "30m", "False positive simulation for daily looks", "An inflation measurement"),
            ("6", "25m", "Non-significant result reported with power", "An honest inconclusive report"),
            ("7", "30m", "Business translation and decision memo", "A decision memo"),
        ],
        diagram=""" pre-registration: H0, direction, alpha, power, n, stopping rule
     |
 data collection (fixed horizon)
     |
 [1] assumption checks --> notes when violated
 [2] statistic + df + p from the correct distribution
 [3] effect size + confidence interval (attached, always)
     |
 decision: significant --> effect interval -> business units
           inconclusive --> power + interval (never "no effect")
     |
 simulation: false positive rate, daily-look vs fixed-horizon""",
        notes=[
            "Write the plan before writing the data pipeline, or you will rationalise the outcome.",
            "Include one deliberately underpowered case and report it honestly.",
            "The daily-look simulation makes the inflation concrete; use your own metric if you have one.",
            "The decision memo must be writable without mentioning a p-value.",
        ],
        deliverables=[
            "Pre-registration document with power arithmetic.",
            "Verified test suite with effect sizes attached by construction.",
            "False positive comparison between daily looks and a fixed horizon.",
            "Analysis write-up plus a decision memo in business units.",
        ],
        grading=[
            ("Design", "25%", "Pre-registered with real power and sample size arithmetic"),
            ("Correctness", "25%", "Tests verified, correct df, assumptions checked"),
            ("Honesty", "30%", "Effect size and interval always; power on inconclusive"),
            ("Discipline", "10%", "Multiple looks and multiplicity accounted for"),
            ("Communication", "10%", "Decision memo in business units"),
        ],
        stretch=[
            "Add a sequential design and compare time-to-decision at equal error rates.",
            "Add permutation and bootstrap alternatives for assumption-light results.",
            "Add equivalence or non-inferiority framing for a practical-significance question.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Experiment Inference for a Live Ranking Change",
        scenario="A marketplace tests a ranking change with a live A/B framework. "
                 "The team reported 'significant at p < 0.05, ship it' and the "
                 "change was reverted a week later. Nothing in the process "
                 "distinguished a real improvement from a daily look.",
        scale=[
            ("Traffic", "18M sessions/day, peak 5k QPS"),
            ("Primary metric", "GMV per session, heavy-tailed and noisy"),
            ("Current practice", "p < 0.05 from a nightly check, no effect size, no power"),
            ("Outcome", "one revert last month, one disputed claim in the current test"),
            ("Constraint", "trading decisions must move weekly, so speed matters"),
        ],
        diagram=""" experiment registry (H0, direction, alpha, power, n, horizon)
     |
 assignment (stable hash) --> telemetry
     |
 [1] assumption checks: variance, independence, heavy tails
 [2] primary test: Welch t on GMV/session (or variance reduction applied)
 [3] effect size + 95% interval, always reported
 [4] guardrails as non-inferiority checks
     |
 decision engine
   significant + interval clears business threshold -> promote
   inconclusive -> report power, extend horizon if planned, do not ship
     |
 decision memo: effect, interval, power, business translation
 monitoring: sequential re-check with alpha control""",
        components=[
            ("Pre-registration and power",
             ["Every experiment registers hypothesis, direction, alpha, power, MDE, sample size and horizon before exposure",
              "Sample size derived from the variance of the primary metric, measured on recent traffic rather than assumed",
              "Minimum detectable effect agreed with the business before the run",
              "Registration is required for traffic allocation; unregistered tests are not reported as decisions"]),
            ("Assumptions and inference",
             ["Variance checked per arm; Welch's t used unless equal variance is justified",
              "Heavy tails addressed with a variance-reduction technique or a rank-based sensitivity analysis",
              "Primary effect reported with a confidence interval, never a p-value alone",
              "Guardrails evaluated as non-inferiority bounds with pre-agreed margins"]),
            ("Decision engine",
             ["Ship requires the confidence interval's lower bound to clear a pre-agreed business threshold, not merely p < alpha",
              "Inconclusive results report power and either extend the horizon as planned or stop, with the reason recorded",
              "Override path is possible but logged, expiring and reviewed monthly",
              "Every decision produces a memo with effect, interval, power and business translation"]),
            ("Ongoing discipline",
             ["Interim looks use a sequential design with alpha control, or are recorded as non-decisional",
              "Variance-reduction technique calibrated on recent traffic so its gain is known before the test",
              "Reverted changes reviewed to extract what the inference missed",
              "Experiment portfolio view: running, inconclusive, shipped, reverted"]),
        ],
        timeline=[
            ("Week 1-2", "Experiment registry with mandatory pre-registration and power from measured variance"),
            ("Week 3", "Assumption checks and a rank-based sensitivity analysis added to the report"),
            ("Week 4", "Decision engine requiring an interval-based business threshold"),
            ("Week 5-6", "Sequential interim looks with alpha control; override review process"),
            ("Week 8", "Post-incident review of the reverted change; portfolio dashboard live"),
        ],
        runbook=[
            "# Registered plan for an experiment",
            "curl -s 'localhost:8088/experiments/exp-221/plan' | jq '{hypothesis,direction,alpha,power,n,horizon,mde}'",
            "",
            "# Assumption checks and the chosen test",
            "curl -s 'localhost:8088/experiments/exp-221/assumptions' | jq '{varianceRatio,independent,heavyTailed,test,notes}'",
            "",
            "# Effect size with interval, plus power if inconclusive",
            "curl -s 'localhost:8088/experiments/exp-221/result' | jq '{estimate,ci,power,clearsBusinessThreshold}'",
            "",
            "# Guardrail status as non-inferiority bounds",
            "curl -s 'localhost:8088/experiments/exp-221/guardrails' | jq '.[] | {metric,delta,lower,bound,status}'",
            "",
            "# Overrides and reverts in the last 90 days",
            "curl -s 'localhost:8088/experiments/overrides?window=90d' | jq '.[] | {id,actor,reason,expiresAt,reverted}'",
        ],
        metrics=[
            "Process: pre-registration compliance at 100% before exposure.",
            "Decision quality: fraction of shipped changes whose interval clears the business threshold.",
            "Reversals: reverts per quarter with a recorded cause.",
            "Honesty: experiments reporting power when inconclusive, versus shipping anyway.",
            "Speed: median time-to-decision against the planned horizon, with sequential re-check rules.",
        ],
        failures=[
            ("A change ships on p < 0.05 with a trivial effect", "No business threshold on the interval", "Require the interval's lower bound to clear a pre-agreed threshold"),
            ("Interim looks inflate the false positive rate", "Daily uncorrected significance checks", "Use a sequential design with alpha control; interim looks are non-decisional"),
            ("A test concludes 'no difference' after a short run", "No power reporting", "Report power and MDE; extend the horizon only as pre-registered"),
            ("Heavy-tailed GMV/session makes the t-test unreliable", "Assumptions unchecked", "Variance reduction plus a rank-based sensitivity analysis reported alongside"),
            ("Overrides become routine", "No expiry or review", "Overrides expire automatically and are reviewed monthly with outcomes"),
        ],
        backlog=[
            "Variance-reduction technique calibrated per metric from historical traffic.",
            "Sequential design with alpha spending implemented in the decision engine.",
            "Automated assumption checks blocking tests that violate stated requirements.",
            "Equivalence testing for 'no meaningful difference' questions.",
            "Post-hoc analysis of reverted experiments fed back into the pre-registration defaults.",
        ],
        urls=URLS,
        closer="The deliverable is an experimentation framework where a ship "
               "decision requires an interval that clears a business threshold, "
               "inconclusive means power rather than optimism, and no interim look "
               "can manufacture a result.",
    ),
))
