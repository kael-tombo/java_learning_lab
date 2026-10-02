# Experiment Tracking with MLflow — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What are the four core concepts in MLflow?
A) Experiments, Runs, Parameters, Metrics
B) Experiments, Runs, Artifacts, Models
C) Tracking, Projects, Models, Registry
D) Tracking, Experiments, Artifacts, Deployments

**Answer: C** — MLflow has four components: (1) Tracking (log params/metrics/artifacts), (2) Projects (packaging code), (3) Models (standard format for packaging), (4) Model Registry (versioning, staging, deployment).

---

### Q2: What is an MLflow "Run"?
A) A single execution of a training script with logged parameters, metrics, and artifacts
B) A trained model artifact
C) An experiment configuration
D) A deployment instance

**Answer: A** — Run = one execution within an Experiment. Contains: parameters (key-value inputs), metrics (key-value measures, can be time-series), artifacts (files: models, plots, data), tags (metadata).

---

### Q3: What is the difference between `log_param` and `log_metric`?
A) Params are immutable (logged once); metrics can be updated over time (e.g., per epoch)
B) Params are for numbers; metrics are for strings
C) Params are stored in DB; metrics in file system
D) No difference

**Answer: A** — Parameters: logged once at start (learning rate, batch size). Metrics: logged multiple times (loss per epoch, accuracy per step). MLflow UI plots metrics over time.

---

### Q4: What is an MLflow "Artifact"?
A) A hyperparameter value
B) Any file output by a run (model, plot, dataset, log)
C) A metric value
D) A tag

**Answer: B** — Artifacts = files logged via `log_artifact(local_path)` or `log_artifacts(dir)`. Stored in artifact store (local, S3, Azure, GCS). Model is a special artifact with MLmodel file.

---

### Q5: What is the MLflow Model format?
A) A pickled Python object
B) A directory with MLmodel file (metadata) + model files (pickle, ONNX, etc.) + conda.yaml
C) A Docker image
D) A JAR file

**Answer: B** — MLflow Model = directory with: `MLmodel` (flavors, signature, run_id), model files per flavor (python_function, sklearn, tensorflow, pytorch, xgboost, lightgbm, onnx), `conda.yaml`/`requirements.txt` for dependencies.

---

### Q6: What is a "flavor" in MLflow Models?
A) The model's hyperparameters
B) A convention for saving/loading models from different libraries (sklearn, PyTorch, etc.)
C) The model's accuracy
D) The deployment target

**Answer: B** — Flavor = standardized interface for a framework. Built-in: sklearn, keras, pytorch, tensorflow, xgboost, lightgbm, statsmodels, propeller, onnx, python_function (generic). Enables `mlflow.sklearn.load_model()` etc.

---

### Q7: What is the Model Registry?
A) A database of all experiment runs
B) Centralized model store with versioning, stages (Staging/Production/Archived), and lineage
C) A cache for model artifacts
D) The MLflow UI

**Answer: B** — Model Registry: register models from runs → versions (v1, v2...). Stages: None → Staging → Production → Archived. Transition requests with approval. Lineage: run → model version.

---

### Q8: What is the "python_function" flavor?
A) A flavor only for Python functions
B) Generic flavor allowing any model to be loaded as Python function with `predict(dataframe)` interface
C) A flavor for functional programming
D) The default flavor for all models

**Answer: B** — python_function (pyfunc) = universal deployment interface. Any model can be wrapped as pyfunc. `mlflow.pyfunc.load_model()` returns object with `predict(pandas.DataFrame)` method. Used by deployment tools.

---

### Q9: How does MLflow track experiments without a server?
A) It doesn't — server required
B) Local file store: `mlruns/` directory with run metadata and artifacts
C) In-memory only
D) SQLite database only

**Answer: B** — Default: `mlflow.set_tracking_uri("file:///path")` or `mlruns/` relative to cwd. Creates `mlruns/<experiment_id>/<run_id>/` with `params/`, `metrics/`, `artifacts/`, `tags/`. Good for local dev.

---

### Q10: What is the difference between `mlflow.start_run()` and `mlflow.run()`?
A) `start_run()` begins a run in current process; `run()` executes a project entry point (can be in new process/container)
B) They are the same
C) `run()` is for tracking; `start_run()` for projects
D) `start_run()` requires server; `run()` doesn't

**Answer: A** — `start_run()`: context manager for logging in current script. `mlflow.run(uri, entry_point, parameters)`: runs an MLflow Project (packaged code) — can launch in new Conda env or Docker container.