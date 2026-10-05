# Mini Project — Monitoring & Logging

## Goal
Stand up a local Prometheus + Grafana + Loki stack and observe one app.

## Steps
1. Run Prometheus, Grafana, and Loki via docker compose.
2. Point Prometheus at the app's `/metrics` endpoint
   (add a metrics client library if needed).
3. Create a Grafana dashboard with request rate and error rate panels.
4. Send app logs to Loki; query them with LogQL in Grafana.
5. Add one alert rule: error rate > 5% for 2 minutes.
6. Trigger errors and watch the alert fire.

## Acceptance criteria
- Grafana shows live metrics from the app.
- Logs are queryable by label and correlated with the deploy version.
- At least one alert rule exists and has fired during testing.

## Stretch goals
- Add OpenTelemetry traces between two services.
- Build a "golden signals" dashboard template.

## Estimated time
60 minutes.
