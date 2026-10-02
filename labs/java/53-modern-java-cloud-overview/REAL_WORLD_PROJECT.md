# REAL_WORLD_PROJECT — Multi-cloud product API

Production-grade product-catalog API (the lab-05 domain, re-homed):

- **Portable core**: Spring Boot 3 + virtual threads, actuator probes,
  Micrometer/Prometheus, OTel traces, Flyway migrations, Testcontainers
  integration tests.
- **Per-cloud adapters**: AWS (54), GCP (55), Azure (56) modules for
  secrets, managed Postgres, and queue integration behind ports.
- **Ops proof**: IaC for one cloud, health-gated deploy, autoscaling on
  latency, multizone DB with PITR-tested restore, cost dashboard per
  service, written rollback + exit drill (export + repoint to a second
  cloud, timed).
- **Acceptance**: 99.9% monthly availability design, p99 < 300 ms at
  5× baseline load, RPO ≤ 5 min / RTO ≤ 30 min demonstrated, not asserted.
