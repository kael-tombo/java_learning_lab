# Platform Engineering Quiz

## Questions

1. **Platform vs DevOps**: Define "Platform Engineering". How does it differ from DevOps? What is the "platform product" and who are its "customers"?

2. **Internal Developer Platform (IDP)**: List 5 core capabilities an IDP must provide. For each, name a CNCF/tool example (e.g., Backstage, Crossplane, ArgoCD, Tekton, Kyverno).

3. **Golden Path**: What is a "Golden Path"? Design a Golden Path for "Java Microservice to Production" — list the steps, tools, and guardrails at each step.

4. **Self-Service Infrastructure**: Developers need a Postgres DB. Show how to implement self-service via:
   - (a) CrossPlane CompositeResource (XR) + Composition
   - (b) Terraform Module + GitOps (ArgoCD)
   Compare: which scales better for 1000s of requests/day?

5. **GitOps & ArgoCD**: Explain the GitOps reconciliation loop. What happens when:
   - Drift detected (manual change in cluster)
   - Git commit reverted
   - ArgoCD controller crashes
   How does "App of Apps" pattern work?

6. **Developer Portal (Backstage)**: What problems does Backstage solve? Explain: Software Catalog, Software Templates, TechDocs, Plugins. How does it integrate with GitOps (ArgoCD plugin)?

7. **Policy as Code**: Implement "all containers must have resource limits" using:
   - (a) Kyverno ClusterPolicy
   - (b) OPA Gatekeeper ConstraintTemplate
   Show the YAML for each. Which is easier to debug?

8. **Secrets Management**: Compare: SealedSecrets, External Secrets Operator (ESO), HashiCorp Vault Agent Injector. For each: how does the secret get into the pod? Rotation strategy?

9. **Platform Metrics**: What are the 5 key metrics to measure platform success? (Hint: DORA + platform-specific). Define each and give a target for a mature platform.

10. **Day 2 Operations**: Platform is live. List 5 ongoing responsibilities: capacity planning, upgrade strategy, security patching, cost optimization, developer support. For "upgrade strategy", design a control plane upgrade plan for Kubernetes + ArgoCD + Crossplane with zero downtime.

---

## Answers

1. **Platform Engineering**: Building and maintaining an **Internal Developer Platform (IDP)** as a **product** for **internal developers (customers)**. 
   - **DevOps**: Culture/practices, "you build it you run it", often ad-hoc tooling.
   - **Platform Eng**: Product mindset, dedicated team, paved roads, self-service, reduces cognitive load.
   - **Platform Product**: APIs, CLIs, UI (portal), workflows for deploy, infra, secrets, observability.

2. **IDP Core Capabilities**:
   | Capability | Tool Examples |
   |------------|---------------|
   | Service Catalog/Discovery | Backstage, Port |
   | CI/CD Pipelines | Tekton, GitHub Actions, Argo Workflows |
   | GitOps Deployment | ArgoCD, Flux |
   | Infrastructure Provisioning | CrossPlane, Terraform Controller |
   | Policy & Compliance | Kyverno, OPA Gatekeeper |
   | Secrets Management | External Secrets, Vault, SealedSecrets |
   | Observability | Grafana, Tempo, Loki, Prometheus |
   | Developer Self-Service | Backstage Templates, Kratix |

3. **Golden Path — Java Microservice**:
   ```
   1. Create → Backstage Template (Spring Boot + Helm chart + CI)
   2. Code → IDE (pre-commit: lint, test, checkstyle)
   3. PR → CI (Tekton): build, unit test, contract test, container scan
   4. Merge → CD (ArgoCD): deploy to staging (auto), prod (manual promotion)
   5. Verify → Smoke tests, canary analysis (Flagger/Argo Rollouts)
   6. Operate → Logs (Loki), Metrics (Prometheus), Traces (Tempo), Alerts
   ```
   **Guardrails**: Policy checks in CI (Kyverno), resource quotas, network policies auto-applied.

4. **Self-Service Postgres**:
   - **(a) CrossPlane**:
     ```yaml
     # XR: xpostgresql.yaml
     apiVersion: database.example.org/v1
     kind: XPostgreSQL
     spec:
       params: { version: "15", storage: "100Gi", backup: true }
     ---
     # Composition: maps XR → managed resources (RDS, CloudSQL, or CNPG)
     ```
     Scales: Native K8s API, controller handles reconciliation, 1000s/day fine.
   - **(b) Terraform + ArgoCD**:
     ```hcl
     # module/postgres/main.tf
     resource "aws_db_instance" "pg" { ... }
     ```
     ArgoCD App points to rendered manifests. Scales: TF plan/apply per request = slower, state management complex.
   - **Winner**: CrossPlane for high volume (native K8s, async reconciliation).

