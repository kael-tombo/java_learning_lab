# Real World Project: Backend Performance

## Problem

The flash-sale checkout hardening answers a concrete operational need.
Stakeholders judge it by backend performance behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable backend performance slices.

## Architecture

- Checkout service with budgets serving the flash-sale checkout hardening.
- Load-test harness in CI.
- Latency dashboard with alerts.
- Pool and cache tunables.
- Capacity-runbook.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Backend performance hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: the project closes with a load rehearsal and handover documentation.

## Operations and SLO checklist

- Dashboard tracks backend performance golden signals for the system.
- Alerts page on the build's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Failure modes

- Pool exhaustion freezing checkout at peak.
- Cache stampede after flash-sale start.
- Unoptimized history query timing out receipts.
- Load test missing the real bottleneck.

## Handover

- [ ] A live demo of the offering demonstrating the full backend performance journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining backend performance assumption.
