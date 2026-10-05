# Vision — Kubernetes

## Why this lab exists
Containers solved packaging; Kubernetes solves scheduling, self-healing,
and scale. This lab is the hinge between Docker and everything GitOps.

## What we are building toward
- Declarative desired state: you describe it, the control plane reconciles.
- Apps that survive node loss without human intervention.
- A cluster you understand well enough to debug at 2 AM.

## Principles
- Cattle, not pets: assume any pod dies.
- Declarative manifests checked into git.
- Least privilege via RBAC and scoped service accounts.
- The API server is the only front door — guard it.

## Anti-patterns to retire
- Running `kubectl exec` as routine operations.
- `latest` tags and missing resource requests/limits.
- Cluster admin for every service account.
- "It works on minikube" as the only test.

## Success criteria
- Can explain what the control plane does vs. what kubelets do.
- Can read a Pod spec and predict its scheduling behavior.
- Can recover from a crashed pod and a drained node without panic.

## Looking ahead
Helm (06), orchestration (07), GitOps (12), and platform engineering (20)
all build on this mental model.
