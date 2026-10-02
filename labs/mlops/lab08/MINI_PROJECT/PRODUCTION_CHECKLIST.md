# MLOps Production Readiness Checklist
## For Model Monitoring & Observability Mini-Project

**Purpose:** Comprehensive checklist to validate production readiness of ML model deployment with monitoring, drift detection, and rollback capabilities.

---

## ✅ 1. Pre-Deployment Validation

### Model Quality
- [ ] Model meets minimum performance thresholds on holdout test set
- [ ] Performance validated across key segments (demographics, regions, customer tiers)
- [ ] Fairness/bias metrics within acceptable bounds (demographic parity, equal opportunity)
- [ ] Model card documented with intended use, limitations, ethical considerations
- [ ] Model signature (input/output schema) defined and validated

### Data Validation
- [ ] Training data schema matches serving data schema
- [ ] Feature distributions in training cover expected serving range
- [ ] Data quality checks pass: missing values, outliers, schema compliance
- [ ] Reference distributions for drift detection computed and stored
- [ ] Data lineage tracked: source → feature store → training → model

### Infrastructure
- [ ] Model containerized with multi-stage Docker build (minimal attack surface)
- [ ] Container scanned for vulnerabilities (Trivy, Snyk, or equivalent)
- [ ] Resource requests/limits defined (CPU, memory, GPU if needed)
- [ ] Health check endpoint implemented (`/health`, `/ready`)
- [ ] Graceful shutdown handling (SIGTERM, finish in-flight requests)
- [ ] Model loads within SLA (cold start < 30s, warm < 5s)

---

## ✅ 2. Deployment Configuration

### Deployment Strategy
- [ ] Blue-green OR canary deployment configured
- [ ] Traffic routing rules defined (weights, headers, cookies)
- [ ] Rollback procedure documented and tested (time to rollback < 5 min)
- [ ] Deployment pipeline includes automated validation gates
- [ ] Feature flags for gradual feature rollout

### Environment Parity
- [ ] Dev/Staging/Prod environments use same deployment artifacts
- [ ] Configuration externalized (ConfigMaps, Secrets, not baked in image)
- [ ] Secrets managed via secret store (Vault, AWS Secrets Manager, K8s Secrets)
- [ ] Network policies restrict egress to required endpoints only
- [ ] Pod security standards enforced (non-root, read-only rootfs, drop capabilities)

### Scaling
- [ ] Horizontal Pod Autoscaler (HPA) configured (CPU, memory, custom metrics)
- [ ] Minimum replicas for HA (≥ 3 across availability zones)
- [ ] Maximum replicas defined (prevent runaway scaling)
- [ ] Load testing performed (target QPS, latency percentiles)
- [ ] Queue depth / request latency metrics exposed for scaling decisions

---

## ✅ 3. Monitoring & Observability

### Metrics Collection
- [ ] **System metrics:** CPU, memory, disk, network, GPU utilization
- [ ] **Request metrics:** QPS, latency (p50, p95, p99), error rate, timeout rate
- [ ] **Model metrics:** Prediction distribution, confidence scores, feature drift scores
- [ ] **Business metrics:** Conversion rate, revenue impact, user satisfaction (when labels available)
- [ ] **Cost metrics:** Cost per prediction, daily/monthly spend, cost per model version

### Drift Detection
- [ ] Feature drift monitoring: PSI/KL/JS/Wasserstein per feature (daily)
- [ ] Prediction drift monitoring: PSI on prediction scores (hourly)
- [ ] Data quality monitoring: missing rate, schema violations, cardinality changes
- [ ] Concept drift monitoring: performance metrics when labels arrive (weekly)
- [ ] Drift baselines versioned and updated periodically (monthly retrain baseline)

### Alerting
- [ ] Alert rules defined for each critical metric with appropriate thresholds
- [ ] Alert severity levels: info, warning, critical, page
- [ ] Notification channels configured: Slack (warnings), PagerDuty (critical)
- [ ] Alert deduplication and grouping implemented
- [ ] Runbooks linked to each alert (diagnosis steps, escalation contacts)
- [ ] Alert testing performed (inject synthetic drift, verify alert fires)

### Dashboards
- [ ] Real-time dashboard: system health, request metrics, prediction volume
- [ ] Drift dashboard: feature drift heatmap, prediction drift trends, top drifted features
- [ ] Performance dashboard: accuracy/F1/AUC trends, segment breakdowns
- [ ] Business dashboard: KPI trends, model impact attribution
- [ ] Dashboard accessible to: ML engineers, data scientists, product managers, on-call

### Logging
- [ ] Structured logging (JSON) with correlation IDs (request_id, trace_id)
- [ ] Prediction logs: request_id, timestamp, features, prediction, latency, model_version
- [ ] Audit logs: model deployments, config changes, rollback events
- [ ] Log retention policy defined (hot: 30 days, cold: 1 year)
- [ ] PII/sensitive data redacted from logs

### Distributed Tracing
- [ ] OpenTelemetry instrumentation for end-to-end traces
- [ ] Trace context propagated across service boundaries
- [ ] Key spans: preprocessing, inference, postprocessing, external calls
- [ ] Trace sampling rate configured (100% for errors, 10% for success)

---

## ✅ 4. Model Lifecycle Management

### Model Registry
- [ ] Model registered in Model Registry with versioning
- [ ] Stages enforced: None → Staging → Production → Archived
- [ ] Stage transitions require approval (at least 1 reviewer for Production)
- [ ] Lineage tracked: model version → training run → data version → code version
- [ ] Model artifacts immutable (content-addressable storage)

### Retraining
- [ ] Retraining pipeline automated (trigger: schedule, drift threshold, performance drop)
- [ ] Training data freshness validated (no stale data)
- [ ] Automated model validation in retraining pipeline (performance, drift, fairness)
- [ ] Champion/challenger evaluation before promotion
- [ ] Retraining frequency aligned with data drift rate (e.g., weekly for high-velocity)

### Rollback
- [ ] One-click rollback to previous Production version
- [ ] Rollback tested in staging (full deployment + validation)
- [ ] Rollback time measured and documented (< 5 minutes target)
- [ ] Circuit breaker: prevent auto-rollback loops (max 1 rollback/hour)
- [ ] Post-rollback validation: health checks, smoke tests, metric verification

### A/B Testing
- [ ] Experiment framework for model comparison (random assignment, consistent hashing)
- [ ] Statistical rigor: sample size calculation, power analysis, sequential testing
- [ ] Guardrail metrics monitored during experiment (latency, errors, business KPIs)
- [ ] Experiment results documented with statistical significance
- [ ] Automatic experiment conclusion (significance reached or futility)

---

## ✅ 5. Security & Compliance

### Data Protection
- [ ] Encryption at rest (model artifacts, feature store, logs)
- [ ] Encryption in transit (mTLS between services, TLS for external APIs)
- [ ] PII handling: minimization, pseudonymization, access controls
- [ ] Data residency requirements met (region-specific deployments)
- [ ] Right to deletion / forgetting implemented for training data

### Access Control
- [ ] RBAC for model deployment (only ML engineers + leads)
- [ ] RBAC for model registry (data scientists: read, ML engineers: write, leads: admin)
- [ ] Audit trail for all model lifecycle actions (who, what, when, why)
- [ ] API authentication: mTLS, OAuth2, or API keys with rotation
- [ ] Rate limiting and DDoS protection on inference endpoints

### Vulnerability Management
- [ ] Base image updated monthly (security patches)
- [ ] Dependency scanning in CI/CD (Snyk, Dependabot, Trivy)
- [ ] SBOM (Software Bill of Materials) generated for each release
- [ ] Incident response plan for model compromise (adversarial, data poisoning)

### Compliance
- [ ] Model documentation meets regulatory requirements (SR 11-7, EU AI Act, etc.)
- [ ] Bias/fairness assessment documented for protected attributes
- [ ] Explainability: SHAP/LIME available for high-stakes predictions
- [ ] Data processing agreements with third-party vendors
- [ ] Regular compliance audits scheduled

---

## ✅ 6. Incident Response

### Runbooks
- [ ] Runbook for each alert type (diagnosis, mitigation, escalation)
- [ ] Runbook for model performance degradation
- [ ] Runbook for data drift detection
- [ ] Runbook for system outage (model service down)
- [ ] Runbook for security incident (model extraction, adversarial attack)
- [ ] Runbooks tested quarterly (tabletop exercises)

### On-Call
- [ ] On-call rotation defined with escalation path
- [ ] Runbooks accessible to on-call (wiki, Git, PagerDuty)
- [ ] On-call training completed (shadow shifts, incident simulations)
- [ ] Post-incident review process (blameless postmortems, action items tracked)

### Disaster Recovery
- [ ] Model artifacts backed up to separate region/account
- [ ] Recovery Time Objective (RTO) defined and tested (< 1 hour)
- [ ] Recovery Point Objective (RPO) defined (< 15 minutes)
- [ ] Failover to backup model version tested
- [ ] Chaos engineering: simulate pod failures, zone outages, dependency failures

---

## ✅ 7. Operational Excellence

### Documentation
- [ ] Architecture diagram (components, data flows, dependencies)
- [ ] API documentation (OpenAPI/Swagger for inference endpoint)
- [ ] Runbooks for common operations (deploy, rollback, scale, debug)
- [ ] Model card with monitoring plan
- [ ] Onboarding guide for new team members

### Knowledge Sharing
- [ ] Regular model performance reviews (monthly)
- [ ] Incident retrospectives shared with team
- [ ] Best practices documented and updated
- [ ] Cross-training between ML engineers and data scientists

### Continuous Improvement
- [ ] Monitoring coverage reviewed quarterly (new features, new models)
- [ ] Alert noise measured and reduced (alert fatigue prevention)
- [ ] Dashboard usability tested with stakeholders
- [ ] Cost optimization reviewed monthly (right-sizing, spot instances, batch inference)

---

## ✅ 8. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| ML Engineer (Owner) | | | |
| Data Scientist | | | |
| Engineering Lead | | | |
| Security Reviewer | | | |
| Product Manager | | | |
| On-Call Lead | | | |

---

## 📋 Appendix: Quick Reference Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Feature PSI (any) | > 0.1 | > 0.25 | Investigate, alert DS |
| Prediction PSI | > 0.05 | > 0.1 | Alert on-call |
| Accuracy drop | > 2% | > 5% | Rollback consideration |
| Latency p99 | > 2x baseline | > 5x baseline | Scale / investigate |
| Error rate | > 1% | > 5% | Page on-call |
| Data volume drop | > 20% | > 50% | Check upstream |
| Cost per prediction | > 1.5x budget | > 2x budget | Optimize / alert |

---

## 🔄 Checklist Maintenance

- **Review frequency:** Quarterly or after major incidents
- **Update trigger:** New model type, new regulation, major architecture change, post-incident
- **Version:** 1.0
- **Last updated:** 2026-10-01
- **Owner:** ML Platform Team