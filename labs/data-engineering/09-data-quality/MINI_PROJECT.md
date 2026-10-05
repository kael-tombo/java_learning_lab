# Data Quality (Foundations) — MINI PROJECT

## Project: Expectation Engine + Profiler + Quarantine

A small data-quality layer: a schema registry, a composable expectation
library, a statistical profiler, and a quarantine path with severity routing.

### Scope
- `Expectation` interface with `ExpectationResult` (success, observed, expectation).
- Built-ins: not-null, in-range, in-set, unique, row-count-between, referential,
  regex, monotonic timestamp, no-negative-amount.
- `DataProfiler`: per column — null rate, distinct count, min/max/mean/stddev, top-k.
- `QualityGate`: runs expectations, routes failures to quarantine or to fail.
- Drift detection: compare today's profile to a 14-day baseline (PSI-ish).

### Architecture

```
source rows
   |
[DataProfiler] -> profile snapshot (per column stats) ----> baseline store (14d)
   |
[QualityGate]
   |-- BLOCK  -> quarantine table + fail run
   |-- WARN   -> log + metric, continue
   |-- INFO   -> record only
   v
load target
```

### Implementation

```java
public sealed interface Expectation permits NotNull, InRange, InSet, Unique,
        RowCountBetween, Referential, RegexMatch, NonNegative, MonotonicTimestamp {}

public record Result(boolean success, Object observed, Object expected,
                     Severity severity, String message) {
    public static Result ok(Object observed) {
        return new Result(true, observed, null, Severity.INFO, "");
    }
    public static Result fail(Object observed, Object expected,
                              Severity sev, String msg) {
        return new Result(false, observed, expected, sev, msg);
    }
}

@FunctionalInterface
public interface Check extends Serializable {
    Result apply(Row row, int rowIndex);
}

public record NotNull(String column, Severity severity) implements Check {
    @Override public Result apply(Row row, int i) {
        Object v = row.get(column);
        return v == null || String.valueOf(v).isBlank()
                ? Result.fail(null, "not null", severity, "null in " + column + " row " + i)
                : Result.ok(v);
    }
}
```

### Profiler

```java
public record ColumnProfile(String column, long count, long nulls, long distinct,
                            double min, double max, double mean, double stddev,
                            Map<String, Long> topValues) {
    public double nullRate() { return count == 0 ? 1.0 : (double) nulls / count; }
}

public final class DataProfiler {
    public List<ColumnProfile> profile(List<Row> rows, List<String> columns) {
        Map<String, ColumnStats> acc = new LinkedHashMap<>();
        for (String c : columns) acc.put(c, new ColumnStats(c));
        for (Row r : rows) for (String c : columns) acc.get(c).accept(r.get(c));
        return acc.values().stream().map(ColumnStats::toProfile).toList();
    }
}

static final class ColumnStats {
    long count, nulls; Set<Object> seen = new HashSet<>();
    double sum, sumSq, min = Double.POSITIVE_INFINITY, max = Double.NEGATIVE_INFINITY;
    Map<String, Long> top = new HashMap<>();

    void accept(Object raw) {
        count++;
        if (raw == null) { nulls++; return; }
        seen.add(raw);
        if (raw instanceof Number n) {
            double d = n.doubleValue();
            sum += d; sumSq += d * d;
            min = Math.min(min, d); max = Math.max(max, d);
        }
        top.merge(String.valueOf(raw), 1L, Long::sum);
    }

    ColumnProfile toProfile() {
        double mean = count == 0 ? 0 : sum / count;
        double var = count < 2 ? 0 : Math.max(0, sumSq / count - mean * mean);
        return new ColumnProfile(name, count, nulls, seen.size(), min, max,
                mean, Math.sqrt(var), topK(top, 5));
    }
}
```

### Drift detection

```java
/** Population Stability Index over bucketed numeric distributions. */
public record PsiWarning(String column, double psi, Severity severity) {}

public final class DriftDetector {
    static final List<Double> BUCKETS = List.of(-1d, 0d, 10d, 50d, 100d, 500d, 1_000d,
                                                5_000d, 10_000d, Double.MAX_VALUE);

    public static double psi(double[] expectedFractions, double[] actualFractions) {
        double psi = 0;
        for (int i = 0; i < expectedFractions.length; i++) {
            double e = Math.max(expectedFractions[i], 1e-6);
            double a = Math.max(actualFractions[i], 1e-6);
            psi += (a - e) * Math.log(a / e);
        }
        return psi;
    }

    public List<PsiWarning> compare(List<ColumnProfile> baseline, List<ColumnProfile> today) {
        List<PsiWarning> out = new ArrayList<>();
        for (ColumnProfile b : baseline) {
            ColumnProfile t = find(today, b.column());
            if (t == null) continue;
            double psi = psi(bucketFractions(b), bucketFractions(t));
            // PSI < 0.1 stable, 0.1-0.25 moderate shift, > 0.25 significant.
            if (psi > 0.25) out.add(new PsiWarning(b.column(), psi, Severity.BLOCK));
            else if (psi > 0.10) out.add(new PsiWarning(b.column(), psi, Severity.WARN));
        }
        return out;
    }
}
```

### Gate with quarantine

```java
public final class QualityGate {
    private final List<Check> checks;
    private final SqlSink quarantine;

    public GateReport run(List<Row> rows) {
        List<Row> rejected = new ArrayList<>();
        Map<String, Integer> failuresByColumn = new HashMap<>();
        Severity worst = Severity.INFO;

        for (int i = 0; i < rows.size(); i++) {
            Row r = rows.get(i);
            Severity rowWorst = Severity.INFO;
            List<String> reasons = new ArrayList<>();
            for (Check c : checks) {
                Result res = c.apply(r, i);
                if (res.success()) continue;
                reasons.add(res.message());
                failuresByColumn.merge(columnOf(res.message()), 1, Integer::sum);
                rowWorst = max(rowWorst, res.severity());
            }
            if (!reasons.isEmpty() && rowWorst == Severity.BLOCK) {
                rejected.add(r.withMeta(String.join("; ", reasons)));
            }
            worst = max(worst, rowWorst);
        }
        if (!rejected.isEmpty()) quarantine.write("orders_quarantine", rejected);
        return new GateReport(rows.size() - rejected.size(), rejected.size(), worst, failuresByColumn);
    }
}
```

### Test It

```java
@Test void detectsNullInjection() {
    List<Row> today = load();
    List<Row> poisoned = new ArrayList<>(today);
    poisoned.get(42).put("amount", null);                 // inject one bad row
    assertFalse(new NotNull("amount", Severity.BLOCK).apply(poisoned.get(42), 42).success());
    assertTrue(new NotNull("amount", Severity.BLOCK).apply(today.get(42), 42).success());
}

@Test void detectsDistributionDrift() {
    List<Row> shifted = load().stream().map(r -> r.withField("amount", r.amount() * 12)).toList();
    assertTrue(new DriftDetector().compare(profile(load()), profile(shifted)).size() > 0);
}
```

### Stretch
- Add cross-table checks: `fact.total == dim-decomposed total` within tolerance.
- Route quarantined rows to a topic and build a reprocessing loop with a human gate.
- Emit a quality score per table: `1 - failed_expectations / total_expectations`.

## Deliverables
- [ ] Expectation library covering 5 quality dimensions
- [ ] Profiler with per-column statistics
- [ ] Drift detector with PSI thresholds and severity
- [ ] Gate with quarantine and a per-column failure report
- [ ] Tests for null injection, range violation, and drift
