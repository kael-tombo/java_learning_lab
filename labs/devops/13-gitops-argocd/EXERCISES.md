# ArgoCD & GitOps Exercises

## Exercise 1: Install ArgoCD
Install ArgoCD on a Kubernetes cluster using the official manifests or Helm chart. Access the web UI via port-forward and log in with the admin user.

Requirements:
- Use `kubectl create namespace argocd` then apply the install manifests
- Verify all pods are running: argocd-server, argocd-repo-server, argocd-application-controller, argocd-redis
- Port-forward the ArgoCD server service to localhost:8080
- Retrieve the initial admin password from the secret

## Exercise 2: Deploy Your First Application
Create a Git repository with a simple nginx deployment manifest. Register the repository with ArgoCD and create an Application that deploys nginx.

Steps:
1. Create a GitHub repo with a `k8s/` directory containing nginx-deployment.yaml and nginx-service.yaml
2. Register the repo in ArgoCD via CLI or UI
3. Create an Application pointing to the repo, path, and target namespace
4. Sync the application manually
5. Verify the nginx pod is running with `kubectl get pods`

## Exercise 3: Enable Auto-Sync with Self-Healing
Enable auto-sync with prune and selfHeal on your nginx application.

Tasks:
1. Update the Application to enable automated sync policy
2. Set prune: true and selfHeal: true
3. Manually delete the nginx deployment with kubectl delete deployment nginx
4. Verify ArgoCD automatically recreates it (self-healing)
5. Manually scale the deployment to 5 replicas with kubectl scale
6. Verify ArgoCD reverts it back to the desired state

## Exercise 4: Helm Chart Deployment
Deploy a Helm chart using ArgoCD. Create an Application that sources a Helm chart from a Helm repository.

Steps:
1. Create an Application with source pointing to a Helm repo (e.g., bitnami/nginx)
2. Set the chart name and version
3. Override values via the ArgoCD Application parameters
4. Sync and verify the Helm release is created
5. Update values and verify ArgoCD syncs the changes

## Exercise 5: ApplicationSet with List Generator
Create an ApplicationSet that generates applications for multiple environments using a list generator.

Tasks:
1. Define an ApplicationSet with a list generator containing dev, staging, and production entries
2. Each entry should specify environment-specific parameters like replica count and namespace
3. Use Go template expressions in the template spec
4. Apply the ApplicationSet and verify three Applications are created
5. Sync all applications and verify they are healthy

## Exercise 6: Multi-Cluster Deployment
Configure ArgoCD to manage multiple clusters and deploy applications to each.

Requirements:
1. Register a second cluster (or use the same cluster with different namespaces)
2. Create an ApplicationSet using the cluster generator
3. Deploy different configurations per cluster based on cluster labels
4. Verify applications are created for each registered cluster
5. Test sync across all clusters simultaneously

## Exercise 7: Sync Waves and Resource Ordering
Implement sync waves to manage resource creation order for a stateful application that requires a database to be deployed before the application.

Tasks:
1. Create manifests with sync-wave annotations: CRD (-3), Namespace (-2), ConfigMap (-1), Database (0), Application (1), Service (2), Ingress (3)
2. Apply the Application
3. Verify resources are created in wave order
4. Check that wave 1 resources are not created until wave 0 resources are healthy

## Exercise 8: RBAC and Projects
Configure ArgoCD Projects with RBAC for multi-team access control.

Steps:
1. Create two Projects: team-alpha and team-beta
2. Configure source repositories and destination clusters per project
3. Set up RBAC roles: admin, developer, viewer
4. Create role bindings for users
5. Test access restrictions

## Exercise 9: Sealed Secrets with ArgoCD
Integrate Sealed Secrets with ArgoCD to manage encrypted secrets in Git.

Tasks:
1. Install the Sealed Secrets controller
2. Create a sealed secret from a plain secret
3. Commit the sealed secret YAML to the Git repository
4. Deploy via ArgoCD and verify the secret is unsealed in the cluster

## Exercise 10: Disaster Recovery with ArgoCD
Implement a disaster recovery strategy using ArgoCD.

Steps:
1. Export all ArgoCD configurations using argocd app export
2. Back up the ArgoCD namespace resources
3. Simulate a cluster failure by deleting all applications
4. Restore from backup by reapplying the exported configurations
5. Verify all applications sync and become healthy

## Exercise 11: Custom Health Checks
Implement custom health checks for a custom resource definition (CRD).

Tasks:
1. Define a resource customization in argocd-cm ConfigMap
2. Implement a Lua script for health assessment
3. Test with a sample CRD
4. Verify health status is reported correctly in the ArgoCD UI

## Exercise 12: ArgoCD Notifications
Configure ArgoCD notifications for sync events.

Steps:
1. Install the ArgoCD Notifications controller
2. Configure a Slack webhook trigger for successful syncs
3. Configure an email trigger for sync failures
4. Test by triggering sync events
