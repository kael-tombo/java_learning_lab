# Real-World Project — Container Orchestration

## Scenario
Your cluster runs 200 pods but autoscaling is manual, node pools are
mixed, and every node drain is a fire drill.

## Requirements
- HPA/VPA policies per workload tier.
- Node pools segmented by workload class.
- Safe upgrade runbooks with PDBs everywhere.
- Capacity headroom measured and reported.

## Phase plan
1. **Baseline capacity review**: utilization, headroom, noisy neighbors.
2. **Autoscaling**: enable HPA on stateless services; document metrics sources.
3. **Node pools**: spot vs on-demand; taints/tolerations to isolate batch jobs.
4. **Disruption safety**: PDBs on all stateful and critical services.
5. **Upgrade rehearsal**: cordon/drain/upgrade one node pool in staging.
6. **Cost lens**: right-size requests vs actual usage.

## Deliverables
- Autoscaling policy doc per service tier.
- Node pool design with taints/tolerations.
- Node upgrade runbook tested once, on purpose.

## Risks & mitigations
- HPA thrash → tune stabilization windows.
- Upgrade surprises → canary node pool first.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes docs — autoscaling:
  https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Kubernetes docs — safe evictions / PDBs:
  https://kubernetes.io/docs/concepts/scheduling-eviction/pod-disruption/

## Definition of done
- Traffic spike absorbed without pager-worthy events.
- Node drain completes with zero voluntary eviction failures.
