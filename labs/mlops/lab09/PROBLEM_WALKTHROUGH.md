# Problem Walkthrough: Data Validation & Quality

## Problem 1: E-commerce Training Data Validation Gate — Company: Amazon

### Interview Scenario

> **Interviewer**: "Our training pipelines ingest customer feature snapshots from a few sources, and garbage data has burned us before — one pipeline trained on a table where the age column was 20% nulls, and we shipped a model that silently dropped everyone without a birthdate. We want a validation gate, written in Java, that runs before training and fails fast. The gate needs to check: required columns exist, null ratios stay under thresholds, numeric features respect training bounds, key columns are unique, and categorical distributions haven't drifted. We've sketched a `DataValidator` with expectation methods — take a look at the lab's skeleton and make the demo actually run."
>
> **Candidate**: "Before I touch anything, I need to run the demo — because a validator that can't execute is worse than no validator."

### The Problem

1. Build a `Dataset` with five rows of customer features — `user_id`, `age`, `income`, `credit_score`, `risk_tier`, and `transaction_count_7d` — where one age value is `null` and one transaction count is `150`.
2. Define an expectation suite of 11 checks: four existence, two null-ratio, three range, one uniqueness, and one distribution check.
3. Run the suite and render a markdown-style report with `✓`/`✗` icons, observed vs threshold values, and a final `Passed: X / 12` summary.
4. Gate the pipeline: `allPassed()` must be `false` for this dataset, and the validator itself must execute cleanly on Java 21+.

### Solution Walkthrough

1. **Model the data as columns, not rows.** The `Dataset` holds `Map<String, List<Object>>` in insertion order, and `addColumn(name, values...)` records the max row count. That's the entire contract the expectations need — they index by column name, which is exactly what a schema check is about.
2. **Make every expectation produce a result.** Each `expectColumn*` method constructs an `ExpectationResult` — expectation name, `passed`, `observed`, `threshold`, `details` — and appends it to the validator's list. There is no early exit: the report shows all 12 outcomes even when the first three pass, so the human can see the full damage.
3. **Existence check is the schema gate.** `expectColumnToExist` answers `columns.containsKey(column)` — trivial, but it is the reason the demo includes `nonexistent_column`: observed 0.00 vs threshold 1.00 proves the check isn't a tautology.
4. **Null ratio is computed, not counted.** `expectColumnNullRatioLessThan` filters `Objects::isNull`, divides by the column size, and embeds `(1/5 null)` in details. The age column fails: 0.20 observed vs 0.05 threshold.
5. **Fix the range check's type hazard.** The lab's `expectColumnValuesBetween` accepts `Number min, Number max`, which is fine for callers, but it formats the bounds with `%.1f` while passing the raw `Number` — an `Integer` argument throws `IllegalFormatConversionException` at runtime, so the demo crashes at the first range check on any modern JDK. The walkthrough formats `min.doubleValue()` / `max.doubleValue()` instead, and compares with `v.doubleValue()` — one canonical numeric form for both formatting and arithmetic. (`transaction_count_7d` then fails legitimately: one of five values, 150, is outside `[0, 100]`.)
6. **Uniqueness compares distinct against total.** `expectColumnValuesUnique` counts non-null distinct values and compares to the non-null total — `user_id` passes 5/5.
7. **Distribution check is KL divergence over expected categories.** `expectColumnValueDistribution` iterates the expected map, computes each category's observed probability, and accumulates `actualP * ln(actualP / expectedP)`. For `risk_tier` — low 0.4, medium 0.4, high 0.2 observed vs the same expected — the divergence is exactly 0.0, passing the 0.5 threshold.
8. **The report is the interface.** `printReport` prints the count, `Passed: 8 / 11`, then every result line, then the verdict `✓ Critical threshold: SOME FAILED`. `allPassed()` is the boolean the pipeline consumes — the CI/CD lab wires it as a stage gate before training.
9. **Verify by running.** The expected output below is captured from the actual compiled run — the three failures are the nonexistent column, the age null ratio, and the transaction count range, nothing else.

### Code

