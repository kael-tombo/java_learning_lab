# Debugging ArgoCD Issues

## Common Issues and Solutions

### Issue 1: Application Shows OutOfSync But No Changes
This typically indicates a diff between the generated manifests and the live cluster state. Common causes:
- Dynamic admission controllers (MutatingWebhooks) modify resources after creation
- Operators reconcile resources back to their desired state
- Default values are added by the Kubernetes API server
- Solution: Use ignoreDifferences to suppress known fields

### Issue 2: Application Fails to Sync
Sync failures can be caused by:
- Invalid YAML syntax in manifests
- Missing required fields in Kubernetes resources
- Network issues connecting to Git or target clusters
- Insufficient permissions in the target namespace
- Resource quota limits preventing creation

### Issue 3: Repository Connection Failed
Check the following:
- Repository URL is correct and accessible
- SSH keys or HTTPS credentials are valid
- Git server is reachable from the Repository Server
- Known hosts entry exists for the Git server
- Self-signed TLS certificates are configured in argocd-cm

### Issue 4: Application Stuck in Progressing State
Common causes:
- Pods failing to start due to image pull errors
- Liveness/readiness probes failing
- Persistent volume claims pending
- CRD resources not being reconciled by their controller

### Issue 5: Auto-Sync Not Working
Verify:
- syncPolicy.automated is configured correctly
- selfHeal is enabled for drift correction
- Webhook configuration is correct for instant sync
- Repository Server has correct credentials
- Application controller pod logs show no errors

## Debugging Commands

```bash
# Check ArgoCD component status
kubectl get pods -n argocd
kubectl logs -n argocd deployment/argocd-application-controller
kubectl logs -n argocd deployment/argocd-repo-server
kubectl logs -n argocd deployment/argocd-server

# Debug application
argocd app get myapp
argocd app diff myapp
argocd app logs myapp

# Check repository connection
argocd repo list
argocd repo get (link removed)

# Check cluster connection
argocd cluster list
argocd cluster get https://kubernetes.cluster.local

# Test manifest generation
argocd app manifests myapp --source
```
