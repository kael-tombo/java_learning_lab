# -*- coding: utf-8 -*-
"""Tailored specs for labs/mlops/lab09 .. lab11."""

from mlops_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab09
SPECS.append(dict(
    track="mlops", lab="lab09", full_set=True, level="Intermediate",
    title="Data Validation & Quality", main_class="DataValidationLab",
    problem="Garbage in is not a modelling problem, it is a data problem. Most "
            "silent model failures start as a schema change nobody noticed.",
    why_now="Validation is the cheapest place to catch an incident: a failed "
             "expectation costs seconds, a model trained on corrupted data costs a "
             "quarter of debugging.",
    objectives=[
        "Express data quality as verifiable expectations rather than ad-hoc checks",
        "Implement schema, range, nullability, uniqueness and distribution checks",
        "Approximate a distribution comparison with a rank statistic",
        "Design a validation suite that fails the pipeline rather than logging",
        "Separate blocking expectations from warnings",
        "Track data quality as a metric with trend and ownership",
    ],
    concepts=[
        ("Expectations are executable contracts",
         "An expectation is a statement that can be evaluated: 'column x is never "
         "null', 'column y is between 0 and 1', 'column z is unique'. Bundling them "
         "into a suite gives a validation run an identity that can be compared over "
         "time, which is what turns spot checks into a trend."),
        ("Blocking versus warning",
         "A blocking expectation stops the pipeline. A warning is recorded and "
         "routed. Confusing them is why teams end up ignoring all alerts: a nightly "
         "null rate of 0.5% becomes an error, gets overridden daily, and then "
         "hides a real 60% null rate."),
        ("Schema and contract checks come first",
         "Type, nullability and column existence are cheap and catch the most "
         "destructive failures. An upstream integer that becomes a string will "
         "silently produce garbage features unless a contract blocks it."),
        ("Distribution checks catch subtle drift",
         "Range checks pass while the shape changes. A rank statistic comparing "
         "sorted reference and current samples catches shape change without "
         "assuming a distribution, which matters for skewed business data."),
        ("Validation runs on the data that matters",
         "Validating a sample is a trade: a 1% sample misses a rare corruption. "
         "Full validation is often affordable if the checks are pushed down to the "
         "engine rather than pulled into the JVM."),
        ("Quality is a metric, not a gate alone",
         "Null rate, duplicate rate and freshness need trend dashboards with owners. "
         "A gate tells you it broke; a trend tells you it is degrading before it "
         "breaks."),
    ],
    formulas=[
        ("expectation: violation_count = |{r : predicate(r) false}|", "Expectation", "the atomic unit of validation"),
        ("null_ratio = nulls / rows", "Null ratio", "with a threshold and an owner"),
        ("rate_diff = |p_current - p_reference|", "Rate comparison", "for binary and categorical checks"),
        ("KS = max|F_cur(x) - F_ref(x)|", "Rank statistic", "shape comparison without assuming a form"),
        ("freshness = now - max(event_ts)", "Freshness", "the most common real failure"),
        ("suite_score = 1 - weighted_violations", "Suite result", "comparable over time"),
    ],
    flow=[
        "Declare the schema contract: columns, types, nullability, primary keys.",
        "Add domain expectations: ranges, allowed categories, referential integrity.",
        "Add distribution expectations against a reference sample from production.",
        "Add freshness and volume expectations, which catch upstream stalls first.",
        "Classify each expectation as blocking or warning, with owners.",
        "Run the suite on every pipeline stage that consumes the data and store the results as a trend.",
    ],
    assumptions=[
        "Every expectation has an owner and a threshold with provenance",
        "Blocking expectations are rare enough to be trusted when they fire",
        "Checks are pushed to the engine so full validation is affordable",
        "Reference distributions come from known-good production data",
        "Validation results are stored as a trend, not just a pass or fail",
        "Freshness and volume are validated, since they catch upstream stalls first",
    ],
    pitfalls=[
        ("Warnings are overridden daily and a real break hides among them", "no separation of blocking from warning", "classify expectations explicitly; keep blocking failures rare"),
        ("An integer column became a string and nothing failed", "no type contract on the boundary", "schema expectations run before any transformation"),
        ("Validation passes but the data is 9 days old", "no freshness expectation", "freshness and volume are expectations like any other"),
        ("Sampling 1% misses a corruption affecting 0.5% of rows", "sampling below the failure granularity", "push checks down to the engine and validate fully"),
        ("Duplicate rows double-count revenue", "no uniqueness or primary key expectation", "uniqueness on the natural key plus a duplicate rate trend"),
        ("Every alert is ignored after two weeks", "thresholds copied with no reference history", "set thresholds from observed history and review them quarterly"),
    ],
    java=[
        ("record Expectation(String name, String column, Predicate<Row> check, Severity severity)", "a named, classified, executable check"),
        ("BigDecimal for rate comparisons", "null and duplicate ratios compared at a defensible precision"),
        ("Stream<LongSummaryStatistics> for volume", "row counts and key cardinalities in one pass"),
        ("record ValidationResult(String suite, Instant at, Map<String,Long> violations)", "the stored trend row"),
        ("EnumSet / Map<Expectation,Long> for the report", "all failures listed, not just the first"),
    ],
    links=[
        "**mlops/lab01** runs validation as the first node of the DAG.",
        "**mlops/lab04** validates the inputs before materialising features.",
        "**mlops/lab08** uses validation results as an early drift signal.",
        "**mlops/lab07** puts contract tests in the CI fast lane.",
    ],
    checklist=[
        "Every expectation has an owner and a threshold with provenance.",
        "Blocking and warning expectations are separated and stay rare.",
        "Schema, freshness and volume are validated before anything else.",
        "Checks are pushed down so full validation is affordable.",
        "Results are stored as a trend with history.",
        "Thresholds come from observed production history.",
    ],
    cards=[
        ("What is a data expectation?", "An executable statement about data that can be evaluated and stored, such as a nullability or range rule."),
        ("Why separate blocking from warning expectations?", "So blocking failures stay rare and trustworthy; a gate that fires daily gets ignored."),
        ("Which check catches an upstream type change?", "A schema or type contract on the boundary"),
        ("Why validate freshness and volume?", "They catch upstream stalls and partial loads before any downstream model sees bad data."),
        ("What does a KS-style statistic give you?", "A shape comparison between reference and current samples without assuming a distribution."),
        ("Why is sampling risky for validation?", "A 1% sample misses corruptions affecting less than 1% of rows, which are often the important ones."),
        ("Where should checks run?", "Pushed down to the query engine so full validation is affordable on large tables."),
        ("Why store validation results as a trend?", "A pass or fail tells you it broke; a trend tells you it is degrading before it breaks."),
    ],
    extra_cards=[
        ("What is the cheapest high-value expectation set?", "Schema, nullability, primary key uniqueness, freshness and volume."),
        ("How do you pick a threshold for a null rate?", "From observed history, with a review cadence, rather than a round number."),
        ("What is a duplicate rate expectation for?", "Catching fan-out from a join or a replayed ingestion, which silently double-counts metrics."),
        ("How do you avoid validation blocking on seasonality?", "Use window-aware expectations: volume in the same period last week rather than a flat number."),
        ("What is a validation suite for?", "Grouping expectations under an identity so results are comparable over time and per dataset."),
    ],
    math_why="Data quality is hypothesis testing applied to pipelines: rate "
             "comparisons with a noise floor, sampling detection probability, and "
             "rank statistics for shape.",
    math=[
        ("Rate differences and their noise floor",
         "p_hat = violations / n\nSE(p_hat) = sqrt(p(1-p)/n)\nsignificant if |p_cur - p_ref| > z * sqrt(SE_ref^2 + SE_cur^2)",
         "Comparing two rates without accounting for sampling noise turns normal "
         "variation into alerts. This is the same two-proportion test from "
         "statistics applied to data quality, and it is what makes thresholds "
         "defensible.",
         "Null rate 0.5% on n=1M vs 0.52% on n=1M: difference 0.02 points, "
         "SE_each = 0.00022, pooled SE = 0.00031, z = 0.64. Not a change. At 0.9% "
         "the z is 25 and the alert is unambiguous."),
        ("Sampling and the failure granularity",
         "P(miss a failure affecting fraction f) = (1 - f)^n_sample\nto detect f=0.01 with 95% probability needs n_sample >= 299",
         "The detection probability compounds with sample size. Validating a 1% "
         "sample detects a 50% corruption almost surely and a 0.5% corruption "
         "essentially never, which is why sampling hides exactly the subtle "
         "failures you were hoping to catch.",
         "n=10,000 of 10M (0.1% sample): misses a 1% corruption with probability "
         "0.99^10000 = 4.3e-44, essentially always caught. Misses a 0.01% "
         "corruption with probability 0.99^10000 ~ 0, so 10M rows slip through."),
        ("Rank-based shape comparison",
         "F_ref, F_cur empirical CDFs\nKS = sup_x |F_cur(x) - F_ref(x)|\nnull distribution: KS ~ sqrt(n_eff * alpha * (1 - alpha))",
         "A rank statistic needs no distributional assumption, which is why it works "
         "on skewed business data where a mean-and-variance check is meaningless. "
         "The null distribution gives a threshold rather than a vibe.",
         "With effective n = 10,000 at alpha = 0.5: critical KS at 5% is "
         "1.36/sqrt(10000) = 0.0136. A KS of 0.08 is far beyond chance, indicating "
         "genuine shape change."),
        ("Suite score as a trend",
         "score = 1 - (sum_v w_v * violations_v) / (sum_v w_v * rows)\nblocked if any blocking expectation violates",
         "A weighted score gives a single comparable number across time, while the "
         "blocking rule preserves the property people actually need: the pipeline "
         "must not proceed on broken data. The score informs, the rule decides.",
         "10 expectations, 1M rows, 3 violations in one non-blocking expectation "
         "with weight 0.5: score = 1 - 0.5*3/1e6 = 0.9999985, a flat trend. The "
         "same 3 violations in a blocking expectation stop the pipeline regardless "
         "of score."),
    ],
    math_traps=[
        "Comparing rates without a sampling-noise floor, so normal variation alerts.",
        "Sampling below the granularity of the failures you expect.",
        "Using a flat volume expectation that fires every seasonality peak.",
        "Treating validation score as the gate instead of the blocking rule.",
        "Setting thresholds from round numbers with no reference history.",
    ],
    math_problems=[
        "Compute the sample size needed to detect a 0.5% null-rate regression at 95% power.",
        "Test whether a null rate moved from 0.4% to 0.55% on two samples of 500k.",
        "Compute the critical KS value for two samples of 50k and evaluate a KS of 0.02.",
        "Design a window-aware volume expectation that survives a weekly cycle.",
        "Build a suite of 10 expectations with weights and compute the trend score for two weeks.",
    ],
    tree="""src/
  DataValidationLab.java     driver: runs suites against fixtures, reports results
  DataValidator.java        executes expectations, collects all violations
  Expectation.java          named check with severity, threshold and owner
  SchemaContract.java       columns, types, nullability, primary key
  DistributionCheck.java    rank-based shape comparison against a reference sample
  QualityTrend.java         stores results as a trend and reports slope""",
    tree_note="DataValidator collects every violation before reporting, rather "
              "than throwing on the first one. An operator debugging an overnight "
              "failure needs the whole list, not the first failure.",
    types=[
        ("DataValidator", "runs a suite and returns a full result, never throwing on the first violation"),
        ("Expectation", "name, column, predicate, severity, threshold with provenance, owner"),
        ("SchemaContract", "expected columns, types, nullability, primary key"),
        ("QualityTrend", "stored results with slope reporting per suite"),
    ],
    patterns=[
        ("Suite execution that collects every violation",
         "Operators debug from the whole list at once, and the suite score is "
         "computed from all violations rather than short-circuiting.",
         """public ValidationResult run(ValidationSuite suite, Dataset ds) {
    Map<String, Long> violations = new LinkedHashMap<>();
    List<Violation> details = new ArrayList<>();
    double weighted = 0;
    for (Expectation e : suite.expectations()) {
        long bad = 0;
        for (Row r : ds.rows()) {                 // full scan: sampling hides 0.5% breaks
            if (!e.check().test(r)) {
                bad++;
                if (details.size() < 200) details.add(new Violation(e.name(), r.key()));
            }
        }
        violations.put(e.name(), bad);
        weighted += e.weight() * (double) bad / ds.rows();
        if (bad > e.threshold() && e.severity() == Severity.BLOCKING)
            blocking.add(e.name() + ": " + bad + " > " + e.threshold());
    }
    return new ValidationResult(suite.name(), ds.version(), Instant.now(),
            violations, details, 1 - weighted, blocking);
}"""),
        ("Rate comparison with a sampling-noise floor",
         "A threshold alone turns normal variation into an alert. Comparing against "
         "the reference rate's standard error is what makes it defensible.",
         """public boolean rateRegression(long refViolations, long refRows,
                                long curViolations, long curRows, double z) {
    double pRef = (double) refViolations / refRows;
    double pCur = (double) curViolations / curRows;
    double se = Math.sqrt(pRef * (1 - pRef) / refRows      // SE of the reference rate
                        + pCur * (1 - pCur) / curRows);   // plus SE of the current rate
    if (se == 0) return false;
    double zScore = Math.abs(pCur - pRef) / se;
    return zScore > z;        // only then is the difference more than sampling noise
}"""),
    ],
    costs=[
        ("Full validation scan", "O(rows x expectations)", "push predicates to the engine"),
        ("Schema check", "O(columns)", "metadata only; effectively free"),
        ("Null and duplicate rates", "O(rows)", "one pass, memory O(distinct keys)"),
        ("Shape comparison", "O(n log n)", "sorting both samples once, reused across features"),
    ],
    numerics=[
        "Collect all violations, never throw on the first one.",
        "Compare rates against a sampling-noise floor, not a fixed delta.",
        "Use BigDecimal or scaled doubles for rate comparisons at 1e-4 granularity.",
        "Compute thresholds from observed history and store their provenance.",
        "Make freshness and volume window-aware so seasonality does not alert.",
    ],
    tests=[
        "A suite with a known corrupt fixture reports exactly the expected violation counts.",
        "A rate change within the noise floor does not alert; one beyond it does.",
        "A blocking expectation stops the pipeline; a warning does not.",
        "All violations are reported, not just the first.",
        "A window-aware volume expectation survives a weekly cycle.",
        "Suite score is comparable across runs and changes when violations change.",
    ],
    extensions=[
        "Push predicates into a query engine so validation runs on 100M rows.",
        "Add anomaly detection over the suite score series to catch gradual degradation.",
        "Add a validation summary in the model's metadata so consumers see the data state.",
    ],
    code_checklist=[
        "Every expectation has an owner, a severity and a threshold with provenance",
        "Blocking expectations are rare; warnings are routed, not overridden silently",
        "Schema, freshness and volume validated before transformations",
        "Rate comparisons use a sampling-noise floor",
        "All violations reported together",
        "Results stored as a trend with slope",
    ],
    exercise_selfcheck=[
        "My blocking gate fires rarely enough that people trust it.",
        "My thresholds came from observed history.",
        "I validate freshness and volume, not just ranges.",
        "I can show the quality trend for any suite.",
    ],
    exercises=[
        ("Expectation framework",
         "A reusable, classified check system.",
         ["Define an Expectation type with severity, threshold and owner.",
          "Implement null, range, uniqueness and category checks.",
          "Collect all violations, not just the first.",
          "Write a suite report."],
         "A framework plus a suite report."),
        ("Schema and contract checks",
         "Catch the destructive failures first.",
         ["Declare a schema contract for 3 tables.",
          "Implement type, nullability and primary key expectations.",
          "Simulate an upstream type change.",
          "Confirm the failure blocks before any transformation."],
         "A contract that blocks a simulated upstream break."),
        ("Rate checks with a noise floor",
         "Stop alerting on normal variation.",
         ["Implement rate comparison against a reference.",
          "Generate null-rate series with noise and with a real break.",
          "Tune the z threshold; show false positives and detection.",
          "Report the chosen z."],
         "A comparison showing the noise floor working."),
        ("Shape comparison for skewed data",
         "Range checks pass while the shape changes.",
         ["Implement a rank-based shape comparison.",
          "Build a reference and a skewed current distribution.",
          "Show range checks pass while the comparison fires.",
          "Compute the critical value for your sample sizes."],
         "A demonstration that range checks are insufficient."),
        ("Blocking versus warning",
         "Keep the gate trustworthy.",
         ["Classify 10 expectations by severity.",
          "Show a warning channel that does not block.",
          "Inject a blocking violation and verify the pipeline stops.",
          "Write the routing policy for warnings."],
         "A severity policy with a demonstrated block."),
        ("Freshness and volume",
         "Catch upstream stalls first.",
         ["Implement freshness and volume expectations.",
          "Make volume window-aware for weekly seasonality.",
          "Simulate a stalled upstream.",
          "Verify the alert fires before other checks."],
         "An alert that catches a stalled pipeline."),
        ("Quality trends",
         "See degradation before failure.",
         ["Store suite results with timestamps.",
          "Compute the score trend and its slope.",
          "Alert on sustained slope before a blocking threshold trips.",
          "Show the lead time gained."],
         "A trend alert with a measured lead time."),
        ("Validate at scale",
         "Push checks to the engine.",
         ["Generate 10M rows with injected corruptions.",
          "Compare sampled versus full validation detection rates.",
          "Show sampling misses low-frequency corruption.",
          "Move the checks into a query and measure the speedup."],
         "A detection-rate comparison justifying full validation."),
    ],
    quiz=[
        ("What is a data expectation?", ["A dashboard", "An executable statement about data that can be evaluated and stored", "A test fixture", "A schema file"], 1, "Expectations are the atomic unit that makes validation a trend rather than a spot check."),
        ("Why separate blocking from warning expectations?", ["For clarity", "So blocking failures stay rare and trustworthy", "To reduce cost", "Because warnings are unsupported"], 1, "A gate that fires daily gets ignored, and then hides the real break."),
        ("Which check catches an integer column becoming a string?", ["A range check", "A type or schema contract on the boundary", "A uniqueness check", "A freshness check"], 1, "Schema contracts are cheap and catch the most destructive failures."),
        ("Why validate freshness and volume?", ["To satisfy auditors", "They catch upstream stalls and partial loads before a model sees bad data", "They are easy to compute", "For dashboards"], 1, "Stalled pipelines are the most common real-world data failure."),
        ("What is the risk of sampling for validation?", ["It is slow", "A small sample misses low-frequency corruptions entirely", "It cannot compute rates", "Sampling is not supported"], 1, "A 0.1% sample detects a 50% corruption but essentially never a 0.01% one."),
        ("What does a rank-based shape comparison add over a range check?", ["Speed", "It detects distribution shape change without assuming a form", "It handles nulls", "It samples better"], 1, "Range checks pass while the shape changes, which is where harm usually comes from."),
        ("Why compare rates against a sampling-noise floor?", ["For speed", "Otherwise normal variation produces alerts and the suite gets ignored", "Because rates are unreliable", "To reduce storage"], 1, "A two-proportion significance test is what makes a threshold defensible."),
        ("What is a validation suite for?", ["Documentation", "Grouping expectations under an identity so results are comparable over time", "Performance", "Access control"], 1, "The suite identity is what turns spot checks into a trend."),
        ("What does the blocking rule protect that a score does not?", ["Storage", "The invariant that the pipeline never proceeds on broken data", "Speed", "Schema"], 1, "A weighted score informs; the blocking rule decides."),
        ("Where should validation predicates run?", ["In the JVM after loading", "Pushed down to the query engine", "In the browser", "In the model"], 1, "Pushing down makes full validation affordable on large tables."),
        ("How should you pick a null-rate threshold?", ["A round number", "From observed production history with a review cadence", "From last quarter's value", "Zero"], 1, "Thresholds from history are defensible; round numbers are not."),
        ("What is a window-aware volume expectation?", ["One that ignores volume", "One that compares to the same period in a reference window", "One that samples", "One that alerts daily"], 1, "Flat volume alerts fire on every seasonality peak and get muted."),
        ("Why does an upstream type change need a contract rather than a cast?", ["Performance", "A cast silently produces wrong values instead of failing", "Casts are deprecated", "Types change often"], 1, "Silent wrongness is worse than a failure, because downstream metrics look plausible."),
        ("What should a quality trend dashboard show?", ["A pass or fail", "The score over time with a slope and per-expectation breakdown", "Only alerts", "Row counts"], 1, "A trend shows degradation before a threshold trips."),
        ("Who owns a data quality expectation?", ["Nobody, it is shared", "A named team responsible for the data and the threshold", "The platform team", "The first author"], 1, "Ownership is what turns a gate into something a team will actually fix."),
    ],
    vision=dict(
        future="Data validation converges with drift detection and lineage into a "
               "continuous data quality layer: expectations as code, pushed into "
               "the engine, with trends and ownership. The frontier is anomaly "
               "detection over quality signals rather than hand-written thresholds.",
        good=[
            "Expectations are code, versioned and owned, with thresholds carrying provenance.",
            "Blocking failures are rare enough that the gate is trusted.",
            "Schema, freshness and volume are validated before any transformation.",
            "Quality results are stored as trends with per-expectation breakdown.",
        ],
        ladder=[
            ("L1", "Check", "Schema, nullability, range and uniqueness checks."),
            ("L2", "Classify", "Blocking versus warning, with owners and thresholds."),
            ("L3", "Measure", "Rate comparisons with a noise floor, and quality trends."),
            ("L4", "Scale", "Pushdown validation on huge tables, anomaly detection over quality signals."),
        ],
        behaviors="Validate the data that matters, early, and fail loudly on the "
                  "small number of things that genuinely break models. Keep the "
                  "gate rare enough to be trusted.",
        anti=[
            "Thirty blocking expectations that fire every morning.",
            "Sampling that hides a 0.5% corruption.",
            "No freshness check on a pipeline that once silently went stale for a week.",
            "A quality dashboard showing only pass or fail.",
        ],
        trends=[
            "Expectations as versioned code with change review and impact analysis.",
            "Anomaly detection over data quality signals replacing static thresholds.",
            "Data contracts enforced at the producer boundary rather than the consumer.",
            "Quality metadata attached to model versions so consumers see the data state.",
        ],
        d30="Build an expectation framework with severity, thresholds and owners.",
        d60="Add rate comparisons with a sampling-noise floor and quality trends.",
        d90="Push validation to the engine on a large table and justify full validation with detection rates.",
        metrics=[
            "My blocking gate fires rarely enough to be trusted.",
            "Every threshold has provenance.",
            "I validate freshness and volume, not just ranges.",
            "I can show the quality trend for any suite.",
        ],
        closer="A validation suite is the cheapest insurance in MLOps: it converts "
               "an overnight incident into a failed expectation in seconds.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Data Quality Suite with a Trustworthy Gate",
        brief="Build a validation suite with schema, domain, distribution and "
              "freshness checks, and make the blocking gate reliable.",
        timebox="3 hours",
        why="Every silent model failure in practice begins as a data failure that "
            "nobody validated. This suite is the antidote.",
        requirements=[
            "Expectation framework with severity, threshold, owner and threshold provenance.",
            "Schema contract for 3 tables: columns, types, nullability, primary key.",
            "Domain expectations: ranges, categories, uniqueness, duplicate rate.",
            "Distribution check that fires when a range check passes (skewed data).",
            "Rate comparisons against a reference with a sampling-noise floor.",
            "Freshness and window-aware volume checks that catch a stalled upstream.",
            "Quality trends with a slope alert that beats the blocking threshold.",
        ],
        steps=[
            ("1", "30m", "Expectation framework collecting all violations", "A suite report with every failure"),
            ("2", "30m", "Schema contract; simulate an upstream type change", "A contract that blocks the break"),
            ("3", "25m", "Domain expectations with owners and severities", "A classified expectation set"),
            ("4", "30m", "Distribution check on skewed data", "A case where ranges pass and shape fails"),
            ("5", "30m", "Rate comparison with a noise floor", "A tuned z with demonstrated behaviour"),
            ("6", "30m", "Freshness plus window-aware volume; simulate a stall", "An early alert on a stalled pipeline"),
            ("7", "25m", "Quality trends with slope alerting; measure lead time", "A trend alert with lead time"),
        ],
        diagram=""" dataset version
      |
 [1] schema contract (columns, types, nullability, PK)  -> BLOCKING
 [2] domain (range, category, uniqueness, duplicates)     -> mixed
 [3] distribution (rank shape vs reference)              -> warning
 [4] rates vs reference with noise floor                 -> warning
 [5] freshness + window-aware volume                     -> BLOCKING
      |
 ValidationResult (all violations, weighted score, blocking list)
      |
 quality trend store -> slope alert (before the blocking threshold)
      |
 pipeline gate: block if any BLOCKING expectation violates""",
        notes=[
            "Collect every violation; an operator debugging at 3 a.m. needs the list, not the first failure.",
            "Generate your own noise so you can see false positives before you tune anything.",
            "Inject a 0.5% corruption and test whether sampling catches it; it will not.",
            "The freshness and volume checks should fire before anything else when an upstream stalls.",
        ],
        deliverables=[
            "Expectation framework plus a suite report listing all violations.",
            "Schema contract that blocks a simulated upstream type change.",
            "Distribution check demonstration on skewed data.",
            "Quality trend with slope alerting and a measured lead time.",
        ],
        grading=[
            ("Correctness", "25%", "All violations reported; schema blocks; severities applied"),
            ("Statistical soundness", "25%", "Rate comparison uses a noise floor; distribution check detects shape change"),
            ("Coverage", "20%", "Schema, domain, distribution, freshness and volume all present"),
            ("Trustworthiness", "20%", "Blocking gate fires rarely; thresholds from history"),
            ("Operations", "10%", "Trends stored with slope and a lead-time measurement"),
        ],
        stretch=[
            "Push predicates into a query engine and validate 10M rows.",
            "Add anomaly detection over the suite score series.",
            "Attach validation metadata to a model version so consumers see the data state.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Data Contracts Across a Shared Lakehouse",
        scenario="A data platform serves 60 models from one lakehouse with 40 "
                 "upstream producers and no contracts. A producer changed a column "
                 "from cents to dollars; four models trained on prices 100x too low "
                 "for six weeks before anyone noticed the scores looked odd.",
        scale=[
            ("Producers", "40 upstream tables owned by 11 teams"),
            ("Consumers", "60 models plus analysts reading the same tables"),
            ("Current state", "no contracts; failures detected by model degradation"),
            ("Worst recent incident", "unit change went undetected for 6 weeks"),
            ("Goal", "breakages fail at the producer boundary within minutes"),
        ],
        diagram=""" producers (40 tables / 11 teams)
      |
  contract registry (schema, ranges, semantics, freshness, owners)
      |
  validation executed at the producer boundary (pushdown)
      |
  +---------+ (pass) ------------+---------- (fail) ------------+
  |                              |                             |
 offline (validated snapshot)  feature materialisation   producer blocked, consumer paged
  |                              |
 training (point-in-time)    online serving
  |
 validation results attached to snapshot + model version
  |
 quality trends per table, per consumer""",
        components=[
            ("Contract registry",
             ["Per-table contracts: schema, types, nullability, primary keys, ranges, categories, freshness",
              "Semantic definitions stored with the table so units are unambiguous",
              "Named owner team per table, and a change process with a notice period",
              "Consumer inventory per table so a breaking change can be scoped before it lands"]),
            ("Enforcement at the boundary",
             ["Contracts validated in the producer's pipeline before the table is published",
              "Pushdown execution so full validation is affordable on wide tables",
              "Blocking failures stop publication and page the producer, not the consumers",
              "Warning-level expectations recorded as trends for the producer team"]),
            ("Consumer protection",
             ["Consumers validate again at their boundary as defence in depth",
              "Validation metadata attached to each snapshot and to model versions",
              "Feature store (Lab 04) materialises only from validated snapshots",
              "Unit and range metadata exposed so a consumer can assert on units"]),
            ("Quality operations",
             ["Per-table quality trends with slope alerts and owners",
              "Contract coverage report showing which tables lack contracts",
              "Breaking change review requiring consumer sign-off for high-blast-radius tables",
              "Post-incident review adding a contract for every missed failure mode"]),
        ],
        timeline=[
            ("Week 1-2", "Inventory 40 tables; identify the 20 with the highest consumer count"),
            ("Week 3-4", "Write contracts for those 20 with producer sign-off; enforce at the boundary"),
            ("Week 5", "Pushdown validation engine with full-table execution and measured cost"),
            ("Week 6-7", "Extend contracts to the remaining 20 tables; attach validation metadata to snapshots"),
            ("Week 9", "Consumer sign-off workflow for breaking changes; first drill of a unit-change scenario"),
        ],
        runbook=[
            "# Contract status per table",
            "curl -s localhost:8080/contracts | jq '.[] | {table,owner,contractVersion,coverage}'",
            "",
            "# Validation result for the latest published snapshot",
            "curl -s 'localhost:8080/validation?table=orders&latest=1' | jq '.blocking,.warnings,.score'",
            "",
            "# Quality trend for a table with slope",
            "curl -s 'localhost:8080/quality/trend?table=orders&window=30d' | jq '.score,.slope'",
            "",
            "# Blast radius of a proposed breaking change",
            "curl -s 'localhost:8080/contracts/blast-radius?table=orders&change=price_units' | jq '.consumers'",
            "",
            "# Publish an exception for a known-bad row (time-boxed, logged)",
            "curl -XPOST localhost:8080/validation/exception -d '{\"table\":\"orders\",\"reason\":\"backfill\",\"expiresIn\":\"2h\"}'",
        ],
        metrics=[
            "Coverage: percentage of tables with enforced contracts (target 100% for the top 20 first).",
            "Detection: time from a producer change to a blocking failure (target under 15 minutes).",
            "Blast radius: consumers identified before a breaking change lands (target 100%).",
            "Exceptions: number of time-boxed overrides, all expiring and reviewed.",
            "Outcome: production incidents caused by data breakage, trending to zero.",
        ],
        failures=[
            ("A producer pushes a unit change outside the contract", "Table was not covered", "Blocking failure at publication; page the producer; scope consumers from the inventory"),
            ("An exception becomes permanent", "No expiry on overrides", "Overrides carry a mandatory expiry; expired exceptions block publication and are reviewed monthly"),
            ("Validation cost becomes the bottleneck", "Row-by-row checks in the JVM", "Push predicates into the query engine; measure and optimise the slowest checks"),
            ("Contracts drift from reality as tables evolve", "No change process", "Breaking change review with consumer sign-off and a notice period"),
            ("Consumers still read unvalidated tables directly", "No enforcement on the consumer side", "Deprecate direct access; route consumers through validated snapshots"),
        ],
        backlog=[
            "Semantic layer so units and definitions are queryable rather than documented.",
            "Contract coverage automation discovering new tables and alerting on gaps.",
            "Cross-table referential integrity checks with an owner per relationship.",
            "Consumer-side validation as defence in depth with drift-aware thresholds.",
            "Quarterly drill of a unit-change scenario with measured detection time.",
        ],
        urls=URLS,
        closer="The deliverable is 40 producers whose breakages fail at their own "
               "boundary in minutes, with the blast radius known before a change "
               "lands and no unit change reaching a model for six weeks.",
    ),
))

# ---------------------------------------------------------------- lab10
SPECS.append(dict(
    track="mlops", lab="lab10", full_set=True, level="Advanced",
    title="A/B Testing & Experimentation", main_class="ABTestingLab",
    problem="Two models, one decision. Ship the new one because its offline metric "
            "is better, or keep the old one because it is safer? The only honest "
            "way out is a well-designed experiment on live traffic.",
    why_now="Offline metrics predict offline. Every serious ML organisation needs "
             "a live experimentation capability, including the sequential-testing "
             "discipline that stops you from peeking.",
    objectives=[
        "Design a randomised experiment with power, MDE and a fixed horizon",
        "Compute significance for proportions, means and ratios correctly",
        "Understand why peeking inflates false positives and what to do about it",
        "Interpret practical significance alongside statistical significance",
        "Run a shadow test when you cannot risk user-facing exposure",
        "Design a sequential test or a fixed-horizon plan with alpha control",
    ],
    concepts=[
        ("Randomisation is the whole design",
         "Everything else is bookkeeping. Assignment must be random and consistent, "
         "otherwise treatment and control differ in ways no amount of statistics "
         "repairs. Hash-based assignment on user id gives stability without state."),
        ("Power, MDE and horizon",
         "Power is the probability of detecting a real effect. MDE is the smallest "
         "effect worth detecting at your sample size. These are three quantities "
         "traded against each other, and deciding them before the experiment is what "
         "prevents an underpowered test being declared 'no significant difference'."),
        ("Peeking is a real problem",
         "Checking significance daily and stopping when it crosses 0.05 inflates "
         "the false positive rate far above 5%. Either fix the horizon in advance, "
         "or use a sequential test (group sequential, always-valid) that controls "
         "the error rate while allowing early stopping."),
        ("Guardrail metrics protect the downside",
         "A model can improve conversion and increase complaints, refunds or "
         "latency. Guardrails are non-inferiority bounds checked continuously; if a "
         "guardrail is breached, you stop regardless of how good the primary metric "
         "looks."),
        ("Shadow tests when exposure is unacceptable",
         "A shadow test scores the challenger on live traffic without affecting "
         "decisions. It cannot measure business outcomes directly, but it measures "
         "score distribution, latency and disagreement, which catches most "
         "catastrophic problems before exposure."),
        ("Practical versus statistical significance",
         "A 0.2% lift detected at p = 0.001 may be worth less than its rollout cost. "
         "Report the effect size with an interval, translate it to business units, "
         "and make the decision on value rather than on a p-value."),
    ],
    formulas=[
        ("n = 2 (z_{1-a/2} + z_{1-b})^2 sigma^2 / delta^2", "Sample size for means", "the MDE-driven horizon"),
        ("z = (p1 - p2) / sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)", "Two-proportion z", "standard A/B test"),
        ("power = P(reject | true effect)", "Power", "1 - beta, fixed before launch"),
        ("delta_MDE = (z_{1-a/2} + z_{1-b}) sigma sqrt(2/n)", "MDE", "the effect you can actually see"),
        ("false positive with peeking ~ alpha x looks", "Peeking inflation", "why fixed horizons or sequential tests"),
        ("guardrail breach: lower bound < -delta_guard", "Non-inferiority", "stop regardless of primary metric"),
    ],
    flow=[
        "State the primary metric, the minimum detectable effect, alpha, power and the horizon before launching.",
        "Define guardrail metrics with non-inferiority bounds and a stop rule.",
        "Assign traffic by a stable hash on user id, with an exposure fraction you can ramp.",
        "Pre-register the analysis: the test statistic, the horizon and the stopping rule.",
        "Monitor guardrails continuously; check the primary metric only at planned look points.",
        "Decide on effect size with an interval, in business units, not on the p-value alone.",
    ],
    assumptions=[
        "Assignment is random, stable per unit, and independent of the outcome",
        "Only one primary metric drives the decision; guardrails are separate",
        "Alpha, power, MDE and the horizon were fixed before data collection",
        "Sample ratio mismatch is checked, since it invalidates everything downstream",
        "Guardrail thresholds have non-inferiority bounds agreed in advance",
        "Decisions translate the effect into business units",
    ],
    pitfalls=[
        ("Test declared a winner after 3 days of daily peeking", "repeated uncorrected looks", "fixed horizon or a sequential test with alpha control"),
        ("Sample ratio mismatch not checked", "assignment bug or bot traffic", "assert SRM on every check before looking at metrics"),
        ("No difference found and the test shipped anyway", "underpowered design", "compute power and MDE before launch, not after"),
        ("Conversion up 40%, complaints up 300%", "no guardrails", "non-inferiority guardrails with a stop rule"),
        ("Result depends on excluding outliers after the fact", "post-hoc filtering", "pre-register inclusion and exclusion rules"),
        ("Winning arm introduced novelty effects", "short horizon on a new experience", "extend the horizon or exclude novelty-sensitive segments"),
        ("Users in both arms", "non-sticky assignment", "hash on user id, not session"),
    ],
    java=[
        ("SplittableRandom / stable hash on user id", "assignment without state and stable across sessions"),
        ("AtomicLongArray per arm per metric", "concurrent metric counters with SRM checks"),
        ("NormalDistribution quantile function", "z-values for power and MDE"),
        ("record Experiment(String id, String primaryMetric, int alpha, double power, Instant horizonEnd)", "the pre-registered plan"),
        ("Interleaved guardrail evaluation", "non-inferiority checks that can stop early"),
    ],
    links=[
        "**labs/ml/lab10** supplies the evaluation protocol used offline before any live test.",
        "**mlops/lab03** is where a winning challenger is promoted.",
        "**mlops/lab08** supplies the drift and quality monitoring that runs alongside a test.",
        "**mlops/lab07** gates on offline evaluation so live tests start from a sound baseline.",
    ],
    checklist=[
        "I fixed alpha, power, MDE and the horizon before launching.",
        "Assignment is random and sticky per unit.",
        "I check sample ratio mismatch before reading any metric.",
        "Guardrails have non-inferiority bounds and a stop rule.",
        "I avoid uncorrected peeking.",
        "The decision uses effect size in business units, not just a p-value.",
    ],
    cards=[
        ("What makes an A/B test valid?", "Random, stable assignment of units to arms; everything else is analysis."),
        ("What is power?", "The probability of detecting a real effect of a given size, given the sample size."),
        ("What is MDE?", "The smallest effect the test can detect at your sample size; it decides how long you must run."),
        ("Why is peeking a problem?", "Each look inflates the false positive rate, so crossing 0.05 early is often just noise."),
        ("What are guardrail metrics?", "Non-inferiority bounds on metrics that must not degrade, checked continuously with a stop rule."),
        ("What is sample ratio mismatch?", "The arms receiving traffic in different proportions than designed, which invalidates the analysis."),
        ("When do you use a shadow test?", "When user-facing exposure is unacceptable; it measures score distribution and latency but not business outcomes."),
        ("Statistical versus practical significance?", "Statistical says the effect is unlikely to be noise; practical says it is worth the rollout cost."),
    ],
    extra_cards=[
        ("How do you control error rate with early stopping?", "Use a sequential design such as group sequential boundaries or always-valid confidence sequences."),
        ("What does novelty effect look like?", "An early spike in the treatment arm that decays as users adapt; a short horizon will call it a win."),
        ("Why hash on user id rather than session?", "So a user stays in one arm; otherwise cross-arm contamination dilutes and confuses the result."),
        ("How do you choose the horizon?", "From the sample size your MDE and power require; there is no other honest way."),
    ],
    math_why="Experimentation is power analysis plus error-rate control: how "
             "large a sample you need, what peeking does to your alpha, and how "
             "guardrails bound the downside.",
    math=[
        ("Sample size and MDE",
         "n_per_arm = 2 (z_{1-alpha/2} + z_{1-beta})^2 sigma^2 / delta^2\nfor proportions: n = (z_{a/2} sqrt(2 p_bar (1-p_bar)) + z_b sqrt(p1(1-p1)+p2(1-p2)))^2 / (p1-p2)^2",
         "Sample size is the arithmetic consequence of the effect you want to detect, "
         "the error rates you accept and the variance of the metric. Fixing it "
         "before launch is what makes 'no significant difference' interpretable.",
         "Baseline conversion 4%, want to detect a 0.2% relative lift (4.008% to "
         "4.016%), alpha 0.05, power 0.8: n is roughly 190k per arm, about 8 days at "
         "1M sessions/day. An MDE of 0.5% would need 12k per arm, under a day."),
        ("Two-proportion significance",
         "p_hat_pool = (x1 + x2) / (n1 + n2)\nSE = sqrt(p_pool (1 - p_pool) (1/n1 + 1/n2))\nz = (p1 - p2) / SE,  two-sided p = 2 (1 - Phi(|z|))",
         "The pooled standard error is correct under the null that the rates are "
         "equal, which is what the test assumes. Using unpooled standard errors is a "
         "conservative variant that is valid but slightly less powerful.",
         "p1 = 0.0402 with n1 = 200k, p2 = 0.0400 with n2 = 200k: p_pool = 0.0401, "
         "SE = 0.000632, z = 0.317, p-value 0.75. Nowhere near significance; the "
         "MDE at this n is about 0.18 percentage points."),
        ("Peeking inflates the false positive rate",
         "per-look alpha under independence ~ 1 - (1 - alpha)^k\nfor alpha = 0.05 and k = 10 looks: ~40% false positive\nfixed horizons or sequential boundaries correct this",
         "Repeated uncorrected looks behave like multiple hypothesis testing. The "
         "inflation is severe: ten daily looks turn a 5% error rate into roughly "
         "40%. Sequential designs fix it while still permitting early stopping for "
         "harm.",
         "A test run for 14 days with daily significance checks has an effective "
         "false positive rate near 50% if run until 'significant'. That is how teams "
         "ship noise."),
        ("Guardrail non-inferiority",
         "for each guardrail: lower bound of the effect CI > -delta_guard\nbreach if lower bound <= -delta_guard",
         "A guardrail is a one-sided test that the treatment is not worse than the "
         "control by more than an agreed margin. Because it is one-sided and "
         "pre-specified, it can stop an experiment for harm without stopping it for "
         "benefit.",
         "Latency guardrail: control p99 180 ms, treatment 196 ms, delta_guard 10%. "
         "Effect +16 ms is +8.9%, and with a tight interval the lower bound stays "
         "above +10 ms, so it passes. At +25 ms the bound crosses and the test stops."),
        ("Sequential testing with alpha control",
         "group sequential: O'Brien-Fleming or Pocock boundaries per look\nalpha spending function alpha(t) with total <= alpha\nalways-valid: confidence sequence valid at every t",
         "Alpha-spending approaches pre-plan a boundary schedule that spends a fixed "
         "total error rate across looks. Always-valid confidence sequences are the "
         "modern alternative: valid at every time point with no pre-planned looks.",
         "O'Brien-Fleming spends very little alpha early and most at the end, so an "
         "early stop requires an enormous effect. Pocock spends evenly, so early "
         "stops are easier but the final test is weaker."),
    ],
    math_traps=[
        "Computing sample size after seeing the effect you want to detect.",
        "Using unpooled standard errors without realising it costs power.",
        "Running daily significance checks and stopping at first crossing.",
        "Comparing arms without checking the sample ratio first.",
        "Deciding on a p-value without translating the effect into business units.",
    ],
    math_problems=[
        "Compute required n per arm for a 4% baseline detecting a 10% relative lift at alpha 0.05, power 0.8.",
        "Run a two-proportion test on counts 802/200000 versus 800/200000 and interpret.",
        "Compute the false positive rate over 10 daily looks at alpha 0.05 and explain the fix.",
        "Design a latency guardrail with a non-inferiority bound and decide pass or fail for a given effect and interval.",
        "Compare O'Brien-Fleming and Pocock boundaries qualitatively for early stopping behaviour.",
    ],
    tree="""src/
  ABTestingLab.java         driver: simulate an experiment, report with intervals
  Experiment.java           pre-registered plan: primary metric, alpha, power, horizon
  Assignment.java           stable hash-based assignment on user id
  ABTest.java               two-arm metrics, SRM check, significance, effect intervals
  PowerCalculator.java      sample size and MDE from alpha, power and variance
  SequentialPolicy.java     alpha-spending boundaries and guardrail non-inferiority""",
    tree_note="Assignment is a pure function of user id. That makes the "
              "experiment reproducible, stateless and immune to the "
              "assignment-service outage that has invalidated real tests.",
    types=[
        ("Experiment", "the pre-registered plan including alpha, power, MDE and horizon"),
        ("Assignment", "stable hash-based bucketing with an exposure fraction"),
        ("ABTest", "metric aggregation, SRM check, significance and effect intervals"),
        ("SequentialPolicy", "alpha-spending boundaries plus guardrail non-inferiority checks"),
    ],
    patterns=[
        ("Stateless stable assignment",
         "Hashing the user id means no assignment state to lose, and the same user "
         "always lands in the same arm.",
         """public int arm(String userId, int buckets, double exposureFraction) {
    // pure function of the user id: no state to lose, no session contamination
    long h = stableHash(userId);                 // deterministic across processes
    int bucket = (int) Math.floorMod(h, buckets);
    return bucket < (int) (buckets * exposureFraction) ? 1 : 0;
    // exposureFraction lets you ramp 1% -> 10% -> 50% without changing assignment
}"""),
        ("SRM check before reading any metric",
         "An unequal split invalidates everything downstream, so it is checked "
         "first, every time, and fails loudly.",
         """public void assertSrm(long controlCount, long treatmentCount, int buckets, double alpha) {
    // chi-square goodness of fit against the designed 50/50 split
    double expected = (controlCount + treatmentCount) / 2.0;
    double chi2 = Math.pow(controlCount - expected, 2) / expected
                + Math.pow(treatmentCount - expected, 2) / expected;
    double critical = chiSquareCriticalValue(alpha, 1);        // 3.84 at alpha = 0.05
    if (chi2 > critical)
        throw new SrmDetected(chi2);   // a mismatch invalidates every downstream metric
}"""),
    ],
    costs=[
        ("Assignment per request", "O(1) hash", "stateless; no coordination cost"),
        ("Metric aggregation", "O(1) per event", "counters keyed by arm and metric"),
        ("SRM check", "O(1)", "chi-square against the designed split"),
        ("Sequential boundary computation", "O(1) per look", "precomputed spending function"),
    ],
    numerics=[
        "Check sample ratio mismatch before reading any metric, every time.",
        "Use the pooled standard error for the two-proportion test.",
        "Precompute sequential boundaries rather than recomputing alpha at each look.",
        "Report effect size with an interval, then translate it into business units.",
        "Use stable hashing rather than a random assignment service.",
    ],
    tests=[
        "Assignment is deterministic per user id and stable across processes.",
        "The split matches the exposure fraction within binomial noise.",
        "An SRM injection raises rather than silently continuing.",
        "A known-effect dataset produces the expected significance and effect size.",
        "Sequential boundaries spend no more than the total alpha across all looks.",
        "A guardrail breach stops the test even when the primary metric is positive.",
    ],
    extensions=[
        "Add multi-arm bandits with allocation by expected regret reduction.",
        "Add ratio metrics (revenue per user) with the correct delta-method variance.",
        "Add cluster randomisation for experiments where interference is likely.",
    ],
    code_checklist=[
        "Plan pre-registered before data collection",
        "Assignment is a stable hash, not stored state",
        "SRM checked before every metric read",
        "One primary metric; guardrails separate with agreed bounds",
        "No uncorrected peeking: fixed horizon or sequential boundaries",
        "Decision documented with effect size in business units",
    ],
    exercise_selfcheck=[
        "My alpha, power, MDE and horizon were fixed before launch.",
        "I check SRM before reading metrics.",
        "My test cannot be fooled by peeking.",
        "I have a guardrail with a stop rule.",
    ],
    exercises=[
        ("Power and sample size",
         "Design before you launch.",
         ["Implement the sample size formula for means and proportions.",
          "Compute n for your baseline and target lift.",
          "Derive the MDE at that n.",
          "Convert n into a horizon at your daily traffic."],
         "A pre-registered plan with n, MDE and a horizon date."),
        ("Two-arm analysis",
         "The statistics, done correctly.",
         ["Implement two-proportion and two-mean tests with pooled SE.",
          "Cross-check against a hand calculation.",
          "Compute the effect size with a confidence interval.",
          "Verify on a known-effect synthetic dataset."],
         "An analysis module with verified statistics."),
        ("SRM detection",
         "Catch the bug that invalidates everything.",
         ["Implement the chi-square SRM check.",
          "Inject an assignment bug and confirm detection.",
          "Show that without the check you would read a meaningless result.",
          "Add SRM to the monitoring path."],
         "A test proving an assignment bug is caught."),
        ("Peeking and sequential tests",
         "Stop lying to yourself.",
         ["Simulate 20 tests with a true null effect and daily looks.",
          "Measure the false positive rate with and without correction.",
          "Implement an alpha-spending policy and re-measure.",
          "Show power loss versus early-stopping benefit."],
         "A measurement of the inflation and the fix."),
        ("Guardrails",
         "Protect the downside.",
         ["Define 3 guardrails with non-inferiority bounds.",
          "Simulate a treatment that wins on primary and breaches a guardrail.",
          "Verify the test stops.",
          "Write the stop and communicate procedure."],
         "A guardrail implementation with a demonstrated stop."),
        ("Shadow test",
         "Learn something without exposure.",
         ["Score a challenger on 100% of live traffic.",
          "Measure score distribution, latency and disagreement.",
          "Show what a shadow test can and cannot tell you.",
          "Define the exposure criteria it feeds."],
         "A shadow analysis with explicit limits."),
        ("Practical significance",
         "Translate the effect into value.",
         ["Compute the effect with an interval.",
          "Convert to business units (revenue, complaints, support load).",
          "Compare against rollout cost.",
          "Write a recommendation that is not just 'significant'."],
         "A decision memo in business units."),
        ("Full experiment simulator",
         "Run the whole thing end to end.",
         ["Simulate traffic, assignment, metrics and label delay.",
          "Include novelty effects and weekly seasonality.",
          "Compare fixed-horizon and sequential policies across scenarios.",
          "Report false positive rate and average time to decision."],
         "A simulator with a policy comparison."),
    ],
    quiz=[
        ("What is the single most important requirement for a valid A/B test?", ["A large sample", "Random, stable assignment of units to arms", "A long duration", "Many metrics"], 1, "Everything else is analysis; broken assignment cannot be repaired statistically."),
        ("What does power mean?", ["Sample size", "The probability of detecting a real effect of a given size", "Confidence level", "Variance"], 1, "Power is 1 - beta and must be fixed before launch."),
        ("Why must sample size be computed before the test?", ["For billing reasons", "It follows from the MDE, alpha and power you chose", "Because the API requires it", "To reduce storage"], 1, "Computing it afterwards makes an underpowered result uninterpretable."),
        ("What is sample ratio mismatch?", ["A metric bug", "The arms receiving traffic in different proportions than designed", "Label delay", "Seasonality"], 1, "SRM invalidates everything downstream, so it is checked before any metric."),
        ("Why does peeking inflate false positives?", ["It reduces power", "Each additional look adds another chance to cross the threshold by chance", "It increases variance", "Labels arrive late"], 1, "Ten daily looks at alpha 0.05 behave like a much larger error rate."),
        ("How do you allow early stopping correctly?", ["Increase alpha", "Use a sequential design with alpha control, such as alpha spending", "Stop at first significance", "Use a larger sample"], 1, "Alpha spending or always-valid confidence sequences keep the error rate at the planned level."),
        ("What is a guardrail metric for?", ["Secondary reporting", "Bounding harm: non-inferiority checks that can stop the test", "Increasing power", "Sampling more"], 1, "Guardrails let you stop for harm even while the primary metric looks good."),
        ("What is the difference between statistical and practical significance?", ["They are the same", "Statistical means unlikely to be noise; practical means worth the rollout cost", "Practical uses bigger samples", "Statistical needs more time"], 1, "A tiny reliable effect can still be a bad investment."),
        ("What can a shadow test not measure?", ["Latency", "Business outcomes from user-facing exposure", "Score distribution", "Disagreement with the champion"], 1, "Shadow scoring never changes decisions, so it cannot attribute a business effect."),
        ("Why hash on user id rather than session?", ["Performance", "So a user stays in one arm and does not contaminate both", "Easier debugging", "To reduce storage"], 1, "Cross-arm users dilute the effect and confuse the analysis."),
        ("What is a novelty effect?", ["A bug", "An early spike in the treatment that decays as users adapt", "Sampling bias", "Label noise"], 1, "A short horizon will call a decaying spike a win."),
        ("How do you handle a result that depends on excluding outliers?", ["Exclude them", "Pre-register the exclusion rule; post-hoc filtering invalidates the result", "Report both and pick the better", "Increase the sample"], 1, "Post-hoc filtering lets you find any conclusion you want."),
        ("What should the horizon be?", ["Two weeks by convention", "The time your sample size requires, computed from MDE and power", "Until significant", "One full business quarter"], 1, "A fixed horizon is also what keeps the error rate honest."),
        ("What is the risk of running many arms at once?", ["Cost", "Multiple comparisons inflate the false positive rate across arms", "Label delay", "Storage"], 1, "With 5 arms and 20 looks, uncorrected error rates become very large."),
        ("What should the decision document contain?", ["A p-value", "The effect with an interval, translated into business units, plus guardrail status", "Arm names", "Traffic numbers"], 1, "A decision needs the magnitude, the uncertainty and the value, not just significance."),
    ],
    vision=dict(
        future="Experimentation converges on always-valid inference, "
               "interference-aware designs, and bandit-style allocation for high "
               "volume. The frontier is not more metrics; it is designs that remain "
               "honest when teams look at the data constantly, which they always do.",
        good=[
            "Plans are pre-registered with alpha, power, MDE, horizon and stopping rule.",
            "Assignment is a stable hash and SRM is checked before every read.",
            "Guardrails have non-inferiority bounds agreed in advance.",
            "Decisions quote effect size with an interval in business units.",
        ],
        ladder=[
            ("L1", "Test", "Two arms, fixed horizon, a primary metric."),
            ("L2", "Design well", "Power and MDE computed before launch; SRM checked."),
            ("L3", "Control error", "Sequential or always-valid inference with guardrails."),
            ("L4", "Scale", "Interference-aware designs, multi-arm bandits, shared experimentation."),
        ],
        behaviors="Decide the plan before seeing data. Check SRM before metrics. "
                  "Treat any uncorrected peek as a design flaw. Translate effects "
                  "into money and support load before calling a winner.",
        anti=[
            "Daily significance checks with a stop at first crossing.",
            "Calling 'no significant difference' without having computed power first.",
            "Shipping a treatment because conversion rose 40% and complaints rose 300%.",
            "Filtering outliers after the result looks wrong.",
        ],
        trends=[
            "Always-valid confidence sequences removing the need to pre-plan looks.",
            "Interference-aware and cluster randomisation for marketplace settings.",
            "Bandit allocation replacing fixed A/B for high-volume, low-cost decisions.",
            "Shared experimentation platforms standardising metrics and SRM checks across teams.",
        ],
        d30="Compute power, MDE and horizon for a planned experiment and pre-register it.",
        d60="Implement two-arm analysis with SRM checks and effect intervals.",
        d90="Add sequential inference and guardrails, and demonstrate both on a simulator.",
        metrics=[
            "My plan was fixed before data collection.",
            "I check SRM before reading any metric.",
            "My test cannot be fooled by peeking.",
            "My decision quotes an effect in business units.",
        ],
        closer="An experiment you can stop early is worth more than one that is "
               "statistically pure and never finishes.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Model A/B Test with Sequential Inference",
        brief="Design and run a live-style A/B test with power, SRM checks, "
              "sequential inference and guardrails.",
        timebox="3\u20134 hours",
        why="Every model promotion eventually becomes a live experiment. Doing "
            "this once properly is worth more than any additional offline metric.",
        requirements=[
            "Pre-registered plan: primary metric, MDE, alpha, power, horizon and stopping rule.",
            "Stateless stable assignment on user id with an exposure ramp.",
            "SRM check before every metric read, with an injected assignment bug proving it works.",
            "Two-proportion analysis with pooled SE and effect intervals.",
            "Sequential inference with alpha control; demonstrate the false positive inflation and the fix.",
            "At least 3 guardrails with non-inferiority bounds and a demonstrated stop.",
            "Decision memo with the effect in business units.",
        ],
        steps=[
            ("1", "30m", "Power, MDE and horizon; write the pre-registered plan", "A plan document with numbers"),
            ("2", "25m", "Stateless hash assignment with exposure ramp", "A deterministic assignment function"),
            ("3", "25m", "SRM check plus an injected assignment bug", "A test proving detection"),
            ("4", "30m", "Two-proportion analysis with effect intervals", "Verified statistics"),
            ("5", "40m", "Simulator; measure peeking inflation and sequential correction", "A false positive comparison"),
            ("6", "30m", "Guardrails; simulate primary win with guardrail breach", "A demonstrated stop"),
            ("7", "30m", "Decision memo in business units", "A memo, not a p-value"),
        ],
        diagram=""" traffic -> arm(userId) via stable hash (exposure ramp)
      |
  +---+---+
  |       |
control  treatment            (SRM check FIRST)
  |       |
  +---+---+
      |
  primary metric + 3 guardrails
      |
  sequential boundaries (alpha spending) + non-inferiority guardrails
      |
  decision: effect + interval -> business units -> recommendation""",
        notes=[
            "Write the plan before writing the simulator; otherwise you will rationalise whatever you get.",
            "Inject an assignment bug deliberately; SRM checks that have never fired are untested.",
            "Measure the peeking inflation on a null-effect simulation so the number is memorable.",
            "The decision memo must be writable without reference to p-values.",
        ],
        deliverables=[
            "Pre-registered plan with sample size, MDE and horizon.",
            "Analysis module with SRM check and effect intervals, verified.",
            "Peeking versus sequential false positive comparison.",
            "Guardrail demonstration and a decision memo in business units.",
        ],
        grading=[
            ("Design", "30%", "Pre-registered plan with real power and MDE arithmetic"),
            ("Correctness", "20%", "Assignment stable, SRM detected when injected, pooled SE used"),
            ("Inference", "25%", "Sequential alpha control demonstrated with a measurement"),
            ("Protection", "15%", "Guardrails with a demonstrated stop"),
            ("Decision", "10%", "Memo in business units"),
        ],
        stretch=[
            "Add ratio metrics with delta-method variance.",
            "Add interference-aware cluster randomisation for a marketplace simulation.",
            "Add a bandit allocation policy and compare decisions made to decision quality.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Model Rollout Experimentation Platform",
        scenario="A marketplace rolls out a new ranking model roughly monthly "
                 "across 12 teams. Decisions are made from offline metrics and "
                 "Slack discussion, and last quarter two rollouts had to be "
                 "reverted after customer complaints the offline metrics never saw.",
        scale=[
            ("Sessions", "~120M/month, peak 5k QPS"),
            ("Rollouts", "~12 model rollouts per month, each 5-30% of traffic"),
            ("Primary metric", "GMV per session, with a 30-day order attribution window"),
            ("Current practice", "Offline metric comparison plus Slack approval"),
            ("Historical problem", "2 reverts in the last quarter; 1 rollout shipped with no guardrails"),
        ],
        diagram=""" experiments service
   |
 registration: primary metric, MDE, alpha, power, horizon, guardrails
   |
 assignment (stable hash on user + session, exposure ramp 1->5->25->50%)
   |
 measurement pipeline: exposure events + outcomes (30-day attribution)
   |
 +-+------------------+------------------+
 |                  |                  |
 SRM check      primary metric     guardrails (non-inferiority)
 |                  |                  |
 +------------------+------------------+
   |
 sequential inference (alpha spending) + exposure ramp gating
   |
 decision record -> registry promotion (lab03) with the experiment attached

 platform dashboards: active experiments, time-to-decision, effect sizes
 quarterly review: experiments run, reverts, guardrail stops""",
        components=[
            ("Experiment service and registry",
             ["Pre-registration requiring primary metric, MDE, alpha, power, horizon and guardrails before exposure",
              "Assignment by stable hash with an exposure ramp; no assignment state to lose",
              "Experiment record attached to the promoted model version and the decision memo",
              "Templates per experiment type with pre-agreed guardrails and attribution windows"]),
            ("Measurement pipeline",
             ["Exposure events with experiment id, arm, model version and timestamp",
              "Outcomes joined by user with a declared 30-day attribution window for GMV",
              "Join health monitored: match rate, late arrivals and duplicate attribution",
              "Metric definitions centralised so two experiments cannot define GMV differently"]),
            ("Inference and safety",
             ["SRM check before every metric read, blocking the readout on mismatch",
              "Sequential inference with alpha control; fixed horizon for low-risk rollouts",
              "Guardrails as non-inferiority bounds on complaints, refunds, latency and seller-side fairness",
              "Automatic ramp pause on a guardrail breach, with a pre-authorised revert path"]),
            ("Operations and governance",
             ["Decision memo template requiring effect size, interval and business translation",
              "Time-to-decision tracked per experiment; a stalled experiment escalates",
              "Quarterly review of reverts, guardrail stops and experiments never concluded",
              "Experimentation metrics shared with the platform team as a portfolio view"]),
        ],
        timeline=[
            ("Week 1-2", "Stand up exposure event logging and verify the outcome join with a sample audit"),
            ("Week 3", "Experiment service with pre-registration, stable assignment and SRM checks"),
            ("Week 4-5", "Sequential inference plus guardrail definitions agreed with support and risk"),
            ("Week 6-7", "Migrate two teams' monthly rollouts onto the platform; measure time-to-decision"),
            ("Week 9", "All teams migrated; revert drill; quarterly review process established"),
        ],
        runbook=[
            "# Active experiments and their state",
            "curl -s localhost:8080/experiments | jq '.[] | {id,model,exposure,state,guardrails}'",
            "",
            "# Check sample ratio mismatch BEFORE reading metrics",
            "curl -s 'localhost:8080/experiments/exp-221/srm' | jq '{control,treatment,chi2,passed}'",
            "",
            "# Primary metric with effect size and interval (sequential boundaries applied)",
            "curl -s 'localhost:8080/experiments/exp-221/result' | jq '{metric,delta,ci,bounds,decision}'",
            "",
            "# Guardrail status per metric",
            "curl -s 'localhost:8080/experiments/exp-221/guardrails' | jq '.[] | {metric,delta,bound,status}'",
            "",
            "# Pause the ramp and revert on a guardrail breach (pre-authorised)",
            "curl -XPOST localhost:8080/experiments/exp-221/pause -d '{\"reason\":\"guardrail:complaints\"}'",
        ],
        metrics=[
            "Process: pre-registration compliance at 100% before any exposure.",
            "Speed: median time-to-decision, tracked against the planned horizon.",
            "Integrity: SRM checks passing; join match rate above 99%.",
            "Safety: guardrail stops and reverts per quarter, trending down.",
            "Impact: decision-quality review sampling concluded experiments to confirm effect sizes hold.",
        ],
        failures=[
            ("A rollout is reverted a week after launch", "No guardrails at pre-registration", "Block exposure without guardrails; migrate rollouts one team at a time"),
            ("An experiment shows an implausible 400% lift", "SRM mismatch or attribution bug", "SRM check blocks the readout; audit the join before believing anything"),
            ("Experiments never conclude because the horizon is unbounded", "No MDE or sample size computed", "Require MDE, power and horizon at registration; escalate stalled experiments"),
            ("Two teams define GMV differently", "Metric definitions not centralised", "Central registry for metric definitions; reject experiments with ad-hoc definitions"),
            ("Guardrail breach discovered after exposure ramp reached 50%", "Ramp not gated on guardrails", "Gate each ramp step on guardrail status; pause automatically and pre-authorise revert"),
        ],
        backlog=[
            "Interference-aware designs for marketplace experiments where users interact.",
            "Shared guardrail catalogue per experiment type, agreed with support and risk.",
            "Decision-quality sampling to verify concluded effects persist after launch.",
            "Bandit allocation for high-volume, low-cost model choices.",
            "Experiment portfolio view: running, stalled, concluded, reverted.",
        ],
        urls=URLS,
        closer="The deliverable is 12 rollouts a month where every exposure was "
               "pre-registered, every readout passed an SRM check, every decision "
               "carried an effect size in business units, and no rollout was "
               "reverted for a problem the guardrails could have seen.",
    ),
))

# ---------------------------------------------------------------- lab11
SPECS.append(dict(
    track="mlops", lab="lab11", full_set=True, level="Advanced",
    title="Model Governance & Compliance", main_class="ModelGovernanceLab",
    problem="In a regulated decision, 'the model was accurate' is not an answer. "
            "You need to show who approved what, on which data, with which "
            "measured harm across groups.",
    why_now="Governance is becoming an engineering discipline rather than a "
             "spreadsheet exercise: model cards, fairness metrics and audit trails "
             "are buildable artefacts with testable properties.",
    objectives=[
        "Write a model card with intended use, data, metrics and limitations",
        "Compute and interpret core fairness metrics on real data",
        "Design an immutable audit trail covering every lifecycle transition",
        "Map a compliance obligation to an artefact and a test",
        "Distinguish fairness metrics that trade off from those that do not",
        "Build a governance workflow that produces evidence rather than promises",
    ],
    concepts=[
        ("Fairness metrics are in tension",
         "Statistical parity (equal selection rates) and equal opportunity (equal "
         "true positive rates) cannot both hold when base rates differ. Choosing "
         "which to prioritise is a policy decision that must be written down, not a "
         "modelling accident."),
        ("Base rates drive everything",
         "Two groups with different fraud rates will have different false positive "
         "rates under any threshold that treats them identically. This is why "
         "fairness analysis must always report base rates alongside the fairness "
         "metrics, or the numbers are uninterpretable."),
        ("Model cards are interfaces",
         "A model card is not documentation; it is the contract between the model "
         "and the people affected by it. Intended use, out-of-scope use, known "
         "limitations and the metrics that were actually measured are what let "
         "someone downstream decide whether to use the model at all."),
        ("Audit trails must be immutable and complete",
         "The trail has to answer: who promoted what, when, on which evidence, and "
         "under which version of the policy. If the policy can change silently, the "
         "trail is meaningless. Policy versions belong in the record."),
        ("Obligations map to artefacts and tests",
         "A compliance requirement is satisfied by an artefact plus a test that "
         "proves it. 'We have a fairness policy' is not evidence; 'the promotion "
         "gate fails when group disparity exceeds 0.05, and a test proves it' is."),
        ("Documentation decays silently",
         "Model cards go stale as features and thresholds change. Generating the "
         "measurable parts of the card from the pipeline, so it cannot drift from "
         "reality, is the only version that stays true."),
    ],
    formulas=[
        ("selection_rate = TP + FP over group", "Statistical parity", "P(yhat=1 | group)"),
        ("TPR_g = TP_g / (TP_g + FN_g)", "Equal opportunity", "equal true positive rates"),
        ("FPR_g = FP_g / (FP_g + TN_g)", "False positive disparity", "the metric that moves with base rates"),
        ("demographic_parity_gap = max_g rate - min_g rate", "Disparate impact", "the quantity a regulator measures"),
        ("disparate_impact_ratio = min_g rate / max_g rate", "Four-fifths style ratio", "below 0.8 flags review"),
        ("audit_record = (actor, action, from, to, policy_version, evidence_hash)", "Audit entry", "immutable and complete"),
    ],
    flow=[
        "Register the model with intended use, out-of-scope use, and the decision it informs.",
        "Record the data: sources, time window, population, known gaps.",
        "Evaluate metrics overall and per group, reporting base rates alongside fairness metrics.",
        "Write the limitations explicitly, including who the model is likely to harm.",
        "Run the promotion gate: fairness thresholds plus lineage plus required sign-offs.",
        "Store the model card, the audit entries and the evidence hash together.",
    ],
    assumptions=[
        "Protected attributes are available for evaluation even if they are excluded from training",
        "Group definitions are documented and reviewed rather than chosen per analysis",
        "Fairness thresholds are set as policy and enforced by the gate",
        "Policy versions are recorded in every audit entry",
        "Model card metrics are generated from the pipeline rather than typed",
        "Limitations are written for a non-technical reader",
    ],
    pitfalls=[
        ("Fairness analysis omits base rates", "uninterpretable disparity numbers", "always report base rate per group first"),
        ("A metric improved for one group and worsened for another", "unexamined trade-off", "publish the full group matrix and get the policy choice in writing"),
        ("Model card is accurate at launch and wrong after two releases", "hand-written documentation", "generate measurable fields from the pipeline"),
        ("Audit log exists but records no policy version", "policy changed silently", "record the policy version in every entry"),
        ("Disparate impact threshold ignored because 'the model is accurate'", "accuracy as an argument against fairness", "accuracy and fairness are separate gates; both must pass"),
        ("Protected attribute used as a training feature", "legal exposure and worse fairness", "exclude from training, include in evaluation only, with justification recorded"),
    ],
    java=[
        ("record ModelCard(String name, String version, IntendedUse, Data, Metrics, Limitations)", "the generated contract"),
        ("Map<String, GroupStats> for per-group evaluation", "base rate plus every metric per group"),
        ("Append-only audit log with a hash chain", "tamper evidence for the compliance export"),
        ("record PolicyVersion(String id, Instant effectiveFrom, Map<String,Double> thresholds)", "the version recorded in every audit entry"),
        ("BigDecimal for disparity ratios", "ratios at four-fifths granularity need exact reporting"),
    ],
    links=[
        "**mlops/lab03** provides the promotion gate that governance extends.",
        "**mlops/lab10** provides the live evidence that a rollout did not cause harm.",
        "**mlops/lab02** provides the run records that audit entries reference.",
        "**mlops/lab08** provides ongoing fairness and quality monitoring after launch.",
    ],
    checklist=[
        "Base rates are reported per group before any fairness metric.",
        "The fairness trade-off is documented as a policy choice, in writing.",
        "Model card metrics are generated, not typed.",
        "Every audit entry records actor, action, versions and policy version.",
        "Fairness thresholds are enforced by the promotion gate.",
        "Limitations are written for a non-technical reader.",
    ],
    cards=[
        ("Why can you not satisfy every fairness metric at once?", "With differing base rates, equal selection rates and equal true positive rates are mathematically incompatible."),
        ("Why report base rates first?", "Because disparity metrics are uninterpretable without knowing how the groups actually differ in outcome rates."),
        ("What is a model card for?", "It is the contract between the model and the people it affects: intended use, data, metrics, limitations."),
        ("What should an audit entry contain?", "Actor, action, from and to versions, policy version and a hash of the supporting evidence."),
        ("Why version your fairness policy?", "So an audit can tell which thresholds applied at the time, rather than today's thresholds retrofitted."),
        ("Should protected attributes be training features?", "No; they belong in evaluation so you can measure harm, with the exclusion documented."),
        ("What does disparate impact measure?", "The ratio or gap in selection rates between groups; a ratio below 0.8 traditionally flags review."),
        ("How do you stop model cards going stale?", "Generate the measurable fields from the pipeline so they cannot diverge from the model."),
    ],
    extra_cards=[
        ("What is equal opportunity?", "Equal true positive rates across groups, so equally-qualified people are equally likely to be flagged."),
        ("What is statistical parity?", "Equal selection rates across groups, which can require a higher error rate for one group when base rates differ."),
        ("Why are accuracy and fairness separate gates?", "A model can be accurate overall and still impose a disproportionate error rate on one group."),
        ("What is the four-fifths rule?", "A heuristic flagging review when the disadvantaged group's selection rate is below 80% of the advantaged group's."),
    ],
    math_why="Fairness is constrained optimisation: base rates fix which trade-offs "
             "are available, and audit integrity is a hash chain that makes history "
             "checkable.",
    math=[
        ("Selection and error rates per group",
         "for each group g and protected attribute a:\n  base_rate(g) = positives_g / n_g\n  selection(g) = (TP_g + FP_g) / n_g\n  TPR(g) = TP_g / positives_g,  FPR(g) = FP_g / negatives_g",
         "You cannot interpret any fairness metric without the base rate. Two groups "
         "with the same accuracy can have very different error distributions, and "
         "that difference is the whole substance of a fairness review.",
         "Group A: 1000 rows, 100 positive, 50 flagged, 40 correct. base 10%, "
         "selection 5%, TPR 40%. Group B: 1000 rows, 300 positive, 60 flagged, 55 "
         "correct. base 30%, selection 6%, TPR 18%. Group B looks similar on "
         "selection and much worse on TPR."),
        ("Disparate impact metrics",
         "ratio = min_g selection(g) / max_g selection(g)\ngap = max_g selection(g) - min_g selection(g)\nheuristic flag: ratio < 0.8",
         "The ratio is scale-free and comparable to the four-fifths heuristic; the "
         "gap is absolute and meaningful when the rates are small. Report both, "
         "because a small-rate domain can show a large gap and a benign ratio.",
         "Selection 6% and 5%: ratio 0.833 (passes 0.8), gap 1 point. Selection "
         "0.6% and 0.4%: ratio 0.667 (flags), gap 0.2 points. The second is far less "
         "impactful in absolute terms but fails the standard heuristic."),
        ("Why parity and equality can conflict",
         "if base_rate_A != base_rate_B and FPR is equal:\n  TPR = 1 - FPR (1 + negative/positive ratio scaled)\nno threshold equalises both selection rates and TPRs",
         "The impossibility is structural, not a modelling failure. Any policy must "
         "therefore choose which notion of fairness to prioritise, which is why the "
         "choice belongs in a written policy rather than in a code comment.",
         "Base rates 10% and 30%. Equal FPR of 0.05 gives TPR of roughly 0.5 and "
         "0.71. Forcing equal TPR requires raising the second group's FPR above "
         "the first's, which is the trade a reviewer must approve."),
        ("Audit chain integrity",
         "entry_i.hash = H(entry_{i-1}.hash + canonical(entry_i))\nverifying the chain detects any modification\npolicy_version stored per entry so thresholds are reconstructible",
         "A hash chain makes the log tamper-evident, which is what turns 'we keep "
         "an audit log' into evidence a regulator accepts. Storing the policy "
         "version per entry is what makes the trail interpretable months later.",
         "Changing entry 400's actor value changes every subsequent hash, so a "
         "reviewer verifying the chain finds the break at entry 400 rather than "
         "discovering an inconsistency months later."),
    ],
    math_traps=[
        "Reporting a fairness ratio without the group base rate.",
        "Comparing a disparity ratio across domains with very different rates without the absolute gap.",
        "Attempting to satisfy parity and equal opportunity simultaneously when base rates differ.",
        "Judging a model on accuracy to dismiss a fairness gate failure.",
    ],
    math_problems=[
        "Compute base rate, selection rate, TPR and FPR per group for a given confusion-matrix breakdown.",
        "Compute the disparate impact ratio and gap; compare against the 0.8 heuristic and explain the discrepancy.",
        "Show with numbers why equal selection rates and equal TPR cannot both hold under differing base rates.",
        "Implement an audit hash chain and demonstrate that a single modified field breaks verification.",
        "Write a fairness policy choosing parity or equal opportunity, with the reasoning and the cost of the alternative.",
    ],
    tree="""src/
  ModelGovernanceLab.java    driver: register, evaluate, gate, audit
  ModelCard.java            generated card: use, data, metrics, limitations
  FairnessEvaluator.java    per-group base rate, selection, TPR, FPR, disparity
  AuditLog.java             append-only hash-chained entries with policy version
  GovernancePolicy.java     versioned thresholds for fairness, drift and evidence
  PromotionGate.java        all governance checks, all reasons reported""",
    tree_note="ModelCard is generated from the pipeline: the group metrics come "
              "from FairnessEvaluator and the data description from the snapshot "
              "metadata. Typed numbers rot; generated ones cannot.",
    types=[
        ("ModelCard", "generated card with intended use, data, per-group metrics and limitations"),
        ("FairnessEvaluator", "per-group base rates and error metrics plus disparity ratios"),
        ("AuditLog", "append-only hash-chained entries carrying the policy version"),
        ("GovernancePolicy", "versioned thresholds evaluated by the promotion gate"),
    ],
    patterns=[
        ("Fairness evaluation that always reports base rates",
         "Base rates come first because every disparity number is uninterpretable "
         "without them, and the group matrix is returned in full.",
         """public FairnessReport evaluate(int[] y, int[] yHat, String[] group) {
    Map<String, int[]> counts = new TreeMap<>();      // per group: TP, FP, FN, TN
    for (int i = 0; i < y.length; i++)
        counts.computeIfAbsent(group[i], k -> new int[4])[index(y[i], yHat[i])]++;

    Map<String, GroupStats> stats = new LinkedHashMap<>();
    for (var e : counts.entrySet()) {
        int tp = e.getValue()[0], fp = e.getValue()[1], fn = e.getValue()[2], tn = e.getValue()[3];
        int n = tp + fp + fn + tn;
        stats.put(e.getKey(), new GroupStats(
                (tp + fn) / (double) n,                 // base rate FIRST: everything else depends on it
                (tp + fp) / (double) n,                 // selection rate
                safe(tp, tp + fn),                      // TPR / equal opportunity view
                safe(fp, fp + tn),                      // FPR
                safe(tp + tn, n)));                     // accuracy, reported but never alone
    }
    double minSel = stats.values().stream().mapToDouble(GroupStats::selection).min().orElseThrow();
    double maxSel = stats.values().stream().mapToDouble(GroupStats::selection).max().orElseThrow();
    return new FairnessReport(stats, maxSel == 0 ? 1 : minSel / maxSel, maxSel - minSel);
}"""),
        ("Hash-chained audit entries with the policy version",
         "Tamper evidence plus the policy in force at the time, so a review months "
         "later can reconstruct which thresholds applied.",
         """public AuditEntry append(String actor, String action, String from, String to,
                           GovernancePolicy policy, List<String> evidence) {
    String canonical = String.join("|", actor, action, from, to,
            policy.versionId(),                                   // thresholds in force at the time
            evidenceHash(evidence), Instant.now().toString());
    String hash = sha256Hex(lastHash + canonical);             // chain: tamper-evident
    AuditEntry entry = new AuditEntry(canonical, hash, lastHash);
    entries.add(entry);
    lastHash = hash;
    return entry;
}

public boolean verifyChain() {
    String prev = "GENESIS";
    for (AuditEntry e : entries) {
        if (!e.hash().equals(sha256Hex(prev + e.canonical()))) return false;  // break found
        prev = e.hash();
    }
    return true;
}"""),
    ],
    costs=[
        ("Per-group fairness evaluation", "O(n)", "one pass grouping by attribute"),
        ("Model card generation", "O(g x m)", "group count times metric count"),
        ("Audit entry append", "O(evidence size)", "hash chain is linear in chain length"),
        ("Chain verification", "O(entries)", "re-hash everything; run on export"),
    ],
    numerics=[
        "Always print the base rate per group before any disparity ratio.",
        "Use BigDecimal or scaled doubles for ratios compared to the 0.8 heuristic.",
        "Guard divisions where a group has no positives or no negatives.",
        "Record the policy version in every audit entry.",
        "Generate card metrics from the pipeline rather than typing them.",
    ],
    tests=[
        "Base rates are present in the report for every group.",
        "A single-group dataset produces a ratio of 1.0 and does not error.",
        "A group with zero positives does not produce NaN.",
        "Modifying any audit field breaks chain verification at that entry.",
        "The promotion gate fails when a fairness threshold is breached, with a named reason.",
        "Generated card metrics equal the metrics recomputed independently.",
    ],
    extensions=[
        "Add threshold-sweep reporting showing how disparity moves with the decision threshold.",
        "Add counterfactual fairness checking by protected attribute.",
        "Export the audit trail and verification result in a regulator-friendly format.",
    ],
    code_checklist=[
        "Base rates reported per group before disparity metrics",
        "Fairness thresholds versioned and enforced by the gate",
        "Policy version recorded in every audit entry",
        "Audit log hash-chained and verifiable",
        "Card metrics generated from the pipeline",
        "Limitations written for a non-technical reader",
    ],
    exercise_selfcheck=[
        "I report base rates before disparity.",
        "My fairness choice is a documented policy, not a default.",
        "My audit trail is tamper-evident.",
        "My model card cannot go stale.",
    ],
    exercises=[
        ("Fairness metrics with base rates",
         "Get the report in the right order.",
         ["Compute base rate, selection, TPR, FPR and accuracy per group.",
          "Guard zero-positive and zero-negative groups.",
          "Compute disparity ratio and gap; compare with 0.8.",
          "Write a sentence explaining the discrepancy."],
         "A report where base rates come first."),
        ("The fairness trade-off, numerically",
         "Show the impossibility with your own numbers.",
         ["Take two groups with different base rates.",
          "Find a threshold equalising selection rates; report TPRs.",
          "Find a threshold equalising TPR; report selection rates.",
          "Write the policy choice with the cost of the alternative."],
         "A documented policy choice with arithmetic."),
        ("Threshold sweep and trade-off curves",
         "See how disparity moves with the operating point.",
         ["Sweep the decision threshold for two groups.",
          "Plot disparity ratio, gap, TPR gap and selection gap.",
          "Identify thresholds satisfying your policy.",
          "Report the business cost at each candidate."],
         "A sweep table with a defended operating point."),
        ("Tamper-evident audit log",
         "Make the trail evidence.",
         ["Implement a hash-chained append-only log.",
          "Record the policy version in every entry.",
          "Modify one field and show verification fails at that entry.",
          "Export the chain and its verification result."],
         "A verifiable audit export."),
        ("Model card generation",
         "Stop the documentation rotting.",
         ["Generate the card from snapshot metadata and evaluation results.",
          "Include intended use, out-of-scope use, data and limitations.",
          "Add a test asserting generated metrics match recomputed ones.",
          "Regenerate after a threshold change and see the card update."],
         "A card that updates itself."),
        ("Governance policy as code",
         "Make obligations testable.",
         ["Encode fairness and evidence requirements as a versioned policy.",
          "Implement the promotion gate reading the policy.",
          "Change the policy and show a previously-passing model now blocked.",
          "Record the policy version in the audit entry."],
         "A policy change that demonstrably blocks a model."),
        ("Obligation-to-test mapping",
         "Turn compliance into engineering.",
         ["List 5 obligations with the artefact and test that satisfies each.",
          "Implement 3 of those tests in CI.",
          "Produce a compliance evidence report.",
          "Run it and fix whatever it finds."],
         "An evidence report generated by tests."),
        ("Full governance walkthrough",
         "Register through to audit.",
         ["Register a model with intended use and limitations.",
          "Evaluate overall and per group.",
          "Write the card; run the gate with a deliberate fairness breach.",
          "Promote, then export the audit trail."],
         "A complete trail from registration to audited promotion."),
    ],
    quiz=[
        ("Why can you not satisfy both statistical parity and equal opportunity?", ["You can, with enough data", "With differing base rates they are mathematically incompatible", "It depends on the model", "Parity is about accuracy"], 1, "The impossibility is structural, so the choice of which to prioritise is a policy decision."),
        ("Why must base rates be reported with fairness metrics?", ["For completeness", "Disparity numbers are uninterpretable without knowing how the groups differ in outcome rates", "Because regulators ask", "To increase sample size"], 1, "Equal accuracy can hide very different error distributions across groups."),
        ("What is a model card?", ["Marketing material", "The contract between the model and the people it affects: use, data, metrics, limitations", "A training log", "A licence"], 1, "It lets a downstream team decide whether the model is appropriate at all."),
        ("What should an audit entry record besides actor and action?", ["Nothing else", "From and to versions, the policy version, and a hash of supporting evidence", "The file path", "The engineer's email"], 1, "The policy version and evidence hash make the trail interpretable months later."),
        ("Why version the fairness policy?", ["For auditing", "So a review can tell which thresholds applied at the time", "To satisfy legal", "Because thresholds change"], 1, "Today's thresholds retrofitted onto a past decision are not evidence."),
        ("Should protected attributes be training features?", ["Yes, for fairness", "No; use them for evaluation so you can measure harm", "Only if legally permitted", "It depends"], 1, "Including them creates legal exposure and often worsens the fairness outcome."),
        ("What does a disparate impact ratio below 0.8 indicate?", ["A violation", "A heuristic flag for review, not proof of discrimination", "Perfect fairness", "No effect"], 1, "It is a screening heuristic from equal-employment practice, not a legal test."),
        ("Can a highly accurate model fail a fairness gate?", ["No", "Yes; accuracy overall can coexist with a disproportionate error rate on one group", "Only with poor data", "Only for regression"], 1, "Accuracy and fairness are separate gates; both must pass."),
        ("Why does documentation go stale?", ["Lack of effort", "Hand-written numbers diverge as features and thresholds change", "Storage limits", "Policy"], 1, "Generating the measurable fields from the pipeline is the only version that stays true."),
        ("What is a hash-chained audit log for?", ["Speed", "Tamper evidence, so a modification is detectable during verification", "Compression", "Access control"], 1, "It turns 'we keep a log' into evidence a reviewer can verify."),
        ("What is statistical parity?", ["Equal accuracy", "Equal selection rates across groups", "Equal recall", "Equal latency"], 1, "P(yhat = 1) is the same for every group, which can require unequal error rates."),
        ("What is equal opportunity?", ["Equal selection rates", "Equal true positive rates across groups", "Equal accuracy", "Equal calibration"], 1, "Equally qualified people are equally likely to be flagged."),
        ("How do you keep the blocking gate trustworthy?", ["Add more checks", "Keep blocking thresholds rare and evidence-based, and report every failure reason", "Turn everything into warnings", "Add approvals"], 1, "A gate that fires constantly gets overridden, and then hides real breaches."),
        ("What belongs in limitations?", ["Only accuracy", "Who the model is likely to harm, out-of-scope uses, and known data gaps, written for a non-technical reader", "Training time", "Feature names"], 1, "Limitations are the part a downstream user actually needs."),
        ("How should compliance be operationalised?", ["A policy document", "Each obligation mapped to an artefact plus a test that proves it", "An annual audit", "Training"], 1, "'We have a policy' is not evidence; a failing test is."),
    ],
    vision=dict(
        future="Model governance becomes engineering: fairness and evidence "
               "requirements expressed as versioned policy code that gates "
               "promotion, with generated documentation that cannot rot. The "
               "frontier is continuous fairness monitoring with automated "
               "remediation rather than annual reviews.",
        good=[
            "Fairness evaluations always report base rates per group before any disparity metric.",
            "The parity-versus-opportunity choice is a written, versioned policy.",
            "Model card metrics are generated from the pipeline.",
            "Audit trails are hash-chained and carry the policy version.",
        ],
        ladder=[
            ("L1", "Document", "A model card with intended use, data, metrics and limitations."),
            ("L2", "Measure", "Per-group fairness evaluation with base rates first."),
            ("L3", "Enforce", "Versioned governance policy gating promotion, with audit trails."),
            ("L4", "Continuously", "Post-launch fairness monitoring with automated remediation."),
        ],
        behaviors="Report base rates before disparities. Treat the fairness "
                  "trade-off as a policy decision requiring sign-off. Generate "
                  "documentation so it cannot lie.",
        anti=[
            "Fairness ratios published without base rates.",
            "Model cards typed by hand and stale within two releases.",
            "Accuracy used to argue past a fairness gate.",
            "An audit trail with no policy version, useless six months later.",
        ],
        trends=[
            "Governance policy as code gating promotion automatically.",
            "Continuous fairness monitoring with segment-level alerts post-launch.",
            "Counterfactual and causal fairness measures beyond statistical parity.",
            "Standardised model reporting aligned with emerging regulatory templates.",
        ],
        d30="Compute per-group fairness metrics with base rates reported first.",
        d60="Build a hash-chained audit log with the policy version per entry.",
        d90="Generate model cards from the pipeline and enforce a versioned fairness policy in the promotion gate.",
        metrics=[
            "I report base rates before any disparity metric.",
            "My fairness choice is documented and signed off.",
            "My audit trail is tamper-evident.",
            "My model card cannot go stale.",
        ],
        closer="Governance is the part of MLOps where 'probably fine' becomes a "
               "finding; build the artefacts that make the answer checkable.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Model Card, Fairness Gate and Audit Trail",
        brief="Generate a model card from the pipeline, enforce a fairness policy "
              "in the promotion gate, and record a tamper-evident audit trail.",
        timebox="3\u20134 hours",
        why="Governance is learnable as engineering: each obligation becomes an "
            "artefact and a test, and the tension between fairness metrics becomes "
            "a documented choice.",
        requirements=[
            "Per-group fairness evaluation with base rates reported before any disparity metric.",
            "Demonstrate the parity-versus-opportunity trade-off numerically and write the policy choice.",
            "Threshold sweep showing how disparity and error rates move with the operating point.",
            "Versioned governance policy enforced by a promotion gate that reports every failure reason.",
            "Hash-chained audit log with the policy version in each entry; demonstrate tamper detection.",
            "Model card generated from the pipeline, with a test proving generated metrics match recomputation.",
            "Obligation-to-test mapping with at least three tests running in CI.",
        ],
        steps=[
            ("1", "30m", "Per-group fairness evaluation with base rates first", "A correct fairness report"),
            ("2", "35m", "Show the trade-off numerically; write the policy", "A signed-off policy choice"),
            ("3", "30m", "Threshold sweep with disparity and cost curves", "A defended operating point"),
            ("4", "30m", "Hash-chained audit log; demonstrate tamper detection", "A verifiable trail"),
            ("5", "35m", "Versioned governance policy in the promotion gate", "A gate that blocks on breach"),
            ("6", "30m", "Generated model card with a parity test", "A card that cannot go stale"),
            ("7", "25m", "Obligation-to-test mapping with three CI tests", "An evidence report"),
        ],
        diagram=""" snapshot metadata --> ModelCard (generated)
                              |
                    per-group evaluation (base rates first)
                              |
                    disparity ratio + gap vs policy thresholds
                              |
                    GovernancePolicy (versioned) --> PromotionGate
                              |                    (all reasons reported)
                        audit entry (hash chain, policy version)
                              |
                    CI tests: fairness, evidence, lineage, additivity""",
        notes=[
            "Put base rates first in the output; everything after it is uninterpretable without them.",
            "Demonstrate the trade-off yourself rather than asserting it exists.",
            "Generate the card from the pipeline and prove it with a parity test.",
            "Change the policy mid-project and show a previously passing model now blocked.",
        ],
        deliverables=[
            "Fairness report with base rates, disparity metrics and a threshold sweep.",
            "Written fairness policy with the trade-off and its cost.",
            "Verifiable audit export demonstrating tamper detection.",
            "Generated model card plus the CI evidence report.",
        ],
        grading=[
            ("Correctness", "25%", "Base rates first; metrics verified; no NaN edge cases"),
            ("Policy", "25%", "Trade-off demonstrated numerically and the choice justified"),
            ("Enforcement", "25%", "Versioned policy blocks promotion with named reasons"),
            ("Evidence", "15%", "Tamper-evident audit with policy version"),
            ("Durability", "10%", "Card generated with a parity test proving it cannot drift"),
        ],
        stretch=[
            "Add counterfactual fairness checking by protected attribute.",
            "Add continuous post-launch fairness monitoring with segment alerts.",
            "Export an audit package in a regulator-friendly format.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Governed Credit Decisioning",
        scenario="A lender uses four models to make credit decisions for 2 million "
                 "applicants a year. Fair-lending counsel requires reason codes "
                 "and disparate-impact analysis for every model change, and the last "
                 "review took three weeks because the evidence was assembled by "
                 "hand each time.",
        scale=[
            ("Volume", "2M applications/year, ~8,000 per business day"),
            ("Models", "4 decisioning models plus a rules engine"),
            ("Regulatory regime", "fair-lending review required for every model change"),
            ("Current evidence", "assembled manually per change, roughly 3 weeks"),
            ("Goal", "evidence produced by the pipeline in days, with every decision traceable"),
    ],
        diagram=""" applications --> snapshot (point-in-time, validated)
        |
 model training --> evaluation (overall + per group, base rates first)
        |
 generated model card (data, metrics, limitations, reason codes)
        |
 governance policy (versioned) --> promotion gate
        |                          (fairness, lineage, evidence, sign-offs)
        | pass -> decisioning with reason codes
        | fail -> blocked with named reasons, owner notified
        |
 audit trail (hash chain, policy version) --> regulator export
        |
 post-launch fairness monitoring by group, continuous""",
        components=[
            ("Fair-lending evaluation",
             ["Per-group evaluation with base rates first, on protected attributes used for evaluation only",
              "Disparate impact ratio and gap evaluated against versioned policy thresholds",
              "Threshold sweep reporting how error rates and disparity move with the operating point",
              "Comparison against prior model versions so a change in disparity is visible"]),
            ("Generated model card and evidence",
             ["Card generated from snapshot metadata, evaluation results and threshold settings",
              "Intended use, out-of-scope use and limitations written by the model owner and reviewed",
              "Reason-code catalogue versioned so adverse action notices remain explainable",
              "Parity test asserting generated card metrics equal recomputed metrics"]),
            ("Governance policy and promotion gate",
             ["Versioned policy encoding fairness thresholds, lineage requirements and sign-offs",
              "Gate reports every failing check with a named reason and an owner",
              "Policy change blocks promotion until re-evaluated, recorded in the audit trail",
              "Four-fifths style screening plus absolute gap, both reported with interpretation"]),
            ("Audit and post-launch monitoring",
             ["Hash-chained audit trail with actor, action, versions, policy version and evidence hash",
              "Chain verification run before every regulator export",
              "Continuous fairness and approval-rate monitoring by group after launch",
              "Regulator export package: card, evaluation, policy version and verified audit chain"]),
        ],
        timeline=[
            ("Week 1-2", "Baseline per-group evaluation on all four models with base rates and disparity"),
            ("Week 3", "Fairness policy versioned and signed off by counsel and risk"),
            ("Week 4-5", "Promotion gate enforcing the policy; model cards generated from the pipeline"),
            ("Week 6-7", "Audit trail with hash chain; verification in the export path"),
            ("Week 9", "Post-launch fairness monitoring; drill a policy-change scenario end to end"),
        ],
        runbook=[
            "# Fair-lending evaluation for a candidate model version",
            "curl -s 'localhost:8088/fairness?model=income-gbm&version=13' | jq '{baseRates,disparityRatio,gap,thresholds}'",
            "",
            "# Policy in force and the thresholds it applies",
            "curl -s localhost:8088/governance/policy | jq '{versionId,thresholds,effectiveFrom}'",
            "",
            "# Promotion gate result with every reason",
            "curl -s 'localhost:8088/governance/gate?model=income-gbm&version=13' | jq '{passed,reasons}'",
            "",
            "# Verify the audit chain before an export",
            "curl -s 'localhost:8088/audit/verify?exportId=ex-221' | jq '{valid,entries,firstBreakAt}'",
            "",
            "# Post-launch disparity by group, compared to the prior version",
            "curl -s 'localhost:8088/monitoring/fairness?model=income-gbm&window=30d' | jq '.byGroup,.deltaVsPrevious'",
        ],
        metrics=[
            "Compliance: promotion blocked on any governance failure (target 100%).",
            "Evidence: regulator evidence package produced by the pipeline (target under 3 days, from 3 weeks).",
            "Fairness: disparity ratio and gap per group, reviewed per release.",
            "Integrity: audit chain verification passing on every export.",
            "Operations: mean time from model candidate to a compliant promotion decision.",
        ],
        failures=[
            ("A model ships with a disparity regression", "Gate evaluated against superseded thresholds", "Version the policy; block promotion until re-evaluated under the current policy"),
            ("Evidence package assembly takes weeks again", "Card and evaluation not generated by the pipeline", "Generate everything from the pipeline; treat manual assembly as a defect"),
            ("Regulator export fails chain verification", "Audit log modified or truncated by a migration", "Verify before export; alert on any chain break and reconcile from backups"),
            ("A group experiences an approval-rate drop in production", "Post-launch traffic differs from the training population", "Pause rollout, run the threshold sweep, and escalate to counsel"),
            ("Reason codes no longer explain adverse decisions", "Model changed without regenerating the catalogue", "Block promotion unless the reason-code catalogue version is updated"),
        ],
        backlog=[
            "Counterfactual fairness checks added to the standard evaluation.",
            "Disparity monitoring with automated thresholds and owner routing post-launch.",
            "Adversarial testing programme with outcomes fed into the policy review.",
            "Quarterly regulator dry run producing an export package end to end.",
            "Model version comparison view showing disparity deltas between versions.",
        ],
        urls=URLS,
        closer="The deliverable is four credit models where every promotion carries "
               "generated evidence, a signed-off fairness policy, a verified audit "
               "chain, and reason codes that still explain the decisions being made.",
    ),
))
