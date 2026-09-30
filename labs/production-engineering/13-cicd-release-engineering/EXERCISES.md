# EXERCISES: Release Engineering & Deployment Strategies
## Lab 13 | Production Engineering Academy

---

## Exercise 1: Zero-Downtime Database Migration Simulation

### Objective
Execute an end-to-end zero-downtime column rename using the Expand-Contract pattern under active multi-threaded traffic.

### Tasks
1. Start an in-memory database with table `users(id, username, phone_number)`.
2. Launch a background thread generating 100 read and write requests per second simulating running v1 application code.
3. Apply Phase 1 Liquibase migration adding nullable `contact_number`. Verify background traffic continues with 0 errors.
4. Update code to dual-write to `contact_number` and `phone_number`. Deploy v2 code while verifying 0 errors.
5. Backfill historical rows: `UPDATE users SET contact_number = phone_number WHERE contact_number IS NULL`.
6. Deploy v3 code reading from `contact_number`.
7. Apply Phase 2 Liquibase migration dropping `phone_number`. Verify 0 errors throughout entire lifecycle.

---

## Exercise 2: Configure Argo Rollout Analysis Template

### Tasks
1. Write a complete Kubernetes `Rollout` manifest with canary steps: 10% -> 25% -> 50% -> 100%.
2. Attach Prometheus analysis template measuring HTTP error rate.
3. Simulate an injected bug returning 5% HTTP 500 errors on Canary pods.
4. Verify that Argo Rollouts detects the threshold violation and triggers an immediate automatic rollback to baseline.
