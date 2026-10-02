# THEORY — Production Java on AWS

## 1. Compute choice: EKS vs ECS vs Lambda

- **EKS** (this lab's path): full Kubernetes semantics — HPA, rolling
  deploys, service mesh later. You own node groups (Graviton!), but ALB
  Controller + Cluster Autoscaler do the heavy lifting.
- **ECS/Fargate**: less YAML, AWS-managed placement; HPA via target
  tracking. Fine when you don't need K8s APIs.
- **Lambda**: only for the spiky/event-driven slices (use the native/CRaC
  artifacts from lab 53) — never the steady API (cost + 15-min limits).

## 2. Data gravity, AWS edition

Aurora PostgreSQL Multi-AZ (one writer, async reader; failover ~30–60 s)
with **PITR tested by restore**, not by faith. ElastiCache Redis with
in-transit TLS + AUTH token from Secrets Manager (never env-baked).
MSK when you need Kafka semantics (replay, compaction); SQS/SNS when you
need queues/topics without operating brokers. Choose per access pattern,
not per hype — the decision table is in ARCHITECTURE.md.

## 3. Identity: IRSA or it didn't happen

Static `AWS_ACCESS_KEY_ID` in env is a breach report waiting to happen.
**IRSA** (IAM Roles for Service Accounts) binds a K8s ServiceAccount to
an IAM role via OIDC — pods get short-lived credentials automatically.
Same for DB: IAM database auth or Secrets-Manager rotation, never
password-in-ConfigMap.

## 4. Rollout + rollback discipline

ALB target-group health (actuator readiness) gates each rolling batch;
HPA scales on p99 latency *and* CPU (CPU-only misses queue-bound
saturation). Every deploy ships with its rollback: previous image tag +
migration reversibility check (Flyway `validate`, backward-compatible
migrations only — expand-then-contract).
