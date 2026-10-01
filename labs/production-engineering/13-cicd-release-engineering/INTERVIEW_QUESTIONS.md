# INTERVIEW QUESTIONS: CI/CD, GitOps & Enterprise Release Engineering
## Lab 13 | Senior / Staff / Principal / Distinguished Level

---

## Senior Level (5–7 Years)

### Q1: Why is executing Flyway or Liquibase database migrations during application pod boot (`spring.flyway.enabled=true`) an architectural anti-pattern in Kubernetes?

**Answer:**
Running schema migrations inside the standard application pod lifecycle causes three major production failure modes:

1. **Concurrency Lock Contention & Starvation**:
   When Kubernetes performs a rolling update or scales out a deployment (e.g. 30 new pods starting concurrently), all 30 pods execute migration logic simultaneously. All 30 pods attempt to acquire an exclusive lock on the migration history table (`flyway_schema_history`). Lock acquisition timeouts cause pods to fail and enter **`CrashLoopBackOff`**.
2. **Violation of the Principle of Least Privilege**:
   If application pods execute DDL (`ALTER TABLE`, `DROP COLUMN`, `CREATE INDEX`), the application's runtime database user must possess elevated DDL administrative privileges. If a remote code execution or SQL injection vulnerability is discovered in the web application, attackers gain full schema-altering access to the database.
3. **Probe Timeout & Inconsistent State**:
   If an `ALTER TABLE` statement takes 45 seconds to scan a large table or waits for an exclusive table lock, the pod's `startupProbe` or `livenessProbe` fails. Kubelet terminates the pod midway through the migration, potentially leaving the database in an inconsistent or locked state.

**The Solution**:
Isolate database migrations into a **dedicated Kubernetes Job** (e.g., an ArgoCD `PreSync` hook) executing with privileged migration credentials *before* any application pods are scheduled. Application pods run with restricted DML-only credentials (SELECT, INSERT, UPDATE, DELETE).

---

### Q2: Walk through the 5-phase Expand-Contract pattern for safely renaming a database column with zero downtime.

**Answer:**
Renaming a column directly (`ALTER TABLE users RENAME COLUMN phone TO mobile`) breaks backward compatibility because running v1 application pods expect `phone` while new v2 pods expect `mobile`. The **Expand-Contract (Parallel Run)** pattern solves this in 5 distinct phases:

1. **Phase 1: Expand (Database Migration 1)**:
   Add the new column `mobile` as nullable. Deploy to database. (v1 code continues reading and writing `phone`; zero impact).
2. **Phase 2: Dual-Write (Application Code Release v2)**:
   Deploy application v2. The repository writes to **both** `phone` and `mobile` simultaneously on all updates/inserts. Reads continue to come from `phone`. (Compatible with both v1 and v2).
3. **Phase 3: Asynchronous Backfill (Data Migration Script)**:
   Run an asynchronous background batch job to copy historical data:
   `UPDATE users SET mobile = phone WHERE mobile IS NULL;`
   Executed in batches of 1,000 rows with pauses to prevent database locking.
4. **Phase 4: Read-New (Application Code Release v3)**:
   Deploy application v3. Switch reads to `mobile` (guarded by a feature flag). Application continues dual-writing to both columns as a safety buffer.
5. **Phase 5: Contract (Database Migration 2)**:
   After 14 days of verified production stability, deploy application v4 (stops writing to `phone`) and execute DDL to drop the legacy `phone` column.

---

## Staff Level (8–12 Years)

### Q3: Compare Rolling Updates, Blue/Green Deployments, and Automated Progressive Canaries across infrastructure cost, rollback latency, blast radius, and cold-start/JIT effects.

**Answer:**

