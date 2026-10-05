# Mini Project — DevOps Deep

## Goal
Assemble the full modern delivery slice for one sample app: build,
sign, deploy via GitOps, secure with mesh, gate with a flag, and
protect with an SLO alert.

## Architecture
```
[ git ] -> [ CI: test, scan, sign, push ]
              |
              v
[ Argo CD ] -> [ Kubernetes + Helm ]
              |            |
        [ Vault sidecar ]  [ Istio/Linkerd mTLS ]
              |
              v
      [ Feature-flag service ]
              |
              v
      [ Prometheus SLO alert -> Slack ]
```

## Steps
1. Build image with the lab-01 Dockerfile; sign with cosign.
2. Push to a registry; record the digest.
3. Argo CD Application points at the signed digest.
4. Enable mesh mTLS across the app's namespaces.
5. Add a feature flag guarding one endpoint; toggle live.
6. Define an SLO and a burn-rate alert in Prometheus.
7. Drill: inject a 5% error rate; verify alert fires and a rollback
   path (revert PR -> Argo CD sync) exists.

## Acceptance criteria
- Signed image deployable only when admission verify passes.
- Flag toggles behavior without a redeploy.
- Burn alert fires during the drill.
- Rollback executed by merging a revert PR.

## Stretch goals
- Canary the change via Argo Rollouts instead of a full revert.
- Emit an SBOM and store it as an OCI artifact.

## Estimated time
2–3 hours across multiple sessions.
