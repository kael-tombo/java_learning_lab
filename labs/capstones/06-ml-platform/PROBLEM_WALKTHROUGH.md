# Problem Walkthrough: ML Platform with Feature Store and Model Registry

## Problem Statement

**Design a machine learning platform that provides a feature store (online + offline), training pipeline orchestration, experiment tracking, model registry with versioning, REST model serving, drift detection, and A/B testing framework.**

The platform must serve 10,000+ features to 100+ models in production, support feature backfilling for historical training, provide sub-10ms online feature serving latency, and track 10,000+ experiments with full reproducibility.

### Business Requirements
- 10,000+ features across 20+ feature groups
- Online feature serving: < 10ms P99 latency
- Feature backfilling for 1-year historical data
- 100+ production models with versioning
- 10,000+ experiments tracked with full parameters and metrics
- Model serving: < 50ms P99 inference latency
- Drift detection (PSI) on 50+ feature distributions
- A/B testing framework with statistical significance testing

### Technical Constraints
- Java 21+ runtime
- Feature store: offline (Parquet/Delta Lake) + online (Redis)
- Model registry: file-based with metadata stored in PostgreSQL
- Training pipeline: configurable DAG with pluggable stages
- Model serving: REST API with pluggable model loaders
- Drift detection: Population Stability Index (PSI)
- A/B testing: t-test / chi-squared for significance

---

## Solution Architecture

### Step 1: Feature Store Design

```java
public class FeatureStore {
    private final OnlineFeatureStore onlineStore;   // Redis-backed
    private final OfflineFeatureStore offlineStore; // Parquet-backed
    private final FeatureRegistry registry;

    public FeatureStore(OnlineFeatureStore online, OfflineFeatureStore offline, FeatureRegistry registry) {
        this.onlineStore = online;
        this.offlineStore = offline;
        this.registry = registry;
    }

    // Online serving (real-time inference)
    public Map<String, Object> getOnlineFeatures(String entityId, List<String> featureNames) {
        Map<String, Object> features = onlineStore.getFeatures(entityId, featureNames);
        if (features.size() < featureNames.size()) {
            // Fallback to offline store for missing features
            List<String> missing = featureNames.stream()
                .filter(f -> !features.containsKey(f)).collect(Collectors.toList());
            Map<String, Object> offlineFeatures = offlineStore.getLatestFeatures(entityId, missing);
            features.putAll(offlineFeatures);
        }
        return features;
    }

    // Offline training data
    public DataFrame getTrainingData(String featureGroup, String entityId,
                                     LocalDate startDate, LocalDate endDate) {
        return offlineStore.getHistoricalFeatures(featureGroup, entityId, startDate, endDate);
    }

    // Feature backfilling
    public void backfillFeatures(String featureGroup, LocalDate startDate, LocalDate endDate) {
        List<FeatureDefinition> features = registry.getFeaturesByGroup(featureGroup);
        for (LocalDate date = startDate; date.isBefore(endDate); date = date.plusDays(1)) {
            LocalDate finalDate = date;
            List<FeatureRow> rows = features.parallelStream()
                .map(f -> computeFeature(f, finalDate))
                .collect(Collectors.toList());
            offlineStore.writeFeatureRows(featureGroup, rows, date);
        }
    }

    // Point-in-time correct join for training
    public DataFrame getPointInTimeTrainingData(String featureGroup, String entityId,
                                                 List<LocalDate> eventTimestamps) {
        return offlineStore.getPointInTimeFeatures(featureGroup, entityId, eventTimestamps);
    }
}

public class OnlineFeatureStore {
    private final RedisCluster redis;

    public void setFeature(String entityId, String featureName, Object value) {
        redis.hset("features:" + entityId, featureName, serialize(value));
        redis.expire("features:" + entityId, Duration.ofHours(24));
    }

    public Map<String, Object> getFeatures(String entityId, List<String> featureNames) {
        return redis.hmget("features:" + entityId, featureNames.toArray(new String[0]))
            .stream().filter(Objects::nonNull)
            .collect(Collectors.toMap(
                entry -> entry.getKey(),
                entry -> deserialize(entry.getValue())));
    }
}

public class OfflineFeatureStore {
    private final String basePath;

    public void writeFeatureRows(String featureGroup, List<FeatureRow> rows, LocalDate date) {
        String path = basePath + "/" + featureGroup + "/dt=" + date.toString();
        // Write as Parquet using DataFrame API
        Dataset<Row> df = session.createDataFrame(rows, FeatureRow.class);
        df.write().mode(SaveMode.Append).parquet(path);
    }

    public DataFrame getHistoricalFeatures(String featureGroup, String entityId,
                                           LocalDate start, LocalDate end) {
        String path = basePath + "/" + featureGroup;
        Dataset<Row> df = session.read().parquet(path);
        return df.filter(col("entity_id").equalTo(entityId))
            .filter(col("dt").between(start.toString(), end.toString()));
    }

    public DataFrame getPointInTimeFeatures(String featureGroup, String entityId,
                                            List<LocalDate> eventTimestamps) {
        // For each event timestamp, get the latest feature value AS OF that timestamp
        // (no future data leakage)
        String path = basePath + "/" + featureGroup;
        Dataset<Row> df = session.read().parquet(path);
        // Implementation: asof join for each event timestamp
        return df.filter(col("entity_id").equalTo(entityId));
    }
}
```

