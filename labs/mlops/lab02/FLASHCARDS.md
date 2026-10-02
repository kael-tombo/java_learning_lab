# Experiment Tracking with MLflow — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What are the 4 MLflow components?
**A:** Tracking, Projects, Models, Model Registry.

---

### Card 2
**Q:** What is MLflow Tracking?
**A:** API to log parameters, metrics, artifacts, tags during runs. UI to compare runs.

---

### Card 3
**Q:** What is an Experiment?
**A:** Container for runs. Each run belongs to one experiment. Named or ID-based.

---

### Card 4
**Q:** What is a Run?
**A:** Single execution logging params, metrics, artifacts, tags. Has unique run_id.

---

### Card 5
**Q:** Parameter vs Metric?
**A:** Param: logged once (input config). Metric: logged multiple times (time-series, e.g., loss per epoch).

---

### Card 6
**Q:** What is an Artifact?
**A:** Any file output: model, plot, dataset, log. Stored in artifact store (local/S3/GCS/Azure).

---

### Card 7
**Q:** What is the artifact store?
**A:** Backend storage for artifacts. Local (./mlruns), S3, Azure Blob, GCS, HDFS, FTP, DB-backed.

---

### Card 8
**Q:** What is MLflow Model format?
**A:** Directory with MLmodel (metadata), model files per flavor, conda.yaml/requirements.txt.

---

### Card 9
**Q:** What is a Flavor?
**A:** Framework-specific save/load convention. Built-in: sklearn, pytorch, tensorflow, xgboost, pyfunc, onnx.

---

### Card 10
**Q:** What is python_function (pyfunc) flavor?
**A:** Universal interface: `predict(pandas.DataFrame)`. Any model can be wrapped. Used for deployment.

---

### Card 11
**Q:** What is Model Registry?
**A:** Centralized model store: versioning (v1, v2...), stages (Staging/Production/Archived), lineage, transitions.

---

### Card 12
**Q:** Model Registry stages?
**A:** None → Staging → Production → Archived. Transitions can require approval.

---

### Card 13
**Q:** What is model lineage?
**A:** Link from model version → source run → params/metrics/artifacts/code version (git commit).

---

### Card 14
**Q:** How to register a model?
**A:** `mlflow.register_model("runs:/<run_id>/model", "MyModel")` or via UI.

---

### Card 15
**Q:** What is an MLflow Project?
**A:** Packaged code with MLproject file: entry points, parameters, conda env. Reproducible runs.

---

### Card 16
**Q:** What is `mlflow.run()`?
**A:** Execute a project entry point. Can run in new conda env or Docker container. Logs to tracking.

---

### Card 17
**Q:** Tracking URI types?
**A:** `file://` (local), `http://` (remote server), `databricks://`, `sqlite://`, `postgresql://`, `mysql://`.

---

### Card 18
**Q:** Backend store vs Artifact store?
**A:** Backend: metadata (params, metrics, tags) — DB. Artifact: files — object store. Can be separate.

---

### Card 19
**Q:** How to log a model?
**A:** `mlflow.sklearn.log_model(model, "model")` — auto-detects flavor, logs as artifact, registers if Model Registry URI set.

---

### Card 20
**Q:** How to load a model?
**A:** `mlflow.sklearn.load_model("models:/MyModel/Production")` or `mlflow.pyfunc.load_model(uri)`.

---

### Card 21
**Q:** Model URI schemes?
**A:** `runs:/<run_id>/path`, `models:/<name>/<stage|version>`, `file://`, `s3://`, `dbfs://`.

---

### Card 22
**Q:** What is model signature?
**A:** Schema of inputs/outputs: `ModelSignature(inputs=Schema([...]), outputs=Schema([...]))`. Enables validation.

---

### Card 23
**Q:** How to infer signature?
**A:** `mlflow.models.infer_signature(input_example, prediction)` or pass `signature=` to `log_model`.

---

### Card 24
**Q:** What is an input example?
**A:** Sample input (pandas.DataFrame, numpy array, dict) logged with model. Used for testing, docs, signature inference.

---

### Card 25
**Q:** How to log metrics at step?
**A:** `mlflow.log_metric("loss", 0.5, step=10)`. Step enables time-series plots in UI.

---

### Card 26
**Q:** What are tags?
**A:** Key-value metadata on runs (e.g., `git.commit`, `user`, `dataset_version`). Filterable in UI.

---

### Card 27
**Q:** How to set tags?
**A:** `mlflow.set_tag("key", "value")` or `mlflow.set_tags({"k1": "v1", "k2": "v2"})`.

---

### Card 28
**Q:** What is autologging?
**A:** `mlflow.autolog()` — automatically logs params, metrics, models for sklearn, tensorflow, pytorch, xgboost, etc.

---

### Card 29
**Q:** How to compare runs in UI?
**A:** Select runs → "Compare" → parallel coordinates, scatter plots, metric history. Filter by params/tags.

---

### Card 30
**Q:** How to delete a run?
**A:** `mlflow.delete_run(run_id)` or UI. Soft delete (restorable). Hard delete: `mlflow.delete_run(run_id, force=True)`.

---

### Card 31
**Q:** What is the tracking server?
**A:** REST API + UI. Runs on port 5000. Backend: SQLite/Postgres/MySQL. Artifact store: local/S3.

---

### Card 32
**Q:** How to run tracking server?
**A:** `mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0`

---

### Card 33
**Q:** What is `mlflow.projects.run()`?
**A:** Run project from Git URI, local path, or Docker. Handles env setup, parameter passing, tracking.

---

### Card 34
**Q:** MLproject file structure?
**A:** YAML with: `name`, `entry_points` (commands, parameters), `conda_env` (dependencies).

---

### Card 35
**Q:** How to deploy MLflow model?
**A:** `mlflow models serve -m models:/MyModel/Production` (REST API). Or `mlflow models build-docker` for container.

---

### Card 36
**Q:** What is model serving input format?
**A:** pyfunc: JSON with `dataframe_split` or `dataframe_records` or `ndarray`. `Content-Type: application/json`.

---

### Card 37
**Q:** How to transition model stage?
**A:** `client.transition_model_version_stage(name, version, "Production")` or UI. Can require approval.

---

### Card 38
**Q:** What is a "champion/challenger" pattern?
**A:** Current Production = champion. New candidate = challenger. A/B test or shadow mode before promoting.

---

### Card 39
**Q:** How to search runs programmatically?
**A:** `mlflow.search_runs(experiment_ids, filter_string, order_by, max_results)` returns pandas.DataFrame.

---

### Card 40
**Q:** Java MLflow client?
**A:** `mlflow-java` or REST API wrapper. Lab implements Java abstraction over MLflow REST API for logging from JVM.