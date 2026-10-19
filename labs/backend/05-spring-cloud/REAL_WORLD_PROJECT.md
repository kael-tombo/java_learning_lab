# Real World Project: Spring Cloud Coordination

## Context

The neighborhood retail chain platform answers a concrete operational need.
Stakeholders judge it by Spring Cloud coordination behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring Cloud coordination slices.

## Plan of record

M1: walking skeleton of the neighborhood retail chain platform with one happy path live.
M2: Spring cloud coordination hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: the project closes with a load rehearsal and handover documentation.

## Design

- Configuration service with versioned files.
- Registry with health-checked members.
- Gateway with route policies.
- Fallback catalog pages.
- Change-audit log.

## Operability bar

- Dashboard tracks Spring Cloud coordination golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Exit criteria

- [ ] A live demo of the build demonstrating the full Spring Cloud coordination journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining Spring Cloud coordination assumption.

## Known hazards

- Stale price served after a failed refresh.
- Registry flapping during network wobble.
- Gateway route shadowing a new service.
- Fallback masking a prolonged till outage.
