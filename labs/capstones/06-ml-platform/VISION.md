# VISION — ML Platform Capstone

> Build the platform that takes a model from notebook to production and keeps
  it correct: features, training, registry, serving, monitoring, and retraining.

## Why this capstone

The model is the easy 5% of ML. The platform is the other 95%: point-in-time
correct features, reproducible training runs, a registry with gates, a serving
path with a training/serving parity guarantee, drift monitoring that pages, and
retraining that cannot silently degrade a model.

## The Arc

1. **Features** — offline/online, point-in-time correctness, skew detection.
2. **Train** — reproducible runs, seeds, data snapshots, experiment tracking.
3. **Register** — a model registry with promotion gates and rollback.
4. **Serve** — low latency, parity with training, shadowing, canary.
5. **Operate** — drift, quality, cost, and automated retraining with a guard.

## Milestones (checkable)
- [ ] M1: build a feature pipeline with a leak test that fails on purpose.
- [ ] M2: make a training run fully reproducible from a data snapshot + code hash.
- [ ] M3: register a model with gates (offline metric, latency, fairness).
- [ ] M4: detect a training/serving skew incident in a controlled experiment.
- [ ] M5: build a retraining loop that refuses to promote a worse model.

## Anti-Goals
- Promoting on a single offline metric.
- Retraining on a schedule with no comparison against the incumbent.
- A feature store where the serving code re-implements the transform.

## Interview Lens
- "How do you know a model is degrading in production?"
- "How do you roll back a model in 30 seconds?"
- "What stops retraining from making things worse?"

## 30-Day Plan
- Wk1 features with a leak test + parity harness.
- Wk2 reproducible training + registry with gates. Wk3 serving + shadow/canary.
- Wk4 drift monitoring + guarded retraining.

## Done = You Can
- Explain how a model reaches production, how you would know it is failing, and
  how you would make it better without making it worse.
