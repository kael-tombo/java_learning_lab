# Real World Project: Spring Boot Basics

## Problem

The neighborhood library network loan coordination answers a concrete operational need.
Stakeholders judge it by Spring Boot basics behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring Boot basics slices.

## Architecture

- Loan service behind a gateway serving the neighborhood library network loan coordination.
- Relational store for holds and copies.
- Cache for availability lookups.
- Structured logs plus RED metrics.
- Nightly overdue sweep job.

## Milestones

M1: walking skeleton of the app with one happy path live.
M2: Spring boot basics hardening plus failure drills against the service.
M3: operability instrumentation across the solution.
M4: the project's load rehearsal and its handover documentation both land.

## Operations and SLO checklist

- Dashboard tracks Spring Boot basics golden signals for the system.
- Alerts page on the build's error budget burn, not on noise.
- Runbook covers restart, rollback, and data repair.
- SLO review cadence owns freshness promises of the platform.

## Failure modes

- Overdue sweep double-charging during a retry.
- Availability cache showing a copy already lent.
- Gateway timeout during hold placement.
- Migration adding a column while loans post.

## Handover

- [ ] A live demo of the offering demonstrating the full Spring Boot basics journey.
- [ ] Runbook a stranger could follow during the outage.
- [ ] Retro naming the riskiest remaining Spring Boot basics assumption.
