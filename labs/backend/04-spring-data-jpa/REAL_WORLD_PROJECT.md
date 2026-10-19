# Real World Project: Spring Data Jpa Querying

## Problem

The enterprise staff directory platform answers a concrete operational need.
Stakeholders judge it by Spring Data JPA querying behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable slices.

## Architecture

- Directory service with faceted search serving the enterprise staff directory platform.
- HR synchronization importer.
- Access-review reporting.
- Cached org-chart snapshots.
- Audit trail of profile edits.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: the build hardening plus failure drills against the service.
M3: the operability instrumentation is in place across the build.
M4: handover documentation written once the load rehearsal clears.

## Operations and SLO checklist

- Dashboard tracks the offering's golden signals for the system.
- Alerts page on the service's error budget burn, not on noise.
- The runbook walks through restart, rollback, and data repair.
- Whoever runs the SLO review cadence answers for freshness promises.

## Failure modes

- Derived-query keyword misread returning wrong staff subset.
- Unbounded export exhausting memory.
- Fetch plan change reintroducing N+1 silently.
- HR sync overwriting manual corrections.

## Handover

- [ ] A live demo of the solution demonstrating the full journey.
- [ ] During an outage, a stranger can work from the runbook alone.
- [ ] Retro naming the riskiest remaining assumption.
