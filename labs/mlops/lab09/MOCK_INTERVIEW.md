# Lab 09: Mock Interview — Data Validation & Quality

**Role**: ML Platform Engineer / MLOps Engineer
**Duration**: 60 minutes
**Focus**: Expectation suites, schema checks, null/range/uniqueness validation, distribution checks, validation gates in pipelines

---

**Interviewer**: "Walk me through the validation model in this lab. What is an expectation, and how do they compose?"

**Candidate**: "The lab is a Java miniature of Great Expectations. An expectation is a verifiable statement about data, produced by a `DataValidator` method and captured as an `ExpectationResult` — `expectation` name, `passed` flag, `observed` vs `threshold`, and `details`. The validator accumulates results into a suite, and `printReport` renders `✓`/`✗` lines with observed/threshold values, then `allPassed()` answers the gate question. The `Dataset` is a tiny columnar structure — `addColumn(name, values...)` builds `Map<String, List<Object>>` with a row count — which is enough to demonstrate the checks without pulling in a real DataFrame library. The five expectation types mirror GE's suite vocabulary: existence, null ratio, range, uniqueness, and distribution."

**Interviewer**: "The demo runs 11 expectations. Walk me through which ones fail and why."

**Candidate**: "Three fail out of 11. `expect_column_to_exist: nonexistent_column` fails with observed 0.0 — it's a deliberately wrong assertion proving the schema check works. `expect_column_null_ratio_less_than: age` fails: the age column has one null out of five — observed null ratio 0.20 — against the 0.05 threshold; the details print `(1/5 null)`. And `expect_column_values_between: transaction_count_7d` fails: one value, 150, exceeds the [0, 100] bound — `(1/5 out of [0.0, 100.0])`. Everything else passes: `user_id` unique (5/5 distinct), `credit_score` in [300, 850], `risk_tier` distribution matching the expected 0.4/0.4/0.2 with KL divergence 0.0. The report closes with `Passed: 8 / 11` and `✓ Critical threshold: SOME FAILED` — the pipeline gate must not deploy on this data."

**Interviewer**: "The distribution check uses KL divergence. How is it computed here, and what are its limits?"

**Candidate**: "`expectColumnValueDistribution` compares each category's observed probability against the expected probability from the expected distribution map: for each entry it counts occurrences, computes `actualP`, and accumulates `actualP × ln(actualP / expectedP)` — KL divergence, the same statistic Lab 08's `computeKLDivergence` uses. It passes if `klDiv <= maxKLDivergence`. The limits: it only sums over categories present in the *expected* map — a new category appearing in production contributes nothing — and it's sensitive to zero counts, which is why real tools (Deequ, GE) layer in PSI, KS tests, and category-set checks. For the demo's `risk_tier`, actual matches expected exactly, so KL is 0.0 — the pass is the boring-but-correct case."

**Interviewer**: "The lab's INTERVIEW notes describe a two-layer validation architecture. What are the two layers, and where does this lab's code sit?"

**Candidate**: "Layer one is batch validation — Spark/Deequ jobs on offline data, computing null rates, min/max, distribution distances, and profile stats daily; that's the training-gate layer, and the lab's `DataValidator` is its miniature. Layer two is online validation — lightweight checks on every inference request: schema conformance, range checks from training min/max, type coercion, missing-value fallback, returning 400 on invalid input. The Lab 05 model server is where layer two lives. The two layers share the same *specification* — the min/max you validate online should come from the batch profiles you computed offline — which is exactly the consistency problem Lab 04's feature store solves for features."

**Interviewer**: "How do you handle schema drift — new columns, deprecated columns — per the lab's Q2?"

**Candidate**: "With an explicit schema evolution policy, not silent tolerance. The interview notes define the two directions: backward compatible — new columns are added as optional, so old models still load old data; forward compatible — models ignore unknown columns, so new data doesn't break serving. Implementation: Avro/Protobuf schemas in a schema registry with compatibility checks at write time — a registry rejects a schema change that violates the policy. The ML consequence: when schema changes significantly, the pipeline auto-retrains — new features available, old features deprecated — which is the data-trigger path from Lab 07. The lab's `expectColumnToExist` is the gate's first line: if the column literally isn't there, nothing else in the suite should run."

**Interviewer**: "Great Expectations vs Deequ — the lab's Q3. When would you pick each for a Java-centric stack?"

