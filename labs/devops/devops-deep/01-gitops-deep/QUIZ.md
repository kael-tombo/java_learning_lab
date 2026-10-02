# GitOps Deep Dive - Quiz

Test your understanding of GitOps principles, ArgoCD/Flux, and declarative deployment patterns.

---

## Questions

### 1. What is the core principle of GitOps that distinguishes it from traditional CI/CD?
A) Git is used only for source code version control
B) Git serves as the single source of truth for both application code and infrastructure state
C) GitOps requires manual approval for every deployment
D) GitOps only works with Kubernetes

### 2. In GitOps, how is drift between the desired state (Git) and actual state (cluster) detected?
A) Manual comparison of manifests
B) Periodic reconciliation loops that compare Git state with cluster state
C) Webhook notifications from the cluster
D) Scheduled kubectl diff commands

### 3. What is the primary architectural difference between ArgoCD and Flux?
A) ArgoCD uses a pull model; Flux uses a push model
B) ArgoCD has a dedicated UI and multi-cluster management; Flux is more lightweight and uses GitRepository/Kustomization CRDs
C) Flux requires a separate controller per cluster; ArgoCD uses a single controller
D) ArgoCD only supports Helm; Flux only supports Kustomize

### 4. Which sync strategy in ArgoCD allows you to preview changes before applying them?
A) Automatic sync
B) Manual sync
C) Phased sync with sync windows
D) Prune-only sync

### 5. What is the purpose of a "Sync Window" in ArgoCD?
A) To limit the time users can access the ArgoCD UI
B) To restrict when automatic synchronization can occur (e.g., business hours only)
C) To define how long a sync operation can take before timing out
D) To schedule when Git repositories are polled for changes

### 6. How does Kustomize differ from Helm in the context of GitOps?
A) Kustomize uses templates; Helm uses overlays
B) Kustomize uses a declarative overlay/patch approach without templates; Helm uses a templating engine with values files
C) Kustomize is only for ArgoCD; Helm is only for Flux
D) Kustomize requires a server-side component; Helm is client-only

### 7. What happens when you enable "Self-Heal" (auto-heal) in ArgoCD?
A) ArgoCD automatically fixes broken application code
B) ArgoCD automatically reverts manual changes made to the cluster that diverge from Git
C) ArgoCD automatically heals failed pods by restarting them
D) ArgoCD automatically updates the Git repository when cluster state changes

### 8. In a GitOps workflow, where should secrets be stored?
A) Directly in Git manifests (base64 encoded)
B) In Git using sealed secrets or external secret operators (e.g., External Secrets Operator, Vault)
C) In the cluster's etcd only
D) In CI/CD pipeline variables only

### 9. What is "Progressive Delivery" in the context of GitOps?
A) Deploying to production progressively faster each sprint
B) Using GitOps to implement canary/blue-green deployments with automated rollback based on metrics
C) Progressively adding more clusters to ArgoCD
D) Progressively migrating from Helm to Kustomize

### 10. Which of the following is NOT a valid GitOps pattern for managing multiple environments (dev, staging, prod)?
A) Separate Git branches per environment
B) Separate Git repositories per environment
C) Single repository with directory structure per environment (using Kustomize overlays)
D) Single manifest file with environment variables inline

---

## Answers

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **B** | GitOps treats Git as the single source of truth for the *entire system state* - both application code and infrastructure/cluster configuration. |
| 2 | **B** | GitOps controllers (ArgoCD ApplicationController, Flux Source/Controller) run continuous reconciliation loops that detect and optionally remediate drift. |
| 3 | **B** | ArgoCD provides a full-featured UI, RBAC, multi-cluster management, and visual diffing. Flux is CNCF-graduated, lighter weight, and uses a set of specialized controllers (source-controller, kustomize-controller, helm-controller) with GitRepository/Kustomization CRDs. |
| 4 | **B** | Manual sync allows you to preview the diff (via `argocd app diff` or UI) before clicking "Sync". Automatic sync applies immediately. |
| 5 | **B** | Sync windows restrict *when* automatic sync can run (e.g., `kind: SyncWindow, schedule: "0 9 * * 1-5", duration: 8h` for business hours). |
| 6 | **B** | Kustomize uses `kustomization.yaml` with `bases`, `patches`, `overlays` - no template syntax. Helm uses Go templates in `templates/` with `values.yaml`. |
| 7 | **B** | Self-heal means the controller detects drift (manual `kubectl edit`, `kubectl delete`, etc.) and automatically re-applies the Git state to revert it. |
| 8 | **B** | Never commit secrets to Git (even base64). Use SealedSecrets (Bitnami), External Secrets Operator (fetch from Vault/AWS Secrets Manager/GCP Secret Manager), or SOPS. |
| 9 | **B** | Progressive delivery = GitOps + canary/blue-green + automated analysis (Prometheus metrics, Kayenta, Flagger) with automated rollback on SLO breach. |
| 10 | **D** | Inline environment variables in a single manifest is an anti-pattern. Use Kustomize overlays, Helm values per env, or separate directories/branches/repos. |

---

## Scoring

- **9-10**: GitOps Expert - You understand the nuances of reconciliation, tooling differences, and security patterns
- **7-8**: GitOps Practitioner - Solid grasp; review self-heal, sync windows, and secret management
- **5-6**: GitOps Learner - Good foundation; focus on ArgoCD vs Flux architecture and progressive delivery
- **<5**: GitOps Beginner - Re-read the README and GUIDE; practice with a local ArgoCD/Flux install