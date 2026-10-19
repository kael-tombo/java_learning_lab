# Real World Project: Spring Security

## System sketch

- Member identity service serving the membership reading platform.
- Role administration console serving the membership reading platform.
- Audit of admin actions.
- Brute-force throttling.
- Breach-notification procedure.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by Spring Security behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring Security slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Spring security hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: the project's load rehearsal and its handover documentation both land.

## What breaks

- Overly broad rule exposing private notes.
- Lockout threshold blocking legitimate reading groups.
- Logout leaving a usable session behind.
- Role rename silently opening admin routes.

## Runbook expectations

- Dashboard tracks Spring Security golden signals for the system.
- Alerts page on the platform's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Ship list

- [ ] A live demo of the platform demonstrating the full Spring Security journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining Spring Security assumption.
