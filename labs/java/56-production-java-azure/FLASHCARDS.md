# FLASHCARDS — Azure

| # | Front | Back |
|---|-------|------|
| 1 | Compute trio? | AKS (full K8s) / Container Apps (serverless+Dapr) / Functions (events). |
| 2 | Ingress probe? | App Gateway → actuator readiness; gates batches + routing. |
| 3 | Federation? | SA↔managed identity via OIDC; short-lived tokens. |
| 4 | Secrets path? | Key Vault references (CSI/env); rotation scheduled. |
| 5 | DB HA + proof? | Zone-redundant + PITR; restore drill proves RPO. |
| 6 | Redis hardening? | TLS + Key Vault keys. |
| 7 | Commands vs streams? | Service Bus (queues/sessions/DLQ) vs Event Hubs (Kafka/replay). |
| 8 | Poison handling? | DLQ + maxDeliveryCount → quarantine. |
| 9 | Hot session? | Serialization ceiling — shard or drop sessions. |
| 10 | KEDA trigger? | Queue backlog (messageCount) — work-native scaling. |
| 11 | SLO alerting? | Burn-rate on Monitor; traces in App Insights. |
| 12 | Flyway placement? | Pre-deploy Job (same race argument, third cloud). |
| 13 | Migrations rule? | Backward-compatible, expand-then-contract. |
| 14 | Spot rule? | Batch only; never the serving path. |
| 15 | Buy-down basis? | Measured-steady baseline only. |
