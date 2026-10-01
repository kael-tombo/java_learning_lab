# ANTI-PATTERNS: CI/CD, Release Engineering & Deployment Pathology
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Running Database Migrations on Application Pod Boot

### The Mistake
```yaml
# In application.yml:
spring:
  flyway:
    enabled: true  # Pod executes migrations automatically during Spring context initialization!
```

### Why It Fails
1. **Concurrency Lock Collision**: When Kubernetes scales up a deployment (e.g. 20 new pods starting concurrently during a rolling update), all 20 pods attempt to acquire the Flyway/Liquibase migration table lock (`flyway_schema_history`) simultaneously. Pods fail to acquire the lock within the timeout and enter `CrashLoopBackOff`.
2. **Excessive Security Privileges**: If application pods run DDL migrations, the application's runtime database credentials must possess `ALTER TABLE`, `DROP COLUMN`, and `CREATE TABLE` permissions. If a SQL injection vulnerability exists in the web app, attackers can drop tables.
3. **Slow Boot & Probe Failures**: If a migration script takes 45 seconds to add a large index, the pod's `startupProbe` or `livenessProbe` times out and Kubelet terminates the pod midway through the migration, leaving the schema in an inconsistent, locked state!

### The Correct Production Fix
Run database migrations as a dedicated, isolated **Kubernetes Job** (e.g., an ArgoCD `PreSync` hook) executing with privileged migration credentials *before* application pods are updated:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-job
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: flyway
          image: flyway/flyway:10.0.0
          args: ["migrate"]
      restartPolicy: Never
```

---

## Anti-Pattern 2: The "Big Bang" Monolithic Production Deploy

### The Mistake
Batched releases: holding code back for 3 weeks across 15 engineering teams, packaging 140 disparate Jira issues into a massive "Release Candidate 4.0", and deploying to production after hours on Friday.

### Why It Fails
- **Enormous Blast Radius**: If any of the 140 merged PRs contains a latent bug, the entire production platform fails.
- **Diagnostic Impossibility**: With dozens of services and database changes landing simultaneously, pinpointing which commit introduced the memory leak or latency spike takes hours.
- **Support Vacuum**: Deploying late in the week leaves skeleton crews to triage complex outages over the weekend.

### The Correct Production Fix
1. **Decouple Deployment from Release**:
   - Continuous Delivery: Merge small, atomic PRs to `main` and deploy to production multiple times per day behind **Feature Flags** (LaunchDarkly / Unleash).
   - The code is deployed safely dark; business release occurs by flipping a flag without deploying code.
2. **Automated Progressive Canaries**: Deploy each atomic PR to 5% of traffic before promoting to 100%.

---

## Anti-Pattern 3: Breaking Backward Compatibility in Database Migrations

### The Mistake
Executing a migration that drops or renames a column while the current production code is still running:
```sql
-- DDL executed in production:
ALTER TABLE accounts DROP COLUMN routing_number;
```

### Why It Fails
In any zero-downtime deployment (Rolling Update, Blue/Green, Canary), **the old application version (v1) and the new version (v2) run concurrently for minutes or hours**.
- The moment `routing_number` is dropped in the database, all currently running v1 pods executing `SELECT routing_number` immediately crash with `PSQLException: column "routing_number" does not exist`.
- If the new v2 code has a bug and needs to be rolled back, rollback is impossible because the old code can no longer run against the mutated database schema!

### The Correct Production Fix
Strictly adhere to the **Expand-Contract Pattern**:
1. Phase 1 (Expand): Add new column as nullable.
2. Phase 2: Dual-write to both old and new columns.
3. Phase 3: Asynchronously backfill data.
4. Phase 4: Switch reads to the new column.
5. Phase 5 (Contract): Drop the old column weeks later after verifying stability.

---

## Anti-Pattern 4: Using Mutable Container Image Tags (`:latest` and Semantic Overwrites)

### The Mistake
```yaml
spec:
  containers:
    - name: payment-service
      image: registry.corp.internal/payments:latest # Or re-tagging :v2.1.0 on every commit!
```

### Why It Fails
1. **Non-Deterministic Rollouts**: Pod A pulling `:latest` at 10:00 AM gets build #142. Pod B scheduled at 10:30 AM due to autoscaling pulls build #145. Nodes in the same cluster run different code under the same tag!
2. **Impossible Rollbacks**: Running `kubectl rollout undo` does nothing because the image tag string (`:latest`) hasn't changed.
3. **Kubelet Image Caching**: If Kubelet's `imagePullPolicy` is `IfNotPresent`, the node never pulls the updated `:latest` image because a local image with that tag already exists!

### The Correct Production Fix
Always use **immutable cryptographic SHA-256 digest pinning** or Git commit SHAs:
```yaml
spec:
  containers:
    - name: payment-service
      image: registry.corp.internal/payments@sha256:7f9a8b1c4e2d3f...
```
This guarantees 100% deterministic, reproducible deployments across all nodes.

---

## Anti-Pattern 5: Forward-Fixing in Production Instead of Immediate Rollback

### The Mistake
When a newly deployed release causes a production P1 outage, engineers attempt to "forward-fix" by rapidly pushing hotfix commits directly to `main` without testing:
*"Don't roll back! I see the bug, it's a one-line fix! Just give me 10 minutes to push a patch!"*

### Why It Fails
- Under emergency adrenaline, engineers write rushed, unvetted code that frequently introduces **secondary, worse bugs**.
- CI/CD build, container scan, and deployment pipelines take 15–20 minutes. Customers endure 20 minutes of complete outage while waiting for a forward-fix that might fail.
- A rollback takes **30 seconds** and returns the system to a proven, verified stable baseline.

### The Correct Production Fix
**The 5-Minute Rollback Invariant**:
If an outage begins following a deployment, the mandatory default action is **immediate automated rollback**. Once the rollback completes and customer traffic is green, the team can analyze the defect calmly in staging.

---

## Anti-Pattern 6: Non-Hermetic Builds & Unpinned Dependencies

### The Mistake
Relying on floating dependency ranges in `pom.xml`:
```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-lang3</artifactId>
    <version>[3.12.0, 3.14.0)</version> <!-- Floating version range! -->
</dependency>
```

### Why It Fails
1. A build executed on Monday pulls version 3.12.0 and passes staging tests.
2. An upstream patch (3.13.0) is published on Tuesday with a subtle breaking change.
3. A production hotfix build on Wednesday pulls 3.13.0, introducing an untested dependency directly into production!
4. **Supply Chain Vulnerability**: Unpinned dependencies allow compromised upstream libraries to compromise builds automatically without code review.

### The Correct Production Fix
Enforce **Hermetic Builds with Locked Dependency Checksums**:
- Use exact, static version strings for every dependency and plugin.
- Configure Gradle dependency verification (`verification-metadata.xml`) or Maven Dependency Convergence to verify SHA-256 hashes of every downloaded JAR file.
