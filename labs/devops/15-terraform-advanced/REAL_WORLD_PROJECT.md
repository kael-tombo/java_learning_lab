# Real-World Project — Terraform Advanced

## Scenario
Multi-account infrastructure is managed by different conventions per
team; audits fail on missing tags and unapproved instance types; a
refactor project stalled because state surgery was too risky.

## Requirements
- A module registry with version pinning.
- Standardized tags enforced via policy-as-code.
- Per-account, per-env state with locking.
- Safe refactor path using move/import/removed blocks.

## Phase plan
1. **Standards RFC**: tags, naming, state layout, module rules.
2. **Module registry**: published modules with semver and changelogs.
3. **Policy gates**: conftest/OPA in CI for tags, SKUs, encryption.
4. **Refactor pilot**: use move+import to reorganize one env without
   downtime.
5. **Cost controls**: tag compliance feeds chargeback reports.
6. **Review ritual**: architecture review for new module consumers.

## Deliverables
- Registry doc and versioning policy.
- Policy bundle in CI.
- Refactor runbook with imported/moved examples.

## Risks & mitigations
- State surgery fear → rehearse on a copy of state.
- Policy fatigue → start with three golden rules, expand slowly.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Terraform docs — moved blocks:
  https://developer.hashicorp.com/terraform/language/block/moved
- Conftest docs — testing Terraform plans:
  (link removed)

## Definition of done
- CI blocks non-compliant plans.
- One env refactored with zero resource replacement surprises.
- Audit tags present on 100% of resources.
