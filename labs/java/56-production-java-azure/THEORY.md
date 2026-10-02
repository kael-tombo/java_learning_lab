# THEORY — Production Java on Azure

## 1. Compute choice: AKS vs Container Apps vs Functions

- **AKS** (this lab's default): full Kubernetes — HPA + KEDA (event-driven
  autoscaling on queue length/lag, not just CPU), AGIC-managed App Gateway
  ingress, Azure CNI networking.
- **Container Apps**: serverless K8s (KEDA + Dapr building blocks out of
  the box) with scale rules + min/max replicas — the Cloud Run analogue;
  native/CRaC artifacts from lab 53 fit here.
- **Functions**: only tariff-shaped event handlers (timers, queue
  triggers) — never the steady API.

## 2. Data gravity, Microsoft edition

Flexible Server PostgreSQL (zone-redundant HA + PITR; **restore drill
proves RPO**), Azure Cache for Redis (TLS + keys in Key Vault), Service
Bus (queues/topics/sessions/DLQ — enterprise messaging with transactions
and duplicate detection) vs Event Hubs (Kafka-protocol streaming, replay,
capture). Service Bus for commands, Event Hubs for telemetry — the same
broker-vs-log split as lab 14, in Azure dress.

## 3. Identity: managed identity federation or it didn't happen

Connection strings with passwords in app config are the Azure breach
classic. **Workload identity federation** binds K8s ServiceAccounts to
Entra managed identities — short-lived tokens, nothing stored. Flexible
Server supports Microsoft Entra auth directly (no DB passwords at all);
Key Vault references (CSI driver or env) carry the rest with rotation.

## 4. Rollout + rollback, Azure tooling

App Gateway health probes (actuator readiness) gate each rolling batch;
HPA + KEDA scale on latency/queue signals; Deployment Stacks/Bicep make
infra declarative and deletable as a unit. Same migration law (backward-
compatible, expand-then-contract) and rollback bundle (previous image +
reversibility proof) as the other clouds.
