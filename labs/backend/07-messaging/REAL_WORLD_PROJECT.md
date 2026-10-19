# Real World Project: Messaging Fundamentals

## System sketch

- Appointment event publisher serving the regional clinic reminder network.
- SMS and email adapters serving the regional clinic reminder network.
- Dead-letter review queue.
- Delivery-attempt dashboard.
- Quiet-hours policy engine.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by messaging fundamentals behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable messaging fundamentals slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Messaging fundamentals hardening plus failure drills against the service.
M3: add the operability instrumentation the solution needs.
M4: load rehearsal done and handover documentation ready for the project.

## What breaks

- Duplicate SMS waking patients at night.
- Poison message blocking morning reminders.
- Topic subscriber missing critical updates.
- Ordering loss scrambling dose instructions.

## Runbook expectations

- Dashboard tracks messaging fundamentals golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- The runbook handles restart, rollback, and data repair end to end.
- Platform freshness promises are owned by the SLO review cadence.

## Ship list

- [ ] A live demo of the service demonstrating the full messaging fundamentals journey.
- [ ] Outage-proof runbook: a stranger can follow it.
- [ ] Retro naming the riskiest remaining messaging fundamentals assumption.