### Step 2: Training Pipeline

```java
public class TrainingPipeline {
    private final List<PipelineStage> stages;
    private final ExperimentTracker experimentTracker;
    private final ModelRegistry modelRegistry;
    private final FeatureStore featureStore;

    public TrainingPipeline(ExperimentTracker tracker, ModelRegistry registry, FeatureStore fs) {
        this.experimentTracker = tracker;
        this.modelRegistry = registry;
        this.featureStore = fs;
        this.stages = new ArrayList<>();
    }

    public TrainingPipeline addStage(PipelineStage stage) {
        stages.add(stage);
        return this;
    }

    public RunResult run(String experimentName, Map<String, Object> parameters) {
        String runId = UUID.randomUUID().toString();
        experimentTracker.createRun(experimentName, runId, parameters);

        PipelineContext ctx = new PipelineContext(runId, parameters);
        try {
            for (PipelineStage stage : stages) {
                long startTime = System.currentTimeMillis();
                ctx = stage.execute(ctx);
                long duration = System.currentTimeMillis() - startTime;

                experimentTracker.logMetric(runId, stage.getName() + "_duration_ms", (double) duration);
                experimentTracker.logParams(runId, ctx.getCurrentParams());
            }

            // Register model if training succeeded
            if (ctx.getModel() != null) {
                String modelVersion = modelRegistry.registerModel(
                    experimentName, ctx.getModel(), ctx.getMetrics());
                experimentTracker.logParam(runId, "model_version", modelVersion);
            }

            experimentTracker.setRunStatus(runId, "COMPLETED");
            experimentTracker.logMetrics(runId, ctx.getMetrics());

            return new RunResult(runId, "COMPLETED", ctx.getMetrics());
        } catch (Exception e) {
            experimentTracker.setRunStatus(runId, "FAILED");
            experimentTracker.logParam(runId, "error", e.getMessage());
            throw new PipelineException("Training failed: " + e.getMessage(), e);
        }
    }
}

public interface PipelineStage {
    String getName();
    PipelineContext execute(PipelineContext ctx);
}

public class DataLoadingStage implements PipelineStage {
    private final FeatureStore featureStore;
    private final String featureGroup;
    private final String entityColumn;
    private final String targetColumn;

    @Override
    public PipelineContext execute(PipelineContext ctx) {
        LocalDate startDate = LocalDate.parse((String) ctx.getParam("start_date"));
        LocalDate endDate = LocalDate.parse((String) ctx.getParam("end_date"));
        List<String> entityIds = (List<String>) ctx.getParam("entity_ids");

        DataFrame trainingData = entityIds.parallelStream()
            .flatMap(id -> featureStore.getPointInTimeTrainingData(
                featureGroup, id, getEventTimestamps(id, startDate, endDate)).stream())
            .collect(Collectors.toList());

        ctx.setAttribute("training_data", trainingData);
        ctx.setAttribute("num_samples", trainingData.size());
        return ctx;
    }
}

public class FeatureEngineeringStage implements PipelineStage {
    @Override
    public PipelineContext execute(PipelineContext ctx) {
        DataFrame data = (DataFrame) ctx.getAttribute("training_data");
        // Feature transformations: scaling, encoding, selection
        // ... processing logic ...
        ctx.setAttribute("processed_data", data);
        return ctx;
    }
}

public class ModelTrainingStage implements PipelineStage {
    @Override
    public PipelineContext execute(PipelineContext ctx) {
        DataFrame data = (DataFrame) ctx.getAttribute("processed_data");
        String modelType = (String) ctx.getParam("model_type");
        Map<String, Object> hyperparams = (Map<String, Object>) ctx.getParam("hyperparameters");

        // Train model based on type
        Model model;
        switch (modelType) {
            case "xgboost":
                model = trainXGBoost(data, hyperparams);
                break;
            case "linear_regression":
                model = trainLinearRegression(data, hyperparams);
                break;
            default:
                throw new IllegalArgumentException("Unknown model type: " + modelType);
        }

        ctx.setModel(model);
        ctx.setMetric("train_rmse", model.evaluate(data));
        return ctx;
    }
}
```

