# GitOps Deep Dive - Exercises

Hands-on pipeline/infrastructure tasks to solidify GitOps concepts. Each exercise builds on the previous one.

---

## Prerequisites

- Kubernetes cluster (kind, k3d, minikube, or cloud)
- `kubectl`, `helm`, `kustomize` installed
- Git repository (local or remote)
- **Choose one**: ArgoCD **or** Flux (both covered)

---

## Exercise 1: Bootstrap GitOps Controller

**Goal**: Install ArgoCD or Flux and verify it's running.

### ArgoCD Path
```bash
# Create namespace and install
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s

# Port-forward UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Login via CLI
argocd login localhost:8080 --username admin --password <password> --insecure
```

### Flux Path
```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Bootstrap Flux to your Git repo
flux bootstrap github \
  --owner=<your-github-username> \
  --repository=flux-infra \
  --branch=main \
  --path=clusters/dev \
  --personal

# Verify controllers
flux check --pre
kubectl get pods -n flux-system
```

**✅ Verify**: UI accessible (ArgoCD) or `flux get all -A` shows resources (Flux).

---

## Exercise 2: Deploy First Application via GitOps

**Goal**: Deploy a sample app (e.g., `nginx` or `kuard`) using GitOps.

### ArgoCD: Create Application Manifest
```yaml
# argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: guestbook
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

```bash
kubectl apply -f argocd-app.yaml
argocd app get nginx
argocd app sync nginx
```

### Flux: Create GitRepository + Kustomization
```yaml
# flux-gitrepo.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/stefanprodan/podinfo
  ref:
    branch: master
---
# flux-kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 5m
  path: ./kustomize
  prune: true
  sourceRef:
    kind: GitRepository
    name: podinfo
  targetNamespace: default
```

```bash
kubectl apply -f flux-gitrepo.yaml -f flux-kustomization.yaml
flux get kustomizations -A
```

**✅ Verify**: `kubectl get pods -n guestbook` (ArgoCD) or `kubectl get pods -n default -l app=podinfo` (Flux) shows running pods.

---

## Exercise 3: Implement Kustomize Overlays for Multi-Environment

**Goal**: Structure a Git repo with base + overlays for dev/staging/prod.

### Repository Structure
```bash
mkdir -p gitops-lab/{base,overlays/{dev,staging,prod}}
cd gitops-lab
git init
```

### Base Manifests
```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
---
# base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
---
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
commonLabels:
  app: myapp
```

### Dev Overlay
```yaml
# overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namespace: dev
namePrefix: dev-
patches:
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: myapp
    spec:
      replicas: 1
  target:
    kind: Deployment
    name: myapp
images:
- name: nginx
  newTag: alpine
commonLabels:
  environment: dev
```

### Staging Overlay
```yaml
# overlays/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namespace: staging
namePrefix: staging-
patches:
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: myapp
    spec:
      replicas: 2
  target:
    kind: Deployment
    name: myapp
images:
- name: nginx
  newTag: alpine
commonLabels:
  environment: staging
```

### Prod Overlay
```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namespace: prod
namePrefix: prod-
patches:
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: myapp
    spec:
      replicas: 3
  target:
    kind: Deployment
    name: myapp
images:
- name: nginx
  newTag: stable
commonLabels:
  environment: prod
```

### Test Locally
```bash
# Preview each environment
kustomize build overlays/dev
kustomize build overlays/staging
kustomize build overlays/prod

# Apply dev
kubectl apply -k overlays/dev
kubectl get all -n dev
```

**✅ Verify**: Each overlay produces different replica counts, namespaces, and labels.

---

## Exercise 4: Configure Automated Sync with Sync Windows

**Goal**: Restrict automatic sync to business hours.

### ArgoCD: Add Sync Window to Application
```yaml
# argocd-sync-window.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx
  namespace: argocd
spec:
  # ... existing spec ...
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    syncWindows:
    - kind: Schedule
      schedule: "0 9 * * 1-5"  # 9 AM Mon-Fri
      duration: 8h              # 8 hours window
      manualSync: false         # allow manual sync outside window