```java
package com.mlops.lab09;

import java.util.*;

public class DataValidationWalkthrough {

    static class ExpectationResult {
        final String expectation;
        final boolean passed;
        final double observed;
        final double threshold;
        final String details;

        ExpectationResult(String expectation, boolean passed, double observed,
                           double threshold, String details) {
            this.expectation = expectation;
            this.passed = passed;
            this.observed = observed;
            this.threshold = threshold;
            this.details = details;
        }

        String toMarkdown() {
            String icon = passed ? "✓" : "✗";
            return String.format("  %s %s (observed=%.2f, threshold=%.2f) %s",
                    icon, expectation, observed, threshold, details);
        }
    }

    static class Dataset {
        final String name;
        final Map<String, List<Object>> columns = new LinkedHashMap<>();
        int rowCount;

        Dataset(String name) { this.name = name; }

        void addColumn(String name, Object... values) {
            columns.put(name, new ArrayList<>(Arrays.asList(values)));
            rowCount = Math.max(rowCount, values.length);
        }

        <T> List<T> getColumn(String name) {
            @SuppressWarnings("unchecked")
            List<T> col = (List<T>) columns.get(name);
            return col;
        }
    }

    static class DataValidator {
        private final List<ExpectationResult> results = new ArrayList<>();

        void expectColumnToExist(Dataset ds, String column) {
            boolean exists = ds.columns.containsKey(column);
            results.add(new ExpectationResult(
                    "expect_column_to_exist: " + column,
                    exists, exists ? 1.0 : 0.0, 1.0, ""));
        }

        void expectColumnNullRatioLessThan(Dataset ds, String column, double maxNullRatio) {
            List<Object> col = ds.getColumn(column);
            if (col == null) {
                results.add(new ExpectationResult(
                        "expect_column_null_ratio: " + column,
                        false, 1.0, maxNullRatio, "Column not found"));
                return;
            }
            long nullCount = col.stream().filter(Objects::isNull).count();
            double nullRatio = (double) nullCount / col.size();
            results.add(new ExpectationResult(
                    "expect_column_null_ratio_less_than: " + column,
                    nullRatio <= maxNullRatio, nullRatio, maxNullRatio,
                    String.format("(%d/%d null)", nullCount, col.size())));
        }

        void expectColumnValuesBetween(Dataset ds, String column, Number min, Number max) {
            List<Number> col = ds.getColumn(column);
            if (col == null) {
                results.add(new ExpectationResult(
                        "expect_column_values_between: " + column,
                        false, 0, 1, "Column not found"));
                return;
            }
            double minD = min.doubleValue();
            double maxD = max.doubleValue();
            long outOfRange = col.stream()
                    .filter(Objects::nonNull)
                    .filter(v -> v.doubleValue() < minD || v.doubleValue() > maxD)
                    .count();
            double violationRatio = (double) outOfRange / col.size();
            results.add(new ExpectationResult(
                    "expect_column_values_between: " + column,
                    violationRatio == 0, violationRatio, 0,
                    String.format("(%d/%d out of [%.1f, %.1f])",
                            outOfRange, col.size(), minD, maxD)));
        }

        void expectColumnValuesUnique(Dataset ds, String column) {
            List<Object> col = ds.getColumn(column);
            if (col == null) return;
            long uniqueCount = col.stream().filter(Objects::nonNull).distinct().count();
            boolean allUnique = uniqueCount == col.stream().filter(Objects::nonNull).count();
            results.add(new ExpectationResult(
                    "expect_column_values_unique: " + column,
                    allUnique, uniqueCount, col.size(), ""));
        }

        void expectColumnValueDistribution(Dataset ds, String column,
                                            Map<Object, Double> expectedDistribution,
                                            double maxKLDivergence) {
            List<Object> col = ds.getColumn(column);
            if (col == null) return;
            long total = col.stream().filter(Objects::nonNull).count();
            if (total == 0) return;
            double klDiv = 0.0;
            for (Map.Entry<Object, Double> entry : expectedDistribution.entrySet()) {
                long actualCount = col.stream().filter(v -> entry.getKey().equals(v)).count();
                double actualP = (double) actualCount / total;
                double expectedP = entry.getValue();
                if (actualP > 0 && expectedP > 0) {
                    klDiv += actualP * Math.log(actualP / expectedP);
                }
            }
            results.add(new ExpectationResult(
                    "expect_column_distribution_kl_divergence: " + column,
                    klDiv <= maxKLDivergence, klDiv, maxKLDivergence, ""));
        }

        void printReport() {
            System.out.printf("Data Validation Report: %d expectations run%n", results.size());
            int passed = (int) results.stream().filter(r -> r.passed).count();
            System.out.printf("Passed: %d / %d%n%n", passed, results.size());
            for (ExpectationResult r : results) {
                System.out.println(r.toMarkdown());
            }
            System.out.printf("%n✓ Critical threshold: %s%n",
                    passed == results.size() ? "ALL PASSED" : "SOME FAILED");
        }

        boolean allPassed() {
            return results.stream().allMatch(r -> r.passed);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Data Validation & Quality ===\n");

        Dataset ds = new Dataset("customer_features");
        ds.addColumn("user_id", "u1", "u2", "u3", "u4", "u5");
        ds.addColumn("age", 25, 34, 45, null, 28);
        ds.addColumn("income", 55000, 72000, 95000, 48000, 120000);
        ds.addColumn("credit_score", 720, 680, 750, 710, 600);
        ds.addColumn("risk_tier", "low", "medium", "low", "high", "medium");
        ds.addColumn("transaction_count_7d", 12, 5, 25, 8, 150);

        DataValidator validator = new DataValidator();

        validator.expectColumnToExist(ds, "user_id");
        validator.expectColumnToExist(ds, "age");
        validator.expectColumnToExist(ds, "income");
        validator.expectColumnToExist(ds, "nonexistent_column");

        validator.expectColumnNullRatioLessThan(ds, "age", 0.05);
        validator.expectColumnNullRatioLessThan(ds, "user_id", 0.0);

        validator.expectColumnValuesBetween(ds, "age", 18, 100);
        validator.expectColumnValuesBetween(ds, "credit_score", 300, 850);
        validator.expectColumnValuesBetween(ds, "transaction_count_7d", 0, 100);

        validator.expectColumnValuesUnique(ds, "user_id");

        Map<Object, Double> riskDistribution = Map.of(
                "low", 0.4, "medium", 0.4, "high", 0.2);
        validator.expectColumnValueDistribution(ds, "risk_tier", riskDistribution, 0.5);

        System.out.println("Validating dataset: " + ds.name);
        System.out.printf("Columns: %s, Rows: %d%n%n", ds.columns.keySet(), ds.rowCount);
        validator.printReport();

        System.out.printf("%nValidation %s%n",
                validator.allPassed() ? "PASSED ✓" : "FAILED — check report above");
    }
}
```