### Step 3: Experiment Tracker

```java
public class ExperimentTracker {
    private final Map<String, ExperimentRun> runs = new ConcurrentHashMap<>();

    public void createRun(String experimentName, String runId, Map<String, Object> params) {
        runs.put(runId, new ExperimentRun(experimentName, runId, params, System.currentTimeMillis()));
    }

    public void logParam(String runId, String key, Object value) {
        ExperimentRun run = runs.get(runId);
        if (run != null) run.getParams().put(key, value);
    }

    public void logMetric(String runId, String key, double value) {
        ExperimentRun run = runs.get(runId);
        if (run != null) {
            run.getMetrics().computeIfAbsent(key, k -> new ArrayList<>()).add(value);
        }
    }

    public void logMetrics(String runId, Map<String, Double> metrics) {
        ExperimentRun run = runs.get(runId);
        if (run != null) metrics.forEach((k, v) -> run.getFinalMetrics().put(k, v));
    }

    public void setRunStatus(String runId, String status) {
        ExperimentRun run = runs.get(runId);
        if (run != null) run.setStatus(status);
    }

    public List<ExperimentRun> getRuns(String experimentName) {
        return runs.values().stream()
            .filter(r -> r.getExperimentName().equals(experimentName))
            .sorted(Comparator.comparingLong(ExperimentRun::getStartTime).reversed())
            .collect(Collectors.toList());
    }

    public ExperimentRun getBestRun(String experimentName, String metricName) {
        return runs.values().stream()
            .filter(r -> r.getExperimentName().equals(experimentName))
            .filter(r -> r.getFinalMetrics().containsKey(metricName))
            .max(Comparator.comparingDouble(r -> r.getFinalMetrics().get(metricName)))
            .orElse(null);
    }

    static class ExperimentRun {
        private final String experimentName;
        private final String runId;
        private final Map<String, Object> params;
        private final Map<String, List<Double>> metrics;
        private final Map<String, Double> finalMetrics;
        private final long startTime;
        private String status = "RUNNING";

        ExperimentRun(String name, String id, Map<String, Object> params, long startTime) {
            this.experimentName = name;
            this.runId = id;
            this.params = new ConcurrentHashMap<>(params);
            this.metrics = new ConcurrentHashMap<>();
            this.finalMetrics = new ConcurrentHashMap<>();
            this.startTime = startTime;
        }
    }
}
```

### Step 4: Model Registry

