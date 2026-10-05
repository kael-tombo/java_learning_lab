# Real-World Project — Service Mesh Operations

## Scenario
The mesh was installed six months ago. Since then: an undocumented
upgrade broke mTLS for half the services, and nobody owns L7 policy
changes that now cause intermittent failures.

## Requirements
- Documented ownership model: platform vs app teams.
- Control-plane upgrade procedure rehearsed in staging.
- Policy repo with review, ownership, and expiry metadata.
- Observability budget: proxy overhead tracked and capped.

## Phase plan
1. **Audit**: export current mesh config; tag every policy with an owner.
2. **Repo**: move mesh config into git; CI validate (`istioctl analyze`).
3. **Stage upgrade**: canary the new control plane in staging; measure.
4. **Traffic check**: run the golden set of requests before/after upgrade.
5. **Overhead report**: p99 added latency per service documented.
6. **Runbooks**: mTLS breakage, proxy crash-loop, config rejected.

## Deliverables
- Mesh config repo and CI checks.
- Upgrade runbook executed once.
- Overhead report.

## Risks & mitigations
- Upgrade regressions → canary control plane.
- Ownership gaps → assign every policy an owner this quarter.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Istio docs — upgrade guidance:
  https://istio.io/latest/docs/setup/upgrade/
- Istio docs — troubleshooting:
  https://istio.io/latest/docs/ops/troubleshooting/

## Definition of done
- Staging upgrade passed with no regressions.
- Every policy has an owner.
- Runbooks tested via a failure drill.
