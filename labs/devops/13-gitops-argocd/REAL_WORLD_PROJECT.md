# Real-World Project — Argo CD

## Scenario
Argo CD is installed, but every team shares one project with admin RBAC,
syncs are fully automated with no guardrails, and nightly incidents hit
prod because a YAML typo slipped through.

## Requirements
- Per-team AppProjects with least-privilege RBAC.
- Automated sync to dev; gated sync to prod.
- CI validation (kubeconform/conftest) before merge.
- Notifications on health/sync transitions.

## Phase plan
1. **Harden RBAC**: map team groups to projects; remove cluster-wide admins.
2. **Policy gates**: add conftest rules (no latest, resources required).
3. **Environment tiers**: dev auto-sync, prod manual sync windows.
4. **Notifications**: route Degraded/Healthy transitions to on-call.
5. **Secret hygiene**: cluster credentials in sealed secrets/external secrets.
6. **Upgrade rehearsal**: staging Argo CD upgrade and rollback.

## Deliverables
- AppProject per team with documented RBAC.
- CI policy ruleset.
- Notification routing config as code.

## Risks & mitigations
- Auto-sync blasts a bad change → tiered sync policies.
- Project sprawl → templates for new teams.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Argo CD docs — user management and RBAC:
  https://argo-cd.readthedocs.io/en/stable/user-management/
- Argo CD docs — application lifecycle and sync:
  https://argo-cd.readthedocs.io/en/stable/user-guide/applications/

## Definition of done
- CI blocks policy-violating manifests.
- Prod deploys require an explicit sync action.
- Upgrade rehearsal passed in staging.