```java
public class ModelRegistry {
    private final String modelStoragePath;
    private final Map<String, List<ModelVersion>> registry = new ConcurrentHashMap<>();

    public ModelRegistry(String modelStoragePath) {
        this.modelStoragePath = modelStoragePath;
    }

    public String registerModel(String modelName, Model model, Map<String, Double> metrics) {
        List<ModelVersion> versions = registry.computeIfAbsent(modelName, k -> new ArrayList<>());
        int versionNumber = versions.size() + 1;
        String version = "v" + versionNumber;

        // Serialize model to disk
        Path modelPath = Paths.get(modelStoragePath, modelName, version);
        try {
            Files.createDirectories(modelPath);
            model.save(modelPath.toString());
        } catch (IOException e) {
            throw new RuntimeException("Failed to save model", e);
        }

        ModelVersion mv = new ModelVersion(modelName, version, metrics, modelPath.toString(), System.currentTimeMillis());
        versions.add(mv);
        return version;
    }

    public Model loadModel(String modelName, String version) {
        List<ModelVersion> versions = registry.get(modelName);
        if (versions == null) return null;

        ModelVersion mv = versions.stream()
            .filter(v -> v.getVersion().equals(version))
            .findFirst().orElse(null);
        if (mv == null) return null;

        return Model.load(mv.getPath());
    }

    public ModelVersion getLatestModel(String modelName) {
        List<ModelVersion> versions = registry.get(modelName);
        if (versions == null || versions.isEmpty()) return null;
        return versions.get(versions.size() - 1);
    }

    public ModelVersion promoteToProduction(String modelName, String version) {
        ModelVersion mv = getModelVersion(modelName, version);
        if (mv != null) {
            mv.setStage("PRODUCTION");
        }
        return mv;
    }

    public List<ModelVersion> getModelHistory(String modelName) {
        return registry.getOrDefault(modelName, Collections.emptyList());
    }

    static class ModelVersion {
        private final String modelName;
        private final String version;
        private final Map<String, Double> metrics;
        private final String path;
        private final long registeredAt;
        private String stage = "STAGING";

        ModelVersion(String name, String version, Map<String, Double> metrics, String path, long time) {
            this.modelName = name; this.version = version; this.metrics = metrics;
            this.path = path; this.registeredAt = time;
        }
    }
}
```

### Step 5: Model Serving

```java
@RestController
public class ModelServer {
    private final Map<String, Model> loadedModels = new ConcurrentHashMap<>();
    private final ModelRegistry registry;

    @PostMapping("/predict/{modelName}/{version}")
    public PredictionResponse predict(@PathVariable String modelName,
                                      @PathVariable String version,
                                      @RequestBody PredictionRequest request) {
        long startTime = System.nanoTime();

        // Load or get cached model
        Model model = loadedModels.computeIfAbsent(
            modelName + ":" + version,
            k -> registry.loadModel(modelName, version));

        if (model == null) {
            throw new ModelNotFoundException("Model " + modelName + ":" + version + " not found");
        }

        // Get online features
        Map<String, Object> features = featureStore.getOnlineFeatures(
            request.getEntityId(), model.getRequiredFeatures());

        // Predict
        Prediction prediction = model.predict(features);

        long latency = System.nanoTime() - startTime;

        // Log prediction for monitoring
        predictionLogger.log(request.getEntityId(), modelName, version,
            features, prediction, latency);

        return new PredictionResponse(prediction.getValue(), latency / 1_000_000.0);
    }

    @PostMapping("/predict/batch/{modelName}/{version}")
    public List<PredictionResponse> predictBatch(@PathVariable String modelName,
                                                  @PathVariable String version,
                                                  @RequestBody List<PredictionRequest> requests) {
        return requests.parallelStream()
            .map(req -> predict(modelName, version, req))
            .collect(Collectors.toList());
    }
}
```

### Step 6: Drift Detection

