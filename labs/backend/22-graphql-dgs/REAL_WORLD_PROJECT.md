# Real World Project: Graphql With Dgs

## System sketch

- Inventory subgraph service serving the city bike-share rider platform.
- Trip-history subgraph serving the city bike-share rider platform.
- Batched loaders per relation.
- Schema-registry checks.
- Rider-app query analytics.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by GraphQL with DGS behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable GraphQL with DGS slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Graphql with dgs hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: documentation hands the project over after the load rehearsal.

## What breaks

- Unbatched resolver melting under rush-hour polling.
- Schema drift between registry and service.
- Overly deep query stalling trip lookups.
- Boundary dispute duplicating bike ownership.

## Runbook expectations

- Dashboard tracks GraphQL with DGS golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Ship list

- [ ] A live demo of the service demonstrating the full GraphQL with DGS journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining GraphQL with DGS assumption.
