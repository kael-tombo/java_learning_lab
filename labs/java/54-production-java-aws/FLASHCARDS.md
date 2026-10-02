# FLASHCARDS — AWS

| # | Front | Back |
|---|-------|------|
| 1 | Compute ladder? | EKS (K8s) / ECS (simpler) / Lambda (spiky slices only). |
| 2 | ALB health path? | Actuator readiness; thresholds 2×15 s healthy / 2×5 s sick. |
| 3 | Rolling knobs? | maxUnavailable 0, maxSurge 1 + readiness gate = zero-downtime. |
| 4 | IRSA? | SA↔role via OIDC; short-lived creds; no static keys. |
| 5 | Secrets path? | Secrets Manager → env/files; rotation scheduled. |
| 6 | Aurora HA? | Multi-AZ writer+readers; failover ~30–60 s; PITR drill-proven. |
| 7 | Redis hardening? | TLS + AUTH token from Secrets Manager. |
| 8 | MSK vs SQS? | Replay/compaction vs no-broker-ops queues. |
| 9 | Flyway placement? | Pre-deploy Job, never app startup (race). |
| 10 | HPA signals? | p99 latency AND CPU; min 3 (= AZs). |
| 11 | Observability trio? | CloudWatch RED + X-Ray traces + JFR dives. |
| 12 | Migration rule? | Backward-compatible, expand-then-contract. |
| 13 | Graviton why? | ~15–25% cheaper/vCPU, JVM-neutral — benchmark first. |
| 14 | Cost tags? | service/env/owner on every stack; alert WoW > 15%. |
| 15 | Rollback ships with? | Previous tag + migration reversibility + written runbook. |
