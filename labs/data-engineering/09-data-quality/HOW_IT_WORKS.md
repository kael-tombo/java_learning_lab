# How Data Quality Works

## Quality Check Implementation
`java
public class QualityCheckExecutor {
    private final List<QualityCheck> checks;
    private final MetricsCollector metrics;

    public QualityReport execute(Dataset<Row> data, QualityConfig config) {
        QualityReport report = new QualityReport();

        for (QualityCheck check : checks) {
            try {
                CheckResult result = check.run(data, config);
                report.addResult(result);
                metrics.recordCheck(check.getName(), result.isPassed());
            } catch (Exception e) {
                report.addError(check.getName(), e);
                metrics.recordFailure(check.getName());
            }
        }
        return report;
    }
}
`

## Great Expectations Integration
`java
public class GreatExpectationsRunner {
    public void runExpectations(Dataset<Row> data) {
        // Example: Validate using Great Expectations
        List<Expectation> expectations = Arrays.asList(
            Expectation.expectColumnToExist("customer_id"),
            Expectation.expectColumnValuesToNotBeNull("customer_id"),
            Expectation.expectColumnValuesToBeBetween("amount", 0, 100000),
            Expectation.expectColumnValueLengthsToBeBetween("zip_code", 5, 10)
        );

        for (Expectation exp : expectations) {
            CheckResult result = exp.validate(data);
            if (!result.isPassed()) {
                alertService.sendQualityAlert(result);
            }
        }
    }
}
`

## Deequ Quality Checks
`java
// Amazon Deequ library for Spark
import com.amazon.deequ.checks.Check;
import com.amazon.deequ.checks.CheckLevel;
import com.amazon.deequ.VerificationSuite;

VerificationResult result = VerificationSuite()
    .onData(data)
    .addCheck(
        new Check(CheckLevel.Error, "Data quality checks")
            .isComplete("customer_id")
            .isUnique("order_id")
            .hasSizeBetween(1000, 1000000)
            .hasMin("amount", d -> d > 0)
            .hasMax("amount", d -> d < 100000)
            .containsURL("email", d -> d == 0))
    .run();
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Data Quality Internals

## Quality Check Engine
`java
public abstract class QualityCheck {
    protected final String name;
    protected final String description;
    protected final CheckSeverity severity;

    public abstract CheckResult run(Dataset<Row> data, QualityConfig config);

    protected CheckResult pass(String details) {
        return new CheckResult(name, true, details, Instant.now());
    }

    protected CheckResult fail(String details) {
        metrics.incrementCounter("quality.failure." + name);
        return new CheckResult(name, false, details, Instant.now());
    }
}
`

## Custom Check Implementation
`java
public class ReferentialIntegrityCheck extends QualityCheck {
    private final String factColumn;
    private final String dimensionTable;
    private final String dimColumn;

    @Override
    public CheckResult run(Dataset<Row> factData, QualityConfig config) {
        Dataset<Row> dimData = spark.table(dimensionTable);

        long orphanCount = factData
            .join(dimData, factData.col(factColumn)
                .equalTo(dimData.col(dimColumn)), "left_anti")
            .count();

        double orphanRate = (double) orphanCount / factData.count() * 100;

        if (orphanRate > config.getThreshold()) {
            return fail(String.format(
                "Found %d orphans (%.2f%%) exceeding threshold %.2f%%",
                orphanCount, orphanRate, config.getThreshold() * 100));
        }
        return pass(String.format("Orphan rate: %.2f%%", orphanRate));
    }
}
`

## Anomaly Detection
`java
public class StatisticalAnomalyDetector {
    public List<Anomaly> detect(Dataset<Row> data, String column) {
        // Compute statistics
        double mean = data.agg(avg(col(column))).first().getDouble(0);
        double stddev = data.agg(stddev(col(column))).first().getDouble(0);

        // Z-score based anomaly detection
        Dataset<Row> anomalies = data
            .withColumn("z_score",
                abs(col(column).minus(mean)).divide(stddev))
            .filter(col("z_score").(3.0));

        List<Anomaly> results = new ArrayList<>();
        for (Row row : anomalies.collectAsList()) {
            results.add(new Anomaly(
                row.get(0).toString(), column,
                row.getAs(column), row.getDouble(row.length()-1)));
        }
        return results;
    }
}
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Data Quality

## Statistical Measures
`
Mean = S(xi) / n
StdDev = sqrt(S((xi - mean)^2) / n)
Z-Score = (xi - mean) / stddev
Outlier Threshold: |Z| > 3 (99.7% confidence)

IQR = Q3 - Q1
Outlier: x < Q1 - 1.5*IQR OR x > Q3 + 1.5*IQR
`

