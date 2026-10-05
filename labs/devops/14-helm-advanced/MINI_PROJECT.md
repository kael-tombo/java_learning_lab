# Mini Project — Helm Advanced

## Goal
Build an umbrella chart bundling an app + database + ingress subchart,
with pre-install migration hooks and CI-rendered templates.

## Steps
1. `helm create` three charts: app, api, shared-lib.
2. Make shared-lib a dependency of app (umbrella chart).
3. Parameterize global values; confirm subcharts inherit globals.
4. Add a `pre-install,pre-upgrade` hook job that runs migrations and
   fails the release when it errors.
5. Add a `post-install` hook that registers the release in an external
   catalog (echo + ConfigMap for the demo).
6. `helm dependency update`, then `helm install` and
   `helm upgrade` through several revisions.
7. Render every revision's manifests and diff two revisions.

## Acceptance criteria
- Umbrella installs all subcharts in one command.
- Hook failure aborts the release with a clear error.
- `helm history` and `helm get manifest` used to audit.

## Stretch goals
- Add an OCI push/pull of the chart.
- Use `helm unittest` for template assertions.

## Estimated time
75 minutes.
