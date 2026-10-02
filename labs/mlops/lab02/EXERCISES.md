# Experiment Tracking with MLflow — Exercises

**Prerequisites:** Python 3.x with `mlflow`, `scikit-learn`, `pandas`. MLflow server: `mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts`. Java 21+ for lab's Java client.

---

## Exercise 1: Basic Tracking API

**Objective:** Log parameters, metrics, artifacts from a training script.

**Tasks:**
1. Start MLflow server locally. Set tracking URI: `mlflow.set_tracking_uri("http://localhost:5000")`.
2. Create experiment: `mlflow.set_experiment("exercise-1-basic")`.
3. Write training script that:
   - Loads a dataset (e.g., Wine, Breast Cancer, or synthetic)
   - Logs params: model_type, hyperparameters, dataset info
   - Trains model (sklearn: LogisticRegression, RandomForest)
   - Logs metrics: accuracy, f1, roc_auc (test set)
   - Logs model: `mlflow.sklearn.log_model(model, "model")`
   - Logs artifact: confusion matrix plot (save fig, `mlflow.log_artifact`)
   - Logs tags: `git_commit`, `user`, `dataset_version`
4. Run script multiple times with different hyperparameters.
5. Open MLflow UI (localhost:5000). Compare runs: parallel coordinates, metric history.
6. **Challenge:** Implement custom metric callback for XGBoost/LightGBM to log per-iteration metrics.

**Expected Answer:** Runs appear in experiment. UI shows param/metric comparison. Model logged as artifact with MLmodel file. Confusion matrix visible in artifacts.

---

## Exercise 2: Autologging and Framework Integration

**Objective:** Use MLflow autologging for automatic tracking.

**Tasks:**
1. Enable autolog: `mlflow.sklearn.autolog()` / `mlflow.xgboost.autolog()` / `mlflow.pytorch.autolog()`.
2. Train models without manual `log_param`/`log_metric` calls.
3. Inspect what autolog captures: params, metrics, model, feature importance (if available).
4. Disable autolog for specific run: `mlflow.autolog(disable=True)`.
5. Combine autolog with manual logging (e.g., custom business metrics).
6. **Challenge:** Implement custom autolog integration for a non-supported library (e.g., custom training loop).

**Expected Answer:** Autolog captures most standard params/metrics/models. Manual logging adds custom metrics. Custom integration requires `mlflow.tracking.MlflowClient` and knowledge of library's callback system.

---

## Exercise 3: MLflow Projects for Reproducibility

**Objective:** Package training code as an MLflow Project.

**Tasks:**
1. Create project structure:
   ```
   my_project/
   ├── MLproject
   ├── conda.yaml
   ├── train.py
   └── requirements.txt
   ```
2. MLproject file:
   ```yaml
   name: my_training_project
   entry_points:
     main:
       parameters:
         learning_rate: {type: float, default: 0.01}
         n_estimators: {type: int, default: 100}
       command: "python train.py --lr {learning_rate} --n-est {n_estimators}"
   conda_env: conda.yaml
   ```
3. conda.yaml with dependencies.
4. train.py reads parameters from argparse, uses `mlflow.start_run()` (autolog works).
5. Run locally: `mlflow run . -P learning_rate=0.1 -P n_estimators=200`.
6. Run with Docker: `mlflow run . --docker-image my-base-image`.
7. **Challenge:** Run project from Git URI: `mlflow run https://github.com/user/repo -P ...`.

**Expected Answer:** Project runs reproducibly in isolated conda env or Docker. Parameters passed via CLI. Tracking logs to server automatically.

---

## Exercise 4: Model Registry and Versioning

**Objective:** Register models, manage versions, promote through stages.

**Tasks:**
1. From Exercise 1 runs, register best model:
   `mlflow.register_model("runs:/<run_id>/model", "ExerciseModel")`
2. In UI: Model Registry → ExerciseModel → versions v1, v2...
3. Add description to model version: `client.update_model_version(name, version, description="...")`
4. Transition stages: `client.transition_model_version_stage("ExerciseModel", 1, "Staging")`
5. Request transition to Production (requires approval if configured).
6. Archive old version: `client.transition_model_version_stage("ExerciseModel", 1, "Archived")`
7. Load model from registry: `mlflow.pyfunc.load_model("models:/ExerciseModel/Production")`
8. **Challenge:** Implement automated promotion: if test metric > threshold, transition to Staging.

**Expected Answer:** Model versions tracked. Stage transitions recorded. Production model loadable by stage name. Lineage: model version → run → params/metrics.

---

## Exercise 5: Model Signature and Input Validation

**Objective:** Define and enforce model input/output schemas.

**Tasks:**
1. Create input example: `input_example = X_test.iloc[:5]`
2. Infer signature: `signature = mlflow.models.infer_signature(input_example, model.predict(input_example))`
3. Log model with signature: `mlflow.sklearn.log_model(model, "model", signature=signature, input_example=input_example)`
4. Inspect logged model: `mlflow models serve -m runs:/<run_id>/model` → test with valid/invalid input.
5. Test validation: send request with wrong columns, wrong types. Observe error response.
4. **Challenge:** Define custom signature for multi-input model (e.g., tabular + text).

