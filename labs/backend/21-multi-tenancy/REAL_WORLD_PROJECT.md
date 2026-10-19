# Real World Project: Multi-Tenancy

## Problem

The fitness-booking SaaS platform answers a concrete operational need.
Stakeholders judge it by multi-tenancy behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable multi-tenancy slices.

## Architecture

- Tenant-aware booking service serving the fitness-booking SaaS platform.
- Per-tenant branding overlays.
- Usage metering per studio.
- Tenant backup and export.
- Abuse isolation between studios.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Multi-tenancy hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: the project's load rehearsal and its handover documentation both land.

## Operations and SLO checklist

- Dashboard tracks multi-tenancy golden signals for the system.
- Alerts page on the build's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Failure modes

- Missing scope leaking one studios roster.
- Onboarding script touching live tenant rows.
- Noisy tenant starving neighbors at peak.
- Backup restore mixing two studios data.

## Handover

- [ ] A live demo of the offering demonstrating the full multi-tenancy journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining multi-tenancy assumption.
