# GitOps & ArgoCD Flashcards

## Card 1
Q: What are the five principles of GitOps?
A: Declarative Configuration, Version Controlled & Immutable, Automated Sync, Pull-Based Deployment, Self-Healing

## Card 2
Q: What is the pull-based deployment model?
A: The GitOps operator runs inside the cluster and pulls the desired state from Git, rather than an external CI system pushing to the cluster.

## Card 3
Q: What are the main components of ArgoCD?
A: API Server, Repository Server, Application Controller, Redis Cache, Dex/SSO Provider

## Card 4
Q: What is an ApplicationSet?
A: A Kubernetes CRD that generates ArgoCD Applications from a template using various generators (List, Cluster, Git, Matrix, etc.)

## Card 5
Q: What are sync waves?
A: Ordered execution groups for resource creation during sync, enabling dependency management through wave annotations.

## Card 6
Q: How does self-healing work in GitOps?
A: The operator continuously compares live cluster state against Git state and automatically reverts any manual changes.

## Card 7
Q: What is the purpose of ignoreDifferences in ArgoCD?
A: To suppress known, benign differences between desired and live state (e.g., fields modified by admission controllers).

## Card 8
Q: How does ArgoCD handle multi-cluster management?
A: Multiple Kubernetes clusters can be registered with ArgoCD, and Applications can target any registered cluster.

## Card 9
Q: What are the sync options in ArgoCD?
A: automated (prune, selfHeal, allowEmpty), manual, syncOptions (CreateNamespace, PruneLast, ServerSideApply, etc.)

## Card 10
Q: How do you handle secrets in GitOps?
A: Using Sealed Secrets, External Secrets Operator, SOPS, or ArgoCD Vault Plugin to encrypt secrets before committing to Git.
