# Data Validation & Quality - Code Deep Dive

**Track:** mlops  |  **Lab:** lab09  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Module Map

```text
src/
  DataValidationLab.java     driver: runs suites against fixtures, reports results
  DataValidator.java        executes expectations, collects all violations
  Expectation.java          named check with severity, threshold and owner
  SchemaContract.java       columns, types, nullability, primary key
  DistributionCheck.java    rank-based shape comparison against a reference sample
  QualityTrend.java         stores results as a trend and reports slope
```

DataValidator collects every violation before reporting, rather than throwing on the first one. An operator debugging an overnight failure needs the whole list, not the first failure.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `DataValidator` | runs a suite and returns a full result, never throwing on the first violation |
| `Expectation` | name, column, predicate, severity, threshold with provenance, owner |
| `SchemaContract` | expected columns, types, nullability, primary key |
| `QualityTrend` | stored results with slope reporting per suite |

---

## 3.1 Suite execution that collects every violation

Operators debug from the whole list at once, and the suite score is computed from all violations rather than short-circuiting.

```java
public ValidationResult run(ValidationSuite suite, Dataset ds) {
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
}
```


---

## 3.2 Rate comparison with a sampling-noise floor

A threshold alone turns normal variation into an alert. Comparing against the reference rate's standard error is what makes it defensible.

```java
public boolean rateRegression(long refViolations, long refRows,
                                long curViolations, long curRows, double z) {
    double pRef = (double) refViolations / refRows;
    double pCur = (double) curViolations / curRows;
    double se = Math.sqrt(pRef * (1 - pRef) / refRows      // SE of the reference rate
                        + pCur * (1 - pCur) / curRows);   // plus SE of the current rate
    if (se == 0) return false;
    double zScore = Math.abs(pCur - pRef) / se;
    return zScore > z;        // only then is the difference more than sampling noise
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Full validation scan | `O(rows x expectations)` | push predicates to the engine |
| Schema check | `O(columns)` | metadata only; effectively free |
| Null and duplicate rates | `O(rows)` | one pass, memory O(distinct keys) |
| Shape comparison | `O(n log n)` | sorting both samples once, reused across features |

## 5. Correctness and Numerics

- Collect all violations, never throw on the first one.
- Compare rates against a sampling-noise floor, not a fixed delta.
- Use BigDecimal or scaled doubles for rate comparisons at 1e-4 granularity.
- Compute thresholds from observed history and store their provenance.
- Make freshness and volume window-aware so seasonality does not alert.

## 6. Test Strategy

- A suite with a known corrupt fixture reports exactly the expected violation counts.
- A rate change within the noise floor does not alert; one beyond it does.
- A blocking expectation stops the pipeline; a warning does not.
- All violations are reported, not just the first.
- A window-aware volume expectation survives a weekly cycle.
- Suite score is comparable across runs and changes when violations change.

## 7. Extension Points

- Push predicates into a query engine so validation runs on 100M rows.
- Add anomaly detection over the suite score series to catch gradual degradation.
- Add a validation summary in the model's metadata so consumers see the data state.

## 8. Review Checklist

- [ ] Every expectation has an owner, a severity and a threshold with provenance
- [ ] Blocking expectations are rare; warnings are routed, not overridden silently
- [ ] Schema, freshness and volume validated before transformations
- [ ] Rate comparisons use a sampling-noise floor
- [ ] All violations reported together
- [ ] Results stored as a trend with slope
