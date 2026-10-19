# Real World Project: Graphql

## Problem

The publishing discovery service answers a concrete operational need.
Stakeholders judge it by GraphQL behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable GraphQL slices.

## Architecture

- GraphQL gateway over catalog and reviews serving the publishing discovery service.
- Per-field load planning.
- Persisted query allowlist.
- Usage analytics per field.
- Deprecation calendar for fields.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Graphql hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: handover documentation sits beside the project's load rehearsal.

## Operations and SLO checklist

- Dashboard tracks GraphQL golden signals for the system.
- Alerts page on the service's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Failure modes

- Nested resolver fanning out hundreds of queries.
- Expensive field abused by a partner script.
- Schema change breaking a mobile release.
- Mutation retry double-posting reviews.

## Handover

- [ ] A live demo of the service demonstrating the full GraphQL journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining GraphQL assumption.
