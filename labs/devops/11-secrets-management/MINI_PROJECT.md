# Mini Project — Secrets Management

## Goal
Move an app's database credentials out of the repo into a Kubernetes
Secret and volume mount, then rotate them without downtime.

## Steps
1. Remove credentials from the app config; read from env vars.
2. Create the secret: `kubectl create secret generic db-creds ...`
3. Mount as env vars in the Deployment.
4. Verify the app connects; creds absent from the image and repo.
5. Rotate: update the Secret, `kubectl rollout restart`, verify new
   connection works.
6. (Stretch) Run Vault dev server and inject via a Vault Agent sidecar.

## Acceptance criteria
- No secrets in `git log` or image layers.
- Rotation performed with a rollout restart and verified.
- Access to the Secret restricted by RBAC.

## Stretch goals
- Enable encryption at rest for Secrets.
- Set up External Secrets Operator syncing from a cloud secret store.

## Estimated time
45 minutes.
