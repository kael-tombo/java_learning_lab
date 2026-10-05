# Mini Project — Platform Engineering

## Goal
Ship a tiny internal developer platform: a service scaffolder that
generates repo, CI, Helm chart, and GitOps app in one run.

## Steps
1. Create a template repo: app code, Dockerfile, CI pipeline, Helm chart.
2. Write a script (`new-service.sh` or Backstage software template) that
   clones the template, renames placeholders, and pushes a new repo.
3. Wire the repo to Argo CD via an app-of-apps pattern.
4. Run the script twice; confirm two services deploy independently.
5. Add a golden-path dashboard: deploy status and SLO per service.
6. Document the one-page "how to run a service" for developers.

## Acceptance criteria
- `new-service` produces a working deployed service.
- Each service has CI + image + Helm + GitOps app.
- Dashboard shows both services.

## Stretch goals
- Add preview environments per PR via Argo CD ApplicationSets.
- Integrate a developer portal (Backstage) catalog entry for each service.

## Estimated time
90 minutes.
