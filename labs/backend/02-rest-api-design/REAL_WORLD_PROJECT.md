# Real World Project: Rest Api Design

## Context

The multi-tenant bookstore catalog platform answers a concrete operational need.
Stakeholders judge it by REST API design behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable REST API design slices.

## Plan of record

M1: walking skeleton of the multi-tenant bookstore catalog platform with one happy path live.
M2: Rest api design hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: load rehearsal runs; handover documentation follows for the project.

## Design

- Catalog service with versioned routes.
- Search index fed by change events.
- Rate-limited partner endpoints.
- OpenAPI contract with examples.
- Consumer-driven contract tests.

## Operability bar

- Dashboard tracks REST API design golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Exit criteria

- [ ] A live demo of the build demonstrating the full REST API design journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining REST API design assumption.

## Known hazards

- Non-idempotent retry creating duplicate loans.
- Page drift when new books arrive mid-traversal.
- Status-code misuse confusing partner retries.
- Breaking field rename without version bump.