```

```bash
kubectl apply -f argocd-sync-window.yaml
```

### Flux: Suspend/Resume via Schedule (using ImageUpdateAutomation for time-based)
```yaml
# Flux doesn't have native sync windows; use external cron or suspend Kustomization
# Alternative: Use Flux Notification + external scheduler
```

**✅ Verify**: ArgoCD UI shows "Sync Window" badge; auto-sync only runs during window.

---

## Exercise 5: Implement Secrets Management with SealedSecrets

**Goal**: Encrypt secrets for Git storage.

### Install SealedSecrets Controller
```bash
# ArgoCD/Flux: Install via Helm
helm repo add sealed-secrets https://web.archive.org/web/20260218090855/https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system --create-namespace

# Get public key
kubeseal --fetch-cert --controller-name=sealed-secrets --controller-namespace=kube-system > pub-cert.pem
```

### Create and Seal a Secret
```bash
# Create raw secret (NEVER commit this!)
cat > mysecret.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
  namespace: dev
type: Opaque
stringData:
  DATABASE_PASSWORD: "super-secret-dev"
  API_KEY: "dev-api-key-123"
EOF

# Seal it (safe to commit)
kubeseal --cert pub-cert.pem --format yaml < mysecret.yaml > sealed-secret-dev.yaml

# Verify sealed secret
cat sealed-secret-dev.yaml
```

### Deploy via GitOps
```yaml
# Add to overlays/dev/kustomization.yaml
resources:
- ../../base
- sealed-secret-dev.yaml  # add this line
```

```bash
git add .
git commit -m "Add sealed secret for dev"
git push
```

**✅ Verify**: `kubectl get secret myapp-secret -n dev -o yaml` shows decrypted values.

---

## Exercise 6: Implement Progressive Delivery with Canary (Flagger + ArgoCD)

**Goal**: Deploy canary with automated metric analysis.

### Prerequisites
```bash
# Install Istio (for traffic splitting) + Flagger
istioctl install --set profile=default -y
kubectl label namespace default istio-injection=enabled

helm repo add flagger https://flagger.app
helm install flagger flagger/flagger \
  --namespace istio-system \
  --set crd.create=true \
  --set meshProvider=istio \
  --set metricsServer=http://prometheus:9090
```

### Create Canary Resource
```yaml
# canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
  namespace: prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: prod-myapp
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 80
    gateways:
    - myapp-gateway
    hosts:
    - myapp.example.com
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 30s
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.prod/  # optional
      timeout: 5s
      metadata:
        type: cmd
        cmd: "hey -z 30s -q 10 -c 2 http://myapp.prod/"
```

### Add to Prod Overlay
```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
- sealed-secret-prod.yaml
- canary.yaml
```

**✅ Verify**: 
```bash
# Trigger new version
kustomize edit set image nginx=nginx:1.25
git commit -am "Update image to 1.25"
git push

# Watch canary progress
kubectl -n prod get canary myapp -w
flagger logs -n prod myapp
```

---

## Exercise 7: App of Apps Pattern (Bootstrap Entire Environment)

**Goal**: Single Application that manages all environment Applications.

### Root Application
```yaml
# root-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/gitops-infra.git
    targetRevision: main
    path: apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Apps Directory Structure
```
apps/
├── platform/
│   ├── ingress-nginx.yaml
│   ├── cert-manager.yaml
│   └── monitoring.yaml
├── dev/
│   ├── myapp-dev.yaml
│   └── database-dev.yaml
├── staging/
│   ├── myapp-staging.yaml
│   └── database-staging.yaml
└── prod/
    ├── myapp-prod.yaml
    ├── database-prod.yaml
    └── canary-prod.yaml
```

Each file is an Application CRD pointing to its own Git path.

**✅ Verify**: `argocd app get root-app` shows all child apps; syncing root syncs all.

---

## Exercise 8: Drift Detection & Remediation Test

**Goal**: Simulate drift and verify self-heal.