## Quality Metrics
`
Completeness = NonNullCount / TotalCount * 100
Uniqueness = DistinctCount / TotalCount * 100
Accuracy = CorrectValues / TotalValues * 100
Timeliness = OnTimeDeliveries / TotalDeliveries * 100
Consistency = MatchedRecords / TotalRecords * 100

Overall DQ Score = WeightedAverage(dimension_scores)
`

## Sampling for Large Data
`
SampleSize = (Z^2 * p * (1-p)) / E^2
Z = 1.96 for 95% confidence
p = expected proportion (0.5 if unknown)
E = margin of error (0.01 = 1%)
`

## Freshness Metrics
`
DataLatency = CurrentTime - LastUpdateTime
PipelineFreshness = Max(SourceLatencies)
SLA Compliance = OnTimeRuns / TotalRuns * 100
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Data Quality

## Quality Check Pipeline
`
Input Data
   |
   v
+----------------+     +----------------+
| Schema Check   |     | Null Check     |
| - Column exists |     | - Non-nullable |
| - Type matches |     | - Null rate    |
+--------+-------+     +-------+--------+
         |                     |
         v                     v
+----------------+     +----------------+     +----------------+
| Range Check    |     | Uniqueness     |     | Format Check   |
| - Min/Max      |     | - No dupes    |     | - Regex match  |
| - Distribution |     | - PK unique   |     | - Pattern val  |
+--------+-------+     +-------+--------+     +-------+--------+
         |                     |                     |
         v                     v                     v
+--------------------------------------------------------+
|                    Quality Report                       |
| Pass: 7/10 | Fail: 3/10 | Score: 70%                   |
| - Schema: PASS                                         |
| - Nulls: PASS (0.1%)                                   |
| - Range: FAIL (negatives found)                        |
| - Uniqueness: PASS                                     |
| - Format: FAIL (invalid emails)                        |
| - Referential: PASS                                    |
+--------------------------------------------------------+
`

## Data Quality Dashboard
`
+---------------------------+---------------------------+
| Overall Quality Score: 87% | Records Checked: 1.2M     |
+---------------------------+---------------------------+
| Dimension    | Score | Trend |                         |
|--------------|-------|-------|                         |
| Completeness | 95%   |   UP  |  [=====               ]|
| Uniqueness   | 99%   |   OK  |  [======              ]|
| Consistency  | 88%   |  DOWN |  [===                 ]|
| Timeliness   | 92%   |   OK  |  [=====               ]|
| Validity     | 85%   |   UP  |  [====                ]|
| Accuracy     | 78%   |   OK  |  [====                ]|
+---------------------------+---------------------------+
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Data Quality Framework

## Complete Quality Validation Framework
`java
@Component
public class DataQualityFramework {

    private final List<QualityRule> rules;
    private final MetricsCollector metrics;
    private final AlertService alertService;

    @Autowired
    public DataQualityFramework(List<QualityRule> rules,
                                 MetricsCollector metrics,
                                 AlertService alertService) {
        this.rules = rules;
        this.metrics = metrics;
        this.alertService = alertService;
    }

    public QualityReport validate(Dataset<Row> data, String datasetName) {
        QualityReport report = new QualityReport(datasetName, Instant.now());
        report.setTotalRecords(data.count());

        for (QualityRule rule : rules) {
            if (rule.appliesTo(datasetName)) {
                RuleResult result = rule.evaluate(data);
                report.addResult(result);

                metrics.gauge("quality." + rule.getName(),
                    result.isPassed() ? 1.0 : 0.0);
                metrics.counter("quality.checks." +
                    (result.isPassed() ? "passed" : "failed")).increment();

                if (!result.isPassed() && rule.getSeverity() == Severity.CRITICAL) {
                    alertService.sendCriticalAlert(datasetName, rule, result);
                }
            }
        }

        report.calculateScore();
        report.setDuration(Duration.between(report.getTimestamp(), Instant.now()));
        return report;
    }
}

@Qualifier("nullCheck")
@Component
class NullCheckRule implements QualityRule {
    @Value("")
    private double nullThreshold;

    @Override
    public boolean appliesTo(String dataset) { return true; }

    @Override
    public RuleResult evaluate(Dataset<Row> data) {
        Map<String, Double> nullRates = new HashMap<>();
        for (String col : data.columns()) {
            long nullCount = data.filter(col(col).isNull()
                .or(col(col).equalTo(""))).count();
            nullRates.put(col, (double) nullCount / data.count());
        }

        List<String> violations = nullRates.entrySet().stream()
            .filter(e -> e.getValue() > nullThreshold)
            .map(e -> String.format("%s: %.2f%% null", e.getKey(), e.getValue() * 100))
            .collect(Collectors.toList());

        String detail = violations.isEmpty() ?
            "All columns within null threshold" :
            String.join("; ", violations);

        return new RuleResult("NullCheck", violations.isEmpty(),
            nullRates, detail, Severity.HIGH);
    }

    @Override
    public Severity getSeverity() { return Severity.HIGH; }
}

@Qualifier("schemaCheck")
@Component
class SchemaCheckRule implements QualityRule {
    @Override
    public RuleResult evaluate(Dataset<Row> data) {
        StructType schema = data.schema();
        List<String> errors = new ArrayList<>();

        // Check required columns exist
        for (String required : Arrays.asList("id", "created_at")) {
            if (Arrays.stream(schema.fieldNames()).noneMatch(required::equals)) {
                errors.add("Missing required column: " + required);
            }
        }

        // Check expected types
        for (StructField field : schema.fields()) {
            if (field.name().endsWith("_id") &&
                !field.dataType().equals(DataTypes.LongType) &&
                !field.dataType().equals(DataTypes.StringType)) {
                errors.add(field.name() + " should be LongType or StringType");
            }
        }

        return new RuleResult("SchemaCheck", errors.isEmpty(),
            schema, String.join("; ", errors), Severity.CRITICAL);
    }
}
`

