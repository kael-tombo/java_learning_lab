# Real World Project: Server-Sent Events

## System sketch

- Score-ingest desk serving the community-league live-score network.
- Broadcast fan-out tier serving the community-league live-score network.
- Replay buffer per match.
- Connection-count dashboard.
- Rain-delay content filler.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by server-sent events behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable server-sent events slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Server-sent events hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: documentation hands the project over after the load rehearsal.

## What breaks

- Cursor loss replaying the whole match.
- Silent connection death during rain delay.
- Fan-out hotspot favoring early subscribers.
- Replay buffer evicting a reconnecting final-over fan.

## Runbook expectations

- Dashboard tracks server-sent events golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Ship list

- [ ] A live demo of the service demonstrating the full server-sent events journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining server-sent events assumption.
