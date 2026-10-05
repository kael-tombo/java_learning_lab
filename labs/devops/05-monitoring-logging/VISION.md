# Vision — Monitoring & Logging

## Why this lab exists
You cannot fix what you cannot see. Observability turns incidents from
guesswork into evidence-driven debugging.

## What we are building toward
- Metrics, logs, and traces correlated by a common request ID.
- Alerts that page only when a human must act.
- Dashboards that tell the story of system health at a glance.

## Principles
- SLOs first, alerts second: alert on symptoms, not noise.
- Structured logs (JSON), never free text soup.
- The three pillars together: metrics, logs, traces.
- Observability is a product feature, budget for it.

## Anti-patterns to retire
- Alerting on CPU while the SLO is latency.
- `grep` across 40 servers during an incident.
- Dashboards nobody has opened in a year.
- Logs at DEBUG in production "temporarily" for months.

## Success criteria
- Can answer "is the system healthy?" in under 30 seconds.
- An alert always maps to a runbook.
- Request latency breakdown visible without asking developers.

## Looking ahead
Advanced topics land in service mesh and SRE labs: golden signals,
error budgets, and trace-based debugging.
