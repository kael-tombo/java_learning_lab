# Real World Project: Scheduling

## Context

The bakery-chain overnight operations answers a concrete operational need.
Stakeholders judge it by scheduling behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable scheduling slices.

## Plan of record

M1: walking skeleton of the bakery-chain overnight operations with one happy path live.
M2: Scheduling hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: the project's load rehearsal and its handover documentation both land.

## Design

- Job scheduler with calendar.
- Order-placement worker.
- Report publisher.
- Overlap and miss dashboards.
- On-call runbook for failures.

## Operability bar

- Dashboard tracks scheduling golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Exit criteria

- [ ] A live demo of the build demonstrating the full scheduling journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining scheduling assumption.

## Known hazards

- Overlapping runs double-ordering flour.
- Crash mid-job leaving half-placed orders.
- Timezone shift firing jobs an hour early.
- Silent missed run discovered at dawn.
