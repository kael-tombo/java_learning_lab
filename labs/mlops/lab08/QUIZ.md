# Model Monitoring & Observability — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is "data drift" in ML monitoring?
A) Model performance degrading over time
B) The distribution of input features changing between training and serving
C) The model parameters changing during training
D) The label distribution changing in the training set

**Answer: B** — Data drift (covariate shift) = P_train(X) ≠ P_serve(X). Model sees different inputs than trained on. Causes performance degradation. Detected via statistical tests on feature distributions.

---

### Q2: What is "concept drift"?
A) P(Y|X) changes over time while P(X) stays same
B) P(X) changes over time
C) Model architecture changes
D) Feature engineering changes

**Answer: A** — Concept drift = relationship between X and Y changes. P(Y|X) shifts. Examples: fraud patterns evolve, seasonal behavior changes. Harder to detect than data drift (need labels).

---

### Q3: What is the Population Stability Index (PSI)?
A) A measure of model accuracy
B) A metric comparing two distributions (e.g., train vs serve) by binning
C) A statistical test for normality
D) A measure of feature importance

**Answer: B** — PSI = Σ (P_serve(bin) − P_train(bin)) × ln(P_serve(bin)/P_train(bin)). Values: <0.1 = no shift, 0.1-0.25 = moderate, >0.25 = significant shift. Used per feature.

---

### Q4: What is KL divergence?
A) Symmetric distance between distributions
B) Asymmetric measure of how one distribution diverges from another
C) A test for stationarity
D) A correlation metric

**Answer: B** — D_KL(P||Q) = Σ P(x) log(P(x)/Q(x)). Asymmetric. Measures information lost when Q approximates P. Used for drift detection on continuous/categorical distributions.

---

### Q5: What is the difference between monitoring "model performance" vs "data drift"?
A) No difference
B) Performance needs labels; drift detection often doesn't
C) Drift detection needs labels; performance doesn't
D) Performance is for regression; drift for classification

**Answer: B** — Performance metrics (accuracy, AUC, RMSE) require ground truth labels (delayed). Data drift detection uses only input features (real-time). Both needed: drift = early warning, performance = ground truth.

---

### Q6: What is a "prediction drift"?
A) Drift in model predictions distribution over time
B) Drift in feature importance
C) Drift in training data
D) Drift in hyperparameters

**Answer: A** — Distribution of model outputs (predictions/probabilities) shifts. Can indicate concept drift or data drift. Monitored via PSI/KL on prediction scores. No labels needed.

---

### Q7: What is the purpose of a "monitoring dashboard"?
A) To replace the model
B) To visualize metrics, drift scores, alerts over time for human operators
C) To automatically retrain the model
D) To store model artifacts

**Answer: B** — Dashboard shows: feature drift trends, prediction drift, performance metrics (when labels arrive), alert history, data volume. Enables human-in-the-loop investigation and decision making.

---

### Q8: What is "alerting" in model monitoring?
A) Sending notifications when metrics exceed thresholds
B) Logging all predictions
C) Retraining the model
D) Storing drift scores

**Answer: A** — Alert rules: feature PSI > 0.2, prediction PSI > 0.1, performance drop > 5%, data volume drop > 50%. Channels: Slack, PagerDuty, email. Severity levels: warning, critical.

---

### Q9: What is "model rollback"?
A) Reverting to a previous model version when issues detected
B) Rolling back training data
C) Rolling back feature engineering
D) Rolling back hyperparameters

**Answer: A** — Rollback = deploying previous model version (from Model Registry) when current version shows degradation. Fast recovery. Requires: model versioning, automated deployment, validation gates.

---

### Q10: What is the "champion/challenger" pattern in monitoring?
A) Running two models simultaneously, comparing performance
B) Training two models and picking best
C) Having backup model ready
D) A/B testing framework

**Answer: A** — Champion = current production model. Challenger = candidate model (shadow or small traffic %). Compare performance on live traffic. Promote challenger if better. Reduces risk of bad deployment.