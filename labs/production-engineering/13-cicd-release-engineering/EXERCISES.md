# EXERCISES: CI/CD, GitOps & Enterprise Release Engineering
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Building an Argo Rollouts Canary with Prometheus Analysis & Auto-Rollback

### 1. Objective
Deploy an Argo Rollouts progressive canary pipeline, simulate a code regression that injects latency into the canary pod, and observe Argo Rollouts detect the metric failure and autonomously abort and rollback within 1 second.

### 2. Implementation Tasks
1. Deploy the Argo Rollouts controller and Prometheus into your local Kubernetes cluster (k3d / Minikube).
2. Deploy the `payment-service-rollout` and `canary-health-metrics` AnalysisTemplate from Pattern 1 of CODE DEEP DIVE.
3. Verify the stable baseline is running with 10 replicas:
   ```bash
   kubectl argo rollouts get rollout payment-service-rollout
   ```
4. Trigger a rollout with a flawed image that introduces a 150ms artificial sleep:
   ```bash
   kubectl argo rollouts set image payment-service-rollout payment-service=registry.corp.internal/payments:v3.5.0-buggy
   ```
5. Launch a load generator sending 500 requests/sec across the service.
6. Watch the real-time rollout dashboard:
   ```bash
   kubectl argo rollouts get rollout payment-service-rollout --watch
   ```
7. Verify that:
   - $5\%$ of traffic routes to the canary pod.
   - Prometheus records P99 latency $> 100\text{ms}$ on the canary pod.
   - AnalysisTemplate fails 3 consecutive iterations.
   - Argo Rollouts marks the rollout as `Degraded`, aborts promotion, and routes $100\%$ of traffic back to the Stable baseline automatically.

---

## Exercise 2: Implementing the 5-Phase Expand-Contract Database Migration in Java

### 1. Objective
Execute a zero-downtime database column renaming pipeline (`users.phone` $\rightarrow$ `users.mobile`) across simulated rolling updates, verifying that neither old v1 pods nor new v2 pods drop a single read or write query.

### 2. Implementation Tasks
1. Start a local PostgreSQL instance and create table `users(id SERIAL PRIMARY KEY, name TEXT, phone TEXT)`.
2. Insert 100,000 synthetic customer records with legacy phone numbers.
3. **Phase 1 (Expand)**:
   - Execute migration: `ALTER TABLE users ADD COLUMN mobile VARCHAR(32);`
4. **Phase 2 (Dual-Write)**:
   - Run a simulated v2 worker pool that performs 1,000 updates/sec writing to both `phone` and `mobile` using the `ExpandContractUserRepository` pattern.
   - Simultaneously run simulated v1 legacy read workers querying `phone`. Verify $0\%$ error rate.
5. **Phase 3 (Async Backfill)**:
   - Execute an asynchronous Java batch worker that scans records where `mobile IS NULL` and updates them in batches of 1,000 with a 50ms pause.
   - Verify all 100,000 historical rows now have non-null `mobile` values.
6. **Phase 4 (Read New)**:
   - Enable feature flag `read-from-new-mobile-schema = true`. Verify reads now pull from `mobile`.
7. **Phase 5 (Contract)**:
   - Deploy v3 code that stops referencing `phone`.
   - Execute final DDL: `ALTER TABLE users DROP COLUMN phone;`
   - Verify zero failed queries throughout the entire 5-phase evolution!

---

## Exercise 3: Hermetic Container Build & Cryptographic Signing via Cosign

### 1. Objective
Build an immutable, minimal Distroless container image for Spring Boot, generate an SBOM, cryptographically sign it with Sigstore Cosign, and enforce verification with a Kyverno cluster admission policy.

### 2. Implementation Tasks
1. Build the multi-stage Distroless container image from Pattern 3 of CODE DEEP DIVE:
   ```bash
   docker build -t ttl.sh/corp/secure-payment:1h .
   docker push ttl.sh/corp/secure-payment:1h
   ```
2. Generate an SBOM using Syft:
   ```bash
   syft ttl.sh/corp/secure-payment:1h -o cyclonedx-json > sbom.json
   ```
3. Generate a local Cosign keypair:
   ```bash
   cosign generate-key-pair
   ```
4. Sign the container image:
   ```bash
   cosign sign --key cosign.key ttl.sh/corp/secure-payment:1h
   ```
5. Deploy a Kyverno policy in Kubernetes enforcing signature verification:
   - Attempt to deploy an unsigned container image $\rightarrow$ verify Kyverno **rejects** the pod with an admission denial.
   - Attempt to deploy the signed container image $\rightarrow$ verify Kyverno **accepts** and schedules the pod successfully.

---

## Exercise 4: Simulating and Resolving a GitOps Configuration Drift Incident

### 1. Objective
Experience and verify ArgoCD's automated drift detection and self-healing mechanics when unauthorized out-of-band changes are made to a production cluster.

### 2. Implementation Tasks
1. Deploy an ArgoCD Application tracking a GitHub repository containing a deployment with 4 replicas.
2. Verify ArgoCD status is `Synced` and `Healthy`.
3. Simulate an unauthorized out-of-band mutation via raw `kubectl`:
   ```bash
   kubectl scale deployment payment-service --replicas=10
   kubectl set env deployment payment-service INJECTED_FLAG="UNAUTHORIZED"
   ```
4. Watch ArgoCD detect the drift:
   - Note the status transitions to `OutOfSync`.
5. Enable automated self-healing on the ArgoCD Application:
   ```bash
   argocd app set payment-service --self-heal --auto-prune
   ```
6. Observe the immediate reconciliation:
   - Within 60 seconds, ArgoCD scales the deployment back to 4 replicas and purges the unauthorized environment variable.
   - Verify that Git remains the single, inviolable source of truth.