**Expected Answer:** Signature enforces input schema at serving time. Input example enables UI testing. Invalid inputs rejected with clear error.

---

## Exercise 6: MLflow Model Serving

**Objective:** Serve models via REST API and Docker.

**Tasks:**
1. Serve locally: `mlflow models serve -m models:/ExerciseModel/Production -p 5001`
2. Test with curl:
   ```bash
   curl -X POST http://localhost:5001/invocations \
     -H "Content-Type: application/json" \
     -d '{"dataframe_split": {"columns": [...], "data": [[...]]}}'
   ```
3. Build Docker image: `mlflow models build-docker -m models:/ExerciseModel/Production -n my-model-image`
4. Run container: `docker run -p 5002:8080 my-model-image`
5. Test container endpoint.
5. **Challenge:** Deploy to Kubernetes using generated Docker image + K8s deployment/service manifests.

**Expected Answer:** REST API accepts JSON, returns predictions. Docker image includes model + dependencies + serving code. K8s deployment enables scaling.

---

## Exercise 7: Java MLflow Client (Lab Implementation)

**Objective:** Use lab's Java abstraction to log from JVM applications.

**Tasks:**
1. Examine lab's `MlflowClient` Java class (simulated REST client).
2. Implement `MlflowTracker` wrapper with:
   - `createExperiment(String name)`
   - `startRun(String experimentId)` → returns runId
   - `logParam(String runId, String key, String value)`
   - `logMetric(String runId, String key, double value, long step)`
   - `logArtifact(String runId, String localPath)`
   - `logModel(String runId, String modelPath, String flavor)`
   - `endRun(String runId, RunStatus status)`
3. Write Java training loop (e.g., simple linear regression) that logs to MLflow.
4. Verify runs appear in MLflow UI alongside Python runs.
5. **Challenge:** Implement batch logging (accumulate metrics, flush periodically) for high-frequency logging.

**Expected Answer:** Java client successfully logs to same tracking server. Runs comparable with Python runs. Enables JVM-based ML pipelines to use MLflow.

---

## Exercise 8: Hyperparameter Tuning with MLflow

**Objective:** Track hyperparameter search as nested runs.

**Tasks:**
1. Implement grid search / random search loop.
2. For each combination: `with mlflow.start_run(nested=True):` train + log.
3. Parent run: logs search config (param grid, search strategy).
4. Child runs: each logs params + metrics.
5. In UI: parent run shows nested runs table. Compare child runs.
6. Use `mlflow.search_runs(experiment_ids, filter_string="tags.mlflow.parentRunId='<parent_id>'")` to analyze.
7. **Challenge:** Integrate with Optuna: `optuna.integration.MLflowCallback` for automatic logging.

**Expected Answer:** Nested runs organize hyperparameter search. Parent run = experiment overview. Child runs = individual trials. Queryable via API.

---

## Exercise 9: Data and Model Lineage

**Objective:** Track data versions and model lineage.

**Tasks:**
1. Log dataset as artifact: `mlflow.log_artifact("data/train.parquet", "dataset")`
2. Compute data hash (MD5/SHA256) and log as param: `mlflow.log_param("data_hash", hash)`
3. Log dataset version/tag: `mlflow.set_tag("dataset_version", "v1.2")`
4. In Model Registry: view lineage → model version → run → data artifact + hash.
5. Implement `Dataset` class (MLflow 2.9+): `mlflow.log_input(dataset, context="training")`
6. **Challenge:** Build lineage graph: data version → run → model version → deployment.

**Expected Answer:** Data hash ensures reproducibility. Lineage shows full traceability. MLflow 2.9+ Dataset API provides structured lineage.

---

## Exercise 10: End-to-End MLflow Project

**Objective:** Complete MLflow workflow from experiment to production.

**Scenario:** Binary classification for customer churn prediction.

**Requirements:**
1. **Experiment Phase:**
   - 3+ experiments: baseline, feature engineering, model comparison
   - Each experiment: 10+ runs with different configs
   - Use autolog + custom metrics (business KPI: precision@top_k%)
2. **Model Selection:**
   - Compare runs across experiments using `mlflow.search_runs`
   - Select best model by business metric
   - Register to Model Registry with full lineage
3. **Staging Validation:**
   - Load Staging model
   - Run validation suite: performance, fairness, drift checks
   - Automated promotion decision
4. **Production Deployment:**
   - Build Docker image for Production model
   - Deploy to K8s (or local Docker)
   - Health check endpoint + prediction endpoint
5. **Monitoring Setup:**
   - Log production predictions to separate MLflow experiment
   - Track data drift metrics (PSI, KS test) weekly
6. **Deliverable:** 
   - Running MLflow server with experiments
   - Model in Production stage
   - Docker image deployed
   - 3-page report: experiment summary, model card, deployment architecture

**Reflection:** How would you handle: model rollback, A/B testing multiple model versions, retraining automation, multi-team collaboration?