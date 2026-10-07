# ArgoCD Code Deep Dive

## ArgoCD Application YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-production
  namespace: argocd
  labels:
    app: myapp
    environment: production
    team: platform
spec:
  project: default
  source:
    repoURL: (link removed).git
    targetRevision: HEAD
    path: k8s/overlays/production
    helm:
      valueFiles:
        - values-prod.yaml
      parameters:
        - name: replicaCount
          value: "5"
        - name: image.tag
          value: 1.2.3
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
      - RespectIgnoreDifferences=true
      - ApplyOutOfSyncOnly=true
      - ServerSideApply=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
    - group: autoscaling
      kind: HorizontalPodAutoscaler
      jsonPointers:
        - /spec/metrics
```

## Multi-Cluster ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp-multi-cluster
  namespace: argocd
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]
  generators:
    - clusters:
        selector:
          matchLabels:
            environment: production
    - list:
        elements:
          - environment: prod
            region: us-east-1
          - environment: prod
            region: eu-west-1
  template:
    metadata:
      name: '{{name}}-myapp-{{environment}}'
      labels:
        environment: '{{environment}}'
        region: '{{region}}'
    spec:
      project: default
      source:
        repoURL: (link removed).git
        targetRevision: HEAD
        path: 'k8s/overlays/{{environment}}'
      destination:
        server: '{{server}}'
        namespace: myapp-{{environment}}
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

## Sync Waves Example

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp-system
  annotations:
    argocd.argoproj.io/sync-wave: "-5"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: myapp-system
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: myapp-system
  annotations:
    argocd.argoproj.io/sync-wave: "-2"
type: Opaque
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp-system
  annotations:
    argocd.argoproj.io/sync-wave: "0"
spec:
  replicas: 3
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
          image: myapp:1.2.3
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: myapp-system
  annotations:
    argocd.argoproj.io/sync-wave: "1"
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
```

## ArgoCD Config Management Plugins

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  configManagementPlugins: |
    - name: custom-plugin
      generate:
        command: ["/usr/local/bin/custom-plugin"]
      parameters:
        static:
          - name: values
            title: Values file
            string: true
          - name: parameters
            title: Parameters
            collectionType: map
```

## RBAC Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly
  policy.csv: |
    p, role:org-admin, applications, *, */*, allow
    p, role:org-admin, clusters, get, *, allow
    p, role:team-lead, applications, sync, */*, allow
    p, role:team-lead, applications, get, */*, allow
    g, alice, role:org-admin
    g, bob, role:team-lead
    g, team-alpha, role:team-lead
  scopes: '[groups, email]'
```

## ArgoCD CLI Commands

```bash
# Login to ArgoCD
argocd login argocd.example.com --sso

# List applications
argocd app list

# Create application
argocd app create myapp \
  --repo (link removed).git \
  --path k8s/overlays/production \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace myapp-production \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Sync application
argocd app sync myapp --prune

# Get application details
argocd app get myapp

# Rollback application
argocd app rollback myapp abcdef123

# Set application parameters
argocd app set myapp --helm-set replicaCount=5

# List clusters
argocd cluster list

# Add cluster
argocd cluster add my-cluster-context

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
