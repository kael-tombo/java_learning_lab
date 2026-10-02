# MINI_PROJECT — Catalog API on GKE + Cloud Run

Deploy the lab-53 service twice from one image:

1. **GKE Autopilot** (steady API): Gateway + HPA, AlloyDB/Cloud SQL,
   Memorystore, Pub/Sub + DLQ, Workload Identity, Secret Manager, Flyway
   Job, Cloud Deploy canary.
2. **Cloud Run** (spiky webhook slice): concurrency sweep result applied,
   minScale 0 vs 1 costed, native/CRaC variant for the cold path.
3. PITR restore drill (canary diff), poison-message drill (DLQ proof),
   burn-rate alert firing drill (synthetic error budget burn).
4. Labeled bill after 7 days: Autopilot vs Run split with the break-even
   math attached + rollback drill (previous revision).

Deliverable: repo (Terraform + manifests + runbooks) + ops report.
