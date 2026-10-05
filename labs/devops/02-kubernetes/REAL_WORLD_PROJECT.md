# Real-World Project — Kubernetes

## Scenario
Your platform team adopts Kubernetes for 40 services. Within weeks:
services have no resource limits, images are `:latest`, and one bad
deploy takes the cluster down during a traffic spike.

## Requirements
- Every workload declares requests/limits and probes.
- Image tags are immutable (semver or SHA).
- Deployments are reversible in under 5 minutes.
- RBAC follows least privilege.

## Phase plan
1. **Baseline**: inventory deployments; flag missing limits, missing
   probes, `:latest` tags.
2. **Golden template**: a Helm chart / kustomize overlay that every team
   must inherit — probes, resources, PDB, and securityContext by default.
3. **Progressive rollout**: enable `maxSurge`/`maxUnavailable` policies;
   rehearse `kubectl rollout undo` in staging.
4. **Observability hooks**: wire Prometheus annotations / ServiceMonitor.
5. **Policy layer**: add PodSecurity admission (restricted) and a
   default-deny NetworkPolicy baseline.
6. **Chaos drill**: kill the busiest pod and a node; verify the SLO.

## Deliverables
- Golden manifest template with docs.
- Per-service checklist PR that closes the baseline gaps.
- Game-day report with findings and fixes.

## Risks & mitigations
- Template fatigue → provide one `make deploy` path.
- Team pushback → enforce via admission webhook, not wiki pages.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes official docs — pod lifecycle and probes:
  https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- Kubernetes docs — resource management:
  https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

## Definition of done
- 100% of services use the golden template.
- Rollback time measured and under 5 minutes.
- One chaos drill executed and documented.
