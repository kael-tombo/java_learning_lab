# Real World Project: Transaction Management

## Problem

The cooperative bank payments ledger answers a concrete operational need.
Stakeholders judge it by transaction management behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable transaction management slices.

## Architecture

- Transfer orchestration service serving the cooperative bank payments ledger.
- Double-entry posting store.
- Reconciliation batch.
- Fraud-hold interception.
- Regulator export.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Transaction management hardening plus failure drills against the service.
M3: instrumentation for operability threaded through the solution.
M4: deliver the load rehearsal and its handover documentation.

## Operations and SLO checklist

- Dashboard tracks transaction management golden signals for the system.
- Alerts page on the build's error budget burn, not on noise.
- Restart, rollback, and data repair are all in the runbook.
- Freshness commitments belong to the SLO review cadence.

## Failure modes

- Lost update under concurrent withdrawals.
- Phantom reads shifting a daily total.
- Overly strict isolation throttling peak traffic.
- Nested fee call committing apart from its transfer.

## Handover

- [ ] A live demo of the offering demonstrating the full transaction management journey.
- [ ] The runbook is followable by a stranger during an outage.
- [ ] Retro naming the riskiest remaining transaction management assumption.
