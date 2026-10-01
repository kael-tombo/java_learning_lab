# THEORY: CI/CD, GitOps & Enterprise Release Engineering for Java
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Zero-Downtime Deployment Archetypes: Mechanics, Trade-offs & Failure Modes

Deploying software to distributed production systems without interrupting active user traffic requires strict adherence to mathematical deployment models.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Deployment Archetypes                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ 1. Rolling Update (In-Place Kubernetes Default):                       │
│    Pod 1 (v1 -> v2) ──► Pod 2 (v1 -> v2) ──► Pod 3 (v1 -> v2)          │
│    • Resource Cost: 1.0x - 1.25x (low cost)                            │
│    • Dual-Version Concurrency: Fleet runs v1 and v2 simultaneously!     │
│    • Invariant: DB schema & Kafka events must be 100% backward/forward  │
│      compatible across both versions.                                  │
│                                                                        │
│ 2. Blue/Green Deployment (Atomic Traffic Cutover):                     │
│    [Blue Pool (v1): 100% Traffic]      [Green Pool (v2): 0% Traffic]   │
│                      \                   /                             │
│                       [Ingress / Router]                               │
│    • Resource Cost: 2.0x (requires doubling fleet capacity)            │
│    • Cutover: Instant atomic flip (0 -> 100% traffic)                  │
│    • Danger: Instant traffic flip dumps cold JIT caches & shocks       │
│      downstream database connection pools ("Thundering Herd").         │
│                                                                        │
│ 3. Automated Progressive Canary (Gold Standard):                       │
│    Step 1: 95% Traffic -> v1 (Baseline)  |   5% Traffic -> v2 (Canary) │
│    Step 2: Automated Analysis (Prometheus P99, 5xx rate, GC pauses)   │
│    Step 3: Promotion: 5% -> 20% -> 50% -> 100%                         │
│    Step 4: Rollback: Instant 100% revert to v1 if metric degrades > 5% │
└────────────────────────────────────────────────────────────────────────┘
```

### Detailed Comparative Analysis

| Dimension | Rolling Update | Blue/Green Deployment | Automated Progressive Canary (Argo Rollouts) |
|:---|:---:|:---:|:---:|
| **Infrastructure Overhead** | $+25\%$ (`maxSurge`) | **$+100\%$ ($2\times$ nodes)** | $+5\%$ to $+20\%$ |
| **Rollback Duration** | Slow (Rolling reverse: 2–5m) | **Instant ($\approx 1\text{ second}$)** | **Instant ($\approx 1\text{ second}$)** |
| **Blast Radius** | Medium ($25\% - 50\%$ users) | High (All users if bad) | **Minimal (Only $1\% - 5\%$ of users)** |
| **Database Compatibility** | Strict (Expand-Contract) | Strict (Expand-Contract) | Strict (Expand-Contract) |
| **Cold Start / JIT Shock** | Progressive warming | **Severe Cold-Start Spike** | Progressive warming on Canary |
| **Verification Gate** | Smoke tests only | Manual / Synthetic staging | **Automated statistical metric analysis (Mann-Whitney U test)** |

---

## 2. Database Schema Migration Invariants: The Expand-Contract (Parallel Run) Pattern

The cardinal rule of zero-downtime distributed systems:
$$\text{Application code and database schema changes must NEVER be deployed simultaneously!}$$

If a deployment renames a database column from `phone_number` to `mobile_number` while deploying code that expects `mobile_number`:
- During a rolling update, old pods (v1) crash because `phone_number` is gone.
- New pods (v2) crash if they start before the migration executes.
- Rollback is impossible because the old code cannot read the new column!

```
                    The 5-Phase Expand-Contract Pipeline:
Phase 1: EXPAND (Database Migration 1)
  • Add column 'mobile_number' as NULLABLE.
  • Existing v1 code continues reading and writing 'phone_number'.
  • Zero application downtime; v1 code completely unaffected.

Phase 2: DUAL-WRITE (Application Code Release v2)
  • Application v2 writes to BOTH 'phone_number' AND 'mobile_number'.
  • Reads continue from 'phone_number'.
  • Backward-compatible with v1 code.