**Candidate**: "Great Expectations is Python-native: rich expectation library, data docs, notebook-friendly — the right tool when the DS workflow is Python and validation lives beside analysis. Deequ is Spark-native (Scala) with automated constraint suggestion and scales to huge datasets — the right tool when validation is a Spark batch job in production. The interview notes make the pragmatic point: for a Java ecosystem, Deequ is more natural because it integrates with the Spark stack the platform already runs. This lab sits between them: a dependency-free Java implementation of the *semantics* both tools share — which is why its class names (`expectColumnToExist`, `expectColumnValuesBetween`) deliberately mirror GE's API."

**Interviewer**: "The lab's `expectColumnValuesBetween` takes `Number` bounds. What type hazards does that create, and what does the walkthrough fix?"

**Candidate**: "The signature accepts `Number min, Number max`, which is great for callers — `18, 100` as ints, `300.0` as doubles. But the implementation formats them with `%.1f`, and the `%f` specifier only accepts floating-point types — an `Integer` argument throws `IllegalFormatConversionException` at runtime. The lab's demo passes integer literals, so it crashes on the first range check; the walkthrough's version formats `min.doubleValue()` / `max.doubleValue()` instead. The lesson: a `Number`-typed API must normalize to a concrete numeric type before formatting or arithmetic — the same discipline applies to the feature store's `Number` casts and to JSON deserialization of bounds."

**Interviewer**: "How does validation gate the training pipeline — where does `allPassed()` plug in?"

**Candidate**: "The CI/CD lab answers it directly: its `data-validation` job runs `com.mlops.lab09.DataValidationLab` as a stage, and the generated workflow makes training `needs: data-validation`. The gate semantics: `allPassed()` true → proceed to feature engineering and training; false → the pipeline stops and alerts, exactly like the champion-gate in Model Evaluation. The guide's best practices add the levels: fail the pipeline on *critical* expectation failures, alert on *warning* failures, and track validation results over time for trend analysis. And the suite itself is versioned alongside the code — expectations change with the data contract, reviewed in the same PR as the model code."

**Interviewer**: "Real-time validation at inference — the lab's Q4. What does the serving layer need to check per request?"

**Candidate**: "Four checks, per the interview notes: schema validation — the JSON body matches a declared schema; range checks — each feature within training min/max (this lab's `expectColumnValuesBetween`); type coercion — safe conversion with explicit failure rather than silent cast; and missing-value handling — a policy (default, median) instead of a crash. Invalid input returns a 400 with a clear message — Lab 05's server already does the plumbing (`400 {"error": ...}`). The key design point: the online checks must derive from the offline profiles, so 'valid' means the same thing at training and serving time — the numeric bounds, the allowed categories, the required fields all come from one definition."

**Interviewer**: "The lab has no `expectColumnValuesBetween` on a nullable column guard beyond `Objects::nonNull`. What happens with nulls in range checks, and what should the policy be?"

**Candidate**: "The implementation filters `Objects::nonNull` before the range comparison, so nulls are silently ignored by the between-check — they're policed separately by `expectColumnNullRatioLessThan`. That separation is actually the right policy shape: each check has one responsibility, and the *combination* defines the contract. The production refinement: nulls and out-of-range values should be distinguished in the report — a null is 'missing data' (handled by policy), an out-of-range value is 'corrupt data' (handled by rejection). The lab's `ExpectationResult` already carries `details` for exactly this nuance — `(1/5 null)` vs `(1/5 out of [0.0, 100.0])` — so the humans reading the report can tell the difference at a glance."

**Interviewer**: "Tie the lab to its LeetCode references: log aggregation, valid parentheses, error monitoring."

**Candidate**: "Design a Log Aggregation System is the validation-results pipeline: every check run produces a record (suite, dataset, timestamp, pass/fail) that must be collected and queryable — which is how you build the 'track validation results over time' best practice. Valid Parentheses (20) is the schema-validation pattern: nesting and pairing rules over tokens — JSON schema validation is the same stack discipline, matching brackets for JSON. Design an Error Monitoring System covers the alerting side: which failed expectations page who, and how failures trend over time. The through-line: validation is not a test you run once — it's a telemetry source."

**Interviewer**: "What's the most common failure you've seen in data validation in production, and what does this lab's design guard against?"

**Candidate**: "The 'validation theater' failure: expectations exist, the report prints all green, but the expectations are so weak that corrupt data sails through — the age column at 20% nulls with a 5% threshold should stop the pipeline, and in the demo it does. The second failure: validation runs but nobody can act on it — this lab guards by making the report the gate: `allPassed()` is a boolean consumed by the pipeline, not a PDF for the shelf. The third: expectations drift from the real contract — the lab's answer is that expectations are code, versioned with the pipeline, so the contract changes are reviewed like any other change. And the fourth, seen in this very lab's original code: the validator itself crashes on a type hazard — which is why the walkthrough fix matters: validation code must be as battle-tested as the data it checks."
