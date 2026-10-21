# Common Mistakes in ArgoCD & GitOps

## Mistake 1: Storing Secrets in Git
Storing plaintext secrets in Git repositories defeats the purpose of GitOps security. Always use Sealed Secrets, External Secrets Operator, SOPS, or Vault integration for sensitive data.

## Mistake 2: Not Enabling Self-Healing
Without self-healing, manual changes to the cluster (kubectl scale, edit deployment) persist and cause configuration drift. Always enable selfHeal: true in production environments once the initial deployment is verified.

## Mistake 3: Ignoring Resource Pruning
Deleting manifests from Git without enabling prune leaves orphaned resources in the cluster. Always set prune: true in automated sync policies, but ensure you understand which resources will be affected.

## Mistake 4: Overlooking RBAC Configuration
Default ArgoCD installation uses a single admin user. For production deployments, configure RBAC with least-privilege access, integrate with SSO, and define Project-scoped permissions.

## Mistake 5: Not Testing Sync Waves
Assuming Kubernetes resources can be created in any order leads to deployment failures. Always define sync waves for applications with dependencies on other resources.

## Mistake 6: Using Only Manual Sync
Manual sync is useful for learning but impractical for production. Teams get comfortable with manual sync and forget to enable automation. Transition to automated sync early.

## Mistake 7: Poor Git Repository Structure
A flat directory structure with hundreds of YAML files becomes unmanageable. Use a consistent directory hierarchy organized by cluster, namespace, and application.

## Mistake 8: Not Monitoring ArgoCD Itself
ArgoCD is critical infrastructure. Monitor ArgoCD components with Prometheus, set up alerts for sync failures, and back up ArgoCD configuration regularly.

## Mistake 9: Ignoring Webhook Configuration
Relying solely on polling (3 minute default) delays deployment propagation. Configure webhooks from Git providers for near-instant sync triggering.

## Mistake 10: Mixing Different Config Management Tools
Using Helm, Kustomize, and raw YAML in the same project without clear boundaries creates confusion. Standardize on one config management tool per team or project.
