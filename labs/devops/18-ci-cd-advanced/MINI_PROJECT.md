# Mini Project — CI/CD Advanced

## Goal
Extend lab 03's pipeline with a canary deploy and an automated rollback
on elevated error rates.

## Steps
1. Add a canary stage using Argo Rollouts or a manual traffic split.
2. Route 10% of traffic to the new version; run golden requests.
3. Watch error rate metric; auto-promote at <1% for 5 minutes.
4. Inject a bad deploy; confirm automatic abort and rollback.
5. Add an SBOM generation step and an image scan gate.
6. Sign the image (cosign) and verify before deploy stage.

## Acceptance criteria
- Canary rolls forward or back on metrics, not vibes.
- SBOM artifact attached to the release.
- Signed images required by admission control.

## Stretch goals
- Blue/green variant with DNS cutover.
- Progressive delivery across two regions.

## Estimated time
90 minutes.
