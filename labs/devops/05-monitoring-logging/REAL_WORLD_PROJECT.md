# Real-World Project — Monitoring & Logging

## Scenario
A growing SaaS discovers outages from Twitter, not from their own
monitoring. Logs live on individual pods, metrics are noisy, and nobody
knows which alerts matter.

## Requirements
- Centralized metrics (Prometheus/Mimir), logs (Loki/ELK), traces (Tempo/Jaeger).
- SLOs defined per user-facing service.
- Alerts tied to SLOs with runbooks.
- Retention and cost limits agreed.

## Phase plan
1. **SLO workshop**: pick one service; define availability and latency SLOs.
2. **Metrics pipeline**: Prometheus or managed equivalent scraping all
   services; golden-signals dashboards per service.
3. **Log pipeline**: structured JSON logs shipped centrally; a saved
   query per service for top errors.
4. **Tracing**: OpenTelemetry instrumentation on critical paths; trace
   id injected into logs.
5. **Alerting**: burn-rate alerts on SLO violations; route to PagerDuty/on-call.
6. **Runbooks**: every alert links to a documented response.

## Deliverables
- SLO definitions for the chosen service.
- Dashboards + alert rules committed as code.
- Runbook index.

## Risks & mitigations
- Alert fatigue → review every alert quarterly; delete noisy ones.
- Cardinality explosion → limit label values; document budgets.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Prometheus docs — querying and alerting:
  https://prometheus.io/docs/prometheus/latest/querying/basics/
- Grafana docs — dashboards:
  https://grafana.com/docs/grafana/latest/dashboards/

## Definition of done
- At least one burn-rate alert fired in a drill.
- On-call can locate failing traces without asking the app team.