```java
public class DriftDetector {

    // Population Stability Index (PSI)
    // PSI = sum((P_i - Q_i) * ln(P_i / Q_i))
    // P_i = proportion in expected distribution (bin i)
    // Q_i = proportion in actual distribution (bin i)
    public double calculatePSI(double[] expected, double[] actual, int numBins) {
        double[] expectedHist = buildHistogram(expected, numBins);
        double[] actualHist = buildHistogram(actual, numBins);

        double psi = 0;
        for (int i = 0; i < numBins; i++) {
            double p = expectedHist[i] / expected.length;
            double q = actualHist[i] / actual.length;

            // Handle zero bins
            if (p == 0) p = 0.0001;
            if (q == 0) q = 0.0001;

            psi += (p - q) * Math.log(p / q);
        }
        return psi;
    }

    private double[] buildHistogram(double[] values, int numBins) {
        double min = Double.MAX_VALUE;
        double max = -Double.MAX_VALUE;
        for (double v : values) {
            min = Math.min(min, v);
            max = Math.max(max, v);
        }

        double binWidth = (max - min) / numBins;
        double[] histogram = new double[numBins];

        for (double v : values) {
            int bin = (int) ((v - min) / binWidth);
            if (bin >= numBins) bin = numBins - 1;
            histogram[bin]++;
        }

        return histogram;
    }

    public DriftReport analyzeDrift(String modelName, String version,
                                     Map<String, double[]> referenceDistributions,
                                     Map<String, double[]> currentDistributions) {
        DriftReport report = new DriftReport(modelName, version);

        for (Map.Entry<String, double[]> entry : referenceDistributions.entrySet()) {
            String featureName = entry.getKey();
            double[] reference = entry.getValue();
            double[] current = currentDistributions.get(featureName);

            if (current == null) continue;

            double psi = calculatePSI(reference, current, 10);
            DriftLevel level;

            if (psi < 0.1) {
                level = DriftLevel.NONE;
            } else if (psi < 0.25) {
                level = DriftLevel.MODERATE;
            } else {
                level = DriftLevel.SEVERE;
            }

            report.addFeatureDrift(featureName, psi, level);
        }

        return report;
    }

    enum DriftLevel { NONE, MODERATE, SEVERE }

    static class DriftReport {
        private final String modelName;
        private final String version;
        private final Map<String, FeatureDrift> drifts = new HashMap<>();
        private DriftLevel overallLevel = DriftLevel.NONE;

        void addFeatureDrift(String feature, double psi, DriftLevel level) {
            drifts.put(feature, new FeatureDrift(feature, psi, level));
            if (level.ordinal() > overallLevel.ordinal()) {
                overallLevel = level;
            }
        }
    }
}
```

### Step 7: A/B Testing

