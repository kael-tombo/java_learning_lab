# Real World Project: Kafka Integration

## Context

The museum digital-experience analytics answers a concrete operational need.
Stakeholders judge it by Kafka integration behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Kafka integration slices.

## Plan of record

M1: walking skeleton of the museum digital-experience analytics with one happy path live.
M2: Kafka integration hardening plus failure drills against the service.
M3: add the operability instrumentation the solution needs.
M4: load rehearsal done and handover documentation ready for the project.

## Design

- Click-ingest topic family.
- Sessionization consumer.
- Real-time dashboard sink.
- Archival replay bucket.
- Schema evolution policy.

## Operability bar

- Dashboard tracks Kafka integration golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- The runbook walks through restart, rollback, and data repair.
- Freshness promises live with the SLO review cadence.

## Exit criteria

- [ ] A live demo of the build demonstrating the full Kafka integration journey.
- [ ] During an outage, a stranger can work from the runbook alone.
- [ ] Retro naming the riskiest remaining Kafka integration assumption.

## Known hazards

- Rebalance storm stalling intake.
- Offset committed before handling loses clicks.
- Hot partition from a viral exhibit.
- Retention expiry deleting events under dispute.
