# Technical Architecture: ML Platform

## Architecture Overview

```
[Feature Pipeline]          [Training Pipeline]          [Serving Pipeline]
       |                           |                           |
+--------------+         +------------------+         +------------------+
| Feature      |         | Data Loading     |         | Model Server     |
| Computation  +-------->+ Feature Eng.     +-------->+ Feature Store    |
+--------------+         | Model Training   |         | (Online)         |
       |                 | Validation       |         +--------+---------+
+--------------+         +--------+---------+                  |
| Offline      |                  |                           |
| Feature Store|         +--------v---------+         +--------v---------+
| (Parquet)    |         | Experiment       |         | Prediction       |
+--------------+         | Tracker          |         | Logger           |
       |                 +--------+---------+         +--------+---------+
+--------------+                  |                           |
| Online       |         +--------v---------+         +--------v---------+
| Feature Store|         | Model Registry   |         | Drift Detector   |
| (Redis)      |         |                  |         | A/B Test         |
+--------------+         +------------------+         +------------------+
```

## Component Breakdown

### 1. Feature Store
- **Offline store**: Parquet files partitioned by date (dt=YYYY-MM-DD) in data lake (S3/ADLS)
- **Online store**: Redis hashes (key: "features:{entity_id}", field: feature_name, value: serialized)
- **Feature registry**: PostgreSQL table with feature definitions (name, type, source, owner, freshness SLA)
- **Point-in-time join**: Spark-based as-of join for training data; uses window function with ORDER BY timestamp
- **Freshness**: Online store TTL = 24 hours; offline store retains 2 years of historical data

### 2. Training Pipeline
- **DAG structure**: Configurable stages via PipelineStage interface; stages run sequentially with checkpointing
- **Typical stages**: DataLoading → FeatureEngineering → TrainTestSplit → ModelTraining → Evaluation → Registration
- **Hyperparameter tuning**: Grid search or Bayesian optimization as a pipeline stage; parallel trials across worker pool
- **Data versioning**: Training data snapshot hash logged with experiment; enables exact reproducibility

### 3. Experiment Tracker
- **Storage**: In-memory ConcurrentHashMap for current session; persisted to PostgreSQL for long-term storage
- **Run structure**: experiment_name / run_id / params / metrics (time series) / final_metrics / artifacts
- **Query API**: List runs by experiment, get best run by metric, compare runs in parallel (side-by-side table)
- **Integration**: Model registry pulls from experiment tracker; each registered model links to its training run

### 4. Model Registry
- **Storage**: File system (models/{name}/{version}/model.bin) + PostgreSQL metadata table
- **Versions**: Auto-incrementing (v1, v2, v3); each version stores: metrics, feature set, training run ID, timestamp
- **Stages**: NONE → STAGING → CANARY → PRODUCTION → ARCHIVED; only one model per name can be in PRODUCTION
- **Validation gates**: On promote to PRODUCTION: accuracy check (metrics >= previous), latency test, drift test against reference

### 5. Model Server
- **Framework**: Spring Boot REST controller with /predict/{name}/{version} and /predict/batch endpoints
- **Model loading**: Lazy loading on first request; cached in ConcurrentHashMap with LRU eviction (max 5 models per node)
- **Feature integration**: Server calls FeatureStore.getOnlineFeatures for each prediction request
- **Prediction logging**: Async logger writes to Kafka topic for drift monitoring and A/B analysis
- **Health check**: /health/readiness checks model loaded + feature store connectivity

### 6. Drift Detector
- **Schedule**: Runs every 6 hours against rolling 7-day window of prediction data vs fixed 30-day reference window
- **Metrics**: PSI for numerical features, Chi-squared test for categorical features
- **Alerting**: SEVERE drift triggers PagerDuty alert; MODERATE drift creates JIRA ticket for investigation
- **Auto-remediation**: If overall drift > 0.25 for 3 consecutive checks, auto-rollback to previous PRODUCTION model version

### 7. A/B Test Framework
- **Assignment**: Hash-based (userId + experimentName) modulo 100 for deterministic, sticky assignment
- **Variants**: Control (current model) vs Treatment (candidate model); can support multi-variant (A/B/C)
- **Metrics**: Primary (revenue, CTR), Secondary (latency, error rate), Guardrail (drift, data quality)
- **Significance**: Welch's t-test for continuous metrics; Chi-squared for categorical; minimum p < 0.05 for significance
- **Minimum runtime**: 7 days or 10,000 samples per variant, whichever is later; no early stopping

## Data Flow

### Training Run
```
1. Data Scientist: configure experiment yaml (features, model_type, hyperparameters)
2. TrainingPipeline.run("fraud-detection-v3", params)
3. ExperimentTracker.createRun(name, runId, params)
4. DataLoadingStage: read training data from OfflineFeatureStore (point-in-time correct)
5. FeatureEngineeringStage: transform, scale, encode, split train/test
6. ModelTrainingStage: train model, evaluate on test set
7. ExperimentTracker.logMetrics(runId, {"auc": 0.89, "f1": 0.82})
8. ModelRegistry.registerModel("fraud-detection", model, {"auc": 0.89, "f1": 0.82})
9. ExperimentTracker.setRunStatus(runId, "COMPLETED")
```

### Online Serving
```
1. Client: POST /predict/fraud-detection/v4 {"entity_id": "user_123", "features": [...]}
2. ModelServer: load model "fraud-detection:v4" (cached or from registry)
3. FeatureStore.getOnlineFeatures("user_123", ["avg_transaction_amount", "txn_velocity_1h", ...])
4. Redis: HMGET features:user_123 avg_transaction_amount txn_velocity_1h
5. Model.predict(features) -> 0.97 (fraud probability: 97%)
6. PredictionLogger: async log prediction + features to Kafka topic
7. Response: {"prediction": 0.97, "latency_ms": 12.3}
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Java 21 | Runtime |
| Framework | Spring Boot 3.2 | REST serving |
| Feature store (online) | Redis 7 | Low-latency serving |
| Feature store (offline) | Apache Parquet + Spark | Historical data |
| Pipeline orchestration | Custom DAG | Training workflows |
| Experiment tracking | Custom + PostgreSQL | Run metadata |
| Model registry | Filesystem + PostgreSQL | Model artifacts |
| Drift detection | Custom (PSI) | Distribution monitoring |
| A/B testing | Custom (t-test, chi-sq) | Statistical testing |
| Metrics | Micrometer + Prometheus | Observability |

## Deployment Topology

```
Training (Kubernetes Batch Jobs):
  - Spark driver pod (1 CPU, 4GB RAM)
  - Spark executor pods (10 CPU, 16GB RAM each)
  - Feature backfill cron job (daily, off-peak)

Serving (Kubernetes Deployments):
  - Model server pods: 5 replicas, HPA (CPU > 70%)
  - Feature store: Redis Cluster (6 pods, 3 masters, 3 replicas)
  - Drift detector: Single pod (scheduled every 6h)
  - Prediction logger: Kafka topic (3 brokers, 6 partitions)
```

## Security

- **Model access control**: Read-only API for serving; write API requires auth token (model registration)
- **Feature store ACL**: Online store accessible only from model server pods (network policy)
- **Training data access**: Spark jobs run with service account; data lake paths restricted by IAM
- **Audit trail**: All model promotions logged; approved version must be reviewed by peer