## Integration with Data Pipeline
`java
@Component
public class QualityPipelineIntegration {
    private final DataQualityFramework quality;

    @EventListener
    public void onPipelineComplete(PipelineCompleteEvent event) {
        Dataset<Row> output = spark.read()
            .format(event.getOutputFormat())
            .load(event.getOutputPath());

        QualityReport report = quality.validate(output, event.getPipelineName());

        if (report.getScore() < event.getQualityThreshold()) {
            event.setStatus(PipelineStatus.QUALITY_FAILED);
            quality.alertService.sendPipelineQualityAlert(event, report);
        } else {
            log.info("Pipeline {} passed quality checks (score: {})",
                event.getPipelineName(), report.getScore());
        }
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Data Quality Implementation

## Step 1: Define Quality Rules
`java
// Define rules for each dataset
QualityConfig config = QualityConfig.builder()
    .dataset("customers")
    .addRule(NotNull("customer_id"))
    .addRule(Unique("email"))
    .addRule(Range("age", 0, 150))
    .addRule(Regex("phone", "\\d{10}"))
    .build();
`

## Step 2: Set Thresholds
`properties
# quality.properties
quality.null.threshold=0.05
quality.duplicate.threshold=0.001
quality.range.outlier.threshold=0.01
quality.freshness.hours=24
`

## Step 3: Implement Check Runner
`java
@Component
public class ScheduledQualityRunner {
    @Scheduled(cron = "0 0 * * * ?") // Every hour
    public void runAllQualityChecks() {
        for (String dataset : qualityConfig.getDatasets()) {
            Dataset<Row> data = spark.table(dataset);
            QualityReport report = framework.validate(data, dataset);
            reportStore.save(report);
        }
    }
}
`

## Step 4: Set Up Alerts
`java
@Component
public class QualityAlertHandler {
    @EventListener
    public void onQualityFailure(QualityFailureEvent event) {
        if (event.getSeverity() == Severity.CRITICAL) {
            pagerDuty.trigger(event);
        } else {
            slack.sendMessage("#data-quality", event.formatMessage());
        }
    }
}
`

## Step 5: Monitor Dashboard
`java
@RestController
@RequestMapping("/api/quality")
public class QualityDashboard {
    @GetMapping("/score/{dataset}")
    public ResponseEntity<QualityScore> getScore(@PathVariable String dataset) {
        return ResponseEntity.ok(reportStore.getLatestScore(dataset));
    }

    @GetMapping("/trend/{dataset}/{days}")
    public ResponseEntity<List<QualityScore>> getTrend(
            @PathVariable String dataset, @PathVariable int days) {
        return ResponseEntity.ok(reportStore.getTrend(dataset, days));
    }
}
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Data Quality Mistakes

## 1. Checking Quality Only at the End
`java
// WRONG - check only at load time
data.write().save();
qualityCheck(data);

// RIGHT - check at every stage
Dataset<Row> bronze = extract(source);
validateBronze(bronze);
Dataset<Row> silver = transform(bronze);
validateSilver(silver);
Dataset<Row> gold = aggregate(silver);
validateGold(gold);
`

## 2. Not Handling Empty DataFrames
`java
// WRONG - fails on empty data
data.groupBy("col").count().show();

// RIGHT - check for empty
if (data.isEmpty()) {
    log.warn("Empty dataset skipped");
    return QualityReport.empty();
}
`

## 3. Thresholds Too Strict or Loose
`java
// WRONG - not configurable
if (nullRate > 0.01) fail();

// RIGHT - configurable thresholds
@Value("")
private double nullThreshold;
`

