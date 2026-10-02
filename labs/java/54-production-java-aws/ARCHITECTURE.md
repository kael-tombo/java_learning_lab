# ARCHITECTURE — AWS production topology

```
Route53 → ALB (health: /actuator/health/readiness)
  → EKS nodes (Graviton, private subnets, 3 AZ)
      → Java pods (HPA: p99 + CPU; IRSA ServiceAccount)
        → Aurora PostgreSQL Multi-AZ (PITR enabled)
        → ElastiCache Redis (TLS + AUTH, Secrets Manager)
        → MSK (events) / SQS+SNS (queues)
  Observability: CloudWatch (RED alarms) + X-Ray (traces) + JFR sidecar
  Supply: ECR images → CDK pipeline → rolling deploy + rollback tags
  Secrets: Secrets Manager → env/files; rotation scheduled
```

## Service map (ports pattern)

| Concern | AWS service | Java wiring |
|---|---|---|
| Ingress | ALB + target group | readiness probe path |
| Compute | EKS (Graviton nodes) | MaxRAMPercentage per node size |
| RDBMS | Aurora PostgreSQL Multi-AZ | Flyway job, IAM/secret auth |
| Cache | ElastiCache Redis | RedisTemplate + TLS + AUTH |
| Events | MSK (or SQS/SNS) | Kafka binder / SQS listener |
| Metrics/alarms | CloudWatch | Micrometer CloudWatch registry |
| Traces | X-Ray | OTel AWS propagator |
| Identity | IAM IRSA | ServiceAccount annotation |
| Images | ECR | layered Dockerfile (lab 53) |
| IaC | CDK | stack per env + cost tags |
