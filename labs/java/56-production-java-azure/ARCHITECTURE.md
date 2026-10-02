# ARCHITECTURE — Azure production topology

```
Azure DNS → Application Gateway (probe: /actuator/health/readiness)
  → AKS (private VNet, 3 zones)  — or —  Container Apps (spiky slices)
      → Java pods (HPA + KEDA; federated managed identity)
        → Flexible Server PostgreSQL (zone-redundant HA + PITR)
        → Azure Cache for Redis (TLS + Key Vault keys)
        → Service Bus (queues/topics + DLQ) / Event Hubs (streams)
  Observability: Azure Monitor (SLO burn) + Application Insights (traces)
  Supply: ACR images → Bicep/Deployment Stacks → rolling deploy + rollback
  Secrets: Key Vault references (CSI/env); rotation scheduled
```

| Concern | Azure service | Java wiring |
|---|---|---|
| Ingress | App Gateway (AGIC) | readiness probe path |
| Compute | AKS (or Container Apps) | MaxRAMPercentage; KEDA scalers |
| RDBMS | Flexible Server PG | Flyway job; Entra auth/Key Vault |
| Cache | Azure Cache for Redis | Redisson/Lettuce + TLS + key |
| Commands | Service Bus | queues/topics/sessions + DLQ |
| Streams | Event Hubs | Kafka protocol / capture |
| Metrics/SLO | Azure Monitor | Micrometer + burn-rate alerts |
| Traces | Application Insights | OTel Azure exporter |
| Identity | Entra workload federation | SA annotation, no secrets |
| Images | ACR | layered Dockerfile (lab 53) |
| IaC | Bicep / Deployment Stacks | RG per env + tags |
