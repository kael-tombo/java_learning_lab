# Real World Project: Rest Apis With Spring

## Problem

The regional repairs franchise order hub answers a concrete operational need.
Stakeholders judge it by REST APIs with Spring behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable slices.

## Architecture

- Order intake service serving the regional repairs franchise order hub.
- Technician assignment queue.
- SMS notification adapter.
- Audit log of status transitions.
- Admin dashboard feed.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: the build hardening plus failure drills against the service.
M3: operability instrumentation lands across the solution.
M4: load rehearsal first, handover documentation after.

## Operations and SLO checklist

- Dashboard tracks the offering's golden signals for the system.
- Alerts page on the service's error budget burn, not on noise.
- Restart, rollback, and data repair each get a runbook section.
- The SLO review cadence is where freshness promises get checked.

## Failure modes

- Completion posted twice by a retrying technician app.
- Validation gap admitting orders without contact details.
- Slow listing under franchise-wide polling.
- Assignment race between two dispatchers.

## Handover

- [ ] A live demo of the solution demonstrating the full journey.
- [ ] The runbook is followable by a stranger during an outage.
- [ ] Retro naming the riskiest remaining assumption.
