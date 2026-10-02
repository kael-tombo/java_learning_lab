# REAL_WORLD_PROJECT — GCP production platform

Lab-53 real-world project, GCP-flavored, acceptance-gated:

- **Topology**: ARCHITECTURE.md as built (GKE + Run slices, AlloyDB,
  Memorystore, Pub/Sub + DLQs).
- **SLOs**: 99.9% monthly, p99 < 300 ms at 5× baseline, RPO ≤ 5 min / RTO ≤
  30 min — demonstrated via drills, load tests, restore diffs.
- **Security**: Workload Identity everywhere, secret rotation, VPC-SC
  perimeter review, Binary Authorization on deploy, Cloud Audit Logs on.
- **Ops**: on-call runbook (5xx spike, DB failover, zone loss, poison
  backlog, bad deploy), quarterly game-day, monthly cost review
  (Autopilot-vs-Standard + committed-use on proven baseline).
- **Exit drill**: export-tested backup repointed cross-region (or second
  cloud per lab 53), timed and documented.