| Criterion | Rolling Update | Blue/Green Deployment | Automated Progressive Canary (Argo Rollouts) |
|:---|:---:|:---:|:---:|
| **Infrastructure Cost** | **Minimal ($+25\%$ `maxSurge`)** | Heavy ($+100\%$ — requires $2\times$ nodes) | **Low ($+5\%$ to $+20\%$)** |
| **Rollback Duration** | Slow (2–5m rolling replacement) | **Instant ($\approx 1\text{s}$ router flip)** | **Instant ($\approx 1\text{s}$ router flip)** |
| **Blast Radius** | Large ($25\% - 50\%$ users impacted) | Complete (100% of users if flawed) | **Minimal (Only $1\% - 5\%$ of users)** |
| **JIT / Cache Shock** | Smooth (incremental warming) | **Severe (100% cold JIT cache shock)** | Smooth (warm baseline absorbs 95%) |
| **Verification Gate** | Manual smoke tests | Manual pre-cutover testing | **Autonomous statistical Prometheus analysis** |

**Architectural Recommendation**:
- Use **Rolling Updates** for non-critical internal tools and dev/staging environments.
- Use **Blue/Green** for legacy stateful services where mixed-version execution is strictly prohibited.
- Use **Automated Progressive Canaries** for all Tier-0 customer-facing microservices.

---

### Q4: How does GitOps (ArgoCD) enforce continuous reconciliation, drift detection, and pull-based security? What happens when an engineer modifies a pod with `kubectl edit`?

**Answer:**

**1. The GitOps Architecture**:
- Desired system state is stored declaratively in a version-controlled Git repository.
- ArgoCD runs inside the Kubernetes cluster and continuously monitors both the Git repository and the live cluster state via Kubernetes informers.

**2. Drift Detection & Self-Healing**:
$$\text{Drift} = \text{Manifests in Git} \ominus \text{Live Resources in K8s etcd}$$
If an engineer attempts an out-of-band change using `kubectl edit deployment/payment-service`:
1. Kubelet updates the etcd state.
2. ArgoCD's reconciliation loop detects that the live etcd resource deviates from the Git commit.
3. If `selfHeal: true` is configured, ArgoCD **immediately overrides the manual modification**, resetting the deployment back to the exact declared Git manifest within 60 seconds.
4. An audit event is logged.

**3. Pull-Based Security Model**:
Traditional CI/CD systems (Jenkins, GitLab CI) require broad cluster-admin kubeconfig credentials to push manifests into the cluster from outside the firewall. If the CI server is compromised, the entire production cluster is compromised.
- Under GitOps, the CI server has zero cluster access. It only pushes code to Git.
- ArgoCD pulls changes from inside the firewall, reducing the attack surface to zero external inbound ports.

---

### Q5: How does Automated Canary Analysis (ACA) utilize the Mann-Whitney U test to evaluate canary health rather than comparing raw metric averages?

**Answer:**
Comparing raw metric averages (e.g. `mean(canary_latency) vs mean(baseline_latency)`) is fundamentally flawed in distributed systems:
- A single outlier request (e.g. a GC pause or client TCP reconnect taking 2 seconds) distorts the arithmetic mean of 10,000 fast requests.
- Latency and error distributions in web systems are non-normal and heavily right-skewed.

**The Mann-Whitney U Test (Wilcoxon Rank-Sum)**:
The canary analysis engine (e.g. Kayenta / Argo Rollouts) treats latency and error metrics as non-parametric probability distributions:
1. It collects $N$ discrete observations from the Baseline and $M$ observations from the Canary over equal rolling time windows.
2. It ranks all combined observations from lowest to highest.
3. It tests the null hypothesis: *Is the probability of a randomly selected Canary metric being worse than a Baseline metric greater than 50%?*
4. It computes a $p$-value:
   - If $p \ge 0.05$: Metric distributions are statistically indistinguishable. The canary is healthy.
   - If $p < 0.01$: The canary demonstrates statistically significant degradation. The analysis fails.
5. This eliminates false-positive rollbacks caused by transient noise while guaranteeing real performance regressions are caught.

---

## Principal / Distinguished Level (12+ Years)

### Q6: Design an end-to-end continuous delivery pipeline that allows 200 developers to deploy 40 microservices to production 20 times per day with zero downtime, zero data loss, and automated rollbacks.

