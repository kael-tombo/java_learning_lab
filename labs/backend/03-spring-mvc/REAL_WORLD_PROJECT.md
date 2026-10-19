# Real World Project: Spring Mvc Dispatch

## Context

The university campus commerce portal answers a concrete operational need.
Stakeholders judge it by Spring MVC dispatch behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring MVC dispatch slices.

## Plan of record

M1: walking skeleton of the university campus commerce portal with one happy path live.
M2: Spring mvc dispatch hardening plus failure drills against the service.
M3: the solution gains operability instrumentation.
M4: load rehearsal done and handover documentation ready for the project.

## Design

- Storefront web tier.
- Interceptor-based locale and tenant resolution.
- Centralized error views.
- Request-timing metrics.
- Bot-throttling filter.

## Operability bar

- Dashboard tracks Spring MVC dispatch golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- Restart, rollback, and data repair each get a runbook section.
- Freshness commitments belong to the SLO review cadence.

## Exit criteria

- [ ] A live demo of the build demonstrating the full Spring MVC dispatch journey.
- [ ] The runbook is followable by a stranger during an outage.
- [ ] Retro naming the riskiest remaining Spring MVC dispatch assumption.

## Known hazards

- Ambiguous mapping shadowing a checkout route.
- Interceptor ordering leaking tenant context.
- Unresolved argument failing late with 500.
- Error view itself throwing during outage.
