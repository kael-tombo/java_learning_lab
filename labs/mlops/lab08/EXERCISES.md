# Model Monitoring & Observability — Exercises

**Prerequisites:** Python 3.x with `numpy`, `pandas`, `scipy`, `evidently`, `prometheus-client`, `grafana` (optional). Java 21+ for lab's implementation.

---

## Exercise 1: Statistical Drift Detection Implementation

**Objective:** Implement core drift detection metrics from scratch.

**Tasks:**
1. Implement `psi(reference, production, bins=10)`:
   - Bin reference by quantiles (qcut)
   - Compute expected % per bin from reference
   - Compute actual % per bin from production
   - PSI = Σ (actual% − expected%) × ln(actual%/expected%)
   - Handle zero bins (add small epsilon)
2. Implement `kl_divergence(p, q, bins=10)` for continuous (histogram) and categorical.
3. Implement `js_divergence(p, q)` = 0.5×KL(p||m) + 0.5×KL(q||m) where m=(p+q)/2.
4. Implement `wasserstein_distance(p, q)` using scipy or manual (EMD for 1D = ∫|CDF_p − CDF_q|).
5. Implement `ks_test(p, q)` using scipy.stats.ks_2samp.
6. Test on:
   - Same distribution → all metrics near 0
   - Shifted mean → PSI, KL, Wasserstein increase
   - Changed variance → KS, Wasserstein sensitive
   - Categorical shift → Chi2, PSI
7. **Challenge:** Implement multivariate drift: PCA on reference, project both, compute drift on PC scores.

**Expected Answer:** Functions return correct drift scores. PSI ≈ 0 for same, >0.2 for significant shift. Wasserstein captures shape changes. KS gives p-value.

---

## Exercise 2: Drift Detection on Real Features

**Objective:** Apply drift detection to tabular dataset features.

**Tasks:**
1. Load dataset (UCI Adult, California Housing, or synthetic with known drift).
2. Split: reference (train), production (test + synthetic drift injection).
3. Inject drift: shift 2 features mean by 2σ, change 1 categorical distribution.
4. Compute per-feature PSI, KL, KS for all features.
5. Rank features by drift score. Identify drifted features.
6. Visualize: drift score bar chart, distribution overlay plots (ref vs prod) for top 5.
7. **Challenge:** Implement feature importance weighted drift: Σ importanceᵢ × driftᵢ.

**Expected Answer:** Drifted features rank highest. Distribution plots show clear shifts. Non-drifted features near zero.

---

## Exercise 3: Prediction Drift Monitoring

**Objective:** Monitor model output distribution shifts.

**Tasks:**
1. Train model on reference data. Get predictions on reference and production.
2. For classification: monitor predicted class distribution, predicted probability distribution (per class).
3. For regression: monitor prediction mean, variance, quantiles.
4. Compute PSI on prediction scores (probability of positive class).
3. Correlate prediction drift with feature drift: which feature drifts drive prediction drift?
4. **Challenge:** Implement "prediction stability index" — PSI on binned predictions. Alert if > 0.1.

**Expected Answer:** Prediction drift often precedes performance drop. Correlation analysis identifies root cause features.

---

## Exercise 4: Performance Monitoring with Delayed Labels

**Objective:** Simulate delayed label arrival and performance tracking.

**Tasks:**
1. Simulate streaming: each timestep = 1 hour of predictions.
2. Labels arrive with delay: exponential distribution (mean=24 hours).
3. Maintain rolling window of (prediction, label) pairs as labels arrive.
4. Compute rolling metrics: accuracy, AUC, F1 (classification) / MAE, RMSE (regression).
4. Plot: metric vs time, label arrival lag histogram.
5. Detect performance drop: metric < threshold for N consecutive windows.
6. **Challenge:** Implement "expected performance" estimation using drift-performance correlation from historical data.

**Expected Answer:** Performance metrics lag behind drift. Rolling window shows delayed detection. Label delay distribution affects monitoring latency.

---

## Exercise 5: Monitoring Dashboard with Evidently

**Objective:** Build interactive monitoring dashboard using Evidently AI.

**Tasks:**
1. Install: `pip install evidently`
2. Create `ColumnMapping` with target, prediction, numerical_features, categorical_features.
3. Generate reports:
   - `DataDriftReport()` — per-feature drift
   - `DataQualityReport()` — missing, outliers, schema
   - `RegressionPerformanceReport()` / `ClassificationPerformanceReport()`
   - `TargetDriftReport()` — label distribution
   - `PredictionDriftReport()` — prediction distribution
4. Export as HTML. Schedule daily generation.
5. Create dashboard: combine multiple reports in one HTML.
6. **Challenge:** Deploy as FastAPI service serving latest report. Add historical trend plots.

**Expected Answer:** Evidently generates comprehensive HTML reports. Dashboard shows all monitoring aspects. Automatable in pipeline.

---

## Exercise 6: Alerting System

**Objective:** Implement alerting rules and notification delivery.

**Tasks:**
1. Define alert rules (YAML/JSON):
   ```yaml
   rules:
     - name: "feature_drift_high"
       metric: "psi"
       condition: "> 0.2"
       severity: "critical"
       cooldown_hours: 4
     - name: "performance_drop"
       metric: "accuracy"
       condition: "< 0.85"
       severity: "warning"
       window: "7d"
   ```
2. Implement `AlertEngine`:
   - Evaluate rules against current metrics
   - Track alert state: firing, resolved, acknowledged
   - Cooldown: don't re-fire same alert within cooldown period
   - Escalation: warning → critical if persists
3. Notification channels: `SlackNotifier`, `EmailNotifier`, `PagerDutyNotifier`, `WebhookNotifier`.
4. Test: inject drift, verify alert fires, verify cooldown works.
5. **Challenge:** Implement alert grouping: group related feature drifts into single alert.

**Expected Answer:** Alert engine evaluates rules, manages state, sends notifications. Cooldown prevents spam. Escalation ensures attention.

---

## Exercise 7: Champion/Challenger Evaluation

**Objective:** Implement shadow/canary evaluation framework.

**Tasks:**
1. Deploy champion model (serving 100% traffic).
2. Deploy challenger model (shadow mode: receives copy of requests, logs predictions).
3. Log: request_id, features, champion_pred, challenger_pred, timestamp.
4. When labels arrive: join with predictions, compute metrics for both.
5. Comparison: side-by-side metrics, statistical significance test (McNemar for classification, paired t-test for regression).
6. Decision logic: if challenger significantly better (p<0.05) AND no regression on key segments → promote.
7. **Challenge:** Implement gradual traffic shifting (canary): 1% → 5% → 25% → 100% with automated metric checks at each step.

**Expected Answer:** Shadow mode enables risk-free comparison. Statistical test prevents false promotion. Canary reduces blast radius.

---

## Exercise 8: Model Rollback Automation

**Objective:** Implement automated rollback on degradation detection.

**Tasks:**
1. Define rollback triggers:
   - Critical alert firing for > 30 min
   - Performance metric < threshold for 3 consecutive windows
   - Prediction drift PSI > 0.25 sustained
2. Implement `RollbackManager`:
   - `get_previous_stable_version(model_name)` — from Model Registry (last Production version before current)
   - `validate_rollback_candidate(version)` — quick sanity check (load, predict on sample)
   - `execute_rollback(model_name, version)` — update Model Registry stage, trigger deployment
3. Integration: alert webhook → rollback manager → deployment pipeline.
4. Safety: max 1 rollback per hour. Manual approval for rollback to version > 2 generations back.
5. **Challenge:** Implement "circuit breaker": if rollback also degrades → alert on-call, don't auto-rollback further.

**Expected Answer:** Rollback restores previous working version quickly. Safety limits prevent oscillation. Circuit breaker prevents automated damage.

---

## Exercise 9: Java Monitoring Implementation (Lab)

**Objective:** Implement monitoring components in Java per lab.

**Tasks:**
1. Create `DriftDetector` interface: `computeDrift(ReferenceDistribution ref, ProductionDistribution prod)`.
2. Implement `PSIDriftDetector`, `KLDriftDetector`, `KSDriftDetector`.
3. Create `MonitoringJob` scheduled task:
   - Fetch recent predictions from feature store / prediction log
   - Compute reference distributions (cached, updated weekly)
   - Run drift detectors per feature
   - Write results to monitoring store (DB, Prometheus)
   - Evaluate alert rules
4. Expose `/metrics` endpoint for Prometheus scraping:
   - `model_drift_psi{feature="age"} 0.05`
   - `model_performance_accuracy 0.92`
   - `model_alert_active{alert="feature_drift_high"} 1`
5. **Challenge:** Implement efficient streaming drift computation using reservoir sampling for reference window.

**Expected Answer:** Java components compute drift, expose metrics. Integrates with Prometheus/Grafana stack. Scheduled job runs periodically.

---

## Exercise 10: End-to-End Monitoring Project

**Objective:** Deploy complete monitoring for a production model.

**Scenario:** Credit scoring model in production.

**Requirements:**
1. **Architecture:** Diagram showing: model serving → prediction log → monitoring job → metrics store → dashboard/alerting.
2. **Implementation:**
   - Instrument model server to log: request_id, features, prediction, latency to Kafka/DB
   - Daily monitoring job (Airflow/Prefect/cron):
     * Compute feature drift (PSI) vs training baseline
     * Compute prediction drift
     * When labels available (weekly): compute performance
     * Generate Evidently report
     * Evaluate alerts
   - Dashboard (Grafana): feature drift heatmap, prediction drift trend, performance trend, data volume, alert history
   - Alerting: Slack for warnings, PagerDuty for critical
   - Rollback: Model Registry + ArgoCD/K8s deployment
3. **Testing:** Simulate drift by shifting input data. Verify detection, alerting, dashboard update.
4. **Documentation:** Runbook for each alert type. Model card with monitoring plan.
5. **Deliverable:** Running monitoring stack + 3-page runbook + dashboard screenshots.

**Reflection:** What's the optimal monitoring frequency? How to handle: seasonal patterns, new categories, label delay, multiple model versions?