# On-Call Runbook: ML Platform (Capstone 06)

> Scope: `FeatureStore`, `TrainingPipeline`, `ExperimentTracker`, `ModelRegistry`, `ModelServer`, `DriftDetector`, `ABTestFramework`.
> Audience: on-call engineer for a team running this Java ML platform in production.

## 1. Service Map & SLOs

| Component | SLO | Key signal |
|---|---|---|
| `ModelServer.predict` | p95 latency < 200 ms, error rate < 0.5% | latency tracker in `ModelServer`, HTTP 5xx rate |
| `FeatureStore` online read | p99 < 20 ms, freshness < 5 min | ingestion lag, `getOnline` miss rate |
| Training pipeline | > 95% runs succeed in 24 h | `TrainingPipeline` run status |
| Drift detection | alert within 1 h of PSI breach | `DriftDetector` alert history |

## 2. Triage Decision Tree (first 5 minutes)

```
predict latency spike or 5xx?
├─ YES → §3 Model-Serving Incident
├─ NO → predictions wrong but fast?
│   ├─ YES → §4 Stale Features / Drift
│   └─ NO → training / registry / A-B issue? → §5
```

Always: note model name + version (`ModelRegistry` production pointer), time of last promotion, last deploy, last feature ingestion.

## 3. Runbook: Model-Serving Outage / Latency Spike

**Symptoms:** `predict` p95 jumps, timeouts, `ModelServer` error log growth, CPU saturation on serving hosts.

**Diagnose (0–10 min):**
1. Confirm scope: one model or all? One model → bad promotion; all → infra/feature store.
2. Check production pointer: which `modelId` is live in `ModelRegistry`? When was `promoteToProduction` last called and by whom?
3. Check `ModelServer` latency tracker per model; correlate with deploy time.
4. Check `FeatureStore` online miss rate — a miss storm forces fallback/default features and can inflate latency.

**Mitigate (10–20 min):**
- Single-model regression: roll back the production pointer to the previous version (`promoteToProduction(previousModelId)`), then `undeploy`/`deploy` the rolled-back version. Verify p95 recovers for 10 min.
- All-model latency: scale serving replicas horizontally first; do NOT tune model code during the incident.
- If a recent `TrainingPipeline` run auto-promoted: freeze auto-promotion until post-mortem.

**Do NOT:** edit hyperparameters or retrain during the incident; push an untested registry entry to production.

## 4. Runbook: Wrong Predictions — Stale Features or Drift

**Symptoms:** latency normal, accuracy/business metric drops, `DriftDetector` PSI alert fires, `ExperimentTracker` best-run comparison disagrees with live metrics.

**Diagnose:**
1. Read `DriftDetector` alert history: which feature group, what PSI vs threshold, since when?
2. Check `FeatureStore.ingestOnline` lag per group (`user_features` etc.): is online store hours behind offline export?
3. Compare live prediction distribution vs `ExperimentTracker` validation metrics for the promoted run — divergence confirms serving/training skew (e.g., different imputation, different `ChunkingStrategy`-style preprocessing).

**Mitigate:**
- If ingestion stalled: resume backfill job, monitor freshness back under 5 min before declaring recovery.
- If PSI breach with fresh features (true concept drift): roll back to last known-good model version that is robust to the shift, then schedule retraining on recent data — do not retrain on the stale window.
- If A/B test imbalance (`ABTestFramework` assignment skew) is polluting the read: stop the test, pin 100% to control, then re-analyze.

## 5. Runbook: Training / Registry / Experiment Anomalies

- **Training runs failing:** check `TrainingPipeline` config (train-split, hyperparameters) for the failing run vs last green run; quota/GPU exhaustion is the most common cause — check scheduler queue before code.
- **Registry promotion dispute:** `ModelRegistry` archival list is the source of truth; never re-register the same artifact path under a new ID to "fix" — promote the existing versioned ID so audit trail survives.
- **`ExperimentTracker` metric conflict:** metric name mismatch (e.g., `accuracy` vs `acc`) silently breaks best-run comparison; normalize metric logging before trusting winner selection.

## 6. Post-Incident Checklist

- [ ] Production pointer history captured (before/after model IDs, timestamps, actor)
- [ ] PSI alert + feature freshness graphs attached
- [ ] Rollback verified for ≥ 30 min of stable p95 + business metric
- [ ] Freeze/reenable auto-promotion explicitly recorded
- [ ] Action items: freshness monitor, promotion canary, drift threshold review
