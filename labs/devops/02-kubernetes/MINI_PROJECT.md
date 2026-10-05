# Mini Project — Kubernetes

## Goal
Deploy a two-tier app (frontend + backend) to a local cluster with
services, probes, and a rolling update.

## Architecture
```
[ Deployment: web (2 replicas) ] --> [ Service: web ]
[ Deployment: api (3 replicas) ] --> [ Service: api ] --> [ Redis sidecar-ish ]
ConfigMap for shared config, Secret for credentials.
```

## Steps
1. Start a local cluster (`kind` or `minikube`).
2. Write `ConfigMap` with `API_URL` values.
3. Write a `Deployment` for `api` with:
   - `replicas: 3`, resource requests/limits
   - `livenessProbe` and `readinessProbe` on `/health`
4. Expose it with a `ClusterIP` Service.
5. Write a `Deployment` + `Service` for `web` referencing the api.
6. `kubectl apply -f .` and watch `kubectl get pods -w`.
7. Break something (bad image tag) and observe the rollout stall.
8. Roll back: `kubectl rollout undo deployment/api`.

## Acceptance criteria
- All pods `Running` and `Ready`.
- `kubectl describe pod` shows probe config.
- Rolling update completes; old ReplicaSet scaled down.
- Rollback returns to previous version in under a minute.

## Stretch goals
- Add an HPA based on CPU.
- Add a `NetworkPolicy` default-deny ingress.

## Estimated time
60–90 minutes.
