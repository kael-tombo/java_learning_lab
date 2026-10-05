# Real-World Project — Helm Advanced

## Scenario
Forty charts have diverged; fixes land in one but not the others. Hook
jobs fail silently in prod and rollbacks skip data migrations.

## Requirements
- Shared library chart (labels, probes, servicemonitors, networkpolicy).
- One umbrella chart per product, embedding app charts from teams.
- CI gates: lint, kubeval, install-test in kind, plus changelog.
- Deprecation/versioning policy published.

## Phase plan
1. **Extract common patterns** into the library chart via helpers.
2. **Migrate charts** to the library one product at a time.
3. **Hook hygiene**: idempotent migration jobs, TTL after finish, clear
   failure semantics documented.
4. **CI factory**: ct lint + ct install for every chart PR.
5. **Release process**: semver bumps, chartmuseum/OCI publishing, notes.
6. **Rollback drill**: upgrade with a bad hook; verify hook failure
   blocks and history shows failed release.

## Deliverables
- Library chart with usage docs.
- CI workflow for chart validation.
- Versioning and deprecation policy.

## Risks & mitigations
- Library upgrade breaks all charts → staged rollout, canary one product.
- Hook edge cases → document every hook's lifecycle.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Helm docs — hooks:
  https://helm.sh/docs/topics/charts_hooks/
- helm-unittest plugin docs:
  https://github.com/helm-unittest/helm-unittest

## Definition of done
- CI gates green on all chart PRs.
- At least one product fully on the library chart.
- Rollback drill documented.
