# Real World Project: Micronaut

## Problem

The coastal sensor network backend answers a concrete operational need.
Stakeholders judge it by Micronaut behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Micronaut slices.

## Architecture

- Buoy-ingest service serving the coastal sensor network backend.
- Threshold alerting.
- Harbor dashboard feed.
- Sensor-health tracking.
- Storm-mode escalation.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Micronaut hardening plus failure drills against the service.
M3: the operability instrumentation is in place across the build.
M4: load rehearsal done and handover documentation ready for the project.

## Operations and SLO checklist

- Dashboard tracks Micronaut golden signals for the system.
- Alerts page on the build's error budget burn, not on noise.
- Restart, rollback, and data repair are all in the runbook.
- The SLO review cadence is where freshness promises get checked.

## Failure modes

- Missing introspection entry hiding a buoy type.
- Threshold misconfiguration silencing storm alerts.
- Sensor burst overwhelming the intake.
- Dashboard polling amplifying load.

## Handover

- [ ] A live demo of the offering demonstrating the full Micronaut journey.
- [ ] A runbook clear enough that a stranger can follow it mid-outage.
- [ ] Retro naming the riskiest remaining Micronaut assumption.
