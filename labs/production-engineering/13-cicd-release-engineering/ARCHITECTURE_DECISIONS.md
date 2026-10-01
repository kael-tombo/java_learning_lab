# ARCHITECTURE DECISIONS: Enterprise Release Engineering & GitOps Standards
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: GitOps-Driven Declarative Delivery via ArgoCD

### Status: ACCEPTED

### Context
Deployments were executed by external Jenkins CI pipelines pushing changes via direct `kubectl apply` using shared cluster-admin credentials. Manual configuration drift, unrecorded cluster mutations, and fragmented deployment tracking resulted in frequent environment divergence and high rollback latency ($> 30\text{ minutes}$).

### Decision
1. **Adoption of GitOps (ArgoCD)**:
   - Git is the single, immutable source of truth for all Kubernetes workloads, Helm charts, and infrastructure manifests.
   - ArgoCD operates inside the Kubernetes cluster, continuously reconciling actual cluster state against Git.
2. **Automated Drift Self-Healing**:
   - ArgoCD sync policy configured with `selfHeal: true`. Any unauthorized manual `kubectl edit` is overwritten within 60 seconds back to the declared Git baseline.
3. **Pull-Based Cluster Security**:
   - External CI servers are stripped of cluster-admin privileges. CI simply creates a Git commit bumping the image tag in the deployment repository; ArgoCD pulls the update from within the firewall.

### Consequences
- Cluster configuration drift eliminated fleet-wide.
- Audit trail completely codified in Git commit history.
- Rollback execution time reduced to the time required to run `git revert` ($< 60\text{ seconds}$).

---

## ADR-02: Automated Progressive Canary Analysis (Argo Rollouts + Prometheus)

### Status: ACCEPTED

### Context
Standard Kubernetes rolling updates exposed $25\% - 50\%$ of users to regressions during deployments before human engineers could detect latency spikes or errors. Releases were high-stress, all-or-nothing operations requiring manual smoke-testing.

### Decision
1. **Mandatory Canary Deployment Archetype**:
   - Production deployments must use **Argo Rollouts** rather than standard Kubernetes Deployments.
2. **Standardized Progressive Traffic Schedule**:
   - Step 1: Route $5\%$ of traffic to the canary replica for 15 minutes.
   - Step 2: Automated Analysis phase evaluating HTTP 5xx error rate, P99 latency, and GC overhead against Prometheus baselines.
   - Step 3: Promote to $20\%$ for 15 minutes $\rightarrow 50\% \rightarrow 100\%$.
3. **Automated Rollback Criteria**:
   - If Canary HTTP error rate exceeds Baseline $+ 0.2\%$ or P99 latency degrades by $> 10\%$, Argo Rollouts **aborts and rolls back to 100% baseline instantly** with zero human intervention.

### Consequences
- Blast radius of flawed deployments capped at $\le 5\%$ of users.
- Human fatigue eliminated: canaries evaluate and promote autonomously 24/7.

---

## ADR-03: Zero-Downtime Database Schema Migration Standard (The Expand-Contract Invariant)

### Status: ACCEPTED

### Context
Application deployments that included schema changes frequently caused production outages because running v1 application pods could not operate against the mutated database schema before being upgraded. Attempting to rollback also failed because old code could not read the altered schema.

### Decision
1. **Decoupled 5-Phase Expand-Contract Pipeline**:
   - Code and schema changes **must never be coupled in the same deployment**.
   - Phase 1 (Expand): Add new columns/tables as nullable.
   - Phase 2 (Dual-Write): Application code writes to both old and new columns.
   - Phase 3 (Backfill): Asynchronous batch data backfill.
   - Phase 4 (Read New): Application switches reads to new column.
   - Phase 5 (Contract): Drop old column weeks later.
2. **Isolation from Pod Startup**:
   - `spring.flyway.enabled` and `spring.liquibase.enabled` are **strictly forbidden** inside application container pods.
   - Migrations must execute as dedicated Kubernetes Jobs (ArgoCD `PreSync` hooks) with dedicated migration credentials.

### Consequences
- $100\%$ zero-downtime database migrations achieved across all rolling releases.
- Eliminates database migration lock collisions during pod autoscaling.

---

## ADR-04: Immutable Artifact Tagging & Cryptographic Signing Policy (Cosign / SLSA)

### Status: ACCEPTED

### Context
Use of mutable tags (`:latest`, `:staging`) and unverified container images introduced non-deterministic production deployments and exposed the platform to software supply chain tampering.

### Decision
1. **Mandatory Immutable Digest Pinning**:
   - Production manifests must reference container images by immutable SHA-256 digest (`image@sha256:...`) or unique Git commit SHA tags. Mutable tags are blocked by CI/CD linters.
2. **Cryptographic Image Signing via Cosign**:
   - Every container built in CI must be signed using Sigstore Cosign with GitHub Actions OIDC keyless signing.
3. **Cluster Admission Enforcement (Kyverno)**:
   - A Kyverno ClusterPolicy deployed in Kubernetes rejects any Pod creation whose container image lacks a valid cryptographic signature from the corporate identity.

### Consequences
- Prevents deployment of untrusted or tampered container binaries.
- Guarantees 100% reproducible, deterministic pod scheduling across all nodes.

---

## ADR-05: Continuous Delivery & Feature Flag Standard (Decoupling Deploy from Release)

### Status: ACCEPTED

### Context
Code branches lived for weeks in isolation ("feature branch hell") because teams waited for scheduled release windows to merge, leading to massive merge conflicts and high-risk releases.

### Decision
1. **Trunk-Based Development**:
   - Engineers commit directly to `main` (or short-lived branches merged within 24 hours).
   - Long-lived feature branches are forbidden.
2. **Feature Flags as Default Architecture**:
   - Any incomplete, risky, or significant new feature must be wrapped in a **Feature Flag** (LaunchDarkly / Unleash).
   - Code is deployed continuously to production in a "dark" state (flag disabled).
   - Business release occurs by flipping the flag dynamically in production without a code deployment.
3. **Dead Code & Flag Retirement Policy**:
   - Feature flags must be removed and cleaned up within 30 days of achieving 100% rollout.

### Consequences
- Lead time from commit to production reduced from 14 days to $< 45\text{ minutes}$.
- Eliminates "Big Bang" release risk completely.