### Expected Output

```
=== Data Validation & Quality ===

Validating dataset: customer_features
Columns: [user_id, age, income, credit_score, risk_tier, transaction_count_7d], Rows: 5

Data Validation Report: 11 expectations run
Passed: 8 / 11

  ✓ expect_column_to_exist: user_id (observed=1.00, threshold=1.00)
  ✓ expect_column_to_exist: age (observed=1.00, threshold=1.00)
  ✓ expect_column_to_exist: income (observed=1.00, threshold=1.00)
  ✗ expect_column_to_exist: nonexistent_column (observed=0.00, threshold=1.00)
  ✗ expect_column_null_ratio_less_than: age (observed=0.20, threshold=0.05) (1/5 null)
  ✓ expect_column_null_ratio_less_than: user_id (observed=0.00, threshold=0.00) (0/5 null)
  ✓ expect_column_values_between: age (observed=0.00, threshold=0.00) (0/5 out of [18.0, 100.0])
  ✓ expect_column_values_between: credit_score (observed=0.00, threshold=0.00) (0/5 out of [300.0, 850.0])
  ✗ expect_column_values_between: transaction_count_7d (observed=0.20, threshold=0.00) (1/5 out of [0.0, 100.0])
  ✓ expect_column_values_unique: user_id (observed=5.00, threshold=5.00)
  ✓ expect_column_distribution_kl_divergence: risk_tier (observed=0.00, threshold=0.50)

✓ Critical threshold: SOME FAILED

Validation FAILED — check report above
```

*(The lab's original `expectColumnValuesBetween` crashes with `IllegalFormatConversionException: f != java.lang.Integer` on Java 21+ because `%.1f` receives the raw `Number` argument; this walkthrough normalizes with `min.doubleValue()` / `max.doubleValue()` — the fix is the lesson.)*

## Problem 2: Streaming Session-Events Schema Gate — Company: Duolingo

### The Problem

A Kafka consumer ingests ~2M daily app session events as JSON. A schema change silently renames `streak` to `streak_len`, and the training job that reads the event lake computes features over a now-empty column. Design a pre-training validation for the stream.

### Solution Walkthrough

1. **Validate the sink table, not the raw stream.** The feature table materialized from events is the contract training consumes — run the suite against it daily, mirroring Problem 1's validator.
2. **Existence checks catch the rename immediately.** `expectColumnToExist("streak")` fails with observed 0.00; the report names the missing column and the pipeline stops before feature engineering.
3. **Add null-ratio and range expectations for the features derived from the event:** `expectColumnNullRatioLessThan("streak_len", 0.05)` and `expectColumnValuesBetween("streak", 0, 3650)` — using the `doubleValue()` fix so the range check survives integer bounds.
4. **Distribution check on device type and locale** catches event-lake repartitioning bugs that shift the population without breaking schema — KL divergence over expected category probabilities, threshold 0.10.
5. **Fail the daily batch, alert the owning team, and block training until a human triages** — validation failures during ingestion are cheaper than model rollbacks, so the gate belongs in the batch orchestrator, not the training repo.

## Problem 3: The Stale Expectation Suite — Company: Plaid

### The Problem

A fraud model's training gate has passed every night for six weeks. The team changed the label definition from "confirmed fraud" to "disputed transaction", which tripled the positive rate. The validation report stayed green. Where did the suite fail, and how do you make the failure visible?

### Solution Walkthrough

1. **The suite tested the distribution the team expected — but nobody updated the expectation when the label changed.** `expectColumnValueDistribution` on `label` still declared `positive: 0.02`, while the new data carries `positive: 0.06` — KL divergence of ~0.47 against a threshold of 0.05 should have fired.
2. **The bug is governance, not math:** expectation thresholds drifted out of sync with the contract. The fix is to version the expectation suite with the label definition — a change to the label is a change to the suite, reviewed in the same PR (Lab 11's model-card discipline).
3. **Add the missing checks the suite never had:** `expectColumnToExist("dispute_reported_at")` and a null-ratio check on the new label source column, so a definition change can't silently alter the input schema.
4. **Alert on stagnation:** an expectation that has passed every run for N days without a code change is suspicious — schedule a human review of long-green suites, because a gate nobody ever sees trip is a gate that protects nothing.
