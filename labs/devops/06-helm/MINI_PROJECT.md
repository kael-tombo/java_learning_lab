# Mini Project — Helm

## Goal
Write a Helm chart for the two-tier app from lab 02 and deploy it to two
environments with different values.

## Steps
1. `helm create myapp` — scaffold a chart.
2. Replace the deployment templates with api + web.
3. Parameterize image tags, replicas, and service types in `values.yaml`.
4. Create `values-dev.yaml` and `values-prod.yaml` overlays.
5. `helm template myapp ./myapp -f values-dev.yaml` and inspect output.
6. `helm install myapp-dev ./myapp -n dev --create-namespace`.
7. Upgrade with a new image tag; check `helm history`.
8. Roll back: `helm rollback myapp-dev 1`.

## Acceptance criteria
- Chart installs cleanly in a fresh namespace.
- dev and prod differ only by values files.
- Upgrade and rollback both work and are verified.

## Stretch goals
- Add `helm lint` and `helm test` steps.
- Publish the chart to a local OCI registry.

## Estimated time
60 minutes.
