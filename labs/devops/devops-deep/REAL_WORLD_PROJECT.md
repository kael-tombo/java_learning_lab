# Real-World Project — DevOps Deep

## Scenario
Medium-size org: 30 services, no shared deploy path, SLOs defined on a
wiki but nobody alerts on them, and a security review found later that
images are unsigned and prod has long-lived DB creds.

## Requirements
- One golden CI/CD path; language templates per runtime.
- All prod images signed and verified at admission.
- Dynamic DB credentials via Vault; static ones rotated.
- SLOs live as code; burn-rate alerts routed to on-call.
- Incident reviews blameless with tracked action items.

## Phase plan
1. **Golden path**: templates producing build -> sign -> deploy -> observe.
2. **GitOps rollout**: import existing services into Argo CD; dev first,
   prod after a freeze window.
3. **Security hardening**: admission verify, distroless images, read-only
   root filesystems, network policy defaults.
4. **Secrets migration**: Vault dynamic creds for the top 10 services;
   rotation drill; revoke static ones.
5. **SRE layer**: SLIs/SLOs per critical service; burn alerts; dashboards.
6. **Delivery safety**: canary on tier-1 services via Rollouts.
7. **Incident practice**: GameDay covering kill-a-node, bad deploy,
   and a blameless postmortem write-up.

## Deliverables
- Golden-path template repo with CI.
- Admission policy bundle.
- Vault policies and rotation log.
- SLO catalog and burn-alert rules.
- Incident response playbook and one real postmortem.

## Risks & mitigations
- Big scope → one team and one service at a time; iterate monthly.
- Metric disputes → define SLIs with service owners, not infra alone.
- Tool fatigue → the golden path must beat bespoke setup time.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- CNCF project docs — Argo CD and Argo Rollouts:
  https://argoproj.github.io/cd/
- Google SRE book — error budgets and alerting:
  https://sre.google/workbook/alerting-on-slos/

## Definition of done
- Tier-1 services: signed images, dynamic creds, canary option, burn alert.
- One GameDay executed; postmortem action items tracked and reviewed.
- Rollback demonstrated via git revert -> GitOps sync.
