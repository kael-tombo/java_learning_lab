# Real World Project: Spring Cloud Resilience

## System sketch

- Discovery registry with health checks serving the multi-warehouse bookstore platform.
- Gateway with per-route timeouts serving the multi-warehouse bookstore platform.
- Breaker dashboards per dependency.
- Central banner and pricing config.
- Chaos-drill calendar.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by Spring Cloud resilience behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring Cloud resilience slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Spring cloud resilience hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: load rehearsal runs; handover documentation follows for the project.

## What breaks

- Breaker stuck open after pricing recovers.
- Retry storm during shipping degradation.
- Discovery lag routing to a dead member.
- Central-config outage freezing banner updates.

## Runbook expectations

- Dashboard tracks Spring Cloud resilience golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Ship list

- [ ] A live demo of the service demonstrating the full Spring Cloud resilience journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining Spring Cloud resilience assumption.
