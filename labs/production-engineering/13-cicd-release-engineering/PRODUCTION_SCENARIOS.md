# PRODUCTION SCENARIOS: CI/CD, GitOps & Release Engineering War Stories
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The Coupled Database Column Rename Rolling Outage

### 1. Incident Context & Architecture
- **Service**: `user-authentication-service` (Spring Boot 3.x, 40 replicas on AWS EKS).
- **Incident**: An engineering team deployed a database migration and code change simultaneously in Release v2.4.0.
- **The Intended Change**: Renaming column `users.password_hash` to `users.credential_hash`.

### 2. The Disaster During Rolling Update
At 14:10 UTC, the Helm rolling update was initiated:
- Kubernetes started terminating old v1 pods and creating new v2 pods.
- Release v2.4.0 included a Flyway migration that executed:
  ```sql
  ALTER TABLE users RENAME COLUMN password_hash TO credential_hash;
  ```
- **The Catastrophic Failure**:
  - The migration completed in 200ms.
  - However, **30 out of 40 pods were still running old v1 code**!
  - As soon as the column was renamed, all 30 running v1 pods attempting to authenticate users began throwing:
    ```text
    org.postgresql.util.PSQLException: ERROR: column "password_hash" does not exist
    ```
  - User login success rate collapsed from $99.9\%$ to **$25\%$**.
  - Total outage duration: **35 minutes**, impacting over 120,000 active users.

### 3. The Failed Rollback Attempt
The on-call engineer attempted to roll back the deployment to v1 (`kubectl rollout undo`):
- All new v2 pods were terminated and replaced with old v1 pods.
- **The System Did Not Recover!** Old v1 pods still failed because the database column in PostgreSQL remained renamed as `credential_hash`!
- The team had to frantically craft an emergency manual SQL migration:
  `ALTER TABLE users RENAME COLUMN credential_hash TO password_hash;`
  to restore service.

### 4. Systemic Post-Mortem Remediation
Adopted the **Expand-Contract Architecture Standard**:
- Code and schema changes were decoupled into separate weekly release cadences.
- Direct column renames were strictly banned by CI linters; all renames must proceed through the 5-phase Expand-Contract parallel-run pipeline with feature-flagged read switches.

---

## Scenario 2: The Mutable `:latest` Tag Divergence & Phantom Autoscaling Bug

### 1. Incident Context & Architecture
- **Service**: `inventory-reservation-service` (12 replicas).
- **Configuration**: Deployment manifest specified:
  ```yaml
  image: registry.corp.internal/inventory:latest
  imagePullPolicy: IfNotPresent
  ```

### 2. The Mystery Bug
For two weeks, the platform functioned normally. On a Thursday afternoon, traffic increased due to a marketing promotion, triggering the Horizontal Pod Autoscaler (HPA) to scale the deployment from 12 pods to 24 pods:
- Suddenly, **50% of inventory reservation calls began failing with obscure serialization errors**!
- The remaining 50% of requests succeeded perfectly!
- All 24 pods reported identical image tags (`registry.corp.internal/inventory:latest`).
- Engineers spent 4 hours fruitlessly checking network connections, Redis caches, and database locks.

### 3. Forensic Discovery
An SRE inspected the container image SHA-256 digests across the worker nodes:
```bash
kubectl get pods -l app=inventory -o custom-columns=NAME:.metadata.name,IMAGE_ID:.status.containerStatuses[0].imageID
```
*The Shocking Output*:
- **Pods 1 through 12**: Running digest `sha256:7f9a...` (Built 14 days ago).
- **Pods 13 through 24 (New HPA pods)**: Running digest `sha256:b42c...` (Built 2 days ago by an unvetted experiment merged to main)!
- Because `imagePullPolicy` was `IfNotPresent`, older nodes kept their cached image from 2 weeks prior, while new worker nodes spun up by Karpenter pulled the newly pushed `:latest` image!
- Half the cluster was running old code, and half was running unreleased experimental code under the exact same tag!

### 4. Production Remediation
1. Replaced all mutable tags with immutable cryptographic SHA-256 digest references: `image@sha256:...`.
2. Deployed a Kyverno admission policy that blocks any pod creation using `:latest` or mutable semantic tags.

---

## Scenario 3: The Argo Rollouts Automated Canary Save

### 1. Incident Context
- **Service**: `recommendation-feed-service` (Java 21).
- **Workload**: 40,000 requests/sec.
- **The Defect**: A developer introduced a subtle memory leak: every user request created an un-evicted entry in an unbounded in-memory cache.

### 2. The Canary Execution & Autonomous Catch
At 10:00 UTC, ArgoCD initiated the canary rollout of Release v3.8.0:
- **10:00 UTC**: Argo Rollouts routed **$5\%$ of traffic** (2,000 req/sec) to a single Canary pod. $95\%$ of traffic remained on the 19 Stable baseline pods.
- **10:05 UTC**: The Prometheus `AnalysisTemplate` began evaluating the 5-minute rolling window:
  - Error rate: $0.01\%$ (Passed).
  - P99 Latency: $18\text{ms}$ (Passed).
  - **Metric 3: Canary GC Pause Frequency & Heap Growth Rate**:
    ```promql
    rate(jvm_gc_pause_seconds_count{rollouts_pod_template_hash="canary"}[2m])
    ```
    The Canary pod's GC frequency climbed by **$420\%$** relative to the Baseline pods due to rapid Eden space exhaustion.
- **10:08 UTC**: The Automated Canary Analysis failed 3 consecutive health evaluations.
- **10:08:02 UTC**: **Argo Rollouts autonomously aborted the rollout and reverted traffic weight to 100% Stable baseline in 1.2 seconds!**

### 3. Business Outcome
- **Zero Customer Outage**: Only $5\%$ of users were exposed to a minor latency bump for 8 minutes; core checkout was completely unaffected.
- The defect was caught, isolated, and rolled back autonomously without paging an on-call engineer or convening a war room!

---

## Scenario 4: The Concurrent Flyway Startup Deadlock Cascade

### 1. Incident Context
- **Fleet**: 50 microservices sharing a high-availability PostgreSQL database cluster.
- **Configuration**: Every service had `spring.flyway.enabled: true` in its base template.

### 2. The Cluster-Wide Meltdown
Following a cluster-wide Kubernetes node patching event, 25 microservice deployments (over 200 pods) were rebooted simultaneously across the worker nodes:
- All 200 pods booted at the exact same moment.
- Every pod connected to PostgreSQL and attempted to execute:
  `LOCK TABLE flyway_schema_history IN ACCESS EXCLUSIVE MODE;`
- With 200 concurrent transactions competing for exclusive table locks, PostgreSQL's lock manager exhausted its shared lock table memory (`max_locks_per_transaction`).
- Over 140 pods failed with `FlywayException: Unable to obtain table lock` and crashed.
- Kubernetes restarted the crashed pods, which immediately re-bombarded PostgreSQL with new lock requests, locking the entire cluster into an unrecoverable **CrashLoopBackOff storm**.

### 3. Production Remediation
1. Disabled Flyway in all Spring Boot application YAML files (`spring.flyway.enabled: false`).
2. Migrated all schema migrations into isolated ArgoCD `PreSync` Kubernetes Jobs that run sequentially before deployments begin.
3. Pod startup times dropped by $30\%$, and migration lock collisions were permanently eliminated.
