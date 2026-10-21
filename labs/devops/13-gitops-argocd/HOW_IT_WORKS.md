# How ArgoCD Works

## The Pull-Based Model
ArgoCD operates on a pull-based deployment model. Unlike traditional CI/CD tools that push deployments to the cluster (requiring cluster API access from the CI system), ArgoCD runs inside the cluster and pulls the desired state from Git. This eliminates the need for external systems to have credentials to access the cluster.

## Desired State Reconciliation
The core mechanism is the reconciliation loop:
1. ArgoCD polls the Git repository at a configurable interval (default 3 minutes)
2. The Repository Server clones the repo and generates Kubernetes manifests
3. The Application Controller compares these manifests against what is running in the cluster
4. If they match, no action is taken
5. If they differ, ArgoCD applies the changes (if auto-sync is enabled)

## Webhook Integration
For instant deployment triggering, ArgoCD integrates with Git webhooks:
1. Developer pushes code to Git
2. Git server sends a webhook payload to ArgoCD API Server
3. API Server notifies the Application Controller
4. Controller immediately triggers a reconciliation cycle

## Multi-Cluster Management
ArgoCD can manage multiple Kubernetes clusters from a single installation:
1. Each cluster is registered with its API server URL and credentials
2. Applications specify which cluster to deploy to
3. The Application Controller communicates with each cluster's API server directly
4. ApplicationSet generators can create applications for all registered clusters automatically

## Self-Healing Mechanism
When self-healing is enabled, ArgoCD actively monitors for configuration drift:
1. Periodic reconciliation detects differences between Git and cluster
2. If manual changes are detected (kubectl edit, kubectl scale, etc.)
3. ArgoCD automatically reverts the changes to match Git configuration
4. The revert operation is logged for audit purposes

## Resource Pruning
When manifests are removed from Git, ArgoCD can automatically remove the corresponding resources from the cluster:
1. Reconciliation detects resources in the cluster not present in Git
2. If prune is enabled, those resources are deleted
3. PruneLast option ensures pruning happens after all other sync operations
4. Cascade deletion follows Kubernetes garbage collection rules
