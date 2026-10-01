# CHECKLIST: CI/CD, GitOps & Enterprise Release Engineering Readiness
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Build Pipeline & Supply Chain Security (SLSA Level 3)

- [ ] **Hermetic & Reproducible Builds**:
  - [ ] Pinned base image digests used in all Dockerfiles (`eclipse-temurin:21-jre-jammy@sha256:...`).
  - [ ] Maven/Gradle dependencies locked with cryptographic checksum verification (`gradle/verification-metadata.xml`).
  - [ ] Build execution occurs in ephemeral, single-use CI runners with zero arbitrary outbound internet access during compilation.
- [ ] **Vulnerability Scanning & SBOM Generation**:
  - [ ] Software Bill of Materials (SBOM) generated in CycloneDX JSON format during every CI build via Syft.
  - [ ] Container images scanned for CVE vulnerabilities via Trivy/Grype; builds fail automatically on Critical or High unpatched CVEs.
- [ ] **Cryptographic Signing (Sigstore Cosign)**:
  - [ ] Container images cryptographically signed using keyless OIDC authentication in GitHub Actions.
  - [ ] Kyverno / OPA admission controller deployed in Kubernetes, rejecting any image lacking a valid cryptographic signature.

---

## 2. GitOps & Declarative Delivery Governance (ArgoCD)

- [ ] **Git as Single Source of Truth**:
  - [ ] All Kubernetes manifests, Helm values, and network policies tracked in version-controlled Git repositories.
  - [ ] Direct `kubectl apply` or manual cluster mutations strictly forbidden; external CI servers stripped of cluster-admin credentials.
- [ ] **Continuous Drift Reconciliation & Self-Healing**:
  - [ ] ArgoCD applications configured with `automated: {prune: true, selfHeal: true}`.
  - [ ] Unauthorized manual modifications (`kubectl edit`) overwritten back to declared Git state within 60 seconds.
- [ ] **Immutable Artifact Tagging**:
  - [ ] Mutable tags (`:latest`, `:staging`) strictly banned from production deployment manifests.
  - [ ] Manifests reference images by immutable SHA-256 digest (`image@sha256:...`) or unique Git commit SHAs.

---

## 3. Automated Progressive Canary & Zero-Downtime Rollouts

- [ ] **Argo Rollouts Architecture**:
  - [ ] Critical Tier-0 services deployed using `Rollout` resources rather than standard Deployments.
  - [ ] Traffic schedule configured: $5\%$ Canary for 15 minutes $\rightarrow 25\% \rightarrow 50\% \rightarrow 100\%$.
- [ ] **Automated Canary Analysis (Prometheus)**:
  - [ ] `AnalysisTemplate` configured with real-time Prometheus evaluations:
    - HTTP 5xx error rate $\le 0.2\%$.
    - P99 latency degradation $\le 10\%$.
    - JVM GC pause overhead $\le 3.0\%$.
  - [ ] Automated instant rollback executed if analysis fails 3 consecutive iterations.

---

## 4. Zero-Downtime Database Schema Migration Invariants

- [ ] **Isolation from Application Boot**:
  - [ ] `spring.flyway.enabled: false` and `spring.liquibase.enabled: false` enforced across all application configurations.
  - [ ] Migrations executed strictly as dedicated Kubernetes Jobs (ArgoCD `PreSync` hooks) with dedicated migration credentials.
- [ ] **Strict Expand-Contract Pattern**:
  - [ ] Application code changes and database schema changes never deployed in the same release.
  - [ ] Column additions deployed as NULLABLE (Expand phase).
  - [ ] Column renames or table splits execute via Dual-Write $\rightarrow$ Async Backfill $\rightarrow$ Feature Flag Read Switch $\rightarrow$ Contract (Drop old column weeks later).

---

## 5. Feature Flag Architecture & Deployment Decoupling

- [ ] **Dark Launching Standard**:
  - [ ] All significant business logic or risky integrations wrapped in Feature Flags (LaunchDarkly / Unleash).
  - [ ] Code deployed to production with flags disabled (dark state); release decoupled from code deployment.
- [ ] **Flag Retirement Governance**:
  - [ ] Feature flags tagged with expiration dates; mandatory cleanup PRs filed within 30 days of reaching 100% traffic.
