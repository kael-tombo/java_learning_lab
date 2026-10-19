# Real World Project: Backend Security Hardening

## Context

The law-firm client-document exchange answers a concrete operational need.
Stakeholders judge it by backend security hardening behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable backend security hardening slices.

## Plan of record

M1: walking skeleton of the law-firm client-document exchange with one happy path live.
M2: Backend security hardening plus failure drills against the service.
M3: operability instrumentation lands across the solution.
M4: load rehearsal done and handover documentation ready for the project.

## Design

- Vault service with tiered routes.
- Managed secret store.
- Upload sandbox and scanner.
- Immutable audit ledger.
- Quarterly access recertification.

## Operability bar

- Dashboard tracks backend security hardening golden signals for the system.
- Alerts page on the app's error budget burn, not on noise.
- The runbook walks through restart, rollback, and data repair.
- Freshness commitments belong to the SLO review cadence.

## Exit criteria

- [ ] A live demo of the build demonstrating the full backend security hardening journey.
- [ ] A runbook clear enough that a stranger can follow it mid-outage.
- [ ] Retro naming the riskiest remaining backend security hardening assumption.

## Known hazards

- Upload bypass smuggling an executable.
- Over-logged PII in the audit trail.
- Stale contractor account downloading briefs.
- Header leak guiding a targeted attack.