## 4. Not Monitoring Trends
`java
// WRONG - check each run independently
// Fix: Track metric trends over time
// Alert on: 10% degradation over 7 days
// Alert on: 3 consecutive failures
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Data Quality Issues

## Common Failure Patterns

### High Null Rate After Schema Change
`java
// Source added new columns
// Check for schema drift
Dataset<Row> sourceSchema = spark.read().json(sourcePath);
sourceSchema.schema().printTreeString();
`

### Data Duplication After Pipeline Restart
`java
// Check for duplicate batches
data.groupBy("batch_id")
    .count()
    .filter(col("count").(1))
    .show();
`

### Referential Integrity Failures
`java
// Find orphan records
data.join(dimTable, "key", "left_anti")
    .groupBy("source")
    .count()
    .show();
`

### Freshness Issues
`java
// Check max timestamp
data.agg(max("updated_at")).show();
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Data Quality

## Before: Ad-hoc Checks
`java
// Scattered quality checks
if (data.filter(col("id").isNull()).count() > 100) { alert(); }
if (!data.schema().fieldNames().contains("email")) { alert(); }
`

## After: Unified Framework
`java
QualityReport report = framework.validate(data, "customers");
if (!report.isPassed()) { alert(report); }
`

## Before: Hardcoded Rules
`java
// Rule embedded in pipeline code
`

## After: Declarative Configuration
`yaml
# quality-rules.yaml
customers:
  rules:
    - type: NOT_NULL
      columns: [customer_id, email]
    - type: UNIQUE
      columns: [customer_id]
    - type: RANGE
      column: age
      min: 0
      max: 120
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Data Quality Performance

## Efficient Checks on Large Data
`java
// Sampling for large datasets
Dataset<Row> sample = data.sample(false, 0.01); // 1% sample
qualityChecks(sample);

// Approximate distinct counts for speed
data.agg(approx_count_distinct(col("id"))).show();

// Use summary statistics
data.describe().show();
`

## Incremental Quality Checks
`java
// Only check new/changed data
Dataset<Row> incremental = data.filter(
    col("etl_loaded_at").(lastCheckTime));
qualityChecks(incremental);
`

## Parallel Check Execution
`java
ExecutorService pool = Executors.newFixedThreadPool(4);
List<Future<CheckResult>> futures = rules.stream()
    .map(rule -> pool.submit(() -> rule.evaluate(data)))
    .collect(Collectors.toList());
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Data Quality Security

## Sensitive Data Handling
`java
// Never expose PII in quality alerts
public class SafeQualityCheck {
    public CheckResult checkEmails(Dataset<Row> data) {
        long invalidCount = data.filter(
            col("email").isNotNull()
                .and(not(col("email").rlike("^[A-Za-z0-9+_.-]+@(.+)$"))))
            .count();

        // Don't include the actual invalid emails in alert
        if (invalidCount > 0) {
            return fail(String.format("Found %d invalid emails", invalidCount));
        }
        return pass();
    }
}
`

## Access Control
`java
@PreAuthorize("hasRole('DATA_QUALITY_ADMIN')")
public void updateQualityThresholds(QualityConfig config) { ... }

@PreAuthorize("hasRole('DATA_ENGINEER')")
public QualityReport viewReport(String dataset) { ... }
`

## Audit Trail
`java
@Entity
public class QualityAudit {
    @Id private Long id;
    private String dataset;
    private String rule;
    private boolean passed;
    private String details;
    private String executedBy;
    private Instant executedAt;
}
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Data Quality Architecture

## Quality Platform Architecture
`
+------------------------------------------------------+
|                   Data Quality Platform               |
+----------+---------+----------+----------+-----------+
| Quality  | Schema  | Anomaly  | Metrics  | Alerting  |
| Rules    | Checks  | Detect   | Store    | Service   |
+----------+---------+----------+----------+-----------+
|                  Rule Engine                         |
|      Executes checks, collects results               |
+------------------------------------------------------+
|               Data Sources                           |
|  Bronze   | Silver   | Gold    | Streams             |
+------------------------------------------------------+
`

## Spring Boot Integration
`java
@SpringBootApplication
@EnableScheduling
@EnableConfigurationProperties(QualityProperties.class)
public class DataQualityApplication {
    public static void main(String[] args) {
        SpringApplication.run(DataQualityApplication.class, args);
    }
}
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Data Quality Exercises

## Exercise 1: Basic Quality Checks
Implement checks for nulls, duplicates, and type validation on a dataset.

## Exercise 2: Anomaly Detection
Build a statistical anomaly detector using z-scores.

## Exercise 3: Schema Evolution
Implement schema drift detection and auto-remediation.

## Exercise 4: Quality Dashboard
Create a REST API that returns quality metrics and trends.

## Exercise 5: Streaming Quality
Implement real-time quality validation on a Kafka stream.
