# Real World Project: File And Batch Processing

## Problem

The payroll-bureau nightly intake answers a concrete operational need.
Stakeholders judge it by file and batch processing behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable slices.

## Architecture

- File-drop watcher serving the payroll-bureau nightly intake.
- Chunked import workers.
- Quarantine review console.
- Duplicate-run guard.
- Payroll-audit export.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: the build hardening plus failure drills against the service.
M3: the solution gains operability instrumentation.
M4: handover documentation written once the load rehearsal clears.

## Operations and SLO checklist

- Dashboard tracks the offering's golden signals for the system.
- Alerts page on the service's error budget burn, not on noise.
- Runbook sections: restart, rollback, data repair.
- Whoever runs the SLO review cadence answers for freshness promises.

## Failure modes

- Memory blowup on a wide malformed row.
- Resume re-posting already-paid salaries.
- Quarantine overflow hiding fraud patterns.
- Silent encoding change garbling names.

## Handover

- [ ] A live demo of the solution demonstrating the full journey.
- [ ] Someone unfamiliar could execute the runbook during an outage.
- [ ] Retro naming the riskiest remaining assumption.
