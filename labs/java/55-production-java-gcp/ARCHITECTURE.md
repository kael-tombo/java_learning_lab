# ARCHITECTURE — GCP production topology

```
Cloud DNS → Global LB (health: /actuator/health/readiness)
  → GKE Autopilot (private, 3 zones)  — or —  Cloud Run (spiky slices)
      → Java pods (HPA: p99 + CPU; KSA→GSA Workload Identity)
        → AlloyDB / Cloud SQL PostgreSQL (HA + PITR)
        → Memorystore Redis (TLS + AUTH, Secret Manager)
        → Pub/Sub (topics/subscriptions + DLQ topics)
  Observability: Cloud Monitoring (SLO burn) + Cloud Trace + Profiler
  Supply: Artifact Registry → Cloud Deploy (canary → stable)
  Secrets: Secret Manager → env/volumes; rotation scheduled
```

| Concern | GCP service | Java wiring |
|---|---|---|
| Ingress | GCLB + Gateway | readiness probe path |
| Compute | GKE Autopilot (or Cloud Run) | MaxRAMPercentage; concurrency tune |
| RDBMS | AlloyDB / Cloud SQL PG | Flyway job; Auth Proxy/connector |
| Cache | Memorystore Redis | Lettuce + TLS + AUTH |
| Events | Pub/Sub | pull subs (workers), push (HTTP) |
| Metrics/SLO | Cloud Monitoring | Micrometer + burn-rate alerts |
| Traces | Cloud Trace (+Profiler) | OTel GCP exporter |
| Identity | Workload Identity | KSA annotation, no JSON keys |
| Images | Artifact Registry | layered Dockerfile (lab 53) |
| IaC | Terraform + Cloud Deploy | workspace per env + labels |
