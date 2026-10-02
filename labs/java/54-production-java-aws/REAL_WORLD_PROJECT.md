# REAL_WORLD_PROJECT — AWS production platform

The lab-53 real-world project, AWS-flavored, acceptance-gated:

- **Topology**: ARCHITECTURE.md as built (EKS/ALB/Aurora/Redis/MSK-or-SQS).
- **SLOs**: 99.9% monthly, p99 < 300 ms at 5× baseline, RPO ≤ 5 min / RTO ≤
  30 min — all *demonstrated* (drills, load tests, restore diffs).
- **Security**: IRSA everywhere, Secrets rotation, Security Groups least-
  privilege, GuardDuty + CloudTrail on the account, image scanning in ECR.
- **Ops**: on-call runbook (5xx spike, DB failover, AZ loss, bad deploy),
  game-day each quarter, cost review monthly (Graviton + Aurora I/O watch).
- **Exit drill**: export-tested backup repointed at a second region (or
  cloud per lab 53), timed and documented.