```java
public class ABTestFramework {

    // Assign user to variant based on experiment config
    public String assignVariant(String userId, String experimentName, ABTestConfig config) {
        int hash = (userId + experimentName).hashCode();
        int bucket = Math.abs(hash) % 100;

        int cumulative = 0;
        for (VariantConfig variant : config.getVariants()) {
            cumulative += variant.getAllocationPct();
            if (bucket < cumulative) return variant.getName();
        }
        return config.getVariants().get(0).getName();
    }

    // Two-sample t-test for significance
    public SignificanceResult testSignificance(double[] controlMetrics, double[] treatmentMetrics) {
        double meanControl = mean(controlMetrics);
        double meanTreatment = mean(treatmentMetrics);
        double varControl = variance(controlMetrics, meanControl);
        double varTreatment = variance(treatmentMetrics, meanTreatment);

        int n1 = controlMetrics.length;
        int n2 = treatmentMetrics.length;

        // Welch's t-test (unequal variance)
        double tStatistic = (meanTreatment - meanControl)
            / Math.sqrt(varControl / n1 + varTreatment / n2);

        // Degrees of freedom (Welch-Satterthwaite)
        double df = Math.pow(varControl / n1 + varTreatment / n2, 2)
            / (Math.pow(varControl / n1, 2) / (n1 - 1)
               + Math.pow(varTreatment / n2, 2) / (n2 - 1));

        double pValue = 2 * (1 - cumulativeTDistribution(Math.abs(tStatistic), df));
        boolean significant = pValue < 0.05;

        return new SignificanceResult(meanControl, meanTreatment,
            tStatistic, pValue, significant,
            (meanTreatment - meanControl) / meanControl * 100);
    }

    // Chi-squared test for categorical metrics
    public SignificanceResult testChiSquared(long[][] contingencyTable) {
        int rows = contingencyTable.length;
        int cols = contingencyTable[0].length;

        long[] rowSums = new long[rows];
        long[] colSums = new long[cols];
        long total = 0;

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                rowSums[i] += contingencyTable[i][j];
                colSums[j] += contingencyTable[i][j];
                total += contingencyTable[i][j];
            }
        }

        double chiSquared = 0;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                double expected = (double) rowSums[i] * colSums[j] / total;
                if (expected > 0) {
                    chiSquared += Math.pow(contingencyTable[i][j] - expected, 2) / expected;
                }
            }
        }

        double df = (rows - 1) * (cols - 1);
        double pValue = 1 - chiSquaredCDF(chiSquared, df);
        boolean significant = pValue < 0.05;

        return new SignificanceResult(0, 0, chiSquared, pValue, significant, 0);
    }
}
```

---

## Best Practices

### Feature Store
1. **Online/Offline consistency**: Use the same feature computation code for both online and offline to avoid training-serving skew
2. **Point-in-time correctness**: Training data must use feature values as they existed at the time of the prediction (no future data leakage)
3. **Feature backfilling**: Backfill in chronological order; validate feature distributions match between historical and current data
4. **Feature validation**: Each feature must have a schema (type, range, nullability) and data quality checks before ingestion

### Experiment Tracking
1. **Reproducibility**: Log exact code version (git commit), data version, parameters, environment, and random seed with every run
2. **Parameter vs metric**: Parameters are inputs (hyperparameters, data paths); metrics are outputs (accuracy, latency) — never confuse the two
3. **Nested runs**: Parent run = full pipeline; child runs = individual stages or cross-validation folds for granular tracing

### Model Registry
1. **Versioning scheme**: Semantic versioning (major.minor.patch) or simple incremental (v1, v2, v3); always pin exact version for production
2. **Model lineage**: Each model version must link to the experiment run, training data version, and feature set that produced it
3. **Promotion workflow**: STAGING → CANARY → PRODUCTION; automated validation gates at each stage (accuracy, latency, drift tests)

### Model Serving
1. **Model caching**: Cache loaded models in memory (LRU with max 5 models per node); unload models not accessed in 1 hour
2. **Feature pre-fetching**: For batch predictions, pre-fetch all required features in a single Redis pipeline to reduce round trips
3. **Shadow deployment**: Deploy new model version alongside current production model; compare predictions without serving to users

### Drift Detection
1. **PSI thresholds**: PSI < 0.1 (no drift), 0.1-0.25 (moderate — investigate), > 0.25 (severe — retrain or rollback)
2. **Feature-level monitoring**: Monitor PSI per feature, not just aggregate model score; single feature drift can pinpoint data pipeline issues
3. **Scheduled evaluation**: Run drift detection daily against a fixed reference window (last 30 days of training data)

## Performance Benchmarks

| Component | Latency (P99) | Throughput | Scaling |
|-----------|--------------|------------|---------|
| Online feature get (single) | 5ms | 10K QPS | Redis cluster |
| Online feature get (batch 10) | 8ms | 5K QPS | Redis pipeline |
| Model inference (XGBoost) | 15ms | 3K QPS | Horizontal pods |
| Model inference (NN) | 30ms | 1K QPS | GPU-enabled pods |
| Drift detection (50 features) | 100ms | 10/min | Single-threaded |
| A/B significance test | 20ms | 100/min | Single-threaded |
| Batch prediction (10K rows) | 2s | 5/min | Parallel execution |
