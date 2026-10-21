# ArgoCD Internals

## Reconciliation Loop Implementation
The Application Controller implements a continuous reconciliation loop. Each application is processed in a worker goroutine that:
1. Fetches the desired state from the Repository Server (generated manifests)
2. Queries the live state from the target Kubernetes cluster
3. Compares the two states using a three-way diff algorithm
4. If differences exist, updates the application status and triggers sync
5. Logs all changes for audit purposes

## Three-Way Diff Algorithm
ArgoCD uses a three-way merge diff that compares:
- Last Synced State (from the sync result history)
- Current Live State (from the cluster)
- Desired State (from Git)

This approach prevents unnecessary syncs when the cluster state matches the last synced state even if the desired state differs temporarily.

## Resource Tracking
Each managed resource is tracked with an owner annotation (argocd.argoproj.io/tracking-id) in the format: {application}:{group}/{kind}/{namespace}/{name}. This allows ArgoCD to determine which Application owns each resource and enables proper pruning.

## Health Assessment System
Health is determined through:
1. Built-in health checks for standard Kubernetes resources (Deployment, StatefulSet, Service, etc.)
2. Custom health checks defined in resource.customizations
3. Lua scripts for complex health assessment logic

## Caching Architecture
- Repository Server caches Git repositories locally with configurable TTL
- Application state is cached in Redis
- Kubernetes API responses are cached with informer-backed watches
- Session data is stored in Redis

## Sync Operation Pipeline
1. PreSync hooks run (if configured)
2. Resources are applied in wave order (ascending by wave number)
3. Health of each wave is verified before proceeding to the next
4. PostSync hooks run
5. Sync result is recorded in application history
6. Application status is updated
