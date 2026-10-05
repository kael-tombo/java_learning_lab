# Mini Project — GitOps

## Goal
Point a GitOps operator at a git repo and watch it reconcile a change
you make in git, and a change you sneak in with kubectl.

## Steps
1. Install Argo CD or Flux in a local cluster.
2. Create a git repo with `deployment.yaml` and `service.yaml`.
3. Register the repo with the operator; sync the app.
4. Edit the manifest in git (replicas 1 -> 3), push, watch sync.
5. Edit the live Deployment with kubectl; watch the operator revert it.
6. Remove the chart/manifest from git; watch the operator prune it.

## Acceptance criteria
- Git change reflected in the cluster automatically.
- Out-of-band change reverted by reconciliation.
- Prune works and is understood.

## Stretch goals
- Use Kustomize overlays for two environments.
- Add a helm chart source instead of raw manifests.

## Estimated time
60 minutes.
