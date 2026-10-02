# VISION — Modern Java in the Cloud

## 1. The thesis

Java lost the first cloud decade (heavyweight JVMs on tiny VMs, slow
cold starts billed by the millisecond) and is winning the second: virtual
threads erased the async-complexity tax, containers made the JVM's memory
model explicit and tunable, and native images + CRaC attacked startup.
The vision: **write ordinary Java, ship one artifact, run it well on any
of the three clouds** — portability as architecture, not accident.

## 2. Philosophy: boring portability, sharp edges contained

- **Boring core**: Jakarta EE / MicroProfile APIs, 12-factor config,
  OpenTelemetry traces, standard health endpoints. This 80% never changes
  between clouds.
- **Sharp edges, isolated**: one module per cloud for IAM, managed data,
  provider queues, and IaC. Labs 54–56 each own exactly one sharp edge;
  nothing else imports cloud SDKs.
- **Managed-service gravity is real**: RDS/Aurora, AlloyDB, Azure SQL pull
  architectures toward one provider. Counter it with repository ports,
  standard SQL, and export-tested backups — decide lock-in consciously,
  per service, with an exit drill.

## 3. Why Java, now

Mature observability (JFR, Micrometer, mature APM agents), the deepest
hiring pool, virtual threads collapsing "reactive vs simple" into simple,
and frameworks (Quarkus, Micronaut, Spring Boot 3) that build
container-first. The JVM's explicit memory model — a liability on
unbounded VMs — becomes an asset under cgroup limits: you can *prove* fit.

## 4. What "production" means (the bar for labs 54–56)

Every production lab must demonstrate: health-gated deploys, externalized
secrets, traced requests end-to-end, autoscaling on a real signal,
multizone data, backup/restore proof, cost attribution per service, and a
written rollback. Anything less is a demo with a cloud bill.
