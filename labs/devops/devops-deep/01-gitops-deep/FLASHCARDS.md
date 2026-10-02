# GitOps Deep Dive - Flashcards

Use these for spaced repetition review. Format: **Question** (front) → **Answer** (back).

---

## Core Concepts

**What is GitOps?**
→ A operational framework that applies Git workflows (pull requests, code review, CI) to infrastructure and application deployment. Git is the single source of truth; automated agents reconcile cluster state to Git state.

**What are the 4 principles of GitOps? (OpenGitOps)**
→ 1. **Declarative**: System described declaratively (YAML/JSON)
→ 2. **Versioned & Immutable**: Stored in Git with full history
→ 3. **Pulled Automatically**: Software agents pull desired state
→ 4. **Continuously Reconciled**: Agents continuously observe and correct drift

**What is "drift" in GitOps?**
→ Divergence between the desired state in Git and the actual state in the cluster (caused by manual `kubectl` changes, failed deployments, external mutations).

**What is "reconciliation"?**
→ The continuous process where a controller compares actual state → desired state → applies corrections to converge them. The core control loop of GitOps.

---

## ArgoCD

**What is the ArgoCD Application CRD?**
→ Custom resource representing a deployed application: source (repo/path/targetRevision), destination (cluster/namespace), sync policy, and status (health, sync status, resources).

**ArgoCD sync policies: `automated` vs `manual`?**
→ `automated`: Controller automatically applies changes when Git changes (supports `prune`, `selfHeal`, `allowEmpty`). `manual`: Requires user to click "Sync" in UI/CLI.

**What does `selfHeal: true` do?**
→ If a user manually changes a live resource (e.g., `kubectl edit deployment`), ArgoCD detects drift on next reconciliation and reapplies the Git manifest to revert it.

**What does `prune: true` do?**
→ Deletes resources from the cluster that exist in the cluster but have been removed from Git (prevents orphaned resources).

**What is a Sync Window?**
→ A time-bounded schedule (cron + duration) that restricts when *automatic* sync can occur. Example: `schedule: "0 9 * * 1-5", duration: 8h` = weekdays 9am-5pm.

**How does ArgoCD handle multi-cluster?**
→ Register clusters via `argocd cluster add <context>` or secret with kubeconfig. Applications specify `destination.server` (cluster URL) and `destination.namespace`.

**What is the App of Apps pattern?**
→ A root Application that manages other Application resources as its manifests. Enables bootstrapping entire environments (platform, tenant apps) from a single Git commit.

---

## Flux

**What are the main Flux controllers?**
→ 1. **source-controller**: GitRepository, HelmRepository, Bucket, OCIRepository
→ 2. **kustomize-controller**: Kustomization (builds/applies kustomize overlays)
→ 3. **helm-controller**: HelmRelease (manages Helm chart releases)
→ 4. **notification-controller**: Alerts/webhooks on events
→ 5. **image-automation-controller**: ImageUpdateAutomation, ImageRepository, ImagePolicy

**Flux GitRepository vs ArgoCD Application source?**
→ Flux separates *source* (GitRepository CRD) from *deployment* (Kustomization/HelmRelease CRDs). ArgoCD combines both in Application CRD.

**What is a Kustomization in Flux?**
→ CRD that points to a GitRepository + path, defines kustomize build options (patches, images, replicas), and controls apply behavior (prune, validation, health checks).

**How does Flux handle image updates?**
→ ImagePolicy defines semver/filters for container images; ImageUpdateAutomation commits new image tags to Git (updating Kustomization/HelmRelease), triggering GitOps sync.

---

## Patterns & Practices

**Kustomize overlay structure for multi-env?**
```
base/
  deployment.yaml
  service.yaml
  kustomization.yaml
overlays/
  dev/
    kustomization.yaml  # patches: replicaCount=1, image=dev-tag
  staging/
    kustomization.yaml  # patches: replicaCount=2, image=staging-tag
  prod/
    kustomization.yaml  # patches: replicaCount=5, image=prod-tag
```

**How to manage secrets in GitOps?**
→ 1. **SealedSecrets**: Encrypt secrets with cluster public key → commit SealedSecret to Git → controller decrypts in cluster.
→ 2. **External Secrets Operator**: SecretStore (Vault/AWS/GCP/Azure) + ExternalSecret CRD → controller syncs secrets to cluster.
→ 3. **SOPS**: Encrypt files with age/PGP → commit encrypted → decrypt at apply time (via kustomize secretGenerator or Flux decryption).

**What is progressive delivery with GitOps?**
→ GitOps + Canary/Blue-Green + Automated Analysis. Tools: Flagger (ArgoCD/Flux), Argo Rollouts, Flux Flagger integration. Metrics from Prometheus drive automated promotion/rollback.

**How to implement drift detection alerts?**
→ ArgoCD: Application status `sync.status` = `OutOfSync` + `health.status` = `Degraded` → Alertmanager/Notification controller → Slack/PagerDuty.
→ Flux: Kustomization condition `Ready=False` + `Stalled=True` → Notification controller → webhook.

---

## Commands Quick Reference

| Task | ArgoCD CLI | Flux CLI |
|------|------------|----------|
| List apps | `argocd app list` | `flux get kustomizations -A` |
| Sync app | `argocd app sync <name>` | `flux reconcile kustomization <name> -n <ns>` |
| Diff app | `argocd app diff <name>` | `flux diff kustomization <name> -n <ns>` |
| Get app status | `argocd app get <name>` | `flux get kustomization <name> -n <ns>` |
| Rollback | `argocd app rollback <name> <revision>` | `flux suspend ks <name> && flux resume ks <name>` (or Git revert) |
| Pause auto-sync | `argocd app set <name> --sync-policy none` | `flux suspend kustomization <name> -n <ns>` |