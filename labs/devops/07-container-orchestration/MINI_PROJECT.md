# Mini Project — Container Orchestration

## Goal
Demonstrate scheduling, scaling, and self-healing with a small cluster.

## Steps
1. Create a deployment with `replicas: 1`.
2. `kubectl scale deployment/app --replicas=5` and observe.
3. Delete a pod manually: it is recreated.
4. Drain a node in kind/minikube: pods reschedule.
5. Add a liveness probe that fails on demand (`/fail` endpoint) and
   watch the kubelet restart the container.
6. Add a PodDisruptionBudget and verify `voluntary disruptions allowed`=1.

## Acceptance criteria
- Scaling and self-healing observed with real commands.
- PDB in place and reasoned about.
- Notes on pod eviction behavior captured.

## Stretch goals
- Add a nodeSelector and tolerations demo.
- Trigger a preemption and explain what happened.

## Estimated time
45 minutes.
