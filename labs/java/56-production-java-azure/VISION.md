# VISION — Production Java on Azure

## 1. Thesis

Azure rewards Java teams embedded in Microsoft estates: Entra ID for
identity, Azure SQL for managed durability, Container Apps for
serverless containers and AKS when control matters. Vision: **one
Spring Boot artifact, health-gated onto Container Apps/AKS, observed
in Azure Monitor — enterprise-compliant by default, portable by design.**

## 2. Reference shape

Front Door / App Gateway → Container Apps (scale rules) or AKS (HPA)
→ Azure SQL (zone-redundant, PITR) + Azure Cache for Redis; Service
Bus / Event Hubs for messaging; Key Vault + managed identity (no
static keys); ACR + Bicep/Terraform; Monitor + App Insights + OTel.

## 3. Cost / latency tradeoffs

| Choice | Latency effect | Cost effect |
|--------|---------------|-------------|
| Container Apps scale-to-zero | Possible cold starts (min replicas fix) | ~Zero idle cost |
| AKS (system + user pools) | Steady, tunable | Node + management overhead |
| Azure SQL serverless / Hyperscale | Autoscale reads/writes | Pause/low-compute savings; watch IO |
| Service Bus vs Event Hubs | Queues vs streams semantics | Bus for commands, Hubs for telemetry |
| Redis for sessions | −p99 on hot reads | Fixed SKU cost |

Rule: pick messaging by pattern (commands → Service Bus, streams →
Event Hubs/Kafka); never let analytics touch the OLTP database.

## 4. Career trajectory

Operator (revisions + Log Analytics) → Tuner (scale rules, SQL
PITR drills) → Architect (AKS vs Container Apps, cost attribution) →
Platform owner (landing zones, policy, org SLOs). Azure + Java is
the enterprise modernization fast lane.

## 5. Six-month learning path

```
Month 1-2: Container Apps/AKS deploys, probes, scaling; Key Vault + identity.
Month 3-4: Azure SQL HA + PITR drill; Redis caching; App Insights tracing.
Month 5:   Service Bus/Event Hubs, migration jobs, Monitor alerts + runbooks.
Month 6:   Cost Management per service, rollback + exit drill, present SLOs.
```

## 6. Success bar

99.9% availability design, p99 < 300 ms at 5x load, RPO ≤ 5 min /
RTO ≤ 30 min demonstrated, rollback written and rehearsed.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://learn.microsoft.com/en-us/azure/aks/
- https://learn.microsoft.com/en-us/azure/container-apps/
- https://learn.microsoft.com/en-us/azure/azure-sql/