5. **GitOps Loop**:
   - **Desired State**: Git (manifests, Helm values, Kustomize)
   - **Actual State**: Cluster (ArgoCD caches)
   - **Reconcile**: Compare → Diff → Apply (or alert)
   - **Drift**: ArgoCD shows `OutOfSync`, auto-heal if `selfHeal: true`
   - **Revert**: Git revert → ArgoCD syncs to previous commit
   - **Controller crash**: New controller reads Git, resumes reconciliation
   - **App of Apps**: Root Application manages child Applications (per env/team)

6. **Backstage**:
   - **Software Catalog**: Graph of components, APIs, resources, systems, owners (ingest from Git, K8s, cloud)
   - **Software Templates**: Scaffolder — `template.yaml` → generates repo, CI, ArgoCD App
   - **TechDocs**: Docs-as-code (MkDocs) → published automatically
   - **Plugins**: ArgoCD (sync status), Kubernetes (pod logs), Cloud (cost), etc.
   - **Integration**: ArgoCD plugin shows sync status in catalog; template creates ArgoCD Application

7. **Policy as Code**:
   - **(a) Kyverno**:
     ```yaml
     apiVersion: kyverno.io/v1
     kind: ClusterPolicy
     metadata: { name: require-resource-limits }
     spec:
       validationFailureAction: Enforce
       rules:
       - name: check-limits
         match: { any: [{ resources: { kinds: ["Pod"] } }] }
         validate:
           message: "Container must have resources.limits"
           pattern:
             spec:
               containers:
               - resources:
                   limits:
                       memory: "?*"
                       cpu: "?*"
     ```
   - **(b) OPA Gatekeeper**:
     ```yaml
     # ConstraintTemplate
     apiVersion: templates.gatekeeper.sh/v1
     kind: ConstraintTemplate
     metadata: { name: k8srequiredlimits }
     spec:
       crd:
         spec:
           names: { kind: K8sRequiredLimits }
       targets:
       - target: admission.k8s.gatekeeper.sh
         rego: |
           violation[{"msg": msg}] {
             container := input.review.object.spec.containers[_]
             not container.resources.limits.memory
             msg := "Container missing memory limit"
           }
     ---
     # Constraint
     apiVersion: constraints.gatekeeper.sh/v1beta1
     kind: K8sRequiredLimits
     metadata: { name: require-limits }
     ```
   - **Debug**: Kyverno — `kubectl get polr` (PolicyReport) shows pass/fail per resource. OPA — `kubectl get constraints` + audit.

8. **Secrets Comparison**:
   | Tool | Mechanism | Rotation |
   |------|-----------|----------|
   | **SealedSecrets** | Encrypt secret → SealedSecret (safe in Git) → Controller decrypts in cluster | Manual re-seal |
   | **External Secrets Operator** | SecretStore (Vault/AWS/GCP) → ExternalSecret → Controller syncs to K8s Secret | Auto (poll interval) |
   | **Vault Agent Injector** | Sidecar injects secrets via sink (file/env) at startup | Template re-render on change (SIGHUP) |

9. **Platform Metrics** (DORA + Platform):
   | Metric | Definition | Mature Target |
   |--------|------------|---------------|
   | **Deployment Frequency** | How often code reaches prod | On-demand (multiple/day) |
   | **Lead Time for Changes** | Commit → production | < 1 hour |
   | **Mean Time to Recovery** | Incident → restored | < 30 min |
   | **Change Failure Rate** | % deployments causing incidents | < 5% |
   | **Developer Onboarding Time** | New hire → first prod deploy | < 1 day |
   | **Platform Adoption** | % teams using Golden Path | > 90% |
   | **Self-Service Ratio** | Self-service requests / total tickets | > 80% |

10. **Control Plane Upgrade Plan**:
    ```
    Phase 1: Preparation (1 week before)
      - Test in staging: upgrade K8s (1.28→1.29), ArgoCD, Crossplane, CRDs
      - Verify all Compositions, Policies, Apps work
      - Backup etcd (velero)
    
    Phase 2: Control Plane (maintenance window)
      - Upgrade K8s control plane (master nodes) — draining, uncordon
      - Upgrade ArgoCD (helm upgrade, check CRD migrations)
      - Upgrade Crossplane (check provider versions)
      - Upgrade Kyverno/OPA (check policy compatibility)
    
    Phase 3: Data Plane (rolling)
      - Upgrade worker nodes (maxSurge=25%, maxUnavailable=0)
      - Restart DaemonSets (CNI, CSI, monitoring)
      - Verify all workloads healthy
    
    Phase 4: Validation
      - Run integration tests
      - Check ArgoCD sync status (all green)
      - Verify CrossPlane XRs reconciled
      - Cost check (no zombie resources)
    
    Rollback: If any phase fails → pause, investigate, rollback via etcd restore or helm rollback.
    ```