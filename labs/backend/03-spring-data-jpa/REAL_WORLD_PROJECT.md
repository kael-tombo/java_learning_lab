# Real World Project: Spring Data Jpa

## System sketch

- Rental bounded-context service serving the video-chain rental ledger.
- Read-optimized history projection serving the video-chain rental ledger.
- Late-fee calculation job.
- Archival export pipeline.
- Membership analytics feed.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by Spring Data JPA behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring Data JPA slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Spring data jpa hardening plus failure drills against the service.
M3: operability instrumentation lands across the solution.
M4: the project gets a load rehearsal plus handover documentation.

## What breaks

- N+1 queries slowing history pages.
- Partial checkout leaving films reserved but unpaid.
- Derived-query rename silently changing semantics.
- Schema drift between environments.

## Runbook expectations

- Dashboard tracks Spring Data JPA golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- The runbook handles restart, rollback, and data repair end to end.
- Freshness promises live with the SLO review cadence.

## Ship list

- [ ] A live demo of the service demonstrating the full Spring Data JPA journey.
- [ ] The runbook is followable by a stranger during an outage.
- [ ] Retro naming the riskiest remaining Spring Data JPA assumption.