```bash
# 1. Deploy app via GitOps (Exercise 2)
# 2. Manually mutate the deployment
kubectl -n guestbook patch deployment nginx -p '{"spec":{"replicas":10}}'

# 3. Check ArgoCD status
argocd app get nginx
# Should show: Status: OutOfSync, Health: Degraded

# 4. Wait for self-heal (or trigger manually)
argocd app sync nginx --dry-run  # preview
# Or wait ~3 min for automated selfHeal

# 5. Verify replicas back to 1
kubectl get deployment nginx -n guestbook
```

**Flux equivalent**:
```bash
# Mutate
kubectl -n default patch deployment podinfo -p '{"spec":{"replicas":10}}'

# Check
flux get kustomization podinfo -n flux-system
# Should show: Ready=False, Stalled=True

# Reconcile
flux reconcile kustomization podinfo -n flux-system
```

---

## Exercise 9: Disaster Recovery - Cluster Restore from Git

**Goal**: Simulate cluster loss and recover entirely from Git.

```bash
# 1. Backup current state (optional)
kubectl get all -A -o yaml > cluster-backup.yaml

# 2. Nuke the cluster (or create new kind cluster)
kind delete cluster
kind create cluster --name gitops-dr

# 3. Reinstall GitOps controller only
# (ArgoCD or Flux bootstrap)

# 4. Apply root App of Apps
kubectl apply -f root-app.yaml

# 5. Watch everything restore
argocd app get root-app -w
# Or
flux get all -A -w
```

**✅ Verify**: All namespaces, deployments, services, secrets restored from Git.

---

## Exercise 10: Multi-Cluster GitOps (Advanced)

**Goal**: Manage multiple clusters from single Git repo.

### Register Clusters (ArgoCD)
```bash
# On cluster-1 (hub)
argocd cluster add cluster-1-context --name cluster-1

# On cluster-2 (managed)
argocd cluster add cluster-2-context --name cluster-2
```

### Application with Multiple Destinations
```yaml
# multi-cluster-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-multi
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/gitops-apps.git
    targetRevision: main
    path: overlays/prod
  destinations:
  - server: https://cluster-1.example.com:6443
    namespace: prod
  - server: https://cluster-2.example.com:6443
    namespace: prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**✅ Verify**: Same app deployed to both clusters; drift detected per cluster.

---

## Challenge Exercises

| # | Challenge | Description |
|---|-----------|-------------|
| 1 | **GitOps CI/CD Pipeline** | Build a GitHub Actions/GitLab CI pipeline that: runs `kustomize build`, validates with `kubeconform`, runs `opa` policy checks, then commits to GitOps repo |
| 2 | **Policy as Code** | Add OPA/Gatekeeper policies (e.g., "no privileged containers", "must have resource limits") enforced at sync time |
| 3 | **GitOps with Terraform** | Use Terraform to provision cluster + ArgoCD, then ArgoCD manages everything else (TF for infra, GitOps for apps) |
| 4 | **Audit Trail** | Implement admission webhook that logs all mutating operations to audit log; correlate with Git commits |
| 5 | **GitOps for Non-K8s** | Use Crossplane or Terraform Controller to manage cloud resources (RDS, S3, VPC) via GitOps |

---

## Validation Checklist

After completing all exercises, you should be able to:

- [ ] Install and configure ArgoCD **or** Flux from scratch
- [ ] Deploy applications using GitRepository + Kustomization (Flux) or Application CRD (ArgoCD)
- [ ] Structure Kustomize base/overlay for multi-environment
- [ ] Configure automated sync with self-heal and prune
- [ ] Restrict sync windows (ArgoCD) or implement equivalent (Flux)
- [ ] Manage secrets securely with SealedSecrets or External Secrets Operator
- [ ] Implement canary deployments with automated rollback
- [ ] Bootstrap entire platform using App of Apps pattern
- [ ] Detect and remediate drift automatically
- [ ] Recover cluster state entirely from Git

---

## Resources

- [OpenGitOps Principles](https://opengitops.dev/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Flux Documentation](https://fluxcd.io/docs/)
- [Kustomize Documentation](https://kubectl.docs.kubernetes.io/references/kustomize/)
- [SealedSecrets](https://github.com/bitnami-labs/sealed-secrets)
- [Flagger Progressive Delivery](https://flagger.app/)
- [External Secrets Operator](https://external-secrets.io/)