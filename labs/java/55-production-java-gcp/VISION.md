# VISION — Production Java on GCP

## 1. Thesis

GCP rewards Java teams that go serverless-first and let the platform
absorb undifferentiated work: Cloud Run for bursty services, GKE
Autopilot when Kubernetes control matters, Cloud SQL + AlloyDB for
durable state, BigQuery for analytics off the transactional path.
Vision: **one Spring Boot artifact, scale-to-zero where idle, GKE
where steady — with traces and costs joined per service.**

## 2. Reference shape

Cloud Load Balancer → Cloud Run (min/max instances, concurrency per
instance) or GKE Autopilot → Cloud SQL (HA, PITR) + Memorystore Redis;
Pub/Sub for events; Secret Manager + Workload Identity (no static
keys); Artifact Registry + Cloud Build; Cloud Trace/Monitoring + OTel.

## 3. Cost / latency tradeoffs

| Choice | Latency effect | Cost effect |
|--------|---------------|-------------|
| Cloud Run scale-to-zero | Cold starts (mitigate: min instances, CRaC/native) | ~Zero idle cost |
| GKE Autopilot | Control, steady throughput | Pay per pod-request, no node mgmt |
| Cloud SQL HA + read replicas | −read p99 | Replica + storage cost |
| Pub/Sub vs Kafka | Pub/Sub: ops-free, at-least-once | Wins until very high sustained MB/s |
| BigQuery offload | −OLTP pressure | Scan-based; partition/cluster tables |

Rule: analytics queries never touch Cloud SQL — export to BigQuery
and keep the transactional p99 clean.

## 4. Career trajectory

Operator (Run revisions + logs) → Tuner (concurrency, min-instances,
PITR drills) → Architect (GKE vs Run decisions, cost per service) →
Platform owner (golden services, org SLOs, FinOps). GCP fluency +
JVM tuning transfers directly to any cloud.

## 5. Six-month learning path

```
Month 1-2: Cloud Run deploys, probes, concurrency tuning; secrets + IAM.
Month 3-4: Cloud SQL HA + PITR drill; Memorystore caching; Cloud Trace.
Month 5:   Pub/Sub events, migration jobs, Monitoring SLOs + runbooks.
Month 6:   BigQuery export, cost per service, rollback + exit drill.
```

## 6. Success bar

99.9% availability design, p99 < 300 ms at 5x load, RPO ≤ 5 min /
RTO ≤ 30 min demonstrated, rollback written and rehearsed.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://cloud.google.com/kubernetes-engine/docs/
- https://cloud.google.com/run/docs/
- https://cloud.google.com/sql/docs/
