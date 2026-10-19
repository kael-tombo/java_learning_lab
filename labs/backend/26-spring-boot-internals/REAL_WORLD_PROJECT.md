# Real World Project: Spring Boot Configuration Internals

## Context

The municipal-services configuration governance answers a concrete operational need.
Stakeholders judge it by Spring Boot configuration internals behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable slices.

## Plan of record

M1: walking skeleton of the municipal-services configuration governance with one happy path live.
M2: the build hardening plus failure drills against the service.
M3: the operability instrumentation is in place across the build.
M4: handover documentation written once the load rehearsal clears.

## Design

- Property-source inventory standard.
- Precedence cheat-sheet per service.
- Profile promotion checklist.
- Binding-failure runbook.
- Configuration-change audit.

## Operability bar

- Dashboard tracks the offering's golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- Restart, rollback, and data repair are all in the runbook.
- Freshness promises live with the SLO review cadence.

## Exit criteria

- [ ] A live demo of the service demonstrating the full journey.
- [ ] Outage-proof runbook: a stranger can follow it.
- [ ] Retro naming the riskiest remaining assumption.

## Known hazards

- Environment variable silently outranking a file fix.
- Relaxed-binding collision merging two keys.
- Profile document loaded in the wrong order.
- Ignored unknown property hiding a typo.
