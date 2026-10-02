# FLASHCARDS — GCP

| # | Front | Back |
|---|-------|------|
| 1 | Compute trio? | Autopilot (managed) / Standard (own pools) / Run (scale-to-zero). |
| 2 | Ingress health? | Gateway readiness path gates rollout. |
| 3 | Workload Identity? | KSA→GSA federation; no exported JSON keys. |
| 4 | Secrets path? | Secret Manager → env/volumes; rotation scheduled. |
| 5 | DB HA + proof? | Regional HA + PITR; restore drill proves RPO. |
| 6 | Redis hardening? | TLS + AUTH from Secret Manager. |
| 7 | Pull vs push? | Workers lease/ack vs HTTP OIDC push. |
| 8 | Ordering keys? | Per-key order at throughput ceiling; shard hot keys. |
| 9 | Poison handling? | DLQ topic + max attempts → quarantine. |
| 10 | Concurrency math? | Instances ≈ RPS·latency/concurrency; virtual threads raise it free. |
| 11 | SLO alerting? | Burn-rate on p99/errors, not raw thresholds. |
| 12 | Flyway placement? | Pre-deploy Job (same race argument). |
| 13 | Migrations rule? | Backward-compatible, expand-then-contract. |
| 14 | Discount stack? | Sustained-use + committed-use on proven-steady baseline. |
| 15 | Run concurrency pick? | Sweep 10–200; knee = production value. |