**Answer — Architecture Blueprint**:

```
[Developer: Git Push to main]
          │
          ▼
┌─────────────────────────────────┐
│ GitHub Actions CI Pipeline      │
├─────────────────────────────────┤
│ 1. Hermetic Maven compile       │
│ 2. Unit & Contract Tests        │
│ 3. Trivy / Syft Vulnerability   │
│ 4. Buildx Multi-Arch Container  │
│ 5. Cosign Keyless Image Signing │
└────────────────┬────────────────┘
                 │ Commits updated image digest to GitOps Repo
                 ▼
┌─────────────────────────────────┐
│ GitOps Repository (k8s-manifest)│
└────────────────┬────────────────┘
                 │ ArgoCD Polls GitOps Repo
                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Kubernetes Production Cluster                                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. ArgoCD PreSync Hook:                                                │
│    Executes isolated Flyway DB Migration Job (Expand-Contract rules)   │
│                                                                        │
│ 2. Argo Rollouts Canary Triggered:                                     │
│    • 5% Traffic to Canary pod for 15 minutes                           │
│    • Prometheus AnalysisTemplate monitors P99 latency & 5xx rates      │
│                                                                        │
│ 3. Automated Decision Gate:                                            │
│    ├─► Healthy (p >= 0.05) ──► Promote: 25% -> 50% -> 100%             │
│    └─► Degradation Detected ─► Instant 1-second abort & revert to v1   │
└────────────────────────────────────────────────────────────────────────┘
```

**Key Architectural Guarantees**:
1. **Contract Testing**: Pact contract tests in CI prevent incompatible API schema changes from merging to `main`.
2. **Feature Flags**: All high-risk code merged dark behind Unleash/LaunchDarkly flags.
3. **Immutable Digest Pinning**: All images referenced by SHA-256 digest; mutable tags blocked by Kyverno policy.
4. **PreStop & Graceful Drain**: All pods implement `sleep 15` PreStop hooks to eliminate 502 Bad Gateway errors.

---

### Q7: How do you achieve SLSA Level 3 compliance and hermetic build security for an enterprise Java platform subject to strict financial regulatory audits (e.g. SOC2, PCI-DSS)?

**Answer — SLSA Level 3 Compliance Framework**:

Supply-chain Levels for Software Artifacts (SLSA) Level 3 requires:

1. **Hermetic, Ephemeral Build Environments**:
   - Builds run in isolated, single-use GitHub Actions runners or Tekton pods that are destroyed immediately after execution.
   - Pinned dependency verification: Maven runs with pinned checksums (`dependency:go-offline`); Gradle uses `gradle/verification-metadata.xml`. The build environment has zero arbitrary outbound internet access during compilation.
2. **Cryptographic Provenance Generation (in-toto)**:
   - The CI pipeline generates an authenticated **in-toto provenance attestation** recording:
     - The exact Git commit SHA that triggered the build.
     - The build runner identity and environment parameters.
     - The cryptographic SHA-256 hashes of all input files and output artifacts.
3. **Keyless Signing via Sigstore Cosign**:
   - The container image and provenance attestation are signed using OpenID Connect (OIDC) tokens issued by GitHub Actions. No long-lived private keys exist to be leaked or stolen!
4. **Automated Admission Control Enforcement (Kyverno / OPA)**:
   - A cluster-wide Kyverno admission controller intercepts every pod creation in Kubernetes:
     ```yaml
     apiVersion: kyverno.io/v1
     kind: ClusterPolicy
     metadata:
       name: verify-image-signature
     spec:
       validationFailureAction: Enforce
       rules:
         - name: verify-cosign-signature
           match:
             resources:
               kinds: [Pod]
           verifyImages:
             - imageReferences: ["ghcr.io/corp/*"]
               attestors:
                 - entries:
                     - keyless:
                         issuer: "https://token.actions.githubusercontent.com"
     ```
   - Any container image lacking a valid cryptographic signature and SLSA provenance attestation is **instantly rejected at the Kubernetes API admission level**.
