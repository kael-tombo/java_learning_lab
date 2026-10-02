# THEORY — Production Java on GCP

## 1. Compute choice: GKE Autopilot vs Standard vs Cloud Run

- **Autopilot** (this lab's default): Google manages nodes; you declare
  pod requests — pay per pod resources, HPA + readiness gates as usual.
- **Standard**: you own node pools (Tau/ARM options, Spot mixing) —
  cheaper at steady scale, more YAML.
- **Cloud Run**: request-driven, concurrency-per-instance tuning, min/max
  instances, scale-to-zero — the native/CRaC artifacts from lab 53 shine
  here. Same container, different front door (no K8s manifests).

## 2. Data gravity, Google edition

AlloyDB (PostgreSQL-compatible, columnar acceleration) or Cloud SQL
PostgreSQL — both HA regional + PITR; **restore-drill proves RPO**.
Memorystore Redis with AUTH + TLS. Pub/Sub: topics → subscriptions (pull
for workers, push for HTTP endpoints), ordering keys for per-key order,
dead-letter topics for poison messages (the lab-14 DLQ pattern, managed).

## 3. Identity: Workload Identity or it didn't happen

Exported service-account JSON keys are the GCP breach classic. **Workload
Identity** federates KSA→GSA — pods get short-lived tokens, nothing to
rotate or leak. Cloud SQL connections via Auth Proxy sidecar or AlloyDB
connectors; secrets from Secret Manager (mounted/env), never baked.

## 4. SLOs as code, rollouts gated

Cloud Monitoring SLOs (burn-rate alerts on p99/errors) + Gateway/Ingress
readiness gating + Cloud Deploy progressive rollout (canary → stable).
Same backward-compatible-migration rule as AWS (expand-then-contract);
same rollback bundle (previous revision + reversibility proof).
