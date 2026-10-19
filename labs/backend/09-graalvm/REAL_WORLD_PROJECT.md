# Real World Project: Graalvm Native Image

## System sketch

- Trail-data compiler serving the field-crew offline mapping tools.
- Native binary release lane serving the field-crew offline mapping tools.
- Map-pack distribution.
- Offline-first sync protocol.
- Device-fleet update channel.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by GraalVM native image behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable GraalVM native image slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Graalvm native image hardening plus failure drills against the service.
M3: the operability instrumentation is in place across the build.
M4: the project gets a load rehearsal plus handover documentation.

## What breaks

- Undeclared reflection breaking a trail renderer.
- Build-time initialization freezing a timestamp.
- Binary size blocking field-device updates.
- Debugging gap when native stack traces obscure causes.

## Runbook expectations

- Dashboard tracks GraalVM native image golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- The runbook handles restart, rollback, and data repair end to end.
- Whoever runs the SLO review cadence answers for freshness promises.

## Ship list

- [ ] A live demo of the service demonstrating the full GraalVM native image journey.
- [ ] Someone unfamiliar could execute the runbook during an outage.
- [ ] Retro naming the riskiest remaining GraalVM native image assumption.
