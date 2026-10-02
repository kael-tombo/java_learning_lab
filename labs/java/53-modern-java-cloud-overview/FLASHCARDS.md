# FLASHCARDS — Cloud overview

| # | Front | Back |
|---|-------|------|
| 1 | Vision in one line? | Ordinary Java, one artifact, runs well on any of the 3 clouds. |
| 2 | Boring vs sharp? | Boring portable core (80%); one sharp module per cloud (IAM/data/queues/IaC). |
| 3 | Container JVM flag? | MaxRAMPercentage (tracks cgroup), never fixed -Xmx. |
| 4 | f vs L rule? | Smaller limit → lower f (non-heap doesn't shrink). |
| 5 | Non-root + layered why? | Least privilege; rebuilds ship app layer only. |
| 6 | Startup trio? | JVM 2–10 s / native ~0.1 s / CRaC ~0.2 s restore. |
| 7 | Virtual threads change? | Blocking code saturates I/O — reactive only for backpressure. |
| 8 | Pinning fix? | ReentrantLock instead of synchronized. |
| 9 | Observability four? | JSON stdout logs, Micrometer RED, OTel traces, JFR dives. |
| 10 | Probes gate what? | Rolling deploys + routing (readiness) / restarts (liveness). |
| 11 | Secrets rule? | Secret manager injection; never baked into layers. |
| 12 | Gravity antidote? | Ports, standard SQL, export-tested backups, conscious lock-in. |
| 13 | Labs 54–56 are? | Three implementations of this vision (AWS/GCP/Azure). |
| 14 | Cold-start math? | λ·S·mem·p — burstiness decides native/CRaC. |
| 15 | Scorecard rows? | Compute, container, serverless, data, messaging, observability, identity, IaC. |
