# Real-World Project — Helm

## Scenario
Each team maintains its own bespoke deployment manifests. A platform
upgrade touches 60 folders by hand and still misses three.

## Requirements
- A small set of official platform charts.
- Teams consume charts, they don't fork them.
- Upgrades via `helm upgrade` with tested defaults.
- Deprecated templates removed on a schedule.

## Phase plan
1. **Consolidate**: merge the top five deployment patterns into shared charts.
2. **Standardize values**: every team supplies values, never edits templates.
3. **CI for charts**: lint, template-render diff, and install test in kind.
4. **Versioning policy**: semver charts, changelog, deprecation window.
5. **Rollout plan**: canary one team, then fleet-wide with a comms plan.
6. **Guardrails**: admission check requiring chart `appVersion` labels.

## Deliverables
- Helm chart repo with CI.
- Migration guide per team.
- Decommissioning list for old bespoke manifests.

## Risks & mitigations
- Chart breaking changes → two-version support window.
- Team resistance → embed a platform engineer in the first migration.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Helm docs — chart best practices:
  https://helm.sh/docs/topics/chart_best_practices/
- Helm docs — CLI reference:
  https://helm.sh/docs/helm/helm/

## Definition of done
- ≥ 80% of services on shared charts.
- Platform upgrade executed via chart bump only.
