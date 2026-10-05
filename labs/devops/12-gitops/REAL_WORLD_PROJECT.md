# Real-World Project — GitOps

## Scenario
Prod changes arrive via a mix of Slack approvals, Jenkins jobs, and
occasional laptop applies. Audits fail; rollback takes an hour.

## Requirements
- One config repo per cluster, protected branches.
- Argo CD/Flux installed and owning every namespace.
- Environments as directories/overlays in that repo.
- Break-glass procedure for emergencies only, with alerting.

## Phase plan
1. **Inventory**: list every deployment method currently in use.
2. **Bootstrap**: install operator; import existing apps as Application CRs.
3. **Strangler pattern**: move one team's apps first; freeze their old path.
4. **Repo structure**: `apps/<team>/<service>/{base,overlay dev,prod}`.
5. **Policies**: require PR reviews, CI validation of manifests before merge.
6. **Drill**: merge a bad manifest and watch reconciliation fail safely;
   then revert via git revert.

## Deliverables
- Config repo with documented layout.
- Migration plan per team.
- Break-glass runbook with alerting.

## Risks & mitigations
- Operator outage → document manual recovery.
- Too big too fast → one team at a time, retro each migration.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OpenGitOps principles:
  https://opengitops.dev/
- Argo CD getting started:
  https://argo-cd.readthedocs.io/en/stable/getting_started/

## Definition of done
- Zero unmanaged namespaces in prod.
- Audit trail fully from git history.
- Rollback via revert demonstrated end-to-end.
