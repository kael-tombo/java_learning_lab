# Real World Project: Cqrs And Event Sourcing

## System sketch

- Booking command service serving the venue ticketing platform.
- Event store with ordered streams serving the venue ticketing platform.
- Seat-availability projections.
- Resale transfer workflow.
- Entry-scan read model.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by CQRS and event sourcing behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: the offering hardening plus failure drills against the service.
M3: the solution gains operability instrumentation.
M4: load rehearsal done and handover documentation ready for the project.

## What breaks

- Projection lag selling an already-held seat.
- Out-of-order event corrupting a section count.
- Snapshot gap hiding a refund event.
- Command retry posting the same hold twice.

## Runbook expectations

- Dashboard tracks the service's golden signals for the system.
- Alerts page on the platform's error budget burn, not on noise.
- Restart, rollback, and data repair are all in the runbook.
- Freshness promises live with the SLO review cadence.

## Ship list

- [ ] A live demo of the platform demonstrating the full journey.
- [ ] Outage-proof runbook: a stranger can follow it.
- [ ] Retro naming the riskiest remaining assumption.
