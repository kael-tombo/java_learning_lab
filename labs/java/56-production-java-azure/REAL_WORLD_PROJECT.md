# REAL_WORLD_PROJECT — Azure production platform

Lab-53 real-world project, Azure-flavored, acceptance-gated:

- **Topology**: ARCHITECTURE.md as built (AKS + Container Apps slices,
  Flexible Server, Redis, Service Bus + DLQ / Event Hubs).
- **SLOs**: 99.9% monthly, p99 < 300 ms at 5× baseline, RPO ≤ 5 min / RTO ≤
  30 min — demonstrated via drills, load tests, restore diffs.
- **Security**: federation everywhere, Key Vault rotation, NSG least-
  privilege, Defender for Cloud + Activity Log on, ACR image scanning.
- **Ops**: on-call runbook (5xx spike, DB failover, zone loss, poison
  backlog, bad deploy), quarterly game-day, monthly cost review
  (reservations on proven baseline, Spot audit for batch).
- **Exit drill**: export-tested backup repointed cross-region (or second
  cloud per lab 53), timed and documented.