Phase 3: ASYNC BACKFILL (Background Data Migration)
  • Background worker or script iterates historical rows:
    UPDATE users SET mobile_number = phone_number WHERE mobile_number IS NULL;
  • Zero lock contention; executed in batches of 1,000 rows.

Phase 4: READ-NEW (Application Code Release v3)
  • Application v3 reads from 'mobile_number'.
  • Still writes to both for safety.
  • Verified healthy for 7 days in production.

Phase 5: CONTRACT (Database Migration 2)
  • Drop 'phone_number' column.
  • Application v4 stops writing to 'phone_number'.
  • Schema migration completed with zero dropped queries.
```

---

## 3. GitOps & Declarative Delivery Engine (ArgoCD & Flux)

### 3.1 The GitOps Core Axioms
1. **Declarative State**: The entire system desired state (Kubernetes manifests, Helm values, network policies) is defined declaratively in Git.
2. **Versioned & Immutable Source of Truth**: Every change is a commit (`git commit -m "Bump image to v3.2.0"`). Rollback is simply `git revert`.
3. **Automated Continuous Reconciliation**: An in-cluster operator (ArgoCD) continuously compares the *desired state* in Git with the *actual state* in the Kubernetes etcd cluster:
   $$\text{Drift} = \text{DesiredState}_{\text{Git}} \ominus \text{ActualState}_{\text{Cluster}}$$
   If an engineer attempts manual out-of-band `kubectl edit`, ArgoCD immediately overwrites the unauthorized change back to the Git baseline ("Self-Healing").
4. **Pull-Based Security Model**: The cluster pulls configurations from Git from *inside* the firewall. No external CI server holds broad cluster-admin SSH or kubeconfig credentials!

---

## 4. Automated Canary Analysis (ACA) & Statistical Metric Evaluation

Relying on human judgment to evaluate whether a canary deployment is healthy is error-prone. Enterprise release engineering uses **Automated Canary Analysis (Kayenta / Prometheus)**.

### 4.1 Key Performance Metric Vector
The canary engine evaluates three real-time telemetry streams over a 30-minute window:
1. **HTTP Error Rate Ratio**:
   $$\text{Canary Error Rate} \le \text{Baseline Error Rate} + 0.1\%$$
2. **Latency Percentile Deviation**:
   $$\text{Canary } P99 \le \text{Baseline } P99 \times 1.05 \quad (\le 5\% \text{ degradation allowed})$$
3. **JVM Memory & GC Stability**:
   $$\text{Canary GC CPU Overhead} \le 3.0\%$$
   $$\text{Canary Unrecovered Heap Growth Rate} \approx 0 \quad (\text{No memory leak})$$

### 4.2 Statistical Significance Testing (Mann-Whitney U Test)
Canary analysis does not compare raw averages (which are easily distorted by outlier spikes). It applies the non-parametric **Mann-Whitney U test** across metric time-series distributions. If the probability that the canary distribution matches the baseline distribution drops beneath $p < 0.01$, the canary is flagged as defective and automatically aborted.

---

## 5. Build Artifact Integrity: Hermetic Builds, SBOM & SLSA Level 3

### 5.1 Hermetic Reproducible Builds
A build is **hermetic** if it depends solely on explicitly declared, pinned inputs and cannot access the external internet during compilation.
- Pinned OpenJDK base image digest: `eclipse-temurin:21-jre-jammy@sha256:7f9a...`
- Maven locked dependency checksums via `maven-dependency-plugin` or Gradle verification metadata (`gradle/verification-metadata.xml`).

### 5.2 Software Bill of Materials (SBOM) & Supply Chain Security
Modern supply chain attacks (e.g. Log4j / SolarWinds) inject malicious code into upstream dependencies:
- **CycloneDX / Syft**: Automatically generates an SBOM in JSON format during compilation, cataloging every transitively bundled JAR file and hash.
- **Trivy / Grype**: Scans the generated container image against CVE vulnerability databases in CI. If a Critical or High vulnerability without a patch exists, the CI pipeline fails before deployment.
- **Cosign (Sigstore)**: Cryptographically signs the container image using keyless OIDC authentication in GitHub Actions. The Kubernetes admission controller (Kyverno / OPA Gatekeeper) strictly rejects any container image lacking a valid cryptographic signature!
