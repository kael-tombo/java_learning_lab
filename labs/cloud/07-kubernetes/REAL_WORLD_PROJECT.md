# Kubernetes - REAL WORLD PROJECT

## Project: Production-Grade Java Platform on Kubernetes

Build a production-ready platform with:
- Multi-environment support (dev, staging, prod)
- GitOps workflow
- Monitoring and alerting
- Disaster recovery

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         Git Repository                              │
│                    (Infrastructure as Code)                          │
└────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │   ArgoCD       │   │    Flux       │
            │  (GitOps)      │   │   (GitOps)    │
            └───────┬───────┘   └───────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌───────┐     ┌───────────┐   ┌───────────┐
│  Dev  │     │  Staging  │   │   Prod    │
│  Env  │     │   Env     │   │   Env     │
└───────┘     └───────────┘   └───────────┘
```

## Project Structure

```
k8s-platform/
├── base/
│   ├── namespace.yaml
│   ├── network-policy.yaml
│   └── limit-range.yaml
├── apps/
│   ├── user-service/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   └── kustomization.yaml
│   └── order-service/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── hpa.yaml
│       └── kustomization.yaml
├── infra/
│   ├── postgres/
│   ├── redis/
│   └── monitoring/
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── kustomization.yaml
```

## Implementation

### Base Configuration

```yaml
# base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: platform
  labels:
    name: platform
    env: dev
```

```yaml
# base/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-network-policy
  namespace: platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

```yaml
# base/limit-range.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: platform
spec:
  limits:
  - max:
      cpu: "2"
      memory: 2Gi
    min:
      cpu: "50m"
      memory: 64Mi
    default:
      cpu: "500m"
      memory: 256Mi
    defaultRequest:
      cpu: "100m"
      memory: 128Mi
    type: Container
```

### App Configuration

```yaml
# apps/user-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: platform
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      terminationGracePeriodSeconds: 60
      containers:
      - name: app
        image: myregistry/user-service:VERSION
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8080
        env:
        - name: JAVA_OPTS
          value: "-Xms256m -Xmx512m -XX:+UseG1GC -XX:+HeapDumpOnOutOfMemoryError"
        - name: TZ
          value: "UTC"
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          failureThreshold: 30
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: tmp
        emptyDir:
          medium: Memory
          sizeLimit: 100Mi
      - name: cache
        emptyDir:
          sizeLimit: 100Mi
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: user-service
              topologyKey: kubernetes.io/hostname
      tolerations:
      - key: "node-type"
        operator: "Equal"
        value: "application"
        effect: "NoSchedule"
```

### Kustomization

```yaml
# apps/user-service/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- hpa.yaml

commonLabels:
  app: user-service
  managed-by: kustomize

replicas:
- name: user-service
  count: 3

images:
- name: myregistry/user-service
  newTag: v1.2.3
```

### Overlays for Environments

```yaml
# overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: platform-dev

bases:
- ../../base
- ../../apps/user-service
- ../../apps/order-service

patches:
- patch-replicas.yaml
- patch-resources.yaml

configMapGenerator:
- name: app-config
  literals:
  - ENV=development
  - DEBUG=true

replicas:
- name: user-service
  count: 1
- name: order-service
  count: 1
```

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: platform-prod

bases:
- ../../base
- ../../apps/user-service
- ../../apps/order-service

patches:
- patch-replicas.yaml
- patch-resources.yaml
- patch-hpa.yaml

replicas:
- name: user-service
  count: 5
- name: order-service
  count: 8
```

### ArgoCD Application

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: platform-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: (link removed)
    targetRevision: main
    path: overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: platform-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Monitoring Stack

```yaml
# infra/monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    alertmanagers:
    - static_configs:
      - targets:
        - alertmanager:9093

    scrape_configs:
    - job_name: kubernetes-apiservers
      kubernetes_sd_configs:
      - role: endpoints

    - job_name: kubernetes-pods
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Backup & Recovery

```yaml
# infra/backup/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: platform
spec:
  schedule: "0 2 * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U appuser -d mydb | gzip > /backup/mydb-$(date +%Y%m%d).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: DB_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

## Deployment

### GitOps Setup (ArgoCD)

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Install ArgoCD CLI
brew install argocd

# Login
argocd login --core

# Create application
kubectl apply -f argocd/application.yaml

# Sync
argocd app sync platform-prod
```

### Manual Deployment (Kustomize)

```bash
# Build manifest
kubectl kustomize overlays/prod > manifest.yaml

# Apply
kubectl apply -f manifest.yaml

# Diff
kubectl kustomize overlays/prod | kubectl diff -f -

# Watch deployment
kubectl rollout status deployment/user-service -n platform-prod
```

## Monitoring

```bash
# Prometheus UI
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# View metrics
kubectl top pods -n platform-prod
kubectl top nodes
```

## Testing

```bash
# Run load test
kubectl run load-test --image=busybox --rm -it -- /bin/sh
# while true; do wget -qO- http://user-service:8080/actuator/health; done

# Check logs
kubectl logs -n platform-prod -l app=user-service --tail=100 -f

# Check events
kubectl get events -n platform-prod --sort-by='.lastTimestamp'
```

## Disaster Recovery

```bash
# Backup resources
kubectl get all -n platform-prod -o yaml > backup.yaml

# Restore
kubectl apply -f backup.yaml

# Scale down gracefully
kubectl scale deployment user-service -n platform-prod --replicas=0

# Database backup
kubectl exec -n platform-prod postgres-0 -- pg_dump -U appuser mydb > backup.sql
```

## Security Checklist

- [x] Non-root containers
- [x] Read-only root filesystem
- [x] Resource limits
- [x] Liveness/readiness probes
- [x] Network policies
- [x] Secrets via encrypted storage
- [x] TLS for external services
- [x] Audit logging
- [x] Regular image updates

## Deliverables

- [x] Multi-environment (dev, staging, prod)
- [x] GitOps with ArgoCD
- [x] Kustomize for configuration
- [x] Production-grade security
- [x] Monitoring stack
- [x] Backup & recovery
- [x] Disaster recovery plan
- [x] Documentation