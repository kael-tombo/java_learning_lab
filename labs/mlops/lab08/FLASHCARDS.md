# Model Monitoring & Observability — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is model monitoring?
**A:** Observing model behavior in production: data drift, concept drift, performance, predictions, system health.

---

### Card 2
**Q:** What is data drift (covariate shift)?
**A:** P_train(X) ≠ P_serve(X). Input distribution changes. Detected via statistical tests on features.

---

### Card 3
**Q:** What is concept drift?
**A:** P_train(Y|X) ≠ P_serve(Y|X). Relationship between features and target changes. Harder to detect (needs labels).

---

### Card 4
**Q:** What is prediction drift?
**A:** Distribution of model outputs (predictions/probabilities) shifts over time. Can indicate data or concept drift.

---

### Card 5
**Q:** What is label drift?
**A:** P(Y) changes. Target distribution shifts. Often accompanies concept drift.

---

### Card 6
**Q:** What is PSI (Population Stability Index)?
**A:** PSI = Σ (P_prod − P_ref) × ln(P_prod/P_ref) per bin. <0.1 stable, 0.1-0.25 moderate, >0.25 significant.

---

### Card 7
**Q:** How to compute PSI?
**A:** Bin reference distribution (e.g., 10 quantiles). Compute expected % per bin. Compare production % per bin. Sum weighted log ratios.

---

### Card 8
**Q:** What is KL divergence?
**A:** D_KL(P||Q) = Σ P(x) log(P(x)/Q(x)). Asymmetric. Measures info loss when Q approximates P. For continuous: integrate.

---

### Card 9
**Q:** What is JS divergence?
**A:** Jensen-Shannon: symmetric, bounded [0,1]. JS(P,Q) = 0.5×D_KL(P||M) + 0.5×D_KL(Q||M) where M=(P+Q)/2.

---

### Card 10
**Q:** What is Wasserstein distance (Earth Mover's Distance)?
**A:** Minimum "work" to transform one distribution to another. Sensitive to distribution shape. Good for continuous features.

---

### Card 11
**Q:** What is KS test (Kolmogorov-Smirnov)?
**A:** Non-parametric test: max difference between CDFs. H₀: same distribution. p-value indicates drift significance.

---

### Card 12
**Q:** What is Chi-squared test for drift?
**A:** For categorical: compare observed vs expected counts per category. H₀: same distribution. Sensitive to sample size.

---

### Card 13
**Q:** When to use which drift test?
**A:** PSI/KL: continuous, binned. JS: bounded metric. Wasserstein: continuous, shape-sensitive. KS: continuous, non-parametric. Chi2: categorical.

---

### Card 14
**Q:** What is the "reference window" for drift detection?
**A:** Baseline distribution (usually training data or recent stable period). Production compared against reference.

---

### Card 15
**Q:** What is a "sliding window" vs "expanding window"?
**A:** Sliding: fixed size recent window. Expanding: all data since start. Sliding adapts to gradual drift; expanding more stable.

---

### Card 16
**Q:** What metrics to monitor for model performance?
**A:** Classification: accuracy, precision, recall, F1, AUC, logloss. Regression: MAE, RMSE, MAPE, R². Business: revenue, conversion.

---

### Card 17
**Q:** Why is performance monitoring delayed?
**A:** Ground truth labels arrive later (hours/days/weeks). Use drift as leading indicator; performance as lagging confirmation.

---

### Card 18
**Q:** What is "data quality monitoring"?
**A:** Check: missing values, out-of-range, schema violations, cardinality changes, duplicate rates. Complementary to drift.

---

### Card 19
**Q:** What is "feature attribution drift"?
**A:** SHAP/feature importance distribution shifts. Indicates which features drive prediction changes.

---

### Card 20
**Q:** What is a monitoring dashboard?
**A:** Visualizes: feature drift trends, prediction drift, performance (when labels), data volume, alert history, system health.

---

### Card 21
**Q:** What are key dashboard components?
**A:** Time-series plots (drift scores), heatmap (feature × time), alert timeline, data volume, performance vs drift correlation.

---

### Card 22
**Q:** What is alerting in monitoring?
**A:** Automated notifications when metrics breach thresholds. Channels: Slack, PagerDuty, email, webhook.

---

### Card 23
**Q:** Alert threshold strategies?
**A:** Static (PSI > 0.2), dynamic (statistical control limits), adaptive (learned baseline). Multiple severity levels.

---

### Card 24
**Q:** What is alert fatigue?
**A:** Too many alerts → ignored. Mitigate: meaningful thresholds, grouping, deduplication, routing, auto-resolution.

---

### Card 25
**Q:** What is model rollback?
**A:** Reverting to previous model version when degradation detected. Requires: Model Registry, automated deployment, fast switchover.

---

### Card 26
**Q:** What is champion/challenger?
**A:** Champion = production model. Challenger = candidate (shadow or small traffic). Compare live performance. Promote if better.

---

### Card 27
**Q:** What is shadow deployment?
**A:** Challenger receives copy of traffic, makes predictions, but predictions NOT served. Compare predictions offline.

---

### Card 28
**Q:** What is canary deployment?
**A:** Challenger serves small % of traffic (1-5%). Gradually increase if metrics good. Full rollout or rollback.

---

### Card 29
**Q:** What is A/B testing for models?
**A:** Randomly assign users to model A or B. Compare metrics with statistical rigor. More controlled than canary.

---

### Card 30
**Q:** What is "model staleness"?
**A:** Time since last retraining. Staleness threshold triggers retraining pipeline. Monitor: days since last train.

---

### Card 31
**Q:** What is "data freshness"?
**A:** Latency between event time and data availability. High latency → stale features → prediction quality drops.

---

### Card 32
**Q:** What is "throughput monitoring"?
**A:** Requests/sec, latency (p50, p95, p99), error rate, queue depth. System health affects prediction quality.

---

### Card 33
**Q:** What is "cost monitoring"?
**A:** Compute cost per prediction, total daily cost, cost per model version. Optimize: batching, model size, instance type.

---

### Card 34
**Q:** What is the "monitoring stack"?
**A:** Collection (Prometheus, OpenTelemetry) → Storage (TSDB) → Visualization (Grafana) → Alerting (Alertmanager, PagerDuty).

---

### Card 35
**Q:** What is OpenTelemetry?
**A:** Vendor-neutral observability framework: traces, metrics, logs. Standardizes instrumentation across languages.

---

### Card 36
**Q:** What is a "model card" in monitoring context?
**A:** Documentation: intended use, performance, limitations, ethical considerations, monitoring plan, contacts.

---

### Card 37
**Q:** What is "incident response" for model degradation?
**A:** Runbook: 1) Acknowledge alert, 2) Check dashboard, 3) Identify root cause (drift? data bug? upstream?), 4) Rollback or retrain, 5) Post-mortem.

---

### Card 38
**Q:** What is "automated retraining trigger"?
**A:** When drift > threshold AND labels available AND performance degraded → trigger retraining pipeline. Human approval gate.

---

### Card 39
**Q:** How to monitor NLP/LLM models?
**A:** Track: token usage, latency, cost, perplexity (if labels), semantic drift (embedding shift), hallucination rate, safety violations.

---

### Card 40
**Q:** What are monitoring best practices?
**A:** Monitor inputs, predictions, system. Alert on leading indicators. Dashboard for investigation. Automate rollback. Document runbooks. Regular review.