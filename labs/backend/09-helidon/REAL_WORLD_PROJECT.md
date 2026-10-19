# Real World Project: Helidon

## Context

The maritime facility operations backend answers a concrete operational need.
Stakeholders judge it by Helidon behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Helidon slices.

## Plan of record

M1: walking skeleton of the maritime facility operations backend with one happy path live.
M2: Helidon hardening plus failure drills against the service.
M3: the solution gains operability instrumentation.
M4: handover documentation written once the load rehearsal clears.

## Design

- Facility registry.
- Shift-planning service.
- Maintenance dispatch.
- Safety-check aud_SLO.
- Harbor-master dashboard.

## Operability bar

- Dashboard tracks Helidon golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- The runbook handles restart, rollback, and data repair end to end.
- The SLO review cadence is where freshness promises get checked.

## Exit criteria

- [ ] A live demo of the build demonstrating the full Helidon journey.
- [ ] During an outage, a stranger can work from the runbook alone.
- [ ] Retro naming the riskiest remaining Helidon assumption.

## Known hazards

- Roster-store lag cascading into lamp reporting.
- Misrouted request hiding a lamp fault.
- Health check masking partial degradation.
- Shift overlap losing lamp coverage.
