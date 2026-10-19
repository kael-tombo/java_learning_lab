# Real World Project: Reactive Webflux

## Problem

The flood-watch telemetry network answers a concrete operational need.
Stakeholders judge it by reactive WebFlux behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable reactive WebFlux slices.

## Architecture

- Sensor-ingest reactive pipeline serving the flood-watch telemetry network.
- Level-broadcast stream.
- Slow-consumer protection.
- Alert-threshold evaluator.
- Historical replay tap.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Reactive webflux hardening plus failure drills against the service.
M3: add the operability instrumentation the solution needs.
M4: handover documentation written once the load rehearsal clears.

## Operations and SLO checklist

- Dashboard tracks reactive WebFlux golden signals for the system.
- Alerts page on the build's error budget burn, not on noise.
- The runbook walks through restart, rollback, and data repair.
- Freshness commitments belong to the SLO review cadence.

## Failure modes

- Hidden blocking call freezing the event loop.
- Unbounded buffer exhausting memory at flood peak.
- Fault terminating the whole broadcast.
- Backpressure misconfiguration dropping crest readings.

## Handover

- [ ] A live demo of the offering demonstrating the full reactive WebFlux journey.
- [ ] During an outage, a stranger can work from the runbook alone.
- [ ] Retro naming the riskiest remaining reactive WebFlux assumption.
