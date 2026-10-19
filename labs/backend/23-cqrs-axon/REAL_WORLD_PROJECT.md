# Real World Project: Cqrs Sagas And Projections

## Context

The parcel-network orchestration platform answers a concrete operational need.
Stakeholders judge it by CQRS sagas and projections behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable slices.

## Plan of record

M1: walking skeleton of the parcel-network orchestration platform with one happy path live.
M2: the build hardening plus failure drills against the service.
M3: the operability instrumentation is in place across the build.
M4: handover documentation written once the load rehearsal clears.

## Design

- Shipment saga coordinator.
- Carrier-adapter steps.
- Compensation ledger.
- Projection-lag monitors.
- Customer-notification timeline.

## Operability bar

- Dashboard tracks the offering's golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- Restart, rollback, and data repair each get a runbook section.
- Whoever runs the SLO review cadence answers for freshness promises.

## Exit criteria

- [ ] A live demo of the service demonstrating the full journey.
- [ ] Someone unfamiliar could execute the runbook during an outage.
- [ ] Retro naming the riskiest remaining assumption.

## Known hazards

- Compensation firing twice after a retry.
- Projection lag hiding a lost parcel.
- Event-shape change breaking replay.
- Deadline misfire cancelling a moving parcel.
