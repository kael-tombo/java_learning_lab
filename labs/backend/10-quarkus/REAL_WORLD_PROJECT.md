# Real World Project: Quarkus

## System sketch

- Packet registry service serving the community seed-exchange network.
- Germination-report flow serving the community seed-exchange network.
- Member-trust scoring.
- Seasonal availability board.
- Partner-nursery sync.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by Quarkus behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Quarkus slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Quarkus hardening plus failure drills against the service.
M3: the solution gains operability instrumentation.
M4: load rehearsal done and handover documentation ready for the project.

## What breaks

- Extension bloat slowing developer turnaround.
- Health check hiding seed-store trouble.
- Germination photo upload overwhelming storage.
- Sync conflict duplicating rare packets.

## Runbook expectations

- Dashboard tracks Quarkus golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- The runbook handles restart, rollback, and data repair end to end.
- Freshness promises live with the SLO review cadence.

## Ship list

- [ ] A live demo of the service demonstrating the full Quarkus journey.
- [ ] Someone unfamiliar could execute the runbook during an outage.
- [ ] Retro naming the riskiest remaining Quarkus assumption.
