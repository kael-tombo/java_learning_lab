# EXERCISES — GCP

## 1. Keyless proof (beginner)
`unset GOOGLE_APPLICATION_CREDENTIALS` in a debug pod; call a GCP API.
Success = Workload Identity works. Break the IAM binding, record the
exact 403, restore. *Why is this safer than a mounted JSON key in two
concrete attack scenarios?*

## 2. Concurrency sweep (beginner)
Deploy the service to Cloud Run at concurrency 10/40/80/200 under fixed
RPS. Plot instances, p99, cost. Explain the knee and choose production
concurrency with virtual-thread reasoning.

## 3. PITR drill (intermediate)
Canary rows → delete → point-in-time restore to a *new* instance → diff.
Record RPO vs ≤5 min claim. Document the runbook steps verbatim.

## 4. Poison-message drill (intermediate)
Publish 10 malformed messages (no DLQ configured first): watch redelivery
stall the subscription. Add DLQ topic + maxDeliveryAttempts=5, replay,
confirm quarantine + healthy flow resume. Argue the attempts number.

## 5. Ordering-key hotspot (advanced)
Publish 100K msgs on one ordering key vs sharded keys; measure per-key
throughput ceiling in both. Decide for an order-events stream: keep global
order, per-user order, or no order — with the throughput math attached.
