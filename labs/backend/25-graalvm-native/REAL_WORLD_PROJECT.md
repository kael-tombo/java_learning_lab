# Real World Project: Graalvm Native Deployment

## System sketch

- Native build-and-sign lane serving the parcel-locker kiosk fleet.
- Fleet image distribution serving the parcel-locker kiosk fleet.
- Kiosk health beacon.
- Offline parcel manifest.
- Remote diagnostics bundle.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by GraalVM native deployment behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable GraalVM native deployment slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Graalvm native deployment hardening plus failure drills against the service.
M3: instrumentation for operability threaded through the solution.
M4: handover documentation written once the load rehearsal clears.

## What breaks

- Dynamic feature slipping past the review into production.
- Image bloat exceeding kiosk storage.
- Missing agent signal hiding a memory leak.
- Slow first interaction after cold boot.

## Runbook expectations

- Dashboard tracks GraalVM native deployment golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- Runbook sections: restart, rollback, data repair.
- Platform freshness promises are owned by the SLO review cadence.

## Ship list

- [ ] A live demo of the service demonstrating the full GraalVM native deployment journey.
- [ ] Outage-proof runbook: a stranger can follow it.
- [ ] Retro naming the riskiest remaining GraalVM native deployment assumption.
