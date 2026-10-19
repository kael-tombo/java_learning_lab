# Real World Project: Caching

## System sketch

- Edge listing cache serving the city-events ticketing front door.
- Price-change invalidation bus serving the city-events ticketing front door.
- Stampede guard at origin.
- Hit-rate SLO dashboard.
- Cache-warming routine.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by caching behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable caching slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Caching hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: handover documentation sits beside the project's load rehearsal.

## What breaks

- Stale price honored after a change.
- Stampede collapsing origin at on-sale minute.
- Eviction sweeping hot listings early.
- Poisoned entry cached from an error response.

## Runbook expectations

- Dashboard tracks caching golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Ship list

- [ ] A live demo of the service demonstrating the full caching journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining caching assumption.
