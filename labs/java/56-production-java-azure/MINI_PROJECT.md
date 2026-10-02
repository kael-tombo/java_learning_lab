# MINI_PROJECT — Catalog API on AKS + Container Apps

Deploy the lab-53 service twice from one image:

1. **AKS** (steady API): VNet + AGIC, HPA + KEDA (queue backlog scaler on
   an orders queue), Flexible Server, Redis, Service Bus + DLQ, federated
   identity, Key Vault CSI, Flyway Job, Bicep/Deployment-Stack rollout.
2. **Container Apps** (spiky webhook slice): scale rules + min/max,
   native/CRaC variant for the cold path, Dapr pub/sub optional.
3. PITR restore drill (canary diff), poison-session drill (DLQ proof),
   KEDA-vs-HPA backlog shootout with drain-time numbers.
4. Tagged bill after 7 days: AKS vs Container Apps split + reservation
   recommendation on the proven-steady slice + rollback drill.

Deliverable: repo (Bicep + manifests + runbooks) + ops report.
