# Real-World Project — Service Mesh

## Scenario
Your org has 120 services with inconsistent retry logic, partial TLS
coverage, and no visibility into East-West traffic.

## Requirements
- Mesh rolled out incrementally, no big-bang cutover.
- mTLS everywhere by default, with audit-friendly exceptions.
- Golden-signals dashboards per service pair.
- Traffic policy changes are PR-reviewed, not click-ops.

## Phase plan
1. **Pilot**: two low-risk services, permissive mTLS, observe.
2. **Observability first**: dashboards + trace sampling before enforcing policies.
3. **Security rollout**: strict mTLS namespace by namespace.
4. **Traffic policy**: retries/timeouts/circuit breakers as reviewed config.
5. **Progressive delivery**: canary a risky service through the mesh.
6. **Operate the mesh**: control-plane upgrade game day.

## Deliverables
- Phased rollout plan with rollback steps.
- Mesh config repo with CI validation.
- On-call guide for mesh-specific failures.

## Risks & mitigations
- Sidecar overhead → benchmark and right-size proxies.
- Debugging complexity → invest in tracing before enforcement.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Istio docs — getting started and mTLS:
  https://istio.io/latest/docs/setup/getting-started/
- Linkerd docs — service profiles and mTLS:
  https://linkerd.io/2/features/

## Definition of done
- mTLS strict across prod namespaces.
- At least one canary executed through the mesh.
- Mesh upgrade rehearsed in staging.
