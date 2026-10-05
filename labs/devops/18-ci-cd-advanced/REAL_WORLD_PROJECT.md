# Real-World Project — CI/CD Advanced

## Scenario
Deploys are high-ceremony, monthly events. Two recent incidents were
caused by unsigned images and a bad config that CI never validated.

## Requirements
- Progressive delivery (canary) on tier-1 services.
- Signed images enforced at admission.
- SBOMs attached to every release.
- Automatic rollback on SLO burn.

## Phase plan
1. **Pipelines-as-code factory**: shared pipeline templates per language.
2. **Canary pilot**: one service on Argo Rollouts with auto-analysis.
3. **Supply chain**: cosign sign + verify, syft SBOM, grype scan.
4. **Admission**: policy controller blocking unsigned images.
5. **Rollback path**: auto-abort on burn rate; tested monthly.
6. **Metrics**: deployment frequency, lead time, MTTR dashboards.

## Deliverables
- Shared pipeline templates repo.
- Rollout manifests with analysis templates.
- Admission policy bundle.

## Risks & mitigations
- Analysis false positives → tune thresholds with staging data.
- Adoption friction → pair one team, document wins.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Argo Rollouts docs — analysis and canary:
  https://argoproj.github.io/rollouts/
- SLSA framework — software supply chain levels:
  https://slsa.dev/

## Definition of done
- Tier-1 services canary by default.
- Unsigned images blocked in prod.
- MTTR reduced and measured.
